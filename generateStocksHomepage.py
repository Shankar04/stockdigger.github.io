#!/usr/bin/python
import sys
import os
import shutil

# File to create Stocks HomePage html file by re-using some sections of the existing homepage and then add stocks information
inputHtmlFileHeader = 'stockData/index_header.html'
inputHtmlFileTail = 'stockData/index_footer.html'
inputStockDataFile = 'stockData/filteredStocksMetricsData_peON_pbON_qrON_nmON.csv'
outputFile = 'stockData/index.html'
#outputFile = 'stockData/StocksFilteredBy_peON_pbON_qrON_nmON.html'

def updateStocksHomePage(inputFile, outputFile):
    with open(outputFile, 'a') as fpOut:
        with open(inputFile, 'r') as fpIn:
            line = fpIn.readline()
            while line:
                # print(line)
                fpOut.write(line)
                line = fpIn.readline()
#Ticker	Company	Industry	Country(Headquarter)	InstitutionalOwnership	MarketCap$	EnterpriseValue$	Volume	AvgVol(1m)	1DayPriceChangePercent
# 10: Price	PBRatio	Price-to-Tangible-Book	PSRatio	Price-to-Median-PS-Value	Price-to-Graham-Number	Price-to-Peter-Lynch-Fair-Value
# 13: Price-to-Intrinsic-Value-DCF(EarningsBased)	Price-to-Intrinsic-Value-DCF(FCFBased)	Price-to-Intrinsic-Value-Projected-FCF	Price-to-Earnings-Power-Value
# 17: PEGRatio	CurrentRatio	QuickRatio	Cash-To-Debt	Equity-to-Asset	Debt-to-Equity	Debt-to-EBITDA	OperatingMargin%	NetMargin%	ROE%	ROA%	ROIC
# 29: WACC	ShillerPERatio	PERatio	ForwardPERatio	PERatiowithoutNRI	EV-to-EBIT	EV-to-EBITDA	EV-to-Revenue	3-YearRevenueGrowthRate	3-YearEBITDAGrowthRate
# 39: 3-YearEPSwithoutNRIGrowthRate	Price-to-Owner-Earnings	Price-to-Free-Cash-Flow	Price-to-Operating-Cash-Flow	PiotroskiF-Score	AltmanZ-Score	BeneishM-Score
# 46: FinancialStrength	ProfitabilityRank	ValuationRank

def addTableHeader(outputFile):
    with open(outputFile, 'a') as fpOut:
        fpOut.write('<table>')
        fpOut.write('  <tr>')
        fpOut.write('    <th> Opinion </th>')
        #fpOut.write('    <th > Opinion Date </th>')
        #fpOut.write('    <th > Opinion Price </th>')
        fpOut.write('    <th > Current Price </th>')
        #fpOut.write('    <th > Change % </th>')
        fpOut.write('    <th> Ticker </th>')
        fpOut.write('    <th> Company </th>')
        fpOut.write('    <th> Industry </th>')
        fpOut.write('    <th> Avg Daily Vol </th>')
        fpOut.write('    <th> Market Cap($M) </th>')
        fpOut.write('    <th> Inst Ownership % </th>')
        fpOut.write('    <th> P/E Ratio(TTM) </th>')
        fpOut.write('    <th> P/B Ratio </th>')
        fpOut.write('    <th> Quick Ratio </th>')
        fpOut.write('    <th> Operating Margin % </th>')
        fpOut.write('    <th> Net Margin % </th>')
        fpOut.write('  </tr>')
        fpOut.write("\n")
def addTableBody(dataRow, outputFile):
    list_vals = dataRow.split(',')
    #print(list_vals)
    with open(outputFile, 'a') as fpOut:
        Opinion = 'BUY'
        fpOut.write('  <tr>')
        fpOut.write('    <td> BUY </td>')
        #fpOut.write('    <td> DATE </td>')
        #fpOut.write('    <td> str(round(float(Opinion Price), 2)) </td>')
        fpOut.write('    <td>' + list_vals[10] + '</td>')
        #fpOut.write('    <td>' + str(round(float(list_vals[8]), 1)) + '</td>')
        fpOut.write('    <td>' + list_vals[0] + '</td>')
        fpOut.write('    <td>' + list_vals[1] + '</td>')
        fpOut.write('    <td>' + list_vals[2] + '</td>')
        fpOut.write('    <td>' + str(int(float(list_vals[8]))) + '</td>')
        fpOut.write('    <td>' + str(round(float(list_vals[5]), 1)) + '</td>')
        # This data field contains '|' separated research links

        fpOut.write('    <td>' + str(round(float(list_vals[4]), 1)) + '</td>')
        fpOut.write('    <td>' + str(round(float(list_vals[35]), 1)) + '</td>')
        fpOut.write('    <td>' + str(round(float(list_vals[11]), 1)) + '</td>')
        fpOut.write('    <td>' + str(round(float(list_vals[22]), 1)) + '</td>')
        fpOut.write('    <td>' + str(round(float(list_vals[26]), 1)) + '</td>')
        fpOut.write('    <td>' + str(round(float(list_vals[27]), 1)) + '</td>')
        fpOut.write('  </tr>')
def addTableCloser(outputFile):
    with open(outputFile, 'a') as fpOut:
        fpOut.write('</table>')
        fpOut.write('<br>')
        fpOut.write('<br>')
        fpOut.write('<br>')
        fpOut.write('<br>')
        fpOut.write('<br>')

def updateStocksHomePageBody(inputStockDataFile, outputFile):
    # Add the header section of table's html code
    addTableHeader(outputFile)
    # Add various stocks data rows
    with open(inputStockDataFile, 'r') as fp:
        for cnt, line in enumerate(fp):
            if cnt > 0: #skip the headr line at 0th row
                addTableBody(line, outputFile )
    # Add closing section of table's html code
    addTableCloser(outputFile)
    # Create a plot of top 10 stocks and store it as an image
    # Add html code also to include the image into home page
    #addPlot()
def pushChangesToGithub():
    if os.path.isfile(outputFile):
           print("Updating github repo file: stockdigger.github.io/index.html")
           shutil.copy(outputFile, 'stockdigger.github.io/')
    os.chdir("stockdigger.github.io")
    os.system("git status")
    os.system("git add index.html")
    os.system('git commit -am "Updated StocksDataTable"')
    os.system("git push origin master")

def main(argv):
    # Backup homepage html file, before re-creating with new content
    if os.path.isfile(outputFile):
           print("Taking Backup of ...".format(outputFile))
           shutil.move(outputFile, outputFile+'_org')
    #Read homepage header section of HTML code and write into new file as is
    updateStocksHomePage(inputHtmlFileHeader, outputFile)
    #Update HTML code for stocks data table by processing an input data file
    updateStocksHomePageBody(inputStockDataFile, outputFile)
    #Read homepage bottom section of HTML code and write into new file as is
    updateStocksHomePage(inputHtmlFileTail, outputFile)
    pushChangesToGithub()

if __name__ == "__main__":
   main(sys.argv)

#git commands to be executed in Gitbash MingW64 commandline window
# cd Downloads/PythonProjects/StockPicker/stockdigger.github.io
#git add index.html
#git commit -m "Updated StocksDataTable"
#git push origin master