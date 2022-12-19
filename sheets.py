from oauth2client.service_account import ServiceAccountCredentials

import gspread
from gspread.models import Spreadsheet
from gspread_dataframe import set_with_dataframe


def get_credentials() -> ServiceAccountCredentials:
    scopes =  ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('secret_key/hrmasters-2c26d45c45f2.json', scopes)
    return credentials


def open_google_spreadsheet(spreadsheet_id: str) -> Spreadsheet:
    credentials = get_credentials(['https://spreadsheets.google.com/feeds'])
    gc = gspread.authorize(credentials)
    return gc.open_by_key(spreadsheet_id)


def pastDataFrame_into_Sheets(df, sheet_name): # returns sheet_id
    OAuthCredentialObject = get_credentials()
    client = gspread.Client(auth=OAuthCredentialObject)
    mysheet = client.create(title=sheet_name, folder_id='1PYwneYSP9AyYNCzdNTeprSIVkd4ZSj9u')
    sheet_id = mysheet.id
    sh = client.open_by_key(sheet_id)
    sh.share('remont.io', perm_type='domain', role='writer')
    worksheet = sh.get_worksheet(0)
    set_with_dataframe(worksheet, df)
    return sheet_id