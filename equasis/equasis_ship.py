import scrapy
import csv
import traceback
from bs4 import BeautifulSoup

ship_file = open('equasis_ship', 'w')
ship_csv = csv.writer(ship_file, delimiter = ",")
company_file = open('equasis_company', 'w')
company_csv = csv.writer(company_file, delimiter = ",")


ship_cols = [
	"IMO number :",
	"Name of ship :",
	"Call Sign :",
	"MMSI :",
	"Gross tonnage :",
	"DWT :",
	"Type of ship :",
	"Year of build :",
	"Flag :",
	"Status of ship :",
	"Last update :"
]

company_cols = [
"ship_imo",
"company_imo",
"role",
"company_name",
"company_address",
"date_of_effect"
]

class LoginSpider(scrapy.Spider):
	name = 'equasis.org'
	start_urls = ['http://www.equasis.org/EquasisWeb/public/HomePage']
	download_delay = .5
	concurrent_requests = 1

	def request_next_imo(self):
		if (len(self.imos)>0):
			imo = self.imos.pop()
			return scrapy.FormRequest.from_response(
				self.front_page_response,
				formdata = {'j_email': 'lyonwj@gmail.com', 'j_password': 'YEBp9azWtj'},
				callback = self.after_login,
				meta = {'imo': imo},
				dont_filter=True
			)

	def parse(self, response):
		print('STARTING!')
		ship_csv.writerow(ship_cols)
		company_csv.writerow(company_cols)

		self.imos = self.get_imos("/Users/niccdias/Desktop/GSP2/columbia-shipping/data/current_nk_flags.csv")
		self.front_page_response = response

		return self.request_next_imo()

	def after_login(self, response):
		imo = response.meta['imo']
		print("LOGGED IN for IMO " + imo)
		if 'Please, try again' in str(response.body):
			self.logger.error("Login failed")
			return
		else:
			return scrapy.Request("http://www.equasis.org/EquasisWeb/restricted/ShipSearch?fs=ShipSearch", 
				callback=self.make_imo_request,
				meta = {'imo': imo},
				dont_filter=True,
				)
			
	def make_imo_request(self, response):
		imo = response.meta['imo']
		yield scrapy.FormRequest.from_response(
			response,
			formdata = {'P_IMO': imo, 'P_PAGE': '1', 'Submit': "SEARCH"},
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
			for col in ship_cols:
				if soup.find(text=col) == None:
					cols.append("")
				else:
					cols.append(soup.find(text=col).parent.findNext('td').contents[0].strip())

			if cols[0]=="":
				cols[0]=imo

				ship_csv.writerow(cols)

			self.scrape_manager_row(imo, soup, 'lignej')
			self.scrape_manager_row(imo, soup, 'ligneb')

		except Exception as e:
			print(e)
			traceback.print_exc()
			print(response)
			print(response.text)

		return self.request_next_imo()


	def scrape_manager_row(self, imo, soup, color):
		company_table = soup.find(text=" Management detail").parent.findNext('table').contents[0]
		yellow_rows = company_table.findAll('tr', {'class':color})
		for row in yellow_rows:
			yellow = []
			yellow.append(imo)
			yellow_cells = row.contents
			for cell in yellow_cells[:5]:
				yellow.append(cell.contents[0].string.strip())
			company_csv.writerow(yellow)

	def get_imos(self, fileurl):
		imos = []

		with open (fileurl) as csvfile:
			reader = csv.reader(csvfile, delimiter=";")
			for row in reader:
				imos.append(row[0])
		print("Running with " + str(len(imos)) + " imos")
		return imos



