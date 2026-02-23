import pandas as pd
import mysql.connector

# =============================
# PATH CONFIG
# =============================
RAW_FILE = r"C:\Users\USER\Desktop\BI-DM Project\data\Raw_zone\raw_data.csv"
STAGING_FILE = r"C:\Users\USER\Desktop\BI-DM Project\data\Staging_zone\staging_data.csv"
CLEAN_FILE = r"C:\Users\USER\Desktop\BI-DM Project\data\Cleansing_zone\clean_data.csv"
PRESENTATION_FILE = r"C:\Users\USER\Desktop\BI-DM Project\data\presentation_zone\presentation.csv"
PREDICTION_FILE = r"C:\Users\USER\Desktop\BI-DM Project\data\Prediction_zone\test_data.csv"

# =============================
# DB CONNECTION
# =============================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="cabondioxideproject"
)
cursor = conn.cursor()

# =============================
# METADATA FUNCTION
# =============================
def insert_pipeline_metadata(cursor, zone, filename, df, status):
    sql = """
    INSERT INTO pipeline_metadata
    (zone, filename, total_rows, total_columns, status)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        zone,
        filename,
        len(df),
        df.shape[1],
        status
    ))

# =============================
# 1️⃣ RAW ZONE
# =============================
raw_df = None
try:
    raw_df = pd.read_csv(RAW_FILE)
    insert_pipeline_metadata(cursor, "Raw", "raw_data.csv", raw_df, "SUCCESS")
except Exception as e:
    insert_pipeline_metadata(cursor, "Raw", "raw_data.csv", pd.DataFrame(), "FAILED")
    print("❌ Raw Zone error:", e)

# =============================
# 2️⃣ STAGING ZONE
# =============================
staging_df = None
if raw_df is not None:
    try:
        staging_df = raw_df[["country_name", "year", "value"]]
        staging_df.to_csv(STAGING_FILE, index=False)
        insert_pipeline_metadata(cursor, "Staging", "staging_data.csv", staging_df, "SUCCESS")
    except Exception as e:
        insert_pipeline_metadata(cursor, "Staging", "staging_data.csv", pd.DataFrame(), "FAILED")
        print("❌ Staging Zone error:", e)

# =============================
# 3️⃣ CLEANSING ZONE
# =============================
clean_df = None
if staging_df is not None:
    try:
        clean_df = staging_df.dropna()

        # Standardize column names
        clean_df = clean_df.rename(columns={
            "country_name": "country",
            "value": "co2"
        })

        clean_df.to_csv(CLEAN_FILE, index=False)
        insert_pipeline_metadata(cursor, "Cleansing", "clean_data.csv", clean_df, "SUCCESS")
    except Exception as e:
        insert_pipeline_metadata(cursor, "Cleansing", "clean_data.csv", pd.DataFrame(), "FAILED")
        print("❌ Cleansing Zone error:", e)

# =============================
# 4️⃣ PRESENTATION ZONE
# =============================
if clean_df is not None:
    try:
        presentation_df = (
            clean_df
            .groupby(["country", "year"], as_index=False)
            .agg(total_co2=("co2", "sum"))
        )

        presentation_df.to_csv(PRESENTATION_FILE, index=False)
        insert_pipeline_metadata(cursor, "Presentation", "presentation.csv", presentation_df, "SUCCESS")
    except Exception as e:
        insert_pipeline_metadata(cursor, "Presentation", "presentation.csv", pd.DataFrame(), "FAILED")
        print("❌ Presentation Zone error:", e)

# =============================
# 5️⃣ PREDICTION ZONE
# =============================
try:
    prediction_df = pd.read_csv(PREDICTION_FILE)
    insert_pipeline_metadata(cursor, "Prediction", "test_data.csv", prediction_df, "SUCCESS")
except Exception as e:
    insert_pipeline_metadata(cursor, "Prediction", "test_data.csv", pd.DataFrame(), "FAILED")
    print("❌ Prediction Zone error:", e)

# =============================
# COMMIT & CLOSE
# =============================
conn.commit()
cursor.close()
conn.close()

print("✅ Pipeline metadata process finished successfully")
