# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 21:13:49 2018

@author: akulap
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 11:18:59 2018

@author: akulap
- https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
- http://www.openbookproject.net/books/bpp4awd/ch04.html
"""
import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
import sqlite3
from io import BytesIO
import gzip

#Create SQLite connection
con = sqlite3.connect('D:/CUNY/698/edgar_Form8K.db')
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS Form8K')
cur.execute('CREATE TABLE Form8K (cik TEXT, company TEXT, type TEXT, date TEXT, path TEXT, ticker TEXT)')
cur.execute('DROP TABLE IF EXISTS ItemsFiled8K')
cur.execute('CREATE TABLE ItemsFiled8K (item TEXT, date TEXT, ticker TEXT, path TEXT)')
con.commit()

#Set quarters, SEC stores data in quarters
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']

#Set interested companies
companies = {'Ford Motor':'F', 'Ford Credit':'F',
           'Fiat':'FCAU', 'Chrysler':'FCAU', 
           'General Motor':'GM', 'GM ':'GM',
           'Mercedes':'DAI.DE', 'Daimler':'DAI.DE',
           'BMW':'BMWYY',
           'Volkswagen':'VWAGY', 'Bentley':'VWAGY', 'Bugatti':'VWAGY', 'Lamborghini':'VWAGY', 'Porsche':'VWAGY',
           'Audi ':'AUDVF', 
           'Toyota':'TM',
           'Nissan Motor':'NSANY',
           'Honda Motor':'HMC',
           'Subaru':'FUJHY',
           'Mitsubishi':'MMTOF', 
           'Renault':'RNO.PA',
           'Mazda':'MZDAY',
           'Hyundai':'HYMTF',
           'Tata':'TTM',
           'Zhejiang':'VLVLY', 'Geely':'VLVLY', 'Polestar':'VLVLY', 'Volvo':'VLVLY',
           'Tesla':'TSLA'
        }


filingItems = {
    "Item 1.01":"Entry into a Material Definitive Agreement",
    "Item 1.02":"Termination of a Material Definitive Agreement",
    "Item 1.03":"Bankruptcy or Receivership",
    "Item 1.04":"Mine Safety - Reporting of Shutdowns and Patterns of Violations",
    "Item 2.01":"Completion of Acquisition or Disposition of Assets",
    "Item 2.02":"Results of Operations and Financial Condition",
    "Item 2.03":"Creation of a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement of a Registrant",
    "Item 2.04":"Triggering Events That Accelerate or Increase a Direct Financial Obligation or an Obligation under an Off-Balance Sheet Arrangement",
    "Item 2.05":"Costs Associated with Exit or Disposal Activities",
    "Item 2.06":"Material Impairments",
    "Item 3.01":"Notice of Delisting or Failure to Satisfy a Continued Listing Rule or Standard; Transfer of Listing",
    "Item 3.02":"Unregistered Sales of Equity Securities",
    "Item 3.03":"Material Modification to Rights of Security Holders",
    "Item 4.01":"Changes in Registrant's Certifying Accountant",
    "Item 4.02":"Non-Reliance on Previously Issued Financial Statements or a Related Audit Report or Completed Interim Review",
    "Item 5.01":"Changes in Control of Registrant",
    "Item 5.02":"Departure of Directors or Certain Officers; Election of Directors; Appointment of Certain Officers; Compensatory Arrangements of Certain Officers",
    "Item 5.03":"Amendments to Articles of Incorporation or Bylaws; Change in Fiscal Year",
    "Item 5.04":"Temporary Suspension of Trading Under Registrant's Employee Benefit Plans",
    "Item 5.05":"Amendment to Registrant's Code of Ethics, or Waiver of a Provision of the Code of Ethics",
    "Item 5.06":"Change in Shell Company Status",
    "Item 5.07":"Submission of Matters to a Vote of Security Holders",
    "Item 5.08":"Shareholder Director Nominations",
    "Item 6.01":"ABS Informational and Computational Material",
    "Item 6.02":"Change of Servicer or Trustee",
    "Item 6.03":"Change in Credit Enhancement or Other External Support",
    "Item 6.04":"Failure to Make a Required Distribution",
    "Item 6.05":"Securities Act Updating Disclosure",
    "Item 7.01":"Regulation FD Disclosure",
    "Item 8.01":"Other Events (The registrant can use this Item to report events that are not specifically called for by Form 8-K, that the registrant considers to be of importance to security holders.)",
    "Item 9.01":"Financial Statements and Exhibits"
}

data = []
form8kdf = pd.DataFrame([])

#Loop for years
for iYear in range(2008,2019,1):
    #Loop of quarters

    for quarter in quarters:
        #Quarter url
        secUrl = "https://www.sec.gov/Archives/edgar/daily-index/" + str(iYear) + "/"+ quarter + '/'
        
        #Get page and extract tables
        pageData = requests.get(secUrl)
        html_content = soup(pageData.content, 'html.parser')
        tables = html_content.findAll("table")
        
        #Loop through tables and get idx files
        for table in tables:
             if table.findParent("table") is None:
                 df = pd.read_html(str(table))[0]

        #Loop through each idx file and save it to local drive
        #Read only master files, it pipe(|) seperated and easy to read
        for index, row in df.iterrows():
            fileCheck = False
            
            if (row[0].startswith( 'master') or row[0].startswith( 'form')):
                if ((iYear==2011) and (quarter in ['QTR3', 'QTR4'])):
                    if row[0].startswith( 'form'):
                        fileCheck = True
                else:
                    if row[0].startswith( 'master'):
                        fileCheck = True
                        
            if fileCheck:
                idxUrl = "https://www.sec.gov/Archives/edgar/daily-index/" + str(iYear) + "/" + quarter + '/' + row[0]
                file_content = requests.get(idxUrl)
                print(idxUrl)
                
                #if file is gzip file
                if row[0].endswith('.gz'):
                    #Read bytes
                    zipFileContent = BytesIO(file_content.content)
                    
                    if ((iYear==2011) and (quarter in ['QTR3', 'QTR4'])):
                        with gzip.GzipFile(fileobj=zipFileContent) as file8kRows:
                            records = [tuple((str(line).rstrip().replace('\\n', '').replace('b\'', '').replace('\'', '')[74:85] + '|' + 
                                              str(line).rstrip().replace('\\n', '').replace('b\'', '').replace('\'', '')[12:73] + '|' + 
                                              str(line).rstrip().replace('\\n', '').replace('b\'', '').replace('\'', '')[0:11] + '|' + 
                                              str(line).rstrip().replace('\\n', '').replace('b\'', '').replace('\'', '')[86:97] + '|' + 
                                              str(line).rstrip().replace('\\n', '').replace('b\'', '').replace('\'', '')[98:141] + '|' + 
                                              ticker).split('|')) 
                                        for line in file8kRows.readlines() if ((str(line).find("edgar/data") > 0) and (str(line).startswith("b\'8-K"))) 
                                            for company, ticker in companies.items() if (str(line.lower()).find(company.lower()) > 0)]
                    else:
                        #Convert to rows and get output
                        with gzip.GzipFile(fileobj=zipFileContent) as file8kRows:
                            records = [tuple((str(line).rstrip().replace('\\n', '').replace('b\'', '').replace('\'', '') + '|' + ticker).split('|')) 
                                        for line in file8kRows.readlines() if ((str(line).find("|edgar/data") > 0) and (str(line).find("|8-K") > 0)) 
                                            for company, ticker in companies.items() if (str(line.lower()).find('|' + company.lower()) > 0)]
                else:
                    #Get matching recored, that is 8-K filing and belongs to interested companies
                    records = [tuple((str(line).rstrip().replace('\\n', '').replace('b\'', '').replace('\'', '') + '|' + ticker).split('|')) 
                                for line in file_content.iter_lines() if ((str(line).find("|edgar/data") > 0) and (str(line).find("|8-K") > 0)) 
                                    for company, ticker in companies.items() if (str(line.lower()).find('|' + company.lower()) > 0)]
                
                cur.executemany('INSERT INTO Form8K VALUES (?, ?, ?, ?, ?, ?)', records)
                con.commit()
                
                for cik, company, type, date, path, ticker in records:
                    url8k = "https://www.sec.gov/Archives/" + path.replace('\'', '')
                    details8k = requests.get(url8k)
                    try:
                        text8k = soup(details8k.content, 'html.parser')
                        textOutput = text8k.get_text()
                    except:
                        textOutput = str(details8k.content)

                    item8ks = [tuple((item8k.replace(" ",'').replace(".",'') +'|'+ date +'|'+ ticker +'|'+url8k).split('|')) 
                                for item8k, item8kDesc in filingItems.items() 
                                    if ((str(textOutput.replace("\'",'').lower()).find(item8kDesc.replace("\'",'').lower()) > 0) or (str(textOutput.replace("\'",'').lower()).find(item8k.replace("\'",'').lower()) > 0))]
                    
                    cur.executemany('INSERT INTO ItemsFiled8K VALUES (?, ?, ?, ?)', item8ks)
                    con.commit()
                
#Close the connection
con.close()
