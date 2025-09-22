import asyncio
import re
import typing as t
from contextlib import suppress
from datetime import timedelta

import nest_asyncio
import uuid_utils as uuid
from acb.actions.encode import load
from acb.adapters import import_adapter
from acb.config import Config
from acb.debug import debug
from acb.depends import depends
from anyio import Path as AsyncPath
from asgi_htmx import HtmxRequest
from fastblocks.applications import FastBlocks
from google.oauth2.service_account import Credentials
from inflection import camelize, pluralize, titleize, underscore
from markupsafe import Markup
from pydantic import AnyUrl, EmailStr
from sqladmin import Admin as SqlAdmin
from sqladmin import expose
from sqladmin.authentication import login_required  # type: ignore
from sqladmin.models import ModelView  # type: ignore
from sqlmodel import SQLModel, select
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_async_jinja import JsonResponse

from ._base import AdminBase, AdminBaseSettings

# from wtforms.fields import TextAreaField
# from wtforms.widgets import TextArea
# from wtforms.fields.datetime import DateTimeField

nest_asyncio.apply()

Auth, Schemas, Storage, Models, Sql, Templates, Pwa = import_adapter()  # type: ignore


class AdminSettings(AdminBaseSettings):
    style: str = "webawesome"
    roles: t.Optional[list[str]] = ["admin", "owner", "contributor", "viewer"]
    favicon: t.Optional[str] = "SSOutlineTransparent1024-blue.png"
    icon: t.Optional[str] = "IconEditSS1024px-white.png"
    nav_icon: t.Optional[str] = "IconEditSS1024px-blue.png"
    url: t.Optional[str] = "/dashboard/"
    logo: t.Optional[str] = "SSComboOutline1024px-blue.png"
    logo_url: t.Optional[AnyUrl] = None
    login_logo: t.Optional[str] = "SSComboOutline1024px-blue.png"
    font: str = "Poppins"
    email: str = "admin@example.com"
    gmail: str = "myemail@gmail.com"
    ios_id: t.Optional[str] = None
    icons: t.Optional[dict[str, str]] = dict(
        content="list",
        store="store",
        site="globe",
        preview="eye",
        analytics="chart-line",
        storage="archive",
        users="users",
        person="users",
        roles="user-shield",
        theme="code",
        cache="piggy-bank",
        change_password="lock",  # nosec B106
        help="question-circle",
        show="eye",
        hide="eye-slash",
        delete="trash",
        top="plus",
        plus_15="angle-double-up",
        plus_5="angle-up",
        minus_5="angle-down",
        minus_15="angle-double-down",
        bottom="minus",
    )
    manifest: t.Optional[dict[str, t.Any]] = None

    def __init__(self, **data: t.Any) -> None:
        super().__init__(**data)
        self.manifest = dict(
            name="SplashBoard",
            short_name="SplashBoard",
            description=self.title,
            start_url=self.url,
            scope=self.url,
        )


class AdminModelView(ModelView):
    form_args = {}
    is_async = True
    page_size = 25
    page_size_options = [25, 50, 100, 200]
    can_delete = True
    details_template = "details.html"
    list_template = "list.html"
    form_widget_args = dict(google_uid=dict(readonly=True), picture=dict(readonly=True))

    # if not current_user().has_role("admin") or not current_user().has_role("owner"):
    #     form_widget_args.gmail = dict(readonly=True)
    #     form_widget_args.role = dict(readonly=True)

    # column_type_formatters = dict(
    #     date=_datetime_format,
    #     # image=_list_image_thumbnail,
    #     # picture=_list_image_thumbnail,
    #     # photo=_list_image_thumbnail,
    #     # video=_list_video_thumbnail,
    # )

    @depends.inject
    def is_accessible(
        self,
        request: Request,
        auth: Auth = depends(),
    ) -> bool:  # type: ignore
        return auth.current_user.is_authenticated(request)

    def is_visible(self, request: Request) -> bool:
        return True

    @depends.inject
    async def get_entries(
        self,
        model: SQLModel,
        sql: Sql = depends(),
    ) -> list[t.Any]:
        async with sql.async_session() as session:
            entries_query = select(model)  # type: ignore
            result = await session.execute(entries_query)
            return result.all()

    async def after_model_change(
        self,
        data: dict[str, t.Any],
        model: t.Any,
        is_created: bool,
        request: Request,
    ) -> None:
        if is_created:
            entries = await self.get_entries(model)
            with suppress(AttributeError):
                for entry in entries:
                    if entry.position == 99999:
                        entry.position = 1
                    else:
                        entry.position = entry.position + 1
                    entry.save()

    async def after_model_delete(self, model: t.Any, request: Request) -> None:
        with suppress(AttributeError):
            rm_position = model.position
            entries = await self.get_entries(model)
            for entry in entries:
                if entry.position > rm_position:
                    entry.position = entry.position - 1
                    entry.save()

    async def on_model_change(
        self,
        data: dict[str, t.Any],
        model: t.Any,
        is_created: bool,
        request: Request,
    ) -> None:
        if "youtube_id" in vars(model) and model.youtube_id:
            for prefix in (
                "https://youtu.be/",
                "http://youtu.be/",
                "https://www.youtube.com/watch?v=",
                "http://www.youtube.com/watch?v=",
            ):
                model.youtube_id = model.youtube_id.lstrip(prefix)
            pattern = r"[&,?]t=(\d+)"
            start = re.search(pattern, model.youtube_id)
            if start and ((not model.start) or model.start == "00:00:00"):
                model.start = timedelta(seconds=int(start.group(1)))
            pattern = r"[&,?]t=(\d+).*"
            model.youtube_id = re.sub(pattern, "", model.youtube_id)
        # if "spotify_id" in vars(model) and model.spotify_id:
        #     ...
        # if "archive_id" in vars(model) and model.archive_id:
        #     ...
        # if "soundcloud_id" in vars(model) and model.soundcloud_id:
        #     ...
        # if "bandcamp_id" in vars(model) and model.bandcamp_id:
        #     ...


@depends.inject
async def create_view(
    app_model: type[SQLModel],
    schemas: Schemas = depends(),
    config: Config = depends(),
) -> t.Any:  # type: ignore
    last_fields = ["visible", "maintainer", "editor", "date_created", "date_modified"]
    schema = getattr(schemas, underscore(app_model.__name__))
    first_fields = [f for f in app_model.model_fields if f in schemas.thing._properties]
    _fields = app_model.model_fields | app_model.__sqlmodel_relationships__
    # debug(schema._properties)
    debug(len(schema._properties))

    # debug(schema._types)

    # debug(schema._fields)
    # debug(len(schema._fields))
    # clip = getattr(schema, "clip", None)
    # if clip:
    #     debug(clip._fields)

    class cls(AdminModelView, model=app_model):  # type: ignore
        form_columns = [
            f
            for f in _fields
            if f in schema._properties
            and f not in first_fields
            and f not in last_fields
        ]
        column_details_list = first_fields + form_columns + last_fields
        form_columns = first_fields + form_columns + [last_fields[0]]

        # for name, field in _fields.items():  # noqa: FURB135
        #     form_kwargs = dict(
        #         label=titleize(
        #             field.alias or name.removesuffix("_id").removesuffix("_object")
        #         )
        #     )
        #     if hasattr(field, "required"):
        #         form_kwargs["validators"] = [DataRequired()]  # type: ignore
        #     form_args[name] = form_kwargs

        column_list = ["name"]
        if "position" in _fields:
            column_list.remove("position")
            column_default_sort = "position"
            column_sortable_list = ["position"]
            column_list.append("position")
        elif "published" in _fields:
            column_default_sort = ("published", True)
        elif "date" in _fields:
            column_default_sort = "date"
        else:
            column_default_sort = "name"
            column_sortable_list = ["name"]
        # column_details_list.extend(last_fields)

    cls.__name__ = f"{app_model.__name__}Admin"
    # cls.name = titleize(app_model.alias or app_model.__name__)
    cls.name = titleize(app_model.__name__)
    cls.name_plural = pluralize(cls.name)
    # cls.icon = f"fa-solid fa-{config.admin.icons[underscore(cls.name)]}"
    debug(cls.__name__)
    debug(cls.name)
    debug(cls.name_plural)
    debug(cls.form_columns)
    debug(cls.column_list)
    debug(cls.column_details_list)
    return cls


class Admin(SqlAdmin, AdminBase):  # type: ignore
    @depends.inject
    def __init__(
        self,
        app: Starlette = FastBlocks(),
        templates: Templates = depends(),
        **kwargs: t.Any,
    ) -> None:
        super().__init__(app, **kwargs)
        self.templates = templates.admin
        asyncio.run(self.create_views())

    @depends.inject
    async def init(
        self,
        models: Models = depends(),
        sql: Sql = depends(),
        templates: Templates = depends(),
    ) -> None:
        async def create_inital_admin_user(
            name: str,
            gmail: EmailStr,
            is_superuser: bool = False,
            role: str = "user",
            **kwargs: str,
        ) -> None:
            user = getattr(models.sql, "Person")(
                name=name, gmail=gmail, is_superuser=is_superuser, role=role, **kwargs
            )
            await user.save()

        async def get_initial_admin_user() -> t.Optional[t.Any]:
            async with sql.session as session:
                user_model = getattr(models.sql, "Person")
                user_query = select(user_model).where(  # type: ignore
                    user_model.gmail == self.config.admin.gmail  # type: ignore
                    and user_model.role == "admin"  # type: ignore
                )
                result = await session.execute(user_query)
                return result.one_or_none()

        if self.config.debug.admin:
            admin_user = await get_initial_admin_user()
            if admin_user is None:
                self.logger.debug("Creating admin superuser...")
                await create_inital_admin_user(
                    name="Default Admin",
                    gmail=self.config.admin.gmail,
                    is_superuser=True,
                    role="admin",
                )
                admin_user = await get_initial_admin_user()
            debug(admin_user)

    @depends.inject
    async def create_views(self, models: Models = depends()) -> None:  # type: ignore
        for model in [m for m in vars(models.sql).values() if issubclass(m, SQLModel)]:
            self.add_view(await create_view(model))
            self.logger.debug(f"Created {model.__name__} admin view")

    # @login_required
    # async def index(self, request: HtmxRequest) -> Response:
    #     """Index route which can be overridden to create dashboards."""
    #
    #     return await self.templates.TemplateResponse(request, "index.html")

    @t.override
    async def login(  # type: ignore
        self, request: Request
    ) -> t.Coroutine[t.Any, t.Any, t.Any] | RedirectResponse | None:
        if self.authentication_backend:
            context = {}
            authenticated = await self.authentication_backend.login(request)
            debug(authenticated)
            if authenticated:
                debug(request.url_for("admin:index"))
                return RedirectResponse(request.url_for("admin:index"), status_code=302)
            context["error"] = "Invalid credentials"
            return await self.templates.TemplateResponse(  # type: ignore
                request, "sqladmin/login.html", context, status_code=200
            )

    @login_required
    async def list(self, request: HtmxRequest) -> Response:
        """List route to display paginated Model instances."""
        await self._list(request)

        model_view = self._find_model_view(request.path_params["identity"])
        pagination = await model_view.list(request)
        pagination.add_pagination_urls(request.url)

        request_page = model_view.validate_page_number(
            request.query_params.get("page"), 1
        )

        if request_page > pagination.page:
            return RedirectResponse(
                request.url.include_query_params(page=pagination.page), status_code=302
            )

        context = {"model_view": model_view, "pagination": pagination}
        return await self.templates.TemplateResponse(
            request, model_view.list_template, context
        )

    @login_required
    async def details(self, request: Request) -> Response:
        """Details route."""
        await self._details(request)

        model_view = self._find_model_view(request.path_params["identity"])

        model = await model_view.get_object_for_details(request.path_params["pk"])
        if not model:
            raise HTTPException(status_code=404)

        context = {
            "model_view": model_view,
            "model": model,
            "title": model_view.name,
        }

        return await self.templates.TemplateResponse(
            request, model_view.details_template, context
        )

    @depends.inject
    @login_required
    @expose("/manifest.json", methods=["GET"])
    def manifest(
        request: Request,  # type: ignore
        pwa: Pwa = depends(),
        config: Config = depends(),
    ) -> Response:
        debug(request)
        resp = JsonResponse(pwa.manifest | config.admin.manifest)
        resp.headers["Content-Type"] = "application/json"
        resp.headers["Cache-Control"] = "max-age=4200, no-cache, must-revalidate"
        return resp

    @login_required
    @expose("/_update_position/<model>", methods=["POST"])  # type: ignore
    async def _update_position(
        self,
        request: Request,
        model_name: str,
        models: Models = depends(),
    ) -> JsonResponse:
        old_index = int(request.query_params.get("old_index"))  # type: ignore
        new_index = int(request.query_params.get("new_index"))  # type: ignore
        sql_model = getattr(camelize(model_name), models)
        debug(old_index, type(old_index))
        debug(new_index, type(new_index))
        moved_entry = sql_model.query.filter_by(position=old_index)[0]
        if old_index > new_index:
            increments = sql_model.query.filter(
                sql_model.position < old_index, sql_model.position >= new_index
            )
            for i, entry in enumerate(increments):
                entry.position = new_index + i + 1
                entry.save()
        else:
            decrements = sql_model.query.filter(
                sql_model.position <= new_index, sql_model.position > old_index
            )
            for i, entry in enumerate(decrements):
                entry.position = new_index - i - 1
                entry.save()
        moved_entry.position = new_index
        moved_entry.save()
        return JsonResponse({"position": new_index})

    @depends.inject
    @login_required
    @expose("/video_preview/<filename>")  # type: ignore
    def _video_preview(
        self,
        filename: str,
        storage: Storage = depends(),
    ) -> Markup:
        return Markup(  # nosec
            '<video width="1024" height="576" controls'
            ' poster=""><source src="{}" type="video/mp4">'
            "Your browser does not support the video "
            "tag.</video>".format(storage.media.get_url(filename))
        )

    @depends.inject
    @login_required
    @expose("/get_upload_url/<_type>/<_format>/<_extension>")  # type: ignore
    async def get_upload_url(
        self,
        _type: str,
        _format: str,
        _extension: str,
        storage: Storage = depends(),
    ) -> dict[str, str]:
        upload_credentials = Credentials.from_service_account_info(
            await load.json(self.config.app.google_upload_json),
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        upload_key = f"{uuid.uuid7()}.{_extension}"
        content_type = f"{_type}/{_format}"
        presigned_url = storage.get_signed_url(
            AsyncPath(upload_key)
        ).generate_signed_url(
            expiration=timedelta(seconds=120),
            content_type=content_type,
            method="PUT",
            credentials=upload_credentials,
        )
        return dict(url=presigned_url, key=upload_key)


depends.set(Admin)


@depends.inject
def get_file_input(field: t.Any, storage: Storage = depends()) -> str:
    if field.data and isinstance(field.data, str):
        cloud_fn = storage.media.get_url(field.data)
        # unique_id = field.data.split('.')[0]
        # if field.name == "image":
        #     cloud_fn = stor.media.get_url(resize(field.data, "240x", fit=1))
        html = (
            '<input id="{0}" name="{0}" type="file" '
            'class="file-upload-input" value="{1}" src="{2}"/>'.format(
                field.name, field.data, cloud_fn
            )
        )
    else:
        html = (
            '<input id="{0}" name="{0}" class="file-upload-input" type="file">'.format(
                field.name
            )
        )
    return Markup(html)  # nosec


# def _datetime_format(value: datetime) -> str:
#     return value.strftime("%a %b %d, %Y - %I:%M %p")

# class AdminKeys:
#     image_keys = dict(
#         # base_path=config.storage_pre,
#         namegen=encode_filename,
#         thumbnail_size=(240, 180, False),
#         allowed_extensions=["png", "jpg", "jpeg"],
#     )
#     video_keys = copy_keys(image_keys, dict(
#           allowed_extensions=["webm", "mp4", "m4v"]))
#     audio_keys = copy_keys(image_keys, dict(allowed_extensions=["m4a", "mp4"]))
#     doc_keys = copy_keys(image_keys, dict(allowed_extensions=["pdf", "doc"]))
#     icon_keys = copy_keys(image_keys, dict(thumbnail_size=(180, 180, False)))
#     # logo_keys = copy_keys(image_keys,
#     #                       dict(thumbnail_size=(240, 135, False)))


# class AdminCKTextAreaWidget(TextArea):
#     def __call__(self, field: str, **kwargs: t.Any) -> t.Any:
#         if kwargs.get("class"):
#             classes = kwargs["class"]
#             kwargs["class"] = classes + " ckeditor"
#         else:
#             kwargs.setdefault("class", "ckeditor")
#         return super(AdminCKTextAreaWidget, self).__call__(field, **kwargs)
#
#
# class AdminCKTextAreaField(TextAreaField):
#     widget: AdminCKTextAreaWidget = AdminCKTextAreaWidget()


# @depends.inject
# def _list_video_thumbnail(
#     model: SQLModel, storage: Storage = depends()  # type: ignore
# ) -> Markup | str:
#     if model.video:
#         input_id = model.video.split(".")[0]
#         video_type = model.video.split(".")[1]
#         return Markup(
#             '<video width="" height="" controls>'
#             '<source src="{}" type="video/{}" '
#             'preload="metadata" id="video-{}">'
#             "Your browser does not support the video tag."
#             "</video>".format(storage.media.get_url(model.video), video_type, input_id)
#         )
#     elif (
#         "youtube_id" in vars(model) and getattr(model, "youtube_id") and not model.video
#     ):
#         return Markup(
#             '<div class="youtube-iframe" '
#             'style="position:relative;padding-top:56.25%;">'
#             '<iframe width="" height="" '
#             'src="https://www.youtube.com/embed/{0}" '
#             'frameborder="0" allowfullscreen '
#             'style="position:absolute;top:0;left:0;width:100%;height:100%;" '
#             'id="youtube-{0}">'
#             "</iframe>"
#             "</div>"
#         ).format(model.youtube_id)
#     return ""
#
#
# def _list_image_thumbnail(model: SQLModel) -> str | Markup:
#     image = None
#     try:
#         image = model.image
#     except AttributeError:
#         try:
#             image = model.photo
#         except AttributeError:
#             with suppress(AttributeError):
#                 image = model.picture
#     if not image:
#         if "video" in vars(model):
#             return _list_video_thumbnail(model)
#         return ""
#     input_id = image.split(".")[0]
#     # thumb = resize(image, "x240", fit=1)
#     return Markup(
#         '<a class="image-popup-link" href="{}"><img '
#         'id="image-{}" class="list-image" src="{}" />'
#         "</a>".format(model.image.url, input_id, model.image.thumbnail_url)
#     )


#
#
# class CustomView(BaseView):
#     name = "Custom Page"
#     icon = "fa-chart-line"
#
#     @expose("/custom", methods=["GET"])
#     def custom_page(self, request):
#         return await self.templates.render_template(
#             "custom.html",
#             context={"request": request},
#         )

# def admin_template_args():
#     template_args = dict(
#         admin_module_icons=admin.module_icons,
#         admin_css=render_inline_css(admin_yml),
#     )
#     for t in (admin() / "js").iterdir():
#         template_args[f"admin_{t.stem.lower()}_js"] = str(t.resolve())
#     return template_args

# def render_admin(self, template, **kwargs):
#     # print(request.method)
#     # if request.method == "POST":
#     #     g.save_db = 1
#     template_args = dict(
#         admin_view=self,
#         admin_base_template=self.admin.base_template,
#         get_url=self.get_url,
#     )
#     kwargs.update(template_args)
#     kwargs.update(admin_template_args())
#     kwargs.update(self._template_args)
#     resp = ""
#     try:
#         template = render_template(template, **kwargs)
#     except UndefinedError:
#         cache_templates(admin())
#         template = render_template(template, **kwargs)
#     # if (deployed or debug.production or debug.css)
#           and request.path != self.get_url(
#     #         'cache.execute_view'):
#     if site.is_deployed or debug.production or debug.css:
#         template = remove_unused_css(template)
#     resp = make_response(template)
#     resp.headers["Cache-Control"] = "no-store, must-revalidate, max-age=0"
#     return resp

# elif "column_default_sort" in view_args.keys():
#     setattr(self, "column_default_sort", view_args["column_default_sort"])
# if "column_list" in view_args.keys():
#     column_list = view_args["column_list"]
#     if debug.position:
#         column_list.append("position")
#     if "visible" in fields:
#         column_list.append("visible")
#     setattr(self, "column_list", column_list)
# for field in fields:
#     if field.endswith("_url"):
#         self.form_extra_fields[field] = URLField(
#             field.replace("_", " ").title(), validators=[Optional(), URL()]
#         )
#     elif field.endswith("_phone"):
#         self.form_extra_fields[field] = TelField(
#             field.replace("_", " ").title(), validators=[Optional()]
#         )
# if "form_excluded_columns" in view_args.keys():
#     for field in view_args["form_excluded_columns"]:
#         fields.remove(field)
# for field in last_fields:
#     fields.remove(field)
# fields.extend(["visible"])
# fields.insert(0, "name")
# self.form_columns = fields

# super().__init__()

# def is_action_allowed(self, name):
#     if "position" in fields:
#         if name in (self.allowed_actions + self.position_actions):
#             return super(AdminModelView, self).is_action_allowed(name)
#     else:
#         if name in self.allowed_actions:
#             return super(AdminModelView, self).is_action_allowed(name)

# form_ajax_refs = {
#     "address": {
#         "fields": ("zip_code", "street"),
#         "order_by": ("id",),
#     }
# }

#     if ac.ckeditor_fields:
#         for f in ac.ckeditor_fields:
#             form_overrides[f] = AdminCKTextAreaField
#     if ac.select_fields:
#         for k, v in ac.select_fields.items():
#             # print(k, v)
#             for x, y in v.items():
#                 form_overrides[x] = Select2Field
#                 form_args[x] = dict(
#                     choices=[
#                         (c, c.replace("_", " ").title().replace(
#                         "Youtube", "YouTube"))
#                         for c in y
#                     ]
#                 )
#                 form_widget_args[x] = {"class": "select input"}
#     form_extra_fields = {
#         "image": PluginImageUploadField("Image", **ak.image_keys),
#         "picture": PluginImageUploadField("Picture", **ak.image_keys),
#         "photo": PluginImageUploadField("Photo", **ak.image_keys),
#         "video": AdminFileUploadField("Video", **ak.video_keys),
#         "audio": AdminFileUploadField("Audio", **ak.audio_keys),
#         "brochure": AdminFileUploadField("Brochure", **ak.doc_keys),
#         "email": EmailField("Email", validators=[Optional(), Email()]),
#         "google_email_field": EmailField(
#             "Google Email", validators=[Email(), Optional()]
#         ),
#         "facebook_email_field": EmailField(
#             "Facebook Email", validators=[Email(), Optional()]
#         ),
#         "youtube_id": StringField("YouTube ID"),
#     }

#     column_display_all_relations = True
#     for field in ac.datetime_fields:
#         form_extra_fields[field] = DateTimeField(
#             field.title().replace("_", " "),
#             validators=[DataRequired()],
#             format="%m-%d-%Y %I:%M %p",
#         )
#         form_widget_args[field] = {"data-date-format": ac.datetime_format}
#     allowed_actions = ["show", "hide", "delete"]
#     position_actions = ["top", "plus_15", "plus_5", "minus_5",
#           "minus_15", "bottom"]
#
#     def _available_media(self, model):
#         _avail = []
#         with suppress(AttributeError):
#             _avail = stor.media.list()
#             try:
#                 image_url = get_storage_media_url(model.image)
#             except AttributeError:
#                 try:
#                     image_url = get_storage_media_url(model.photo)
#                 except AttributeError:
#                     with suppress(AttributeError):
#                         image_url = get_storage_media_url(model.picture)
#             for media in _avail:
#                 if media == image_url:
#                     _avail.remove(media)
#         return _avail
#
#     def get_details_columns(self):
#         try:
#             only_columns = self.column_details_list
#               or self.scaffold_list_columns()
#         except NotImplementedError:
#             raise Exception("Please define column_details_list.")
#
#         columns = self.get_column_names(
#             only_columns=only_columns,
#             excluded_columns=self.column_details_exclude_list
#         )
#         new_list = []
#         end_fields = []
#         for c in columns:
#             if c[0] == "name":
#                 new_list.insert(0, c)
#             elif c[0] in [
#                 "created_by",
#                 "created_at",
#                 "last_edited_by",
#                 "last_edited_at",
#                 "visible",
#             ]:
#                 end_fields.append(c)
#             else:
#                 new_list.append(c)
#         new_list.extend(end_fields)
#         return new_list
#
#     def _get_list_value(
#         self, context, model, name, column_formatters, column_type_formatters
#     ):
#         column_fmt = column_formatters.get(name)
#         if column_fmt is not None:
#             value = column_fmt(self, context, model, name)
#         else:
#             value = self._get_field_value(model, name)
#         choices_map = self._column_choices_map.get(name, {})
#         if choices_map:
#             return choices_map.get(value) or value
#         type_fmt = None
#         for typeobj, formatter in column_type_formatters.items():
#             if isinstance(value, typeobj):
#                 type_fmt = formatter
#                 break
#         if type_fmt is not None:
#             value = type_fmt(self, value)
#         with suppress(AttributeError):
#             value = value.all()
#             value = ", ".join([str(v) for v in value])
#         return value
#
#     # Model handlers
#     def create_model(self, form):
#         try:
#             model = self.model()
#             form.populate_obj(model)
#             model.save()
#             self._on_model_change(form, model, True)
#         except Exception as ex:
#             if not self.handle_view_exception(ex):
#                 flash(
#                     gettext("Failed to create record. %(error)s", error=str(ex)),
#                     "error",
#                 )
#                 ca.self.logger.exception("Failed to create record.")
#             self.session.rollback()
#             return False
#         else:
#             self.after_model_change(form, model, True)
#         return True
#
#     def update_model(self, form, model):
#         try:
#             form.populate_obj(model)
#             model.save()
#             self._on_model_change(form, model, False)
#         except Exception as ex:
#             if not self.handle_view_exception(ex):
#                 flash(
#                     gettext("Failed to update record. %(error)s", error=str(ex)),
#                     "error",
#                 )
#                 ca.self.logger.exception("Failed to update record.")
#             self.session.rollback()
#             return False
#         else:
#             self.after_model_change(form, model, False)
#         return True
#
#     def delete_model(self, model):
#         try:
#             self.on_model_delete(model)
#             model.delete()
#             return True
#         except Exception as ex:
#             if not self.handle_view_exception(ex):
#                 flash(
#                     gettext("Failed to delete record. %(error)s", error=str(ex)),
#                     "error",
#                 )
#                 ca.self.logger.exception("Failed to delete record.")
#             self.session.rollback()
#             return False
#
#     def handle_action(self, return_view=None):
#         url = self.get_url(".index_view").rstrip("?") or get_redirect_target()
#         form = self.action_form()
#         if self.validate_form(form):
#             # using getlist instead of FieldList for backward compatibility
#             ids = request.form.getlist("rowid")
#             action = form.action.data
#             handler = self._actions_data.get(action)
#             if debug.action:
#                 print(action, ids)
#             if handler and self.is_action_allowed(action):
#                 response = handler[0](ids)
#                 if response is not None:
#                     # return response
#                     sleep(1)
#                     return jsonify(action=action, ids=ids, url=url)
#             if not action in ["show", "hide"]:
#                 sleep(1)
#             return jsonify(action=action, ids=ids, url=url)
#         else:
#             flash_errors(form, message="Failed to perform action. %(error)s")
#             return jsonify(url=url)
#
#
#     @action("show", lazy_gettext("Show"))
#     def action_show(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for m in query.all():
#                 m.visible = True
#                 count += 1
#                 m.save()
#             # flash(ngettext('1 record now visible.',
#             #                '{} records now visible.'.format(str(count)),
#             #                count),
#             #       'info')
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to show records. {}".format(err), "error")
#
#     @action("hide", lazy_gettext("Hide"))
#     def action_hide(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for m in query.all():
#                 m.visible = False
#                 count += 1
#                 m.save()
#             # flash(ngettext('1 record now hidden.',
#             #                '{} records now hidden.'.format(str(count)),
#             #                count),
#             #       'info')
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to hide records. {}".format(err), "error")
#
#     @action("top", lazy_gettext("Top"))
#     def action_top(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for q in reversed(query.order_by(self.model.position).all()):
#                 old_position = q.position
#                 new_position = 1
#                 for entry in self.model.query.all():
#                     if (entry.position >= new_position) and (
#                         entry.position < old_position
#                     ):
#                         entry.position = entry.position + 1
#                     # db_session.add(entry)
#                     entry.save()
#                 q.position = new_position
#                 q.save()
#                 count += 1
#                 if debug.position:
#                     print("old", old_position, "new", new_position)
#             flash(
#                 ngettext(
#                     "1 record moved to the top.",
#                     "{} records moved to the top.".format(str(count)),
#                     count,
#                 ),
#                 "info",
#             )
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to move records. {}".format(err), "error")
#
#     @action("bottom", lazy_gettext("Bottom"))
#     def action_bottom(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for q in query.order_by(self.model.position).all():
#                 new_position = len(self.model.query.all())
#                 old_position = q.position
#                 for entry in self.model.query.all():
#                     if (entry.position > old_position) and (
#                         entry.position <= new_position
#                     ):
#                         entry.position = entry.position - 1
#                     # db_session.add(entry)
#                     entry.save()
#                 q.position = new_position
#                 q.save()
#                 count += 1
#                 if debug.position:
#                     print("old", old_position, "new", new_position)
#             flash(
#                 ngettext(
#                     "1 record moved to the bottom.",
#                     "{} records moved to the bottom.".format(str(count)),
#                     count,
#                 ),
#                 "info",
#             )
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to move records. {}".format(err), "error")
#
#     @action("plus_5", lazy_gettext("+5"))
#     def action_plus_5(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for q in reversed(query.order_by(self.model.position).all()):
#                 old_position = q.position
#                 new_position = old_position - 5
#                 if new_position < 1:
#                     new_position = 1
#                 for entry in self.model.query.all():
#                     if (entry.position >= new_position) and (
#                         entry.position < old_position
#                     ):
#                         entry.position = entry.position + 1
#                     # db_session.add(entry)
#                     entry.save()
#                 q.position = new_position
#                 q.save()
#                 count += 1
#                 if debug.position:
#                     print("old", old_position, "new", new_position)
#             flash(
#                 ngettext(
#                     "1 record moved up 5.",
#                     "{} records moved up 5.".format(str(count)),
#                     count,
#                 ),
#                 "info",
#             )
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to move records. {}".format(err), "error")
#
#     @action("plus_15", lazy_gettext("+15"))
#     def action_plus_15(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for q in reversed(query.order_by(self.model.position).all()):
#                 old_position = q.position
#                 new_position = old_position - 15
#                 if new_position < 1:
#                     new_position = 1
#                 for entry in self.model.query.all():
#                     if (entry.position >= new_position) and (
#                         entry.position < old_position
#                     ):
#                         entry.position = entry.position + 1
#                     # db_session.add(entry)
#                     entry.save()
#                 q.position = new_position
#                 q.save()
#                 count += 1
#                 if debug.position:
#                     print("old", old_position, "new", new_position)
#             flash(
#                 ngettext(
#                     "1 record moved up 15.",
#                     "{} records moved up 15.".format(str(count)),
#                     count,
#                 ),
#                 "info",
#             )
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to move records. {}".format(err), "error")
#
#     @action("minus_5", lazy_gettext("-5"))
#     def action_minus_5(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for q in query.order_by(self.model.position).all():
#                 last_position = len(self.model.query.all())
#                 old_position = q.position
#                 new_position = old_position + 5
#                 if new_position > last_position:
#                     new_position = last_position
#                 for entry in self.model.query.all():
#                     if (entry.position <= new_position) and (
#                         entry.position > old_position
#                     ):
#                         entry.position = entry.position - 1
#                     # db_session.add(entry)
#                     entry.save()
#                 q.position = new_position
#                 q.save()
#                 count += 1
#                 if debug.position:
#                     print("old", old_position, "new", new_position)
#             flash(
#                 ngettext(
#                     "1 record moved down 5.",
#                     "{} records moved down 5.".format(str(count)),
#                     count,
#                 ),
#                 "info",
#             )
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to move records. {}".format(err), "error")
#
#     @action("minus_15", lazy_gettext("-15"))
#     def action_minus_15(self, ids):
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             count = 0
#             for q in query.order_by(self.model.position).all():
#                 last_position = len(self.model.query.all())
#                 old_position = q.position
#                 new_position = old_position + 15
#                 if new_position > last_position:
#                     new_position = last_position
#                 for entry in self.model.query.all():
#                     if (entry.position <= new_position) and (
#                         entry.position > old_position
#                     ):
#                         entry.position = entry.position - 1
#                     # db_session.add(entry)
#                     entry.save()
#                 q.position = new_position
#                 q.save()
#                 count += 1
#                 if debug.position:
#                     print("old", old_position, "new", new_position)
#             flash(
#                 ngettext(
#                     "1 record moved down 15.",
#                     "{} records moved down 15.".format(str(count)),
#                     count,
#                 ),
#                 "info",
#             )
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash("Failed to move records. {}".format(err), "error")
#
#     @action(
#         "delete",
#         lazy_gettext("Delete"),
#         lazy_gettext("Are you sure you want to delete the selected " "records?"),
#     )
#     def action_delete(self, ids):
#         count = 0
#         skip = 0
#         try:
#             query = tools.get_query_for_ids(self.get_query(), self.model, ids)
#             if self.fast_mass_delete:
#                 count = query.delete(synchronize_session=False)
#             else:
#                 for q in query.all():
#                     if current_user.id > 2 and q.created_by != current_user.name:
#                         skip += 1
#                         continue
#                     else:
#                         self.delete_model(q)
#                         count += 1
#             flash(
#                 ngettext(
#                     "1 record was successfully deleted.",
#                     "{} records were successfully deleted.".format(str(count)),
#                     count,
#                 ),
#                 "success",
#             )
#             if skip:
#                 flash(
#                     ngettext(
#                         "1 record was not owned by you and was not "
#                         "deleted. (Try 'Hide')",
#                         "{} records were "
#                         "not owned by you and "
#                         "were not deleted. "
#                         "(Try 'Hide')".format(str(skip)),
#                         skip,
#                     ),
#                     "info",
#                 )
#
#         except Exception as err:
#             if not self.handle_view_exception(err):
#                 raise
#             flash(gettext("Failed to delete records.\n{}".format(str(err))),
#               "error")
#
#

# class cls(ModelView):
#     def __init__(self, model, session, name=None, menu_icon_value=None):
#         self.menu_icon_value = menu_icon_value
#         if "position" in fields:
#             setattr(self, "column_default_sort", "position")
#             setattr(self, "column_sortable_list", ["position"])
#         elif "published" in fields:
#             setattr(self, "column_default_sort", ("published", True))
#         elif "date" in fields:
#             setattr(self, "column_default_sort", "date")
#         elif "column_default_sort" in view_args.keys():
#             setattr(self, "column_default_sort", view_args["column_default_sort"])
#         if "column_list" in view_args.keys():
#             column_list = view_args["column_list"]
#             if debug.position:
#                 column_list.append("position")
#             if "visible" in fields:
#                 column_list.append("visible")
#             setattr(self, "column_list", column_list)
#         # for field in fields:
#         #     if field.endswith("_url"):
#         #         self.form_extra_fields[field] = URLField(
#         #             field.replace("_", " ").title(), validators=[Optional(),
#                           URL()]
#         #         )
#         #     elif field.endswith("_phone"):
#         #         self.form_extra_fields[field] = TelField(
#         #             field.replace("_", " ").title(), validators=[Optional()]
#         #         )
#         if "form_excluded_columns" in view_args.keys():
#             for field in view_args["form_excluded_columns"]:
#                 fields.remove(field)
#         for field in last_fields:
#             fields.remove(field)
#         fields.extend(["visible"])
#         fields.insert(0, "name")
#         self.form_columns = fields
#
#         super().__init__(model, session, name=name,
#               menu_icon_value=menu_icon_value)
#
#         def is_action_allowed(self, name):
#             if "position" in fields:
#                 if name in (self.allowed_actions + self.position_actions):
#                     return super(AdminModelView, self).is_action_allowed(name)
#             else:
#                 if name in self.allowed_actions:
#                     return super(AdminModelView, self).is_action_allowed(name)
#
#         cls.__name__ = f"{model}AdminView"
#
#         return cls

# def _setup_templates(self) -> None:
#     templates.env.loader = ChoiceLoader(
#         [
#             FileSystemLoader(self.templates_dir),
#             PackageLoader("starlette_admin", "templates"),
#         ]
#     )
#     # globals
#     templates.env.globals["views"] = self._views
#     templates.env.globals["title"] = self.title
#     templates.env.globals["is_auth_enabled"] = self.auth_provider is not None
#     templates.env.globals["__name__"] = self.route_name
#     templates.env.globals["logo_url"] = self.logo_url
#     templates.env.globals["login_logo_url"] = self.login_logo_url
#     templates.env.globals["custom_render_js"] = lambda r: self.custom_render_js(r)
#     templates.env.globals["get_locale"] = get_locale
#     templates.env.globals["get_locale_display_name"] = get_locale_display_name
#     templates.env.globals["i18n_config"] = self.i18n_config or I18nConfig()
#     # filters
#     templates.env.filters["is_custom_view"] = lambda r: isinstance(r, CustomView)
#     templates.env.filters["is_link"] = lambda res: isinstance(res, Link)
#     templates.env.filters["is_model"] = lambda res: isinstance(res, BaseModelView)
#     templates.env.filters["is_dropdown"] = lambda res: isinstance(res, DropDown)
#     templates.env.filters["get_admin_user"] = (
#         self.auth_provider.get_admin_user if self.auth_provider else None
#     )
#     templates.env.filters["tojson"] = lambda data: json.dumps(data, default=str)
#     templates.env.filters["file_icon"] = get_file_icon
#     templates.env.filters[
#         "to_model"
#     ] = lambda identity: self._find_model_from_identity(identity)
#     templates.env.filters["is_iter"] = lambda v: isinstance(v, (list, tuple))
#     templates.env.filters["is_str"] = lambda v: isinstance(v, str)
#     templates.env.filters["is_dict"] = lambda v: isinstance(v, dict)
#     templates.env.filters["ra"] = lambda a: RequestAction(a)
#     # install i18n
#     templates.env.install_gettext_callables(gettext, ngettext, True)# type: ignore
#     self.templates = templates
