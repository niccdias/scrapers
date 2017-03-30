# Python 3.6.0
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from os import getcwd
import pandas as pd
from time import sleep
from glob import glob

profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', getcwd())
profile.set_preference("browser.helperApps.neverAsk.openFile","application/pdf,application/x-pdf")
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf,application/x-pdf')
profile.set_preference("browser.download.manager.alertOnEXEOpen", False);
profile.set_preference("browser.download.manager.showWhenStarting", False);
profile.set_preference("browser.download.manager.focusWhenStarting", False);  
profile.set_preference("browser.download.useDownloadDir", True);
profile.set_preference("browser.helperApps.alwaysAsk.force", False);
profile.set_preference("browser.download.manager.alertOnEXEOpen", False);
profile.set_preference("browser.download.manager.closeWhenDone", True);
profile.set_preference("browser.download.manager.showAlertOnComplete", False);
profile.set_preference("browser.download.manager.useWindow", False);
profile.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False);
profile.set_preference("pdfjs.disabled", True);

browser = webdriver.Firefox(profile)

csv = pd.read_csv('names_acris.csv', skiprows=1)

for index, row in csv.iterrows():
	URL = "https://a836-acris.nyc.gov/DS/DocumentSearch/PartyName"
	browser.get(URL)

	last = row[0]
	first = row[1]

	print(first.upper())
	print(last.upper())
	
	browser.find_element_by_name('edt_last').send_keys(str(last))
	browser.find_element_by_name('edt_first').send_keys(str(first))

	#process
	browser.find_element_by_name('Submit').click()
	
	sleep(1)

	rows = []
	
	try:
		mySelect = Select(browser.find_element_by_name('com_maxrows'))
		mySelect.select_by_value("99")
		sleep(1)
		
		#write
		trs = browser.find_elements_by_xpath("//tr[@bgcolor='#C6E2FF']")
		rows = []
		counter = 0

		while True:
			for tr in trs:
				row_dict = {}
				cells = tr.find_elements_by_tag_name('td')
				
				docID = tr.find_element_by_name('IMG').get_attribute("onclick")
				row_dict['ID'] = docID[21:-2]
				row_dict['Name'] = cells[2].text
				row_dict['Borough'] = cells[3].text
				row_dict['Block'] = cells[4].text
				row_dict['Lot'] = cells[5].text
				row_dict['Reel/Pg/File'] = cells[6].text
				row_dict['CRFN'] = cells[7].text
				row_dict['Partial'] = cells[8].text
				row_dict['Doc Date'] = cells[9].text
				row_dict['Recorded/Filed'] = cells[10].text
				row_dict['Document Type'] = cells[11].text
				row_dict['Pages'] = cells[12].text
				row_dict['Corrected/Remarks'] = cells[13].text
				row_dict['Doc Amount'] = cells[14].text
				rows.append(row_dict)
			try:
				browser.find_element_by_xpath("//a[@href='JavaScript:go_next()']").click()
				sleep(1)
			except:
				counter += 1
				if counter > 1:
					break
	except:
		pass
	rows_df = pd.DataFrame(rows)
	rows_df.to_csv('acris_names_data.csv')
browser.quit()