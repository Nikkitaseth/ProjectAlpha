#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from utils import read_company_profile
from main import banana
import pandas as pd
from datetime import date as dt
from pandas_datareader import data
from random import choice
import matplotlib.pyplot as plt 
import numpy as np
import bt 
import math

"""
Created on Sat Feb 15 09:34:36 2020
@author: Christopher
"""


"""
GET DATAFRAME WITH UNDERVALUED COMPANIE FROM MAIN.PY (BANANA) AND CONVERT IT TO 
    LIST WHICH IS THEN USED AS SOURCE FOR "TICKER" FEEDING INTO ALL THE OTHER RATIOS
"""

ticker_list = banana
ticker_list.columns = ["Ticker"]


"""
#GENERAL INPUTS FOR FOLLOWING CODE
"""

tickers = ticker_list["Ticker"].to_list()
start_date = dt(2010,1,1)
end_date = dt(2020, 2, 17)

RFR = 0.021 #annual TBOND (10y or 30y?) yield bc we look for long term


"""
#OPTIMIZE FOR MAX SHARPE RATIO BY SOURCING TICKERS FROM DCF OUTPUT
"""

table = bt.get(tickers, start = start_date, end = end_date)

# calculate daily and annual returns of the stocks
returns_daily = table.pct_change()
returns_daily = returns_daily.dropna() 
returns_annual = returns_daily.mean() * 252

# get daily and covariance of returns of the stock
cov_daily = returns_daily.cov()
cov_annual = cov_daily * 252

# empty lists to store returns, volatility and weights of imiginary portfolios
port_returns = []
port_volatility = []
sharpe_ratio = []
stock_weights = []

# set the number of combinations for imaginary portfolios
num_assets = len(tickers)
num_portfolios = 50000

#set random seed for reproduction's sake
np.random.seed(101)

# populate the empty lists with each portfolios returns,risk and weights
for single_portfolio in range(num_portfolios):
    weights = np.random.random(num_assets)
    weights /= np.sum(weights)
    excess_returns = np.dot(weights, returns_annual) - RFR
    volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
    sharpe = excess_returns / volatility
    sharpe_ratio.append(sharpe)
    port_returns.append(excess_returns)
    port_volatility.append(volatility)
    stock_weights.append(weights)

# a dictionary for Returns and Risk values of each portfolio
portfolio = {'Returns': port_returns,
             'Volatility': port_volatility,
             'Sharpe Ratio': sharpe_ratio}

# extend original dictionary to accomodate each ticker and weight in the portfolio
for counter,symbol in enumerate(tickers):
    portfolio[symbol] = [Weight[counter] for Weight in stock_weights]

# make a nice dataframe of the extended dictionary
df = pd.DataFrame(portfolio)

# get better labels for desired arrangement of columns
column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock for stock in tickers]

# reorder dataframe columns
df = df[column_order]

# find min Volatility & max sharpe values in the dataframe (df)
min_volatility = df['Volatility'].min()
max_sharpe = df['Sharpe Ratio'].max()

# use the min, max values to locate and create the two special portfolios
sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]
min_variance_port = df.loc[df['Volatility'] == min_volatility]
sharpe_ratio = round(float(sharpe_portfolio["Sharpe Ratio"]), 3)

# plot frontier, max sharpe & min Volatility values with a scatterplot
plt.style.use('seaborn-dark')
df.plot.scatter(x='Volatility', y='Returns', c='Sharpe Ratio', cmap='Blues', edgecolors='none', figsize=(10, 8), grid=True, marker = 'p')
plt.scatter(x=sharpe_portfolio['Volatility'], y=sharpe_portfolio['Returns'], c='red', marker='+', s=200)
plt.scatter(x=min_variance_port['Volatility'], y=min_variance_port['Returns'], c='blue', marker='+', s=200 )
plt.xlabel('Volatility (Std. Deviation)')
plt.ylabel('Expected Returns')
plt.title('Efficient Frontier')
plt.savefig('Efficient_frontier_max_port.png')


"""
#VALUE AT RISK (VaR) USING TICKERS FROM DCF OUTPUT
"""

def get_Portfolio(tickers, start_date, end_date):
    stock_data = data.DataReader(tickers, data_source='yahoo', start = start_date, end = end_date)['Adj Close']
    
    return stock_data

# Change shape of DataFrame with optimized weights so they can be used as a source for VaR
sharpe_port_weights = sharpe_portfolio.drop(columns =["Returns", "Volatility", "Sharpe Ratio"]).transpose()
sharpe_port_weights.columns = ["Weight"]

# Weights
weights = pd.Series(index = tickers, dtype = float)
weights[tickers]= sharpe_port_weights["Weight"]

# Monte Carlo paramters
monte_carlo_runs = 100 #INCREASE OT 10000 FOR PRESENTATION NUMBERS
days_to_simulate = 5
loss_cutoff = 0.99 # count any losses larger than X% 

# Call that simple function we wrote above
what_we_got = get_Portfolio(tickers, start_date, end_date)

# Compute returns from those Adjusted Closes
returns = what_we_got[tickers].pct_change()
returns = returns.dropna() 

# Calculate mu and sigma
mu = returns.mean()
sigma= returns.std()

# Monte Carlo VaR loop
compound_returns = sigma.copy()
total_simulations = 0
bad_simulations = 0
for run_counter in range(0,monte_carlo_runs): # Loop over runs    
    for i in tickers: # loop over tickers
        # Loop over simulated days:
        compounded_temp = 1
        for simulated_day_counter in range(0,days_to_simulate): # loop over days
            simulated_return = choice(returns[i])
            compounded_temp = compounded_temp * (simulated_return + 1)        
        compound_returns[i]=compounded_temp # store compounded returns
    # Now see if those returns are bad by combining with weights
    portfolio_return = compound_returns.dot(weights) # dot product
    if(portfolio_return<loss_cutoff):
        bad_simulations = bad_simulations + 1
    total_simulations = total_simulations + 1


"""
#TREYNOR
"""

def beta(comp):
    beta = read_company_profile(comp)
    
    ß = pd.DataFrame([float(beta["beta"])])
    return ß

ß_df = pd.DataFrame()
for comp in tickers: 
    t = beta(comp)
    ß_df = ß_df.append(t)

#Combine ß and weights to calculate portfolio ß
ß_df.columns = ["Beta"]
ß_df.index = tickers
weights_TT = pd.DataFrame([sharpe_port_weights["Weight"]]).transpose()
ß_dff = pd.concat([weights_TT, ß_df], axis = 1)
weights_P = pd.Series(index = tickers, dtype = float)
ß_dff.columns = ["Weight", "Beta"]
ß_dff["Components Portfolio Beta"] = ß_dff["Beta"] * ß_dff["Weight"]
ß_T = sum(ß_dff["Components Portfolio Beta"])

treynor_ratio = round(float((sharpe_portfolio["Returns"] - RFR) / ß_T), 3)


"""
#SORTINO RATIO
"""

#S&P500 for r (Benchmark)
Benchmark = ["^GSPC"]
SnP = bt.get(Benchmark, start = start_date, end = end_date)
returns_daily_SnP = SnP.pct_change().dropna()

#Portfolio returns for mu
mu = float(sharpe_portfolio["Returns"]) + RFR
r = float(returns_daily_SnP.mean() * 252)
r_d = pd.DataFrame(returns_daily_SnP.mean())

#Downside Calculations
base = returns_daily
#Need DataFrame for every company and the weight in portfolio

#Sortino Calculation
excess_sortino = float(mu - r)
downside = 0.101869488 #broadcast the r in one column and down all the portfolio returns (need column for that) and then have new column that calculated the ri - r und dann ^2 für sqrt(mean())

sortino_ratio = excess_sortino / downside

#DOWNSIDE CALCULATIONS
c1 = pd.DataFrame(table["mmm"].pct_change().dropna()) 
c1 = c1 * float(sharpe_portfolio["MMM"])

c2 = pd.DataFrame(table["afl"].pct_change().dropna()) 
c2 = c2 * float(sharpe_portfolio["AFL"])

c3 = pd.DataFrame(table["aph"].pct_change().dropna()) 
c3 = c3 * float(sharpe_portfolio["APH"])

c4 = pd.DataFrame(table["aapl"].pct_change().dropna()) 
c4 = c4 * float(sharpe_portfolio["AAPL"])

c5 = pd.DataFrame(table["amat"].pct_change().dropna()) 
c5 = c5 * float(sharpe_portfolio["AMAT"])

c6 = pd.DataFrame(table["adm"].pct_change().dropna()) 
c6 = c6 * float(sharpe_portfolio["ADM"])
    
c7 = pd.DataFrame(table["cci"].pct_change().dropna()) 
c7 = c7 * float(sharpe_portfolio["CCI"])

c8 = pd.DataFrame(table["csx"].pct_change().dropna()) 
c8 = c8 * float(sharpe_portfolio["CSX"])

c9 = pd.DataFrame(table["dg"].pct_change().dropna()) 
c9 = c9 * float(sharpe_portfolio["DG"])

c10 = pd.DataFrame(table["ess"].pct_change().dropna())
c10 = c10 * float(sharpe_portfolio["ESS"])

c11 = pd.DataFrame(table["fe"].pct_change().dropna()) 
c11 = c11 * float(sharpe_portfolio["FE"])

c12 = pd.DataFrame(table["hal"].pct_change().dropna()) 
c12 = c12 * float(sharpe_portfolio["HAL"])

c13 = pd.DataFrame(table["hum"].pct_change().dropna()) 
c13 = c13 * float(sharpe_portfolio["HUM"])

c14 = pd.DataFrame(table["ntap"].pct_change().dropna()) 
c14 = c14 * float(sharpe_portfolio["NTAP"])

c15 = pd.DataFrame(table["orly"].pct_change().dropna()) 
c15 = c15 * float(sharpe_portfolio["ORLY"])

c16 = pd.DataFrame(table["pgr"].pct_change().dropna()) 
c16 = c16 * float(sharpe_portfolio["PGR"])

c17 = pd.DataFrame(table["slg"].pct_change().dropna())
c17 = c17 * float(sharpe_portfolio["SLG"])

c18 = pd.DataFrame(table["sna"].pct_change().dropna()) 
c18 = c18 * float(sharpe_portfolio["SNA"])

c19 = pd.DataFrame(table["sbux"].pct_change().dropna()) 
c19 = c19 * float(sharpe_portfolio["SBUX"])

c20 = pd.DataFrame(table["syy"].pct_change().dropna()) 
c20 = c20 * float(sharpe_portfolio["SYY"])

c21 = pd.DataFrame(table["tjx"].pct_change().dropna()) 
c21 = c21 * float(sharpe_portfolio["TJX"])

c22 = pd.DataFrame(table["v"].pct_change().dropna())
c22 = c22 * float(sharpe_portfolio["V"])

c23 = pd.DataFrame(table["vmc"].pct_change().dropna()) 
c23 = c23 * float(sharpe_portfolio["VMC"])

afgsjh = c1["mmm"] + c2["afl"] + c3["aph"] + c4["aapl"] + c5["amat"] + c6["adm"] + c7["cci"] + c8["csx"] + c9["dg"] + c10["ess"] + c11["fe"] + c12["hal"] + c13["hum"] + c14["ntap"] + c15["orly"] + c16["pgr"] + c17["slg"] + c18["sna"] + c19["sbux"] + c20["syy"] + c21["tjx"] + c22["v"] + c23["vmc"]


semi_variance = afgsjh - returns_daily_SnP["gspc"]

downside_r = pd.DataFrame(afgsjh[0:], returns_daily_SnP["gspc"])


"""
#Information ratio (average alpha per unit of risk)
"""
rp = mu
rb = r
er = semi_variance.std() * math.sqrt(252)

information_ratio = (rp - rb) / er


"""
#OUTPUTS
"""

print("The Sharpe Ratio is ", sharpe_ratio,".")
print("The Treynor Ratio is ", treynor_ratio,".")
print("VaR: The portfolio lost",round((1-loss_cutoff)*100,3),"%", "over",days_to_simulate,"days", round(bad_simulations/total_simulations * 100, 2), "% of the time")
print("The Sortino Ratio is ",round(sortino_ratio, 3))
print("The Information Ratio is ",round(information_ratio, 3))
##################


"""
Calculating downside for Sortino is missing. A lot of work.
Once Sortino is done, use Portfolio returns and benchmark returns to calculate Information ratio
"""
