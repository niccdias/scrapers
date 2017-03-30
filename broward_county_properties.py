import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from os import getcwd

property_df = pd.read_csv('broward_properties.csv', header = 0)

cfn_paths = list(property_df['cfn_path'])

cfns = []
for cfn_path in cfn_paths:
    match = re.match('.*=(.*)', cfn_path)
    cfns.append(match.groups(0)[0])

profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2)
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

grantor_list = []
grantee_list = []

for cfn in cfns:
    URL = 'https://officialrecords.broward.org/oncorev2/ShowDetails.aspx?CFN=' + cfn
    print('Getting' + URL)
    browser.get(URL)
    browser.switch_to.frame(browser.find_element_by_name("contents"))
    grantors = browser.find_element_by_id('lblDirectName').text
    grantor_list.append(grantors.replace('\n', ";"))
    grantees = browser.find_element_by_id('lblReverseName').text
    grantee_list.append(grantees.replace('\n', ";"))
    browser.switch_to.default_content()
    browser.switch_to.frame(browser.find_element_by_name("doc"))
    browser.find_element_by_tag_name('a').click()
    sleep(2)

property_df['grantors'] = grantor_list
property_df['grantees'] = grantee_list

property_df.to_csv('broward_properties.csv')









