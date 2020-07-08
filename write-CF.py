#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Christopher
"""

import requests
import json
from utils import companies

def get_cash_flow(company):
    resp = requests.get(f"https://financialmodelingprep.com/api/v3/financials/cash-flow-statement/{company}")
    resp = resp.json()
    file = open(f"cash-flow-{company}.txt", "w")
    json.dump(resp, file, indent=2)
    file.close()


for company in companies:
    get_cash_flow(company)