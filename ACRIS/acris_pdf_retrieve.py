# Python 3.6.0
# The scraper will dump the files in your current working directory.
# In order to use this scraper, you have to download the Selenium package and geckodriver.
# Install selenium by typing either "pip install selenium" or "pip3 install selenium" in your terminal.
# Install geckodriver by going to this link: https://github.com/mozilla/geckodriver/releases
# After you've downloaded geckodriver, execute the following statement in your terminal, 
	# adding the appropriate directory: export PATH=$PATH:/path/to/folder/with/geckodriver/executable (i.e., the
	# file with the icon that looks like a terminal).

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import selenium
from os import getcwd, system
import pandas as pd
from time import sleep
from glob import glob
from math import isnan
from random import expovariate, choice
from traceback import print_exc

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

profile.set_preference( "places.history.enabled", False )
profile.set_preference( "privacy.clearOnShutdown.offlineApps", True )
profile.set_preference( "privacy.clearOnShutdown.passwords", True )
profile.set_preference( "privacy.clearOnShutdown.siteSettings", True )
profile.set_preference( "privacy.sanitize.sanitizeOnShutdown", True )
profile.set_preference( "signon.rememberSignons", False )
profile.set_preference( "network.cookie.lifetimePolicy", 2 )
profile.set_preference( "network.dns.disablePrefetch", True )
profile.set_preference( "network.http.sendRefererHeader", 0 )

profile.set_preference( "network.proxy.type", 1 )
profile.set_preference( "network.proxy.socks_version", 5 )
profile.set_preference( "network.proxy.socks", '127.0.0.1' )
profile.set_preference( "network.proxy.socks_port", 9050 )

user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8",
"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"]

profile.set_preference("general.useragent.override", choice(user_agents))

csv = pd.read_csv('acris_documents_output.csv', header = 0)
units = csv['Document ID']

browser = webdriver.Firefox(profile)

def get_doc(doc):
	file = './'+str(doc)+'*.pdf'
	if glob(file):
		print("Skipping doc " + doc)
	else:
		print("Retrieving doc " + doc)
		URL = "https://a836-acris.nyc.gov/DS/DocumentSearch/DocumentImageView?doc_id=" + str(doc)
		browser.get(URL)
		
		WebDriverWait(browser, 10).until(lambda s: s.find_element_by_tag_name('iframe').is_displayed())

		browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
		browser.find_element_by_id('vtm_saveTd').click()
		browser.find_element_by_id('vtm_printOK').click()
		
		while not glob(file):
			sleep(.1)
		sleep(expovariate(2/3))

for unit in units:
	try:
		if type(unit) == str:
			docs = unit.split(';')
			for doc in docs:
				get_doc(doc)
		elif type(unit) == float:
			if isnan(unit) == False:
				get_doc(unit)
	except selenium.common.exceptions.TimeoutException as e:
		try:
			alert = browser.switch_to_alert()	
			alert.accept()
		except:
			system("killall tor")
			sleep(2)
			system("tor &")
			sleep(5)
			browser.delete_all_cookies()
			browser.close()
			profile.set_preference("general.useragent.override", choice(user_agents))
			pass
	except Exception as e:
		print_exc()
		pass







