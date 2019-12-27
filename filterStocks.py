import sys
import csv

MIN_MARKET_CAP = 1000
INST_OWNERSHIP = 25
PB_MIN = 0.3
PB_MAX = 2
PS_MIN = 0.1
PS_MAX = 3
OPERATING_MARGIN = 3
NET_MARGIN = 3
STOCK_PRICE = 3
AVG_TRADE_VOL = 100000


#read the input file
#filter the stocks using following criteria [field.replace('c1', 'c2').replace('c3', 'c4')]
#1. Market Cap > 1000(M)
#2. Inst Own > 25(%)
#3. P/B > .3 and < 2
#4. P/S > .1 and < 3
#5. Operating Margin > 3
#6. Net Margin > 3
#7. Price > 3($)
#8. Volume > 100000
# store to output file
outputFile = 'stockData/filteredStocksData.csv'
inputFile = 'stockData/preFilteredStocksData.csv'

def isStockFinancialMetricsMet(list_vals):
    if float(list_vals[4].replace(',', '').replace('"', '')) < MIN_MARKET_CAP:  # Market Cap >1000%
        return False
    if float(list_vals[3]) < INST_OWNERSHIP:  # Institutional ownership > 25%
        return False
    if float(list_vals[5].replace(',', '').replace('"', '')) < PB_MIN or \
            float(list_vals[5].replace(',', '').replace('"', '')) > PB_MAX:  # P/B ratio
        return False
    if float(list_vals[6].replace(',', '').replace('"', '')) < PS_MIN or \
            float(list_vals[5].replace(',', '').replace('"', '')) > PS_MAX:  # P/S > .1 and < 3
        return False
    if float(list_vals[7].replace(',', '').replace('"', '')) < OPERATING_MARGIN:  # Operating Margin > 3
        return False
    if float(list_vals[8].replace(',', '').replace('"', '')) < NET_MARGIN:  # Net Margin > 3
        return False
    if float(list_vals[9].replace(',', '').replace('"', '').replace('$', '')) < STOCK_PRICE:  # Price > 3
        return False
    if float(list_vals[10].replace(',', '').replace('"', '')) < AVG_TRADE_VOL:  # Volume > 100000
        return False
    return True

with open(outputFile, 'w') as fpOut:
    with open(inputFile, 'r') as fpIn:
        data = csv.reader(fpIn,  skipinitialspace=True)
        for list_vals in data:
            if list_vals[0] == 'Ticker':
                continue #skip header line
            if (not isStockFinancialMetricsMet(list_vals)):
            #if (not getStockFinancialMetricsAndCheckToInclude(list_vals)):
                continue #specified stock metrics were not fullfilled
            print(list_vals)
            fpOut.write(list_vals[0])
            fpOut.write('\n')