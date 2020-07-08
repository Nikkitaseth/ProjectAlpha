#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Christopher
"""


import requests
import json
from utils import companies

def get_income_statement(company):
    resp = requests.get(f"https://financialmodelingprep.com/api/v3/financials/income-statement/{company}")
    resp = resp.json()
    file = open(f"income-statement-{company}.txt", "w")
    json.dump(resp, file, indent=2)
    file.close()


for company in companies:
    get_income_statement(company)