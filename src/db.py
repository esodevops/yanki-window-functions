import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import pandas as pd


def load_dotenv_vars():
    load_dotenv()
    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def get_db_connection(cfg):
    return psycopg2.connect(
        host=cfg["host"],
        database=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg["port"],
    )


def create_database_if_not_exists(cfg):
    conn = psycopg2.connect(
        dbname="postgres",
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"],
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (cfg["dbname"],))
    exists = cur.fetchone()
    if not exists:
        cur.execute(f'CREATE DATABASE "{cfg["dbname"]}";')
        logging.info(f"Database '{cfg['dbname']}' created.")
    else:
        logging.info(f"Database '{cfg['dbname']}' already exists.")
    cur.close()
    conn.close()


def create_tables(cfg):
    conn = get_db_connection(cfg)
    cursor = conn.cursor()
    statements = [
        "CREATE SCHEMA IF NOT EXISTS yanki;",
        "DROP TABLE IF EXISTS yanki.payment_method CASCADE;",
        "DROP TABLE IF EXISTS yanki.orders CASCADE;",
        "DROP TABLE IF EXISTS yanki.shipping_address CASCADE;",
        "DROP TABLE IF EXISTS yanki.products CASCADE;",
        "DROP TABLE IF EXISTS yanki.customers CASCADE;",
        """CREATE TABLE IF NOT EXISTS yanki.customers (Customer_ID UUID PRIMARY KEY, Customer_Name TEXT, Email TEXT, Phone_Number TEXT);""",
        """CREATE TABLE IF NOT EXISTS yanki.products (Product_ID UUID PRIMARY KEY, Product_Name TEXT, Brand TEXT, Category TEXT, Price FLOAT);""",
        """CREATE TABLE IF NOT EXISTS yanki.shipping_address (shipping_ID INTEGER PRIMARY KEY, Customer_ID UUID, Shipping_Address TEXT, City TEXT, State TEXT, Country TEXT, Postal_Code INTEGER, FOREIGN KEY (Customer_ID) REFERENCES yanki.customers(Customer_ID));""",
        """CREATE TABLE IF NOT EXISTS yanki.orders (Order_ID UUID PRIMARY KEY, Customer_ID UUID, Product_ID UUID, Quantity INTEGER, Total_Price FLOAT, Order_Date DATE, FOREIGN KEY (Customer_ID) REFERENCES yanki.customers(Customer_ID), FOREIGN KEY (Product_ID) REFERENCES yanki.products(Product_ID));""",
        """CREATE TABLE IF NOT EXISTS yanki.payment_method (Order_ID UUID, Payment_Method TEXT, Transaction_Status TEXT, FOREIGN KEY (Order_ID) REFERENCES yanki.orders(Order_ID));""",
    ]
    for sql in statements:
        cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Schema and tables created successfully.")


def load_csv_to_table(cfg, csv_path, insert_sql):
    conn = get_db_connection(cfg)
    cursor = conn.cursor()
    import csv

    with open(csv_path, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            cursor.execute(insert_sql, row)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info(f"Loaded data from {csv_path} into database.")


# Main entrypoint for schema creation and data loading
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    cfg = load_dotenv_vars()
    create_database_if_not_exists(cfg)
    create_tables(cfg)

    # Define CSVs and insert statements
    csv_table_map = [
        (
            "dataset/cleandata/customers.csv",
            "INSERT INTO yanki.customers (Customer_ID, Customer_Name, Email, Phone_Number) VALUES (%s, %s, %s, %s) ON CONFLICT (Customer_ID) DO NOTHING;",
        ),
        (
            "dataset/cleandata/products.csv",
            "INSERT INTO yanki.products (Product_ID, Product_Name, Brand, Category, Price) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (Product_ID) DO NOTHING;",
        ),
        (
            "dataset/cleandata/shipping_address.csv",
            "INSERT INTO yanki.shipping_address (shipping_ID, Customer_ID, Shipping_Address, City, State, Country, Postal_Code) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (shipping_ID) DO NOTHING;",
        ),
        (
            "dataset/cleandata/orders.csv",
            "INSERT INTO yanki.orders (Order_ID, Customer_ID, Product_ID, Quantity, Total_Price, Order_Date) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (Order_ID) DO NOTHING;",
        ),
        (
            "dataset/cleandata/payment_method.csv",
            "INSERT INTO yanki.payment_method (Order_ID, Payment_Method, Transaction_Status) VALUES (%s, %s, %s);",
        ),
    ]

    for csv_path, insert_sql in csv_table_map:
        if os.path.exists(csv_path):
            load_csv_to_table(cfg, csv_path, insert_sql)
        else:
            logging.warning(f"CSV file not found: {csv_path}")
