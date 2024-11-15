import asyncio
import csv
import re

from datetime import datetime
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext


def create_dataset() -> None:
    today = datetime.now().strftime("%Y-%m-%d_%H.%M")
    with open(rf"C:\Users\danie\PycharmProjects\WikiSpark\crawler\Dataset_{today}.csv", mode="w", newline="") as file:
        csv.writer(file).writerows([["Link", "Abstract"]])


def clean_text(input_text):
    text_without_html = re.sub(r'<[^>]+>', '', input_text)  # HTML tag removal
    cleaned_text = re.sub(r'\s+', ' ', text_without_html)  # line break removal
    return cleaned_text.strip()


async def beautifulsoup_crawler() -> None:
    crawler = BeautifulSoupCrawler()

    # Define the default request handler, which will be called for every request.
    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        context.log.info(f'Processing {context.request.url} ...')

        # Extract data from the page.
        data = {
            'url': context.request.url,
            'title': context.soup.title.string if context.soup.title else None,
            'h1s': [h1.text for h1 in context.soup.find_all('h1')],
            'h2s': [h2.text for h2 in context.soup.find_all('h2')],
            'h3s': [h3.text for h3 in context.soup.find_all('h3')],
        }

        # Push the extracted data to the default dataset.
        await context.push_data(data)

        # Enqueue all links found on the page.
        await context.enqueue_links()

    await crawler.run(['https://crawlee.dev/'])


if __name__ == '__main__':
    asyncio.run(create_dataset())
    # asyncio.run(beautifulsoup_crawler())
