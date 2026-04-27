import pytest

from pymdp.pymdp import MobileMdprMedia, WebMdprMedia


@pytest.mark.parametrize(
    "cls,url,expected_idx",
    [
        (MobileMdprMedia, "https://mdpr.jp/cinema/3928728", "3928728"),
        (WebMdprMedia, "https://mdpr.jp/cinema/3928728", "14567030"),
    ],
)
@pytest.mark.asyncio
async def test_mdpr_media(cls, url: str, expected_idx: str):
    async with cls(url) as mdpr:
        idx = await mdpr.get_image_index()
        assert expected_idx in idx

        image_urls = await mdpr.get_image_urls(idx)
        assert image_urls
