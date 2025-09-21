from typing import Optional, Union, Literal
from instaui import ui
from instaui.dependencies.plugin_dependency import register_plugin
from instaui_tdesign.types import TLocale, TCustomizeLocale
from instaui_tdesign._settings import configure
from instaui_tdesign import consts


def _register_tdesign():
    register_plugin(
        "InstauiTDesign",
        esm=consts.instaui_tdesign_esm_js,
        externals={
            "tdesign-vue-next": consts.tdesign_esm_js,
        },
        css=[consts.tdesign_css, consts.instaui_tdesign_css],
    )


def use(
    *,
    locale: ui.TMaybeRef[Union[TLocale, TCustomizeLocale]] = "en-US",
    theme: Optional[Literal["default", "green", "violet"]] = None,
):
    """Use tdesign ui.

    Args:
        locale (ui.TMaybeRef[Union[TLocale, TCustomizeLocale]], optional): The locale of tdesign ui. Defaults to "en-US".

    Examples:
    .. code-block:: python
        from instaui import ui
        import instaui_tdesign as td

        td.use()

        @ui.page("/")
        def index_page():
            td.input(placeholder="input")
    """

    _register_tdesign()
    configure(locale=locale)
    if theme is not None:
        ui.add_css_link(consts.THEME_CSS_DIR / f"theme-{theme}.css")
