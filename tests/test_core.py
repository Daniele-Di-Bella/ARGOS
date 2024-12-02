import os

from crawler.crawler import create_dataset
from datetime import datetime


def test_create_dataset():
    today = datetime.now().strftime("%Y-%m-%d_%H.%M")
    create_dataset()
    assert os.path.exists(rf"/data-collection\Dataset_{today}.csv")
