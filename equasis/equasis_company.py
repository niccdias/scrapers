import scrapy
import csv
import traceback
from bs4 import BeautifulSoup

company_file = open('company_scrape', 'w')
company_csv = csv.writer(company_file, delimiter = ",")


company_cols = [
	"IMO number :",
	"Name :",
	"Address :",
	"Status :",
	"Last update :",
]

class LoginSpider(scrapy.Spider):
	name = 'equasis_company.org'
	start_urls = ['http://www.equasis.org/EquasisWeb/public/HomePage']
	download_delay = .5
	concurrent_requests = 1

	def request_next_imo(self):
		if (len(self.imos)>0):
			imo = self.imos.pop()
			return scrapy.FormRequest.from_response(
				self.front_page_response,
				formdata = {'j_email': 'ncd2120@columbia.edu', 'j_password': 'oDh4JUng76'},
				callback = self.after_login,
				meta = {'imo': imo},
				dont_filter=True
			)

	def parse(self, response):
		print('STARTING!')
		company_csv.writerow(company_cols)

		self.imos = self.get_imos("/Users/niccdias/Desktop/GSP2/columbia-shipping/data/nknews_imos.csv")
		self.front_page_response = response

		return self.request_next_imo()

	def after_login(self, response):
		imo = response.meta['imo']
		print("LOGGED IN for IMO " + imo)
		if 'Please, try again' in str(response.body):
			self.logger.error("Login failed")
			return
		else:
			return scrapy.Request("http://www.equasis.org/EquasisWeb/restricted/CompanySearch?fs=CompanyInfo", 
				callback=self.make_imo_request,
				meta = {'imo': imo},
				dont_filter=True,
				)
			
	def make_imo_request(self, response):
		imo = response.meta['imo']
		yield scrapy.FormRequest.from_response(
			response,
			formdata = {'P_COMP': imo, 'P_PAGE': '1', 'P_NAME': '', 'Submit': "SEARCH"},
			callback = self.parse_ship,
			meta = {'imo': imo},
			dont_filter=True,
			)

	def parse_ship(self, response):
		imo = response.meta['imo']
		print("PARSING SHIP " + imo)
		try:		
			soup = BeautifulSoup(response.text,'lxml')

			cols = []
			for col in company_cols:
				if soup.find(text=col) == None:
					cols.append("")
				else:
					cols.append(soup.find(text=col).parent.findNext('td').contents[0].strip())

			if cols[0]=="":
				cols[0]=imo

			company_csv.writerow(cols)

		except Exception as e:
			print(e)
			traceback.print_exc()
			print(response)
			print(response.text)

		return self.request_next_imo()

	def get_imos(self, fileurl):
		imos = []

		with open (fileurl) as csvfile:
			reader = csv.reader(csvfile, delimiter=";")
			for row in reader:
				imos.append(row[0])
		print("Running with " + str(len(imos)) + " imos")
		return imos



