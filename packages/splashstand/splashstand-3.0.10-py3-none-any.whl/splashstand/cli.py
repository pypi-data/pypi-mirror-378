import asyncio
import json
from contextlib import suppress
from enum import Enum
from pathlib import Path
from shlex import split
from shutil import rmtree
from subprocess import run as execute

import jinja2_inflection  # type: ignore  # noqa
from acb.actions.encode import dump, load
from acb.adapters import import_adapter, root_path, tmp_path
from acb.adapters.dns._base import DnsRecord
from acb.console import console
from acb.depends import depends
from fastblocks.cli import cli, dev, run  # type: ignore  # noqa

# cli = typer.Typer(rich_markup_mode="rich")

splashstand_path = Path(__file__).parent

app_path = Path.cwd()

if Path.cwd() == splashstand_path:
    raise SystemExit(
        "SplashStand can not be run in the same directory as SplashStand itself."
    )


class BumpOption(str, Enum):
    micro = "micro"
    minor = "minor"
    major = "major"

    def __str__(self) -> str:
        return self.value


@cli.command()
def get_revisions():
    config = depends.get()
    revisions = execute(
        f"gcloud run revisions list --service {config.app.name} "
        # f"--sort-by ~last_deployed_time "
        f"--format json".split(),
        text=True,
        capture_output=True,
    ).stdout
    # print(revisions)
    revisions = [v["metadata"]["name"] for v in json.loads(revisions)]
    return revisions


@cli.command()
def clean_revisions() -> None:
    revisions = get_revisions()
    if len(revisions) > 4:
        for revision in revisions[4:]:
            # logger.info(f"Deleting:  {revision}")
            execute(f"gcloud run revisions delete {revision} --quiet".split())


@cli.command()
def clean_builds() -> None:
    config = depends.get()
    builds = execute(
        "gcloud builds list --sort-by ~create_time --format json".split(),
        text=True,
        capture_output=True,
    ).stdout
    registry = f"gcr.io/{config.app.project}/{config.app.name}"
    builds = [b for b in json.loads(builds) if registry in b["images"][0]][4:]
    for b in builds:
        with suppress(KeyError):
            # pprint(b)
            digest = b["results"]["images"][0]["digest"]
            # print(digest)
            execute(
                f"gcloud container images delete {registry}@{digest} "
                f"--force-delete-tags --quiet".split()
            )


def clean() -> None:
    clean_revisions()
    clean_builds()


def set_keepwarm() -> None:
    config = depends.get()
    comm = split(
        f"gcloud scheduler jobs create http {config.app.name}-keepwarm "
        f'--schedule="*/4 * * * *" '
        f'--http-method=GET --uri="https://{config.app.domain}" '
        f'--time-zone="America/Los_Angeles"'
    )
    execute(comm)


@cli.command()
def reset(debug: bool = False) -> None:
    if debug:
        debug_file = root_path / "settings" / "debug.yml"
        debug_settings = load.yaml(debug_file)
        for k in debug_settings:
            debug_settings[k] = False
        dump.yaml(debug_settings, debug_file)


@cli.command()
def create(builder: bool = False) -> None:
    config = depends.get()
    if builder:
        execute(f"docker build . -t {config.app.name}_builder".split())
    # else:
    #     name = input("App name: ")
    #     app_name = AppSettings().cloud_compliant_app_name(name)
    #     print(f"App name will be:  {app_name}")
    #     ok = input("Proceed (y/n)?  ")
    #     if not ok.lower().startswith("y"):
    #         raise SystemExit
    #     if base_path.exists() or app_name == "splashstand":
    #         raise SystemExit("Application directory exists - project creation stopped")
    #     # title = input("Title: ")
    #     # domain = input("Domain (ie splashstand.org): ")
    #     # if not domain:
    #     #     domain = f"{app_name}.splashstand.com"
    #     # mail_domain = input(f"Mail domain [{domain}]: ")
    #     # if not mail_domain:
    #     #     mail_domain = domain
    #     # admin_email = input("Admin email [admin@splashstand.com]: ")
    #     # if not admin_email:
    #     #     admin_email = "admin@splashstand.com"
    #     # app_pwa_name = input("PWA app name: ")
    #     # admin_pwa_name = input("PWA admin name: ")
    #     # gmail_enabled = False
    #     # is_gmail_enabled = input("Use GMail MX servers [no]: ")
    #     # if is_gmail_enabled.lower().startswith("y"):
    #     #     gmail_enabled = True
    #     # mail_yml = app_dir / "mail.yml"
    #     # mail_yml.touch()
    #     # mail_yml.write_text(f"admin: {admin_email}")
    #     # mail_yml.write_text(f"info: admin@{mail_domain}")
    #
    #     return app_name


@cli.command()
def add_custom_domain() -> None:
    config = depends.get()
    dns = depends.get()
    dns.create_zone()
    domains = execute(
        "gcloud beta run domain-mappings list --format json".split(),
        text=True,
        capture_output=True,
    ).stdout
    domains = json.loads(domains)
    domains = [d["metadata"]["name"] for d in domains]
    new_records = []
    www_domain = f"www.{config.app.domain}"
    if config.app.domain not in domains:
        execute(
            f"gcloud beta run domain-mappings create --service {config.app.name} "
            f" --domain "
            f"{config.app.domain}".split()
        )
    if len(config.app.domain.split(".")) < 3 and not config.app.domain.endswith(
        ".splashstand.net"
    ):
        if www_domain not in domains:
            execute(
                f"gcloud beta run domain-mappings create --service {config.app.name} "
                f"--domain "
                f"{www_domain}".split()
            )
        a_records = execute(
            f"gcloud beta run domain-mappings describe --domain "
            f"{config.app.domain} --format json".split(),
            text=True,
            capture_output=True,
        ).stdout
        a_records = json.loads(a_records)
        a_records = a_records["status"]["resourceRecords"]
        a_ips = []
        aaaa_ips = []
        for record in a_records:
            if record["type"] == "A":
                a_ips.append(record["rrdata"])
            elif record["type"] == "AAAA":
                aaaa_ips.append(record["rrdata"])
        if a_ips:
            record = DnsRecord(name=config.app.domain, type="A", rrdata=a_ips)
            new_records.append(record)
        if aaaa_ips:
            record = DnsRecord(name=config.app.domain, type="AAAA", rrdata=aaaa_ips)
            new_records.append(record)
        if len(config.app.domain.split(".")) < 3:
            www_record = DnsRecord(
                name=www_domain, type="CNAME", rrdata=["ghs.googlehosted.com"]
            )
            new_records.append(www_record)
    # elif config.app.domain.endswith(".splashstand.net"):
    #     app_record = DnsRecord(
    #         name=config.app.domain, type="CNAME", rrdata=["ghs.googlehosted.com"]
    #     )
    #     new_records.append(app_record)
    #     dns.zone = dns.client.zone(config.app.name, "splashstand.net.")
    # pprint(new_records)
    if new_records:
        asyncio.run(dns.create_records(new_records))


def build_revision(deployed: bool = True) -> None:
    # add option for custom builder
    config = depends.get()
    rmtree(tmp_path)
    console.print("Tmp directory removed")
    try:
        execute(
            "uv pip freeze --exclude-editable > requirements.txt".split(),
            capture_output=True,
            text=True,
        )
        success = "uv"
    except ModuleNotFoundError:
        execute("pip freeze >requirements.txt".split(), capture_output=True, text=True)
        success = "pip"
    console.print(f"Generated requirements.txt with {success}")
    execute(
        f"pack build --builder=splashstand_builder --workspace app/{config.app.name}"
        f" --env PYTHON_PATH=/app:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
        f":/sbin:/bin --env DEPLOYED={str(deployed).lower()} --publish"
        f" us-central1-docker.pkg.dev/{config.app.project}"
        f"/splashstand3/{config.app.name}".split()
    )
    # execute(
    #     f"gcloud builds submit --tag us-docker.pkg.dev/{config.app.project}/{config.app.name}".split()
    # )


def deploy_revision(deployed: bool = True, bump: str = "micro") -> None:
    config = depends.get()
    import_adapter("sql")
    settings = dict(
        # timeout="300",
        memory="512Mi",
        region="us-central1",
        # cpu="1000m",
        max_instances="100",
        set_cloudsql_instances=f"{config.app.project}:{config.app.region}:{config.sql.cloudsql_instance}",
    )
    execute(["pdm", "bump", bump])
    execute(
        f"gcloud beta run deploy {config.app.name} "
        f"--image {settings['region']}-docker.pkg.dev/{config.app.project}/splashstand3/{config.app.name}:latest "
        f"--max-instances {settings['max_instances']} --platform managed "
        f"--set-cloudsql-instances {settings['set_cloudsql_instances']} "
        f"--vpc-connector splashstand3-connector "
        f"--service-min-instances 1 "
        f"--set-env-vars DEPLOYED={str(deployed).lower()} "
        f"--memory {settings['memory']} --allow-unauthenticated".split()
    )


@cli.command()
def deploy(build: bool = True) -> None:
    # reset_debug(app_dir)
    if build:
        build_revision()
    deploy_revision()
    clean()
    add_custom_domain()
    set_keepwarm()
    # setup_mail()
