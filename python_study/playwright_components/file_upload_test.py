from playwright.sync_api import expect
from pathlib import Path


def test_upload(page):
    page.goto("https://the-internet.herokuapp.com/upload")
    page.locator("#file-upload").set_input_files("/Users/iill/PyCharmMiscProject/PythonProject/python_study/dummy.txt")
    page.locator("#file-submit").click()
    expect(page.locator("h3")).to_have_text("File Uploaded!")


def test_upload_drag_and_drop(page):
    page.goto("https://the-internet.herokuapp.com/upload")
    file_path = Path(__file__).parent / "dummy.txt"
    page.locator(".dz-hidden-input").set_input_files(file_path)
    page.locator(".dz-preview").hover()
    expect(page.locator(".dz-filename")).to_contain_text("dummy.txt")
