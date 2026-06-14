import os
import pandas as pd
from src.etl import clean_and_normalize, setup_logging


def test_clean_and_normalize():
    setup_logging()
    raw_csv = "dataset/rawdata/yanki_ecommerce.csv"
    out_dir = "dataset/cleandata"
    assert clean_and_normalize(raw_csv, out_dir)
    # Check output files
    for fname in [
        "customers.csv",
        "products.csv",
        "shipping_address.csv",
        "orders.csv",
        "payment_method.csv",
    ]:
        path = os.path.join(out_dir, fname)
        assert os.path.exists(path)
        df = pd.read_csv(path)
        assert not df.empty
