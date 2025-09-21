from pathlib import Path
from typing import Optional, Final
from instaui.zero.options import CdnResourceOption
from instaui_tdesign import consts

_M_TDESIGN_VUE_JS_CDN: Final = "https://cdn.jsdelivr.net/gh/instaui-python/tdesign-vue-next-esm@1.15.5/tdesign-vue-next.esm.min.js"
_M_TDESIGN_VUE_CSS_CDN: Final = (
    "https://cdn.jsdelivr.net/npm/tdesign-vue-next@1.16.1/dist/tdesign.min.css"
)


def override(
    *,
    tdesign_vue_next_js: Optional[str] = None,
    tdesign_vue_next_css: Optional[str] = None,
) -> CdnResourceOption:
    if not tdesign_vue_next_js and not tdesign_vue_next_css:
        return default_override()

    import_maps = {}
    if tdesign_vue_next_js:
        import_maps["tdesign-vue-next"] = tdesign_vue_next_js

    css_links: dict[Path, str] = {}
    if tdesign_vue_next_css:
        css_links[consts.tdesign_css] = tdesign_vue_next_css

    return CdnResourceOption(import_maps=import_maps, css_links=css_links)


def default_override() -> CdnResourceOption:
    return override(
        tdesign_vue_next_js=_M_TDESIGN_VUE_JS_CDN,
        tdesign_vue_next_css=_M_TDESIGN_VUE_CSS_CDN,
    )
