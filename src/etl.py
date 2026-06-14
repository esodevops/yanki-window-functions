import os
import logging
import pandas as pd


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )


def safe_read_csv(path):
    try:
        df = pd.read_csv(path)
        logging.info(f"Loaded {path} successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Failed to load {path}: {e}")
        return None


def clean_and_normalize(raw_csv, out_dir):
    df = safe_read_csv(raw_csv)
    if df is None:
        return False
    df.dropna(subset=["Order_ID", "Customer_ID"], inplace=True)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    customers_df = (
        df[["Customer_ID", "Customer_Name", "Email", "Phone_Number"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    products_df = (
        df[["Product_ID", "Product_Name", "Brand", "Category", "Price"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    shipping_address_df = (
        df[
            [
                "Customer_ID",
                "Shipping_Address",
                "City",
                "State",
                "Country",
                "Postal_Code",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    shipping_address_df.index.name = "Shipping_ID"
    shipping_address_df.reset_index(inplace=True)
    orders_df = (
        df[
            [
                "Order_ID",
                "Customer_ID",
                "Product_ID",
                "Quantity",
                "Total_Price",
                "Order_Date",
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    payment_method_df = (
        df[["Order_ID", "Payment_Method", "Transaction_Status"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    os.makedirs(out_dir, exist_ok=True)
    customers_df.to_csv(f"{out_dir}/customers.csv", index=False)
    products_df.to_csv(f"{out_dir}/products.csv", index=False)
    shipping_address_df.to_csv(f"{out_dir}/shipping_address.csv", index=False)
    orders_df.to_csv(f"{out_dir}/orders.csv", index=False)
    payment_method_df.to_csv(f"{out_dir}/payment_method.csv", index=False)
    logging.info("Cleaned and saved all tables to CSV.")
    return True
