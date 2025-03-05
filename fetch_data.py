import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Define API Scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ✅ Authenticate Google Sheets API
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# ✅ Google Sheet ID
spreadsheet_id = "1Pqp70Q1VbtCk432aGE0xH54gzFiXERagIQdBVVL2uTA"  # Replace with actual ID

# ✅ Open the Sheet
sheet = client.open_by_key(spreadsheet_id).sheet1  

# ✅ Fetch Data & Convert to Pandas DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ✅ Display the Data
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
print("✅ Google Sheets Data Fetched Successfully!\n")
print(df.head())  # Show first 5 rows
