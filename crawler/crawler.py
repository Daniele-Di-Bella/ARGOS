import asyncio
import csv
import re

from datetime import datetime
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext
from crawlee import ConcurrencySettings


def create_dataset() -> None:
    today = datetime.now().strftime("%Y-%m-%d_%H.%M")
    data_path = rf"C:\Users\danie\PycharmProjects\WikiSpark\crawler\Dataset_{today}.csv"
    with open(data_path, mode="w", newline="") as file:
        csv.writer(file).writerows([["Link", "Abstract"]])
    return data_path


def clean_text(input_text):
    text_without_html = re.sub(r'<[^>]+>', '', input_text)  # HTML tag removal
    cleaned_text = re.sub(r'\s+', ' ', text_without_html)  # line break removal
    return cleaned_text.strip()


async def beautifulsoup_crawler(data_path: str, protein: str) -> None:
    concurrency_settings = ConcurrencySettings(
        min_concurrency=1,
        max_concurrency=10,
        desired_concurrency=5
    )

    # Create the crawler with concurrency settings
    crawler = BeautifulSoupCrawler(concurrency_settings=concurrency_settings)

    # This decorator defines the default request handler
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        h2_tag = context.soup.find("h2", string="Abstract")
        if not h2_tag:
            pass
        else:
            abstract_tag = h2_tag.find_next()
            if abstract_tag:
                # Extract abstract text
                raw_text = abstract_tag.get_text(strip=True)
                abstract_text = clean_text(raw_text)
                # Extract data from the page.
                data = {
                    'url': context.request.url,
                    'abstract': abstract_text
                }
                print(f"Abstract found in {context.request.url}: {abstract_text}")

                with open(data_path, mode='a', newline='', encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow([data['url'], data['abstract']])

        # Enqueue all links found on the page
        await context.enqueue_links()

    await crawler.run([f"https://scholar.google.com/scholar?hl=it&as_sdt=0%2C5&q={protein}&btnG="])


if __name__ == '__main__':
    try:
        data_path = create_dataset()
        asyncio.run(beautifulsoup_crawler(data_path, "otogelin"))
    except KeyboardInterrupt:
        print("Crawler interrupted by user")
