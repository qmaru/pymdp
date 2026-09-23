# pymdp

## docker

```shell
docker run --rm ghcr.io/qmaru/pymdp -u "https://mdpr.jp/cinema/3928728"
```

## uv

### source

```shell
uv sync
uv run mdpdl -u "https://mdpr.jp/cinema/3928728"
```

### tool

```shell
# direct
uv tool run --from git+https://github.com/qmaru/pymdp.git mdpdl -h

# install
uv tool install git+https://github.com/qmaru/pymdp.git
mdpdl -u "https://mdpr.jp/cinema/3928728"
```

## package

```shell
# install package
uv add git+https://github.com/qmaru/pymdp.git

# main.py
from pymdp import WebMdprMedia

url = "https://mdpr.jp/cinema/3928728"

async with WebMdprMedia(url) as client:
    image_index = await client.get_image_index()
    if image_index:
        image_urls = await client.get_image_urls(image_index)
        print(image_urls)
    else:
        print("URL cannot match.")
```
