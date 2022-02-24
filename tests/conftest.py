import os
import pytest

import requests
# from pathlib import Path
from zipfile import ZipFile


from tests.common import (
    TEST_DATA_CACHE_DIR,
    HADCRUT4_URL,
    HADCRUT4_NC_ZIP,
)


@pytest.fixture
def load_test_data():
    """
    This fixture ensures that the required test data repository
    has been downloaded to the cache directory within the home directory.
    """

    target = TEST_DATA_CACHE_DIR / HADCRUT4_NC_ZIP

    if not TEST_DATA_CACHE_DIR.is_dir():
        os.makedirs(TEST_DATA_CACHE_DIR.as_posix())

    if not target.exists():
        url = f"{HADCRUT4_URL}/{HADCRUT4_NC_ZIP}"
        with requests.get(url, stream=True) as r:
            with open(target.as_posix(), "wb") as fd:
                for chunk in r.iter_content(chunk_size=16*1024):
                    fd.write(chunk)
    archive = TEST_DATA_CACHE_DIR / HADCRUT4_NC_ZIP
    extract_dir = TEST_DATA_CACHE_DIR / "HadCRUT4"
    if not extract_dir.exists():
        with ZipFile(archive.as_posix(), 'r') as zip:
            zip.extractall(extract_dir.as_posix())
