# model/data_loader.py
import pandas as pd
import mysql.connector

def load_training_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="cabondioxideproject"
    )

    query = """
    SELECT country, year, co2
    FROM clean_co2_emissions
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df