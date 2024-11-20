from crawlee import Request
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawlingContext
from crawlee.router import Router

router = Router[BeautifulSoupCrawlingContext]()


@router.default_handler
async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Listing papers to scrape"""
    await context.enqueue_links(selector="a.c-card__link u-link-inherit", label="nature_paper")


@router.handler("pubmed_paper")
async def detail_handler(context: BeautifulSoupCrawlingContext) -> None:
    """Scraping Nature papers"""
    title = await context.soup.locator("h1.c-article-title").nth(0).text_content()

    # abstract = await context.page.get_by_role("eng-abstract").first.text_content()

    await context.push_data(
        {
            "url": context.request.loaded_url,
            "title": title.strip(),
            # "abstract": abstract,
        }
    )
