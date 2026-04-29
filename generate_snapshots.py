"""Generate fresh PNG snapshots of the Calling Sheet Summary tab."""
import os
import tempfile
import datetime
import requests
import gspread
from google.oauth2.service_account import Credentials
import google.auth.transport.requests
import pypdfium2 as pdfium

SHEET_ID = "1HB79kOjNIeHJXPlDET4ksE3QiUvPi6MfG6i5RSw-gm4"

sa_json = os.environ["GOOGLE_SA_JSON"]
tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
tmp.write(sa_json)
tmp.close()

creds = Credentials.from_service_account_file(
    tmp.name,
    scopes=["https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"],
)
sh = gspread.authorize(creds).open_by_key(SHEET_ID)
gid = next(
    s["properties"]["sheetId"]
    for s in sh.fetch_sheet_metadata()["sheets"]
    if s["properties"]["title"] == "Summary"
)

creds.refresh(google.auth.transport.requests.Request())
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export"
params = {
    "format": "pdf", "gid": gid, "portrait": "false", "size": "A4",
    "fitw": "true", "gridlines": "false", "sheetnames": "false", "printtitle": "false",
}
r = requests.get(url, params=params,
                 headers={"Authorization": f"Bearer {creds.token}"}, timeout=120)
r.raise_for_status()

ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
date_str = datetime.datetime.now(ist).strftime("%Y-%m-%d")

pdf = pdfium.PdfDocument(r.content)
for i, page in enumerate(pdf):
    img = page.render(scale=2.0).to_pil()
    img.save(f"summary_{date_str}_p{i+1}.png", "PNG")
print(f"Generated {len(pdf)} pages for {date_str}")
