from utils import read_income_statement, read_balance_sheet, read_cash_flow, read_company_profile, companies
import pandas as pd

def CompDCF(comp):
    last_year = 2019
    income = read_income_statement(comp, 2014, 2019)
    ebit = read_income_statement(comp, 2014, 2019)
    depre = read_cash_flow(comp, 2014, 2019)
    capex = read_cash_flow(comp, 2014, 2019)
    NWC = read_balance_sheet(comp, 2014, 2019)
    shares = read_income_statement(comp, 2018, 2019)
    debt = read_balance_sheet(comp, 2018, 2019)
    cash = read_balance_sheet(comp, 2018, 2019)
    price = read_company_profile(comp)
    sector = read_company_profile(comp)
    if len(income) < 5:
        last_year = 2018
        income = read_income_statement(comp, 2013, 2018)
        ebit = read_income_statement(comp, 2013, 2018)
        depre = read_cash_flow(comp, 2013, 2018)
        capex = read_cash_flow(comp, 2013, 2018)
        NWC = read_balance_sheet(comp, 2013, 2018)
        shares = read_income_statement(comp, 2017, 2018)
        debt = read_balance_sheet(comp, 2017, 2018)
        cash = read_balance_sheet(comp, 2017, 2018)
        price = read_company_profile(comp)
        sector = read_company_profile(comp)
  

#CALCULATE AVERGE REVENUE GROWTH OVER LAST 5 YEARS
    sum_ = 0
    for year in income:
        sum_ += income[year]["rvgr"]
    avg_rvgr = sum_ / len(income)
 
    
#CALCULATE AVERAGE EBIT MARGIN OVER LAST 5 YEARS
    sume = 0
    for year in ebit:
        sume += ebit[year]["ebit%"]
    avg_ebitp = sume / len(ebit)


#CALCULATE AVERAGE D&A AS % OF REVENUE OVER LAST 5 YEARS
    suma = 0
    for year in depre:
        suma += depre[year]["dna"] / income[year]["rv"]
    avg_dnap = suma / len(depre)

    
#CALCULATE AVERAGE CAPEX AS % OF REVENUE OVER LAST 5 YEARS
    sumc = 0
    for year in capex:
        sumc += (capex[year]["capex"] / income[year]["rv"]) * -1
    avg_capexp = sumc / len(capex)


#CALCULATE AVERAGE CHANGE IN NWC AS % OF REVENUE OVER LAST 5 YEARS
    sum1 = 0
    sum2 = 0
    sum3 = 0
    sum4 = 0
    for i in range(2):
        year1 = last_year - i
        year2 = year1 - i
        year3 = year2 - i
        year4 = year3 - i
        sum1 += NWC[last_year]["ar"] + NWC[last_year]["inv"] - NWC[last_year]["ap"] - NWC[year1]["ar"] - NWC[year1]["inv"] + NWC[year1]["ap"]
        sum2 += NWC[year1]["ar"] + NWC[year1]["inv"] - NWC[year1]["ap"] - NWC[year2]["ar"] - NWC[year2]["inv"] + NWC[year2]["ap"]
        sum3 += NWC[year2]["ar"] + NWC[year2]["inv"] - NWC[year2]["ap"] - NWC[year3]["ar"] - NWC[year3]["inv"] + NWC[year3]["ap"]
        sum4 += NWC[year3]["ar"] + NWC[year3]["inv"] - NWC[year3]["ap"] - NWC[year4]["ar"] - NWC[year4]["inv"] + NWC[year4]["ap"]
        
    delta1 = sum1/income[last_year]["rv"]
    delta2 = sum2/income[year1]["rv"]
    delta3 = sum3/income[year2]["rv"]
    delta4 = sum4/income[year3]["rv"]
    avg_deltaNWC = (delta1 + delta2 + delta3 + delta4)/4
   
    
#CALCULATE FCFFs FOR NEXT 5 YEARS & DISCOUNT THEM
    #DIFFERENT PERPETUAL GROWTH RATES FOR DIFFERENT INDUSTRIES
    HURDLE_RATE = 0.08
    if sector["sector"] == "Technology":
        LT_GROWTH = 0.02        
    elif sector["sector"] == "Industrials":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Financial Services":
        LT_GROWTH = 0.015
    elif sector["sector"] == "Healthcare":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Consumer Cyclical":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Consumer Defensive":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Utilities":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Communication Services":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Real Estate":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Basic Materials":
        LT_GROWTH = 0.01
    elif sector["sector"] == "Energy":
       LT_GROWTH = 0.01
    TAX_RATE = 0.21


    last_rev = income[last_year]["rv"]
    fcffpv = 0
    for i in range(5):
        last_rev = last_rev * (1 + avg_rvgr)
        ebit = last_rev * avg_ebitp
        depre = last_rev * avg_dnap
        capex = last_rev * avg_capexp
        NWC = last_rev * avg_deltaNWC
        nopat = ebit * (1-TAX_RATE) 
        fcff = nopat + depre - NWC - capex
        fcffpv += fcff / ((1 + HURDLE_RATE) ** (i+1))

 
#CALCULATE TERMINAL VALUE & DISCOUNT IT
    ter_fcff = fcff
    tv = (ter_fcff * (1 + LT_GROWTH))/(HURDLE_RATE - LT_GROWTH)
    tvpv = tv / ((1 + HURDLE_RATE) ** (5))
 
 
#LAST YEAR'S DEBT    
    sumd = 0
    for year in debt:
        sumd += debt [year]["debt"]
    debt = sumd


#LAST YEAR'S CASH
    sumca = 0
    for year in cash:
        sumca += cash [year]["cash"]
    cash = sumca
  

#SHARES OUTSTANDING
    sums = 0
    for year in shares:
        sums += shares[year]["shares"]
    shares = sums
    

#CALCULATE ENTERPRISE VALUE, EQUITY VALUE, AND INTRINSIC SHARE PRICE    []
    ev = tvpv + fcffpv
    eqv = ev - debt + cash
    intrinsic_value = round(eqv / shares, 2)


#MARGIN OF SAFETY AND UPPER LIMIT
    margin_of_safety = 1.15
    upper_limit = 1.3

#COMPARE INTRINSIC SHARE PRICE TO ACTUAL SHARE PRICE    
    outp = pd.DataFrame()
    if intrinsic_value > price['price'] * margin_of_safety and intrinsic_value < price['price'] * upper_limit:
        outp = [str(comp)]
        print(outp, intrinsic_value)
        return outp

banana = pd.DataFrame()
for comp in companies:
    Grud = CompDCF(comp)
    banana = banana.append(Grud)