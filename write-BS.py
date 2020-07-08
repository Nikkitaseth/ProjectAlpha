#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Christopher
"""

import requests
import json
from utils import companies

def get_balance_sheet(company):
    resp = requests.get(f"https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/{company}")
    resp = resp.json()
    file = open(f"balance-sheet-{company}.txt", "w")
    json.dump(resp, file, indent=2)
    file.close()


for company in companies:
    get_balance_sheet(company)