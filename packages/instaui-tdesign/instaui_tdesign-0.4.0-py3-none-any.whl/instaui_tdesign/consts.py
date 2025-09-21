from pathlib import Path


static_folder = Path(__file__).parent / "static"

instaui_tdesign_css = static_folder / "instaui-tdesign.css"
instaui_tdesign_esm_js = static_folder / "instaui-tdesign.js"

tdesign_css = static_folder / "tdesign.min.css"
tdesign_esm_js = static_folder / "tdesign.min.js"

THEME_CSS_DIR = Path(__file__).parent / "theme/css"
