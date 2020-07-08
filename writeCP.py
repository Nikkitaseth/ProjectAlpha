#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Christopher
"""

#write company profile
#https://financialmodelingprep.com/api/v3/company/profile/

import requests
import json
from utils import companies

def get_income_statement(company):
    resp = requests.get(f"https://financialmodelingprep.com/api/v3/company/profile/{company}")
    resp = resp.json()
    file = open(f"company-profile-{company}.txt", "w")
    json.dump(resp, file, indent=2)
    file.close()


for company in companies:
    get_income_statement(company)
    
