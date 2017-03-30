import urllib.request
from bs4 import BeautifulSoup
import csv
import ssl
import pandas as pd
from time import sleep
from random import expovariate

appointment_data = pd.read_csv('/Users/niccdias/Desktop/companies_house_w-comp_numbers.csv', header = 0, converters={'Company number': lambda x: str(x)})
companies_csv  = list(appointment_data['Company number'])

urlBase = "https://beta.companieshouse.gov.uk/company/"

f = open("companies_overview.csv", "w")
ch_csv = csv.writer(f, delimiter = ",")

e = open("overview_fails.csv", "w")
fail_csv = csv.writer(e, delimiter = ",")

g = open("overview_done.csv", "w")
done_csv = csv.writer(g, delimiter = ",")

cols = [
	"Name",
	"Number",
	"Address",
	"Dissolved On",
	"Company Type",
	"Incorporated On",
	"Nature of Business"
]

ch_csv.writerow(cols)


for URL in companies_csv:
	try:
		sleep(expovariate(1/1.5))

		context = ssl._create_unverified_context()
		page = urllib.request.urlopen(urlBase + URL, context=context)
		soup = BeautifulSoup(page, 'lxml')
		
		name = soup.find("p", {"id" : "company-name"}).contents[0].strip()
		subheading = soup.find("p", {"id" : "company-number"})
		number = subheading.find("strong").contents[0].strip()
		
		company_cols = [name, number]
		
		company_details  = soup.findAll('dd')
		for detail in company_details:
			company_cols.append(detail.contents[0].strip())

		NoB = soup.find("span", {"id" : "sic0"}).contents[0].strip()
		company_cols.append(NoB)

		ch_csv.writerow(company_cols)
		done_csv.writerow(URL)
		print(str(URL), "DONE!")
	except:
		fail_csv.writerow(URL)
		print("We failed on that one.")