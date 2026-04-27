import argparse
import asyncio
import json
import urllib.parse

import aiohttp
from lxml import etree  # type: ignore


class BaseMdprMedia:
    def __init__(self, url: str):
        self.url = url.strip()
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def get_image_index(self) -> str:
        raise NotImplementedError

    async def get_image_urls(self, image_index: str) -> list[str]:
        raise NotImplementedError


class MobileMdprMedia(BaseMdprMedia):
    def __get_article_id(self) -> str:
        url = self.url
        if "https://mdpr.jp" in url and "photo/details" not in url:
            return url.rstrip("/").split("/")[-1]
        return ""

    async def get_image_index(self) -> str:
        assert self.session is not None, "session not initialized"

        aid = self.__get_article_id()
        if not aid:
            return ""

        mdpr_host = "https://app2-mdpr.freetls.fastly.net"
        headers = {
            "X-Requested-With": "jp.mdpr.mdprviewer",
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 7.1.1; E6533 Build/32.4.A.1.54; wv) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                "Chrome/94.0.4606.85 Mobile Safari/537.36"
            ),
        }

        url = f"{mdpr_host}/articles/detail/{aid}"

        async with self.session.get(url, headers=headers) as resp:
            body = await resp.text()

        html = etree.HTML(body, etree.HTMLParser())
        nodes = html.xpath(r'//div[@class="p-articleBody"]/a')

        for node in nodes:
            app_data = node.get("data-mdprapp-option")
            if not app_data:
                continue

            mdpr_json = json.loads(urllib.parse.unquote(app_data))
            target_url = mdpr_json.get("url", "")

            if aid in target_url:
                return mdpr_host + target_url

        return ""

    async def get_image_urls(self, image_index: str) -> list[str]:
        assert self.session is not None, "session not initialized"

        headers = {
            "mdpr-user-agent": "sony; E653325; android; 7.1.1; 3.10.4838(66);",
            "User-Agent": "okhttp/4.9.1",
        }

        async with self.session.get(image_index, headers=headers) as resp:
            data = await resp.json()

        return [item["url"] for item in data.get("list", []) if "url" in item]


class WebMdprMedia(BaseMdprMedia):
    host = "https://mdpr.jp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    }

    async def get_image_index(self) -> str:
        assert self.session is not None, "session not initialized"

        url = self.url
        if "https://mdpr.jp" not in url:
            return ""

        if "photo/detail" in url:
            return url

        async with self.session.get(url, headers=self.headers) as resp:
            body = await resp.text()

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
        async with self.session.get(image_index, headers=self.headers) as resp:
            body = await resp.text()

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


async def fetch_images(client_cls, url: str):
    async with client_cls(url) as client:
        idx = await client.get_image_index()
        if not idx:
            return []
        return await client.get_image_urls(idx)


async def run(url: str):
    # url = "https://mdpr.jp/cinema/3928728"
    imgs = await fetch_images(MobileMdprMedia, url)

    if not imgs:
        imgs = await fetch_images(WebMdprMedia, url)

    if not imgs:
        print("cannot match.")
        return

    print(imgs)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", type=str, help="Url pics download")
    args = parser.parse_args()
    url = args.url
    if url:
        return url
    else:
        parser.print_help()
        exit()


def cli():
    url = get_args()
    asyncio.run(run(url))


def main():
    url = get_args()
    asyncio.run(run(url))


if __name__ == "__main__":
    main()
