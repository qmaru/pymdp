import argparse
import asyncio
import sys

import httpx2
from lxml import etree


class WebMdprMedia:
    def __init__(self, url: str):
        self.url = url.strip()

        self.host = "https://mdpr.jp"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
        }
        self.session: httpx2.AsyncClient | None = None

    async def __aenter__(self):
        self.session = httpx2.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.aclose()

    async def get_image_index(self) -> str:
        assert self.session is not None, "session not initialized"

        url = self.url
        if self.host not in url:
            return ""

        if "photo/detail" in url:
            return url

        resp = await self.session.get(url, headers=self.headers)
        body = resp.text

        html = etree.HTML(body, etree.HTMLParser())
        nodes = html.xpath(r'//a[@class="c-image__image"]')
        for node in nodes:
            href = node.get("href")
            if "photo/detail" in href:
                return self.host + href

        return ""

    async def get_image_urls(self, image_index: str) -> list[str]:
        assert self.session is not None, "session not initialized"

        urls = []
        resp = await self.session.get(image_index, headers=self.headers)
        body = resp.text

        html = etree.HTML(body, etree.HTMLParser())

        nodes = html.xpath(
            r'//main[@id="js-main-content"]//ol[@class="pg-photo__webImageList"]/li/a/img'
        )
        for node in nodes:
            src = node.get("src")
            if "img_protect" not in src:
                url = src.replace("/thumb/", "/").split("?")[0]
                urls.append(url)

        return urls


async def fetch_images(url: str):
    # url = "https://mdpr.jp/cinema/3928728"
    async with WebMdprMedia(url) as client:
        image_index = await client.get_image_index()
        if image_index:
            return await client.get_image_urls(image_index)
        return []


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", type=str, help="Url pics download")
    args = parser.parse_args()
    url = args.url
    if url:
        return url
    else:
        parser.print_help()
        sys.exit()


def cli():
    url = get_args()
    imgs = asyncio.run(fetch_images(url))

    if not imgs:
        print("cannot match.")
        return

    print(imgs)


if __name__ == "__main__":
    cli()
