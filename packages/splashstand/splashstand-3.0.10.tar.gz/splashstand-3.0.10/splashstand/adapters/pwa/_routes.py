from acb.adapters import import_adapter
from acb.debug import debug
from acb.depends import depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette_async_jinja import JsonResponse

Templates, Pwa = import_adapter()  # type: ignore


@depends.inject
def manifest(request: Request, pwa: Pwa = depends()) -> Response:
    debug(request)
    return JsonResponse(content=pwa.manifest)


@depends.inject
async def serviceworker(
    request: Request,
    templates: Templates = depends(),
) -> Response:
    debug(request)
    return await templates.app.render_template(request, "serviceworker.js")


routes = [
    Route("/manifest.json", manifest, methods=["GET"]),
    Route("/serviceworker.js", serviceworker, methods=["GET"]),
]
