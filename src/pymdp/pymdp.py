import argparse
import asyncio
import json
import urllib.parse

import aiohttp
from lxml import etree


class MdprMedia:
    def __init__(self, url: str):
        self.session = aiohttp.ClientSession()
        self.url = url

    def __get_article_id(self) -> str:
        url = self.url.strip()
        if "https://mdpr.jp" in url:
            if "photo/details" not in url:
                url_parts = url.split("/")
                return url_parts[-1]
        return ""

    async def get_image_index(self) -> str:
        aid = self.__get_article_id()
        if aid == "":
            return ""

        MDPR_HOST = "https://app2-mdpr.freetls.fastly.net"
        USER_AGENT = "Mozilla/5.0 (Linux; Android 7.1.1; E6533 Build/32.4.A.1.54; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36"
        X_REQUESTED_WITH = "jp.mdpr.mdprviewer"

        mobile_index = f"{MDPR_HOST}/articles/detail/{aid}"
        headers = {"X-Requested-With": X_REQUESTED_WITH, "User-Agent": USER_AGENT}

        async with self.session.get(mobile_index, headers=headers) as response:
            body = await response.text()
            html = etree.HTML(body, etree.HTMLParser())
            nodes = html.xpath(r'//div[@class="p-articleBody"]/a')
            for node in nodes:
                app_data = node.get("data-mdprapp-option")
                if app_data:
                    mdpr_json_str = urllib.parse.unquote(app_data)
                    mdpr_json = json.loads(mdpr_json_str)
                    if aid in mdpr_json.get("url"):
                        return MDPR_HOST + mdpr_json.get("url")
        return ""

    async def get_image_urls(self, image_index: str) -> list[str]:
        urls: list[str] = []

        USER_AGENT = "okhttp/4.9.1"
        MDPRUSER_AGENT = "sony; E653325; android; 7.1.1; 3.10.4838(66);"
        headers = {"mdpr-user-agent": MDPRUSER_AGENT, "User-Agent": USER_AGENT}

        async with self.session.get(image_index, headers=headers) as response:
            body = await response.json()
            mdpr_image_list = body["list"]
            for mdpr_image in mdpr_image_list:
                img_url = mdpr_image["url"]
                urls.append(img_url)

        return urls

    async def close(self):
        await self.session.close()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def __aenter__(self):
        return self


async def run(url: str):
    # url = "https://mdpr.jp/cinema/3928728"
    async with MdprMedia(url) as mdpr:
        image_index = await mdpr.get_image_index()
        if image_index:
            image_urls = await mdpr.get_image_urls(image_index)
            print(image_urls)
        else:
            print("URL cannot match.")


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
