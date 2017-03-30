import urllib.request
from bs4 import BeautifulSoup
import csv
import ssl
import pandas as pd
import re
from time import sleep
from random import expovariate

appointment_data = pd.read_csv('/Users/niccdias/Desktop/companies_house_w-comp_numbers.csv', header = 0, converters={'Company number': lambda x: str(x)})
companies_csv  = list(appointment_data['Company number'])

urlBase = "https://beta.companieshouse.gov.uk/company/"
urlEnd = "/officers"

cols = [
	"Company",
	"Name",
	"Correspondence address",
	"Role",
	"Appointed on",
	"Resigned on",
	"Placed registered",
	"Registration number",
	"Date of birth",
	"Nationality",
	"Country of residence",
	"Occupation"
]

first_row = {
	"Company" : "Company",
	"Name" : "Name",
	"Correspondence address" : "Correspondence address",
	"Role" : "Role",
	"Appointed on" : "Appointed on",
	"Resigned on" : "Resigned on",
	"Placed registered" : "Placed registered",
	"Registration number" : "Registration number",
	"Date of birth" : "Date of birth",
	"Nationality" : "Nationality",
	"Country of residence" : "Country of residence",
	"Occupation" : "Occupation"
}

f = open("companies_officers.csv", "w")
ch_csv = csv.DictWriter(f, delimiter = ",", fieldnames=cols)

e = open("officer_fails.csv", "w")
fail_csv = csv.writer(e, delimiter = ",")

g = open("officer_done.csv", "w")
done_csv = csv.writer(g, delimiter = ",")

ch_csv.writerow(first_row)

for URL in companies_csv:

	try:
		sleep(expovariate(1/1.5))

		context = ssl._create_unverified_context()
		page = urllib.request.urlopen(urlBase + URL + urlEnd, context=context)
		soup = BeautifulSoup(page, 'lxml')

		company = soup.find("p", {"id" : "company-name"}).contents[0].strip()

		table = soup.find("div", {"class" : "appointments-list"})
		officers  = table.findAll('div', {"class" : re.compile("appointment-*")})
		
		for officer in officers:
			officer_dict = {"Company" : company}
			name = officer.findNext('a').contents[0].strip()
			officer_dict['Name'] = name
			other_content = officer.findAll('dt')
			for i in other_content:
				key = i.contents[0].strip()
				value = i.findNext('dd').contents[0].strip()
				officer_dict[key] = value
			ch_csv.writerow(officer_dict)
			done_csv.writerow(URL)
			print(str(URL), "DONE!")
	except:
		fail_csv.writerow(URL)
		print("We failed on that one.")









