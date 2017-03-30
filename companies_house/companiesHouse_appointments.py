import urllib.request
from bs4 import BeautifulSoup
import csv
import ssl
import re
from time import sleep
from random import expovariate

urlBase = "https://beta.companieshouse.gov.uk/officers/UdCgm5NXI-mYwwM-1qQefwKI_7Y/appointments?page="

cols = [
	"Appointed",
	"Name",
	"Status",
	"Address",
	"Role",
	"Appointed on",
	"Register Location",
	"Registration Number",
	'Company status',
	'Resigned on',
	'Correspondence address',
	'Register location',
	'Registration number'
]

first_row = {
	"Appointed" : "Appointed",
	"Name" : "Name",
	"Status" : "Status",
	"Address" : "Address",
	"Role" : "Role",
	"Appointed on" : "Appointed on",
	"Register Location" : "Register Location",
	"Registration Number" : "Registration Number",
	'Company status' : 'Company status',
	'Resigned on' : 'Resigned on',
	'Correspondence address' : 'Correspondence address',
	'Register location' : 'Register location',
	'Registration number' : 'Registration number'		
}

f = open("companies_house.csv", "w")
ch_csv = csv.DictWriter(f, delimiter = ",", fieldnames=cols)

f = open("appointment_fails.csv", "w")
fail_csv = csv.writer(f, delimiter = ",")

ch_csv.writerow(first_row)

for pageNum in range(1,105):
	try:
		sleep(expovariate(1/1.5))

		context = ssl._create_unverified_context()
		page = urllib.request.urlopen(urlBase + str(pageNum), context=context)
		soup = BeautifulSoup(page, 'lxml')

		appointed = soup.find("h1", {"class" : "heading-xlarge"}).contents[0].strip()

		table = soup.find("div", {"class" : "appointments-list"})
		companies  = table.findAll('div', {"class" : re.compile("appointment-*")})

		for company in companies:
			company_dict = {"Appointed" : appointed}
			name = company.findNext('a').contents[0].strip()
			company_dict['Name'] = name
			other_content = company.findAll('dt')
			for i in other_content:
				key = i.contents[0].strip()
				value = i.findNext('dd').contents[0].strip()
				company_dict[key] = value
			ch_csv.writerow(company_dict)
		print(str(pageNum) + " DONE.")
	except:
		fail_csv.writerow(pageNum)
		print(str(pageNum) + " FAILED.")






