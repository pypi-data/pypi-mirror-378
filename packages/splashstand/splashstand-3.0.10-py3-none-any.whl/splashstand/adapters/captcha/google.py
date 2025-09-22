import typing as t

from acb.adapters import import_adapter
from acb.config import Config
from acb.depends import depends
from acb.logger import Logger
from google.cloud import recaptchaenterprise_v1 as recaptcha  # type: ignore
from pydantic import SecretStr
from starlette.routing import Router

from ._base import CaptchaBase, CaptchaBaseSettings

# from starlette.responses import Response
# from starlette_async_jinja import JsonResponse


Requests = import_adapter()


class CaptchaSettings(CaptchaBaseSettings):
    @depends.inject
    def __init__(self, config: Config = depends(), **values: t.Any) -> None:
        super().__init__(**values)
        self.production_key = config.recaptcha.production_key
        self.dev_key = config.recaptcha.dev_key
        self.threshold = self.threshold if config.deployed else 0.1


class Captcha(CaptchaBase):
    router: Router = Router()
    logger: Logger = depends()

    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }

    async def init(self) -> None:
        self.logger.info("Recaptcha initialized.")

    async def annotate_assessment(self) -> None:
        client = recaptcha.RecaptchaEnterpriseServiceAsyncClient()
        request = recaptcha.AnnotateAssessmentRequest(
            name=self.config.app.name,
        )
        response = await client.annotate_assessment(request=request)
        self.logger.debug(f"Captcha Response: {response}")

    # @staticmethod

    # def request(payload):
    #     params = urllib.parse.urlencode(payload)
    #     conn = http.client.HTTPSConnection("www.google.com")
    #     conn.request("POST", "/recaptcha/api/siteverify", params, headers)
    #     return json.loads(conn.getresponse().read())
    #
    @depends.inject
    async def is_a_human(
        self,
        secret_key: SecretStr,
        response_token: str,
        action: t.Optional[str] = None,
        threshold: t.Optional[int | float | str] = None,
        requests: Requests = depends(),
    ) -> tuple[bool, int]:
        threshold = float(threshold or self.config.captcha.threshold)
        payload = {"secret": secret_key.get_secret_value(), "response": response_token}
        response = await requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            params=payload,
            headers=self.headers,
            timeout=10,
        ).json()
        if not response["success"]:
            self.logger.warning("Failed communication")
            return False, 101
        elif response["score"] >= threshold:
            if action and response.get("action", None):
                if action != response["action"]:
                    self.logger.warning(
                        f"Bad action name: sent {action}, expected {response['action']}"
                    )
                    return False, 102
            self.logger.debug("Recaptcha verified human.")
            return True, 100
        else:
            self.logger.warning(
                f"Recaptcha threshold failed: got {response['score']}, expected >"
                f" {threshold}"
            )
            return False, 103

    async def recaptcha3(
        self,
        secret_key: SecretStr,
        response_token: str,
        action: t.Optional[str] = None,
        threshold: t.Optional[int | float | str] = None,
    ) -> bool:
        threshold = float(threshold or self.config.captcha.threshold)
        if not self.config.deployed or self.config.debug.production:
            threshold = 0.01
        ok, _ = await self.is_a_human(secret_key, response_token, action, threshold)
        return ok

    # @router.get("/verify/<action>/<token>")
    # async def verify(self, action: str, token: str) -> Response:
    #     threshold = float(self.config.recaptcha.threshold)
    #     if not self.config.deployed or self.config.debug.production:
    #         threshold = 0.01
    #     approved = self.recaptcha3(
    #         secret_key=self.config.google.recaptcha.private_key,
    #         response_token=token,
    #         action=action,
    #         threshold=threshold,
    #     )
    #     if approved:  # type: ignore
    #         return JsonResponse(dict(allowed=True, action=action))
    #     return JsonResponse(dict(allowed=False, action=action))


depends.set(Captcha)
