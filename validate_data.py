import pandas as pd
import os


def validate_csv_columns(path, required_cols):
    try:
        df = pd.read_csv(path)
        missing = set(required_cols) - set(df.columns)
        if missing:
            print(f"Missing columns in {path}: {missing}")
            return False
        return True
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return False


if __name__ == "__main__":
    checks = [
        (
            "dataset/cleandata/customers.csv",
            ["Customer_ID", "Customer_Name", "Email", "Phone_Number"],
        ),
        (
            "dataset/cleandata/products.csv",
            ["Product_ID", "Product_Name", "Brand", "Category", "Price"],
        ),
        (
            "dataset/cleandata/orders.csv",
            [
                "Order_ID",
                "Customer_ID",
                "Product_ID",
                "Quantity",
                "Total_Price",
                "Order_Date",
            ],
        ),
        (
            "dataset/cleandata/payment_method.csv",
            ["Order_ID", "Payment_Method", "Transaction_Status"],
        ),
        (
            "dataset/cleandata/shipping_address.csv",
            [
                "Shipping_ID",
                "Customer_ID",
                "Shipping_Address",
                "City",
                "State",
                "Country",
                "Postal_Code",
            ],
        ),
    ]
    all_ok = True
    for path, cols in checks:
        if not os.path.exists(path):
            print(f"File missing: {path}")
            all_ok = False
        elif not validate_csv_columns(path, cols):
            all_ok = False
    if all_ok:
        print("All CSV files and columns are valid.")
    else:
        print("Some files or columns are missing or invalid.")
