#!/usr/bin/python
import sys
import csv
import re
import urllib.request
import urllib.error
import urllib.response
from bs4 import BeautifulSoup
import ssl

# Basic selection criteria
MIN_STOCK_PRICE = 3
MIN_AVG_TRADE_VOL = 50000
MIN_TRADE_VOL = 10000
MIN_MARKET_CAP_MIL = 500
MIN_INST_OWNERSHIP_PERCENT = 25

#Valuation based selection criteria
MIN_PB_RATIO = 0.3
MAX_PB_RATIO = 3
MIN_PS_RATIO = 0.1
MAX_PS_RATIO = 3
MAX_CURRENT_RATIO = 5
MAX_QUICK_RATIO = 3
MAX_PRICE_TO_OPS_CASHFLOW = 1
MAX_PRICE_TO_TANGIBLE_BOOK_RATIO = 3
MAX_PRICE_TO_INTRINSIC_VALUE_DCF = 3
MAX_PRICE_TO_MEDIAN_PS_VALUE = 3
MAX_PRICE_TO_GRAHAM_NUMBER = 3

#Financial health based selection criteria
MIN_CASH_TO_DEBT = 0.5
MAX_EQUITY_ASSET = 2
MAX_DEBT_TO_EBITDA = 2
MAX_DEBT_TO_EQUITY = 2

# Profitability based selection criteria
MIN_OPERATING_MARGIN_PERCENT = 5
MIN_NET_MARGIN_PERCENT = 5
MIN_ROE_PERCENT = 0
MIN_ROA_PERCENT = 0
MIN_ROIC_PERCENT = 0
MIN_3YR_REV_GROWTH_RATE = 0
MIN_3YR_EBITDA_GROWTH_RATE = 0
MIN_3YR_EPS_GROWTH_RATE = 0

#Dividend based selection criteria
def isPreliminaryStockFinancialMetricsMet(list_vals):
    if float(list_vals[4].replace(',', '').replace('"', '')) < MIN_MARKET_CAP_MIL:  # Market Cap in Millions
        return False
    if float(list_vals[3]) < MIN_INST_OWNERSHIP_PERCENT:  # Institutional ownership > 25%
        return False
    if float(list_vals[5].replace(',', '').replace('"', '')) < MIN_PB_RATIO or \
            float(list_vals[5].replace(',', '').replace('"', '')) > MAX_PB_RATIO:  # P/B ratio
        return False
    if float(list_vals[6].replace(',', '').replace('"', '')) < MIN_PS_RATIO or \
            float(list_vals[5].replace(',', '').replace('"', '')) > MAX_PB_RATIO:  # P/S ratio
        return False
    if float(list_vals[7].replace(',', '').replace('"', '')) < MIN_OPERATING_MARGIN_PERCENT:  # Operating Margin
        return False
    if float(list_vals[8].replace(',', '').replace('"', '')) < MIN_NET_MARGIN_PERCENT:  # Net Margin
        return False
    if float(list_vals[9].replace(',', '').replace('"', '').replace('$', '')) < MIN_STOCK_PRICE:  # Price
        return False
    if float(list_vals[10].replace(',', '').replace('"', '')) < MIN_AVG_TRADE_VOL:  # Volume
        return False
    return True

# This program filter stocks downloaded from internet using the following links:
# https://www.gurufocus.com/screener
##Exchanges will also usually publish an up-to-date list of securities on their web pages. For example, these pages offer CSV downloads:
#NASDAQ: https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download
#AMEX: https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download
#NYSE: https://old.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download

#'\nPiotroski F-Score\n', # Good value >= 5
#'\nAltman Z-Score\n', # SafeValue must be >= 3
#'\nBeneish M-Score\n', # NonManipulative >= 1

# DoubleSpaced fields:
# Also add %of 1DayPriceChange, available in value just before Volume:
DoubleSpacedKeys1=[' Market Cap $: ',' Enterprise Value $: ',' Volume: ',' Avg Vol (1m): ']

# SingleSpaced fields: '\nPrice: ', ' $3.76\n',
SingleSpacedKeys2=['\nPrice: ']
#TripleSpaced fields:
#'\nEarnings Power Value\n', ' ', ' ', '\n2.53\n', '\nNet Current Asset Value\n', ' ', ' ', '\n0.65\n', '\nTangible Book\n', ' ', ' ', '\n1.03\n', '\nProjected FCF\n', ' ', ' ', '\n3.02\n', '\nMedian P/S Value\n', ' ', ' ', '\n4.36\n',
#'\nGraham Number\n', ' ', ' ', '\n2.42\n', '\nDCF (FCF Based)\n', ' ', ' ', '\n5.16\n', '\nDCF (Earnings Based)\n', ' ', ' ', '\n3.62\n',
TripleSpacedPriceKeys3=['\nEarnings Power Value\n','\nNet Current Asset Value\n','\nTangible Book\n','\nProjected FCF\n','\nMedian P/S Value\n',
                  '\nGraham Number\n', '\nDCF (FCF Based)\n','\nDCF (Earnings Based)\n']

DoubleSpacedKeys4=['\nPEG Ratio\n','\nPB Ratio\n','\nPrice-to-Tangible-Book\n','\nPS Ratio\n','\nPrice-to-Median-PS-Value\n',
                   '\nPrice-to-Intrinsic-Value-DCF (Earnings Based)\n','\nPrice-to-Intrinsic-Value-Projected-FCF\n','\nPrice-to-Graham-Number\n',
                   '\nCurrent Ratio\n','\nQuick Ratio\n','\nCash-To-Debt\n','\nEquity-to-Asset\n','\nDebt-to-Equity\n','\nDebt-to-EBITDA\n',
                   '\nOperating Margin %\n','\nNet Margin %\n','\nROE %\n','\nROA %\n']
# Quadraple Spaced fields: '\nWACC vs ROIC\n', ' ', ' ', ' ', '\nROIC 28.08%\n', '\nWACC 2.85%\n',
QudrapleSpacedPriceKeys5=['\nWACC vs ROIC\n']

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
['\nWipro Ltd\n$\n3.76\n', ' -0.04 (-1.05%)\n', ' ', ' ', '\n', ' ', ' Volume: ', ' ', ' 322,608 ', ' Avg Vol (1m): ', ' ', ' 1,229,621 ',
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
        value_element = list_element[indx + valueSpacing]
        #print(element, indx, list_element[indx], valueSpacing, list_element[indx+valueSpacing] )
        # Example: '\nWACC vs ROIC\n', ' ', ' ', ' ', '\nROIC 28.08%\n', '\nWACC 2.85%\n',
        if element == '\nWACC vs ROIC\n':
            ROIC_WACC_KeyVals = value_element.split(' ')
            # print(value_element, ROIC_WACC_KeyVals)
            ROIC_WACC_KeyVal = 0
            if len(ROIC_WACC_KeyVals) > 1:
                ROIC_WACC_KeyVal = round(float(ROIC_WACC_KeyVals[1].replace('%','').replace('\n','')), 2)
            else:
                print('ROIC_WACC_KeyVal info not found, using default 0 value')
            # print(value_element, ROIC_WACC_KeyVal)
            return ROIC_WACC_KeyVal
        elif (valueSpacing < 0 and element == ' Volume: '):
            # '\nWipro Ltd\n$\n3.76\n', ' -0.04 (-1.05%)\n', ' ', ' ', '\n', ' ', ' Volume: ',
            priceChangeVals = value_element.split('(')
            #print(value_element, priceChangeVals)
            priceChangePercent = 0
            if len(priceChangeVals) > 1:
                priceChangePercent = round(float(priceChangeVals[1].replace(')','').replace('%','').replace('\n','')),2)
            else:
                print('PriceChange info not found, using default 0 value')
            # print(value_element, priceChangePercent)
            return priceChangePercent

        #print(element, value_element)
        value_element = value_element.replace(',', '').replace('\n', '').replace(' ', '').replace('$', '').replace('/10', '').replace('Mil','')
        if value_element.find('Bil') > 0:
            value_element=value_element.replace('Bil', '')
            value=round(float(value_element)*1000, 2)
            #print('Bil Found', element, value)
        else:
            value=round(float(value_element),2)

        return value
    except ValueError:
        #print('ValueError Exception:', element, valueSpacing, ValueError)
        print('stockMetric info not found for:', element.replace('\n', ''))
        return 0

def getFilteredStockMetricsData(stockDataUrl):
    #stockMetricsData = {}
    filteredStockMetricsData=''
    try:
        req = urllib.request.Request(
            stockDataUrl, data=None,
            headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
            }
        )
        response = urllib.request.urlopen(req, timeout=10)
        # html = requests.get(stockDataUrl, timeout=5).read()
        # html = urllib.request.urlopen(stockDataUrl).read()
        html = response.read()
        soup = BeautifulSoup(html, features="lxml")
        data = soup.findAll(text=True)
        result = filter(visible, data)
        items_list = list(result)
        # print(items_list)

    except ssl.SSLError as err:
        print('SSLError: Socket Connection timed out with error: ', err)
        return ''
    except urllib.error.HTTPError as e:
        print('HTTPError: The server couldn\'t fulfill the request. Error code: ', e.code)
        return ''
    except urllib.error.URLError as e:
        print('URLError: We failed to reach a server. Reason: ', e.reason)
        return ''
    except:
        print('An error occurred while accessing: ', stockDataUrl)
        return ''

    #Order of keys: DoubleSpacedKeys1 SingleSpacedKeys2 TripleSpacedPriceKeys3 DoubleSpacedKeys4 NoSpacedKeys5 DoubleSpacedKeys6
    #print(DoubleSpacedKeys1)
    #DoubleSpacedKeys1 = [' Market Cap $: ', ' Enterprise Value $: ', ' Volume: ', ' Avg Vol (1m): ']
    for keyFeature in DoubleSpacedKeys1:
        keyData=find_element_in_list(keyFeature, items_list,2)
        # print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)
        # Add any filtering conditions here
        if (keyFeature == DoubleSpacedKeys1[0]) and keyData < MIN_MARKET_CAP_MIL:
            return ''
        if (keyFeature == DoubleSpacedKeys1[2]) and keyData < MIN_TRADE_VOL:
            return ''
        if (keyFeature == DoubleSpacedKeys1[3]) and keyData < MIN_AVG_TRADE_VOL:
            return ''

        filteredStockMetricsData += str(keyData) + ','
        #stockMetricsData[keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', '')] = keyData

    # SingleSpaced fields: '\nPrice: ', ' $3.76\n',
    #print(SingleSpacedKeys2)
    for keyFeature in SingleSpacedKeys2:
        keyData=find_element_in_list(keyFeature, items_list,1)
        # print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)
        # Add any filtering conditions here
        if (keyFeature == SingleSpacedKeys2[0]) and keyData < MIN_STOCK_PRICE:
            return ''

        #Extra field for PriceChange to be added manually right before Price field
        if keyFeature == '\nPrice: ':
            # '\nWipro Ltd\n$\n3.76\n', ' -0.04 (-1.05%)\n', ' ', ' ', '\n', ' ', ' Volume: ',
            extraFeature = ' Volume: '
            priceChangePercent = find_element_in_list(extraFeature, items_list, -5)
            # print('1DayPriceChange %', priceChangePercent)
            filteredStockMetricsData += str(priceChangePercent) + ','
            #stockMetricsData['1DayPriceChangePercent'] = priceChangePercent

        filteredStockMetricsData += str(keyData)+','
        #stockMetricsData[keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', '')] = keyData

    #print(TripleSpacedPriceKeys3)
    # ['\nEarnings Power Value\n', '\nNet Current Asset Value\n', '\nTangible Book\n', '\nProjected FCF\n', '\nMedian P/S Value\n',
    # '\nGraham Number\n', '\nDCF (FCF Based)\n', '\nDCF (Earnings Based)\n']
    for keyFeature in TripleSpacedPriceKeys3:
        keyData=find_element_in_list(keyFeature, items_list,3)
        # print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)
        # Add any filtering conditions here

        filteredStockMetricsData += str(keyData) + ','
        #stockMetricsData[keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', '')] = keyData

    #print(DoubleSpacedKeys4)
    #['\nPEG Ratio\n', '\nPB Ratio\n', '\nPrice-to-Tangible-Book\n', '\nPS Ratio\n', '\nPrice-to-Median-PS-Value\n',
    # '\nPrice-to-Intrinsic-Value-DCF (Earnings Based)\n','\nPrice-to-Intrinsic-Value-Projected-FCF\n', '\nPrice-to-Graham-Number\n',
    # '\nCurrent Ratio\n', '\nQuick Ratio\n', '\nCash-To-Debt\n', '\nEquity-to-Asset\n',
    # '\nDebt-to-Equity\n', '\nDebt-to-EBITDA\n','\nOperating Margin %\n', '\nNet Margin %\n', '\nROE %\n', '\nROA %\n']
    for keyFeature in DoubleSpacedKeys4:
        keyData=find_element_in_list(keyFeature, items_list,2)
        #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)
        # Add any filtering conditions here

        if (keyFeature == DoubleSpacedKeys4[1]) and keyData > MAX_PB_RATIO:
            return ''

        filteredStockMetricsData += str(keyData)+','
        #stockMetricsData[keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', '')] = keyData

    #print(QudrapleSpacedPriceKeys5)
    # Example: '\nWACC vs ROIC\n', ' ', ' ', ' ', '\nROIC 28.08%\n', '\nWACC 2.85%\n',
    for keyFeature in QudrapleSpacedPriceKeys5:
        keyData=find_element_in_list(keyFeature, items_list,4)
        # print('ROIC', keyData)
        # Add any filtering conditions here

        filteredStockMetricsData += str(keyData) + ','
        #stockMetricsData['ROIC'] = keyData

        keyData = find_element_in_list(keyFeature, items_list, 5)
        # print('WACC', keyData)
        #Add any filtering conditions here
        filteredStockMetricsData += str(keyData) + ','
        #stockMetricsData['WACC'] = keyData

    #print(DoubleSpacedKeys6)
    # ['\n3-Year Revenue Growth Rate\n', '\n3-Year EBITDA Growth Rate\n','\n3-Year EPS without NRI Growth Rate\n',
    # '\nPE Ratio\n', '\nForward PE Ratio\n', '\nPE Ratio without NRI\n', '\nShiller PE Ratio\n',
    # '\nPrice-to-Owner-Earnings\n','\nPrice-to-Free-Cash-Flow\n', '\nPrice-to-Operating-Cash-Flow\n', '\nEV-to-EBIT\n', '\nEV-to-EBITDA\n', '\nEV-to-Revenue\n',
    # '\nPiotroski F-Score\n', '\nAltman Z-Score\n', '\nBeneish M-Score\n', '\nFinancial Strength\n','\nProfitability Rank\n', '\nValuation Rank\n']
    for keyFeature in DoubleSpacedKeys6:
        keyData=find_element_in_list(keyFeature, items_list,2)
        # print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), keyData)
        # Add any filtering conditions here

        filteredStockMetricsData += str(keyData) + ','
        #stockMetricsData[keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', '')] = keyData

    return filteredStockMetricsData

def addHeader(startingColNames, outputFile):
    #Order of keys: DoubleSpacedKeys1 SingleSpacedKeys2 TripleSpacedPriceKeys3 DoubleSpacedKeys4 QudrapleSpacedPriceKeys5 DoubleSpacedKeys6
    with open(outputFile, "w") as filehandle:
        filehandle.write('%s,' % startingColNames)
        for keyFeature in DoubleSpacedKeys1:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        for keyFeature in SingleSpacedKeys2:
            if keyFeature == '\nPrice: ':
                filehandle.write('1DayPriceChangePercent,')
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        for keyFeature in TripleSpacedPriceKeys3:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')
        for keyFeature in DoubleSpacedKeys4:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')

        # Example: '\nWACC vs ROIC\n', ' ', ' ', ' ', '\nROIC 28.08%\n', '\nWACC 2.85%\n',
        for keyFeature in QudrapleSpacedPriceKeys5:
            if keyFeature == '\nWACC vs ROIC\n':
                filehandle.write('ROIC,WACC,')
                # print('ROIC,WACC,')
        for keyFeature in DoubleSpacedKeys6:
            filehandle.write('%s,' % keyFeature.replace(',', '').replace(':', '').replace(' ', '').replace('\n', ''))
            if keyFeature==DoubleSpacedKeys6[-1]:
                filehandle.write('\n')
            #print(keyFeature.replace(',', '').replace(' ', '').replace('\n', ''), ',')

'''
Description: 
'''
def main(argv):
    #tickers = argv[1:]
    inputFile = 'stockData/preFilteredStocksData.csv'
    outputFilteredFile = 'stockData/filteredStocksMetricsData.csv'

    fpIn = open(inputFile, 'r')
    stocksDataRows = csv.reader(fpIn, skipinitialspace=True)
    for list_vals in stocksDataRows:
        if list_vals[0] == 'Ticker':
            #Ticker,CompanyName,IndustryName, InstOwnership
            startingColNames = list_vals[0] + ',' + list_vals[1].replace(',', ' ') + ',' +list_vals[2].replace(',', ' ') + ',' + list_vals[3].replace(',', ' ');
            addHeader(startingColNames, outputFilteredFile)
            continue  # skip header line

        if (not isPreliminaryStockFinancialMetricsMet(list_vals)):
            continue  # specified stock metrics were not fullfilled

        print(list_vals)
        ticker=list_vals[0]
        stockDataUrl='https://www.gurufocus.com/stock/'+ticker+'/summary'
        try:
            stockMetricsData = getFilteredStockMetricsData(stockDataUrl)
        except:
            print('An error occurred while accessing: ', stockDataUrl)
            continue

        if not bool(stockMetricsData):
            continue
        #time.sleep(1)
        #print(stockMetricsData)
        #checkStockMetricsDataAndUpdateRecommendationList(list_vals, stockMetricsData, outputFilteredFile)
        with open(outputFilteredFile, 'a') as fpOut:
            fpOut.write('%s\n' % (list_vals[0] + ',' + list_vals[1].replace(',', ' ') + ',' + list_vals[2].replace(',', ' ') + ',' + list_vals[3].replace(',', ' ')
                                    + ','+stockMetricsData ))
    fpIn.close()
if __name__ == "__main__":
   main(sys.argv)
