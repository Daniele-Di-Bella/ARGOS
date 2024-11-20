import asyncio

from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler
from routes import router


async def main(protein: str) -> None:
    """Crawler entry point"""
    crawler = BeautifulSoupCrawler(
        headless=False,
        request_handler=router,
        max_requests_per_crawl=100
    )

    await crawler.run(
        [
            f"https://www.nature.com/search?q={protein}&journal=",
        ]
    )

    await crawler.export_data(f"{protein}.csv")

if __name__ == "__main__":
    asyncio.run(main("otogelin"))
