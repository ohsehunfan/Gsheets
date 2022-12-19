import requests
import pandas as pd
import numpy as np
import time
import datetime
import json

BASE_URL = 'https://new5a6ebcbe84573.amocrm.ru/'
access_token = ''
refresh_token = ''


def get_headers():
    headers = requests.structures.CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + get_token('access_token')
    return headers


def get_token(token_type): # token_type: access_token/ refresh_token
    with open('secret_key/amo.json', 'r') as amo_json:
        myjson = json.loads(amo_json.read())
    print(token_type)
    return myjson[token_type]


def update_token():
    url = f'{BASE_URL}oauth2/access_token'
    params = {
      "client_id": 'a8ae07f2-1af1-440a-bdf7-085bf043d7f1',
      "client_secret": 'pPtrbXR6uYuNwWPw6EIxOosMxMs4Ols3HYkpC84LCB6uDWqjGloBVmHctjuYCeiN',
      "grant_type": "refresh_token",
      "refresh_token": get_token('refresh_token'),
      "redirect_uri": BASE_URL
    }
    new_json = requests.post(url=url, json=params, headers=get_headers())
    print(new_json.text)
    print('refresh_token'+get_token('refresh_token'))
    if new_json.status_code == 200:
        with open('secret_key/amo.json', 'w') as amo_json:
            amo_json.write(new_json.text)
        return new_json.json()['access_token']


def get_correct_token():
    global access_token
    if requests.get(url=f'{BASE_URL}api/v4/leads/pipelines', headers=get_headers()).status_code!= 200:
        access_token = update_token()
    access_token = get_token('access_token')


def getFunnelSteps():
    resp_pipeline = requests.get(url=f'{BASE_URL}api/v4/leads/pipelines', headers=get_headers())  # , params=params)
    pipelines = json.loads(resp_pipeline.text)
    pipelines = pipelines['_embedded']['pipelines']
    steps1 = pd.DataFrame([i for i in pipelines[0]['_embedded']['statuses']])
    steps2 = pd.DataFrame([i for i in pipelines[1]['_embedded']['statuses']])
    steps = pd.concat([steps1, steps2]).reset_index(drop=True).drop(columns=['_links', 'account_id']).drop_duplicates()  #
    return steps


def getLeadsList(t0_, t1_):
    global access_token
    get_correct_token()
    t0 = int(time.mktime(datetime.datetime.strptime(t0_, "%d/%m/%Y").timetuple())) + 5
    t1 = int(time.mktime(datetime.datetime.strptime(t1_, "%d/%m/%Y").timetuple())) - 5
    leads = [];  status = 200;  numpage = 0
    while status == 200:
        params = {
            'limit': 250,
            'order': '[updated_at]=asc',
            'page': numpage
        }
        resp = requests.get(url=f'{BASE_URL}api/v4/leads?filter[created_at][from]={t0}&filter[created_at][to]={t1}',
                           headers=get_headers(), params=params)
        status = resp.status_code
        if status == 200:
            leads += resp.json()['_embedded']['leads']
        numpage += 1
    return leads


def getFieldNameValue(lst) -> dict:
    if all([type(ddict['values']) != list for ddict in lst]):
        return {ddict['field_name']: np.NaN for ddict in lst}
    return {ddict['field_name']: ddict['values'][0]['value'] for ddict in lst}


def getCustomFields(leads_df):
    field_value_example = leads_df['custom_fields_values'][leads_df['custom_fields_values'] != None][0]
    replace_none_fields = [{key: np.NaN for key, value in ddict_.items()} for ddict_ in field_value_example]
    leads_df['custom_fields_values'] = leads_df['custom_fields_values'].apply(
        lambda x: replace_none_fields if x == None else x)
    leads_df['custom_fields_values'] = leads_df['custom_fields_values'].apply(getFieldNameValue)
    customFieldsDf = pd.DataFrame.from_records(leads_df['custom_fields_values'].tolist())
    leads_df = pd.concat([leads_df, customFieldsDf], axis=1, join='inner').drop(columns=['custom_fields_values'])
    funnel_df = getFunnelSteps()

    leads_df['status_id'] = leads_df['status_id'].apply(lambda x: funnel_df[funnel_df['id'] == x]['name'].iloc[0])
    leads_df['created_at'] = pd.to_datetime(leads_df['created_at'], unit='s').dt.tz_localize('Europe/Moscow')
    leads_df['updated_at'] = pd.to_datetime(leads_df['updated_at'], unit='s').dt.tz_localize('Europe/Moscow')
    leads_df['closed_at'] = pd.to_datetime(leads_df['closed_at'], unit='s').dt.tz_localize('Europe/Moscow')
    leads_df['closest_task_at'] = pd.to_datetime(leads_df['closest_task_at'], unit='s').dt.tz_localize('Europe/Moscow')
    return leads_df


def getLeadsDF(t0_='19/12/2022', t1_='21/12/2022'):
    leads = getLeadsList(t0_, t1_)
    leads_df = pd.DataFrame(leads)
    leads_df = getCustomFields(leads_df)
    return leads_df