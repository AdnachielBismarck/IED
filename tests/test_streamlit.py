from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "app" / "main.py"
PAGE_FILES = sorted((ROOT / "app" / "pages").glob("*.py"))


def test_streamlit_main_runs_without_exceptions():
    app = AppTest.from_file(str(MAIN), default_timeout=30).run()
    assert not app.exception


@pytest.mark.parametrize("page_file", PAGE_FILES, ids=lambda path: path.stem)
def test_streamlit_page_runs_without_exceptions(page_file: Path):
    app = AppTest.from_file(str(MAIN), default_timeout=30).run()
    relative_page = page_file.relative_to(MAIN.parent).as_posix()
    app.switch_page(relative_page).run()
    assert not app.exception
