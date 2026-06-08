import asyncio
import random

from loguru import logger

from app.scrapers.base import RawJob


async def fetch_html_playwright(url: str) -> str:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": random.choice([1366, 1440, 1920]), "height": random.choice([768, 900, 1080])},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(random.uniform(2, 4))
            html = await page.content()
        finally:
            await browser.close()

    logger.debug(f"Playwright fetched {len(html)} chars for {url}")
    return html
