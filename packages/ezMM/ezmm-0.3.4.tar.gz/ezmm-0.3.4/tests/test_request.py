import aiohttp
import pytest

from ezmm.request import is_maybe_image_url


@pytest.mark.parametrize("url,expected", [
    ("https://media.cnn.com/api/v1/images/stellar/prod/ap22087057359494.jpg?c=16x9&q=h_653,w_1160,c_fill/f_webp", True),
    ("https://edition.cnn.com/2024/10/30/asia/north-korea-icbm-test-intl-hnk/index.html", False),
    ("https://img.zeit.de/politik/ausland/2024-10/georgien-wahl-stimmauszaehlung-regierungspartei-bild/wide__1000x562__desktop__scale_2", True),
    ("https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg", True),
    ("https://de.wikipedia.org/wiki/Datei:President_Barack_Obama.jpg", False),  # this is the image's article view
    ("https://bingekulture.com/wp-content/uploads/2021/08/cropped-cropped-logo.fw-removebg-preview.png?w=48", False),  # this URL redirects to a webpage
    ("https://www.popularmechanics.com/_assets/design-tokens/fre/static/icons/play.db7c035.svg?primary=%2523ffffff%20%22Play%22", False),  # this is a vector graphic
    ("https://pixum-cms.imgix.net/7wL8j3wldZEONCSZB9Up6B/d033b7b6280687ce2e4dfe2d4147ff93/fab_mix_kv_perspektive_foto_liegend_desktop__3_.png?auto=compress,format&trim=false&w=2000", True),
    ("https://cdn.pixabay.com/photo/2017/11/08/22/28/camera-2931883_1280.jpg", True),  # image is presented as a binary download stream
    ("https://arxiv.org/pdf/2412.10510", False),  # this is a PDF download stream
    ("https://platform.vox.com/wp-content/uploads/sites/2/2025/04/jack-black-wink-minecraft.avif?quality=90&strip=all&crop=12.5%2C0%2C75%2C100&w=2400", True),
    ("https://media.cnn.com/api/v1/images/stellar/prod/02-overview-of-kursk-training-area-15april2025-wv2.jpg?q=w_1110,c_fill", True)
])
@pytest.mark.asyncio
async def test_is_image_url(url, expected):
    async with aiohttp.ClientSession() as session:
        assert await is_maybe_image_url(url, session) == expected
