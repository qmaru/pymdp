import pytest

from pymdp.pymdp import MdprMedia


@pytest.mark.parametrize(
    "url",
    [
        "https://mdpr.jp/cinema/3928728",
    ],
)
@pytest.mark.asyncio
async def test_url(url: str):
    mdpr = MdprMedia(url)
    image_index = await mdpr.get_image_index()
    assert "3928728" in image_index
    image_urls = await mdpr.get_image_urls(image_index)
    assert len(image_urls) != 0
