#!/usr/bin/python
import sys
import pandas
import requests
import re
import urllib.request
from bs4 import BeautifulSoup

# This program filter stocks downloaded from internet using the following links:
##Exchanges will usually publish an up-to-date list of securities on their web pages. For example, these pages offer CSV downloads:
#NASDAQ: https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download
#AMEX: https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download
#NYSE: https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download

#'\nPiotroski F-Score\n', # Good value >= 5
#'\nAltman Z-Score\n', # SafeValue must be >= 3
#'\nBeneish M-Score\n', # NonManipulative >= 1

# DoubleSpaced fields:
# Alos add %of 1DayPriceChange, available in value just before Volume:
DoubleSpacedKeys1=[' Market Cap $: ',' Enterprise Value $: ',' Volume: ',' Avg Vol (1m): ', ]

# SingleSpaced fields: '\nPrice: ', ' $3.76\n',
SingleSpacedKeys2=['\nPrice: ']
#tripleSpaced fields:
#'\nEarnings Power Value\n', ' ', ' ', '\n2.53\n', '\nNet Current Asset Value\n', ' ', ' ', '\n0.65\n', '\nTangible Book\n', ' ', ' ', '\n1.03\n', '\nProjected FCF\n', ' ', ' ', '\n3.02\n', '\nMedian P/S Value\n', ' ', ' ', '\n4.36\n',
#'\nGraham Number\n', ' ', ' ', '\n2.42\n', '\nDCF (FCF Based)\n', ' ', ' ', '\n5.16\n', '\nDCF (Earnings Based)\n', ' ', ' ', '\n3.62\n',
TripleSpacedPriceKeys3=['\nEarnings Power Value\n','\nNet Current Asset Value\n','\nTangible Book\n','\nProjected FCF\n','\nMedian P/S Value\n',
                  '\nGraham Number\n', '\nDCF (FCF Based)\n','\nDCF (Earnings Based)\n']

DoubleSpacedKeys4=['\nPEG Ratio\n','\nPB Ratio\n','\nPrice-to-Tangible-Book\n','\nPS Ratio\n','\nPrice-to-Median-PS-Value\n',
                   '\nPrice-to-Intrinsic-Value-DCF (Earnings Based)\n','\nPrice-to-Intrinsic-Value-Projected-FCF\n','\nPrice-to-Graham-Number\n',
                   '\nCurrent Ratio\n','\nQuick Ratio\n','\nCash-To-Debt\n','\nEquity-to-Asset\n','\nDebt-to-Equity\n','\nDebt-to-EBITDA\n',
                   '\nOperating Margin %\n','\nNet Margin %\n','\nROE %\n','\nROA %\n']
# Same fields: '\nROIC 28.08%\n', '\nWACC 2.87%\n'
NoSpacedKeys5=['\nROIC ', '\nWACC ']

DoubleSpacedKeys6=['\n3-Year Revenue Growth Rate\n','\n3-Year EBITDA Growth Rate\n','\n3-Year EPS without NRI Growth Rate\n',
                   '\nPE Ratio\n','\nForward PE Ratio\n','\nPE Ratio without NRI\n','\nShiller PE Ratio\n','\nPrice-to-Owner-Earnings\n',
                   '\nPrice-to-Free-Cash-Flow\n','\nPrice-to-Operating-Cash-Flow\n','\nEV-to-EBIT\n','\nEV-to-EBITDA\n','\nEV-to-Revenue\n',
                   '\nPiotroski F-Score\n','\nAltman Z-Score\n', '\nBeneish M-Score\n','\nFinancial Strength\n','\nProfitability Rank\n','\nValuation Rank\n']

# Use the Volume Pos, if ever needed to get the Company Name: '\nWipro Ltd\n$\n3.76\n', ' -0.04 (-1.05%)\n',' Volume: ',
# Duplicate Key/Val Pairs: ' P/E (TTM): ', ' ', ' 14.97 ', ' ', ' P/B: ', ' ', ' 2.73 ', ' ',
# UnUsed KeyVal Pairs:  '\nDividend Yield %\n', ' ', ' 0.28 ', '\nForward Dividend Yield %\n', ' ', ' 0.28 ', '\nDividend Payout Ratio\n', ' ', ' 0.05 ',
#                       '\n3-Year Dividend Growth Rate\n', ' ', ' -45 ', '\n5-Year Yield-on-Cost %\n', ' ', ' 0.04 ', '\n3-Year Average Share Buyback Ratio\n', ' ', ' 2.8 ',
#                       '\nEarnings Yield (Greenblatt) %\n', ' ', ' 11.01 ', '\nForward Rate of Return (Yacktman) %\n', ' ', ' 9.51 '
'''
#Sample Html page code converted to text 
['\nWipro Ltd\n$\n3.76\n', ' -0.04 (-1.05%)\n', ' Volume: ', ' ', ' 322,608 ', ' Avg Vol (1m): ', ' ', ' 1,229,621 ',
 ' Market Cap $: ', ' ', ' 21.39 Bil ', ' Enterprise Value $: ', ' ', ' 18.35 Bil ',
 '\nPrice: ', ' $3.76\n',
 '\nEarnings Power Value\n', ' ', ' ', '\n2.5\n', '\nNet Current Asset Value\n', ' ', ' ', '\n0.65\n', '\nTangible Book\n', ' ', ' ', '\n1.02\n',
 '\nProjected FCF\n', ' ', ' ', '\n2.99\n', '\nMedian P/S Value\n', ' ', ' ', '\n4.33\n', '\nGraham Number\n', ' ', ' ', '\n2.4\n',
 '\nDCF (FCF Based)\n', ' ', ' ', '\n5.11\n', '\nDCF (Earnings Based)\n', ' ', ' ', '\n3.59\n',

 '\nPEG Ratio\n', ' ', ' 3.02 ', '\nPB Ratio\n', ' ', ' 2.73 ', '\nPrice-to-Tangible-Book\n', ' ', ' 3.69 ', '\nPS Ratio\n', ' ', ' 2.48 ','\nPrice-to-Median-PS-Value\n', ' ', ' 0.87 ',
 '\nPrice-to-Intrinsic-Value-DCF (Earnings Based)\n', ' ', ' 1.05 ', '\nPrice-to-Intrinsic-Value-Projected-FCF\n', ' ', ' 1.26 ', '\nPrice-to-Graham-Number\n', ' ', ' 1.57 ',

 '\nCurrent Ratio\n', ' ', ' 2.4 ', '\nQuick Ratio\n', ' ', ' 2.38 ', '\nCash-To-Debt\n', ' ', ' 2.96 ', '\nEquity-to-Asset\n', ' ', ' 0.66 ',
 '\nDebt-to-Equity\n', ' ', ' 0.22 ', '\nDebt-to-EBITDA\n', ' ', ' 0.73 ',

 '\nOperating Margin %\n', ' ', ' 17.48 ', '\nNet Margin %\n', ' ', ' 16.58 ','\nROE %\n', ' ', ' 18.1 ', '\nROA %\n', ' ', ' 12.11 ',
 '\nROIC 28.08%\n', '\nWACC 2.87%\n',
 '\n3-Year Revenue Growth Rate\n', ' ', ' 7.6 ', '\n3-Year EBITDA Growth Rate\n', ' ', ' 5.3 ', '\n3-Year EPS without NRI Growth Rate\n', ' ', ' 3.3 ',

 '\nPE Ratio\n', ' ', ' 14.97 ', '\nForward PE Ratio\n', ' ', ' 15.17 ', '\nPE Ratio without NRI\n', ' ', ' 14.97 ',
 '\nShiller PE Ratio\n', ' ', ' 23.48 ', '\nPrice-to-Owner-Earnings\n', ' ', ' 10.76 ',
 '\nPrice-to-Free-Cash-Flow\n', ' ', ' 14.66 ', '\nPrice-to-Operating-Cash-Flow\n', ' ', ' 11.9 ',
 '\nEV-to-EBIT\n', ' ', ' 9.08 ', '\nEV-to-EBITDA\n', ' ', ' 7.85 ', '\nEV-to-Revenue\n', ' ', ' 2.01 ',

 '\nPiotroski F-Score\n', ' ', ' 8 ', '\nAltman Z-Score\n', ' ', ' 5.87 ', '\nBeneish M-Score\n', ' ', ' -2.7 ',
 '\nFinancial Strength\n', ' ', '\n8/10\n', '\nProfitability Rank\n', ' ', '\n9/10\n', '\nValuation Rank\n', ' ', '\n9/10\n',
 ]
'''

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

# if element is found it returns index of element else returns None
def find_element_in_list(element, list_element, valueSpacing):
    try:
        indx = list_element.index(element)
        #print(element, indx, list_element[indx] )
        value_element=list_element[indx + valueSpacing]
        #print(valueSpacing, value_element )
        value_element=value_element.replace(',', '').replace('\n', '').replace(' ', '').replace('$', '').replace('/10','')
        #print(element, value_element)
        if value_element.find('Bil') > 0:
            value_element=value_element.replace('Bil', '')
            value=float(value_element)*1000
            #print('Bil Found', element, value)
        else:
            value=float(value_element)

        return value
    except ValueError:
        print('ValueError Exception:', element, valueSpacing, ValueError)
        return 0

def getStockData(stockDataUrl, filehandle):
    html = urllib.request.urlopen(stockDataUrl)
    soup = BeautifulSoup(html, features="lxml")
    data = soup.findAll(text=True)
    result = filter(visible, data)
    items_list=list(result)
    print(items_list)

    #Order of keys: DoubleSpacedKeys1 SingleSpacedKeys2 TripleSpacedPriceKeys3 DoubleSpacedKeys4 NoSpacedKeys5 DoubleSpacedKeys6
    print(DoubleSpacedKeys1)
    for keyFeature in DoubleSpacedKeys1:
        keyData=find_element_in_list(keyFeature, items_list,2)
        filehandle.write('%s,' % keyData)
        #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)

    # SingleSpaced fields: '\nPrice: ', ' $3.76\n',
    print(SingleSpacedKeys2)
    for keyFeature in SingleSpacedKeys2:
        keyData=find_element_in_list(keyFeature, items_list,1)
        filehandle.write('%s,' % keyData)
        #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)

    print(TripleSpacedPriceKeys3)
    for keyFeature in TripleSpacedPriceKeys3:
        keyData=find_element_in_list(keyFeature, items_list,3)
        filehandle.write('%s,' % keyData)
        #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)

    print(DoubleSpacedKeys4)
    for keyFeature in DoubleSpacedKeys4:
        keyData=find_element_in_list(keyFeature, items_list,2)
        filehandle.write('%s,' % keyData)
        #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)

    print(DoubleSpacedKeys6)
    for keyFeature in DoubleSpacedKeys6:
        keyData=find_element_in_list(keyFeature, items_list,2)
        filehandle.write('%s,' % keyData)
        if keyFeature==DoubleSpacedKeys6[-1]:
            filehandle.write('\n')
        #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)

#preFilteredStocksData file contains some prefiltered stocks to be further filetered for to start monitoring on daily basis
preFilteredStocksDataFile = 'stocksData/preFilteredStocksData.csv'
#Header: Ticker,Company,Industry,Institutional Ownership,Market Cap ($M),PB Ratio,PS Ratio,Operating Margin %,Net Margin %,Price,Avg Daily TradeVolume
#result = pandas.read_csv(preFilteredStocksDataFile)
'''
with open(preFilteredStocksDataFile,'r') as stocksData:
    for dataRow in stocksData:
        stockDataFields = dataRow.split(',')
        if (stockDataFields[0] == 'Ticker'):
            continue #skip header row
        # filter a Stock based on desired criteria
        if (stockDataFields[3] < 10):
            continue
        print(stockDataFields)
'''
def main(argv):
    N_DAYS_AGO = int(argv[1])
    tickers = argv[2:]
    print("lineColor, ticker, cur, min, max, mean, std")
    #Order of keys: DoubleSpacedKeys1 SingleSpacedKeys2 TripleSpacedPriceKeys3 DoubleSpacedKeys4 NoSpacedKeys5 DoubleSpacedKeys6
    with open("stockMetricsData.csv", "w") as filehandle:
        for keyFeature in DoubleSpacedKeys1:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        for keyFeature in SingleSpacedKeys2:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        for keyFeature in TripleSpacedPriceKeys3:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        for keyFeature in DoubleSpacedKeys4:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        #for keyFeature in NoSpacedKeys5:
        #    filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
        #   # print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        for keyFeature in DoubleSpacedKeys6:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            if keyFeature==DoubleSpacedKeys6[-1]:
                filehandle.write('\n')
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')

        for ticker in tickers:
            #lineColor = sorted_colors[random.randint(0,len(sorted_colors)-1)]
            stockDataUrl='https://www.gurufocus.com/stock/'+ticker+'/summary'
            getStockData(stockDataUrl, filehandle)
            #analyseStock(ticker, N_DAYS_AGO, lineColor)
        filehandle.close()
    #time.sleep(100)

if __name__ == "__main__":
   main(sys.argv)
