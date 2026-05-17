from playwright.sync_api import sync_playwright
import csv
from pathlib import Path

def parse_top_movies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.imdb.com/chart/top/")
        page.locator("ul.ipc-inline-list .ipc-title__text").first.wait_for()
        for _ in range(5):
            page.keyboard.press("End")
            page.wait_for_timeout(1000)
        all_titles = page.locator("ul.ipc-inline-list .ipc-title__text")
        all_titles_list = all_titles.all_inner_texts()

        folder_path = Path("../test_data")
        file_path = folder_path / "imdb_top250.csv"

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["rank", "title"])
            for i, title in enumerate(all_titles_list, start=1):
                writer.writerow([i, title])
                print(f"Записано в базу: {i} - {title}")

        browser.close()

if __name__ == '__main__':
    parse_top_movies()