from selenium import webdriver
import time
import csv
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import random
from fake_useragent import UserAgent
from selenium.webdriver import FirefoxProfile


# myProxy = "s30c4f3:J1h2OsZ@93.190.43.137:65233"
#
# proxy = Proxy({
#     'proxyType': ProxyType.MANUAL,
#     'httpProxy': myProxy,
#     'ftpProxy': myProxy,
#     'sslProxy': myProxy,
#     'noProxy': '' # set this value as desired
#     })

ua = UserAgent()
user_agent = ua.random

# FIREFOX
options = webdriver.FirefoxOptions()
options.add_argument("user-agent=%s" % user_agent)

# options.set_preference("user_agent", user_agent)
# profile = FirefoxProfile()
# profile.set_preference("browser.cache.disk.enable", False)
# profile.set_preference("browser.cache.memory.enable", False)
# profile.set_preference("browser.cache.offline.enable", False)
# profile.set_preference("network.http.use-cache", False)

# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('--hide-scrollbars')
driver = webdriver.Firefox(options=options)#, firefox_profile=profile)

# options = Options()
# options.add_argument('--disable-extensions')
# options.add_argument('--profile-directory=Default')
# options.add_argument("--incognito")
# options.add_argument("--disable-plugins-discovery")
# options.add_argument("--start-maximized")
# driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 10)
# driver.implicitly_wait(10)


def login(init=False):
    driver.get('https://www.bet365.com/en/')
    elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Live In-Play"]')))
    elem.click()
    elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[text()="In-Play"]')))
    elem.click()
    elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[text()="Event View"]')))
    elem.click()



def open_new_tab(category_index, subcategory_index, stat_index):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    rand = random.uniform(5,10)
    print(rand)
    time.sleep(rand)
    login()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipn-Classification ipn-Classification-open "]')))
    categories = driver.find_elements_by_css_selector('[class="ipn-Classification ipn-Classification-open "]')
    category = categories[category_index]
    # category.click()
    # time.sleep(1)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipn-Competition "]')))
    subcategories = category.find_elements_by_css_selector('[class="ipn-Competition "]')
    subcategory = subcategories[subcategory_index]
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipn-CompetitionContainer "]>div')))
    stats = subcategory.find_elements_by_css_selector('[class="ipn-CompetitionContainer "]>div')
    stat = stats[stat_index]
    stat.click()
    # time.sleep(1)
    return category, subcategory, stat


def create_tabs():
    login(init=True)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipn-Classification ipn-Classification-open "]')))
    categories = driver.find_elements_by_css_selector('[class="ipn-Classification ipn-Classification-open "]')
    # Only first category (Football)
    for category_id in range(len(categories[:1])):
        category = categories[category_id]
        # category.click()
        # time.sleep(1)
        # item['category_name'] = category.find_element_by_css_selector('[class="ipn-ClassificationButton_Label "]').text
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipn-Competition "]')))
        subcategories = category.find_elements_by_css_selector('[class="ipn-Competition "]')
        # First 5 subcategories
        for subcategory_id in range(len(subcategories)):
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipn-Competition "]')))
            subcategories = category.find_elements_by_css_selector('[class="ipn-Competition "]')
            subcategory = subcategories[subcategory_id]
            # item['category_name'] = category.find_element_by_css_selector('[class="ipn-ClassificationButton_Label "]').text
            # item['subcategory_name'] = subcategory.find_element_by_css_selector('[class="ipn-CompetitionButton "]').text
            stats = subcategory.find_elements_by_css_selector('[class="ipn-CompetitionContainer "]>div')
            # If there is more that one match in category
            # if len(stats) > 1:
            for stat_id in range(len(stats)):
                driver.delete_all_cookies()
                print(len(driver.window_handles))
                category, subcategory, stat = open_new_tab(category_id, subcategory_id, stat_id)

create_tabs()
windows = driver.window_handles
items = []


def run():
    for window in windows[1:]:
        item = {}
        driver.switch_to.window(window)
        # Turn on if stats is not updating
        # TODO: wait until execution of js is finished
        time.sleep(0.1)
        stat = driver.find_element_by_css_selector('[class*="ipn-Fixture-selected"]')
        # teams = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ipn-TeamStack_Team')))
        teams = stat.find_elements_by_class_name('ipn-TeamStack_Team')
        item['team1'] = teams[0].text
        item['team2'] = teams[1].text
        timer = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ipn-ScoreDisplayStandard_Timer')))
        item['timer'] = timer.text
        goals = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ipn-ScoreDisplayStandard_Score')))
        goals = goals.text.split('-')
        item['team1_goals'] = goals[0]
        item['team2_goals'] = goals[1]

        # container = driver.find_element_by_css_selector('[class="ipe-SoccerGridContainer "]')
        container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipe-SoccerGridContainer "]')))

        def parse_container(className, name):
            # elem = container.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="{}"]'.format(className)))
            elem = container.find_element_by_css_selector('[class*="{}"]'.format(className))
            # elem = elem.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipe-SoccerGridCell "]'))
            team = elem.find_elements_by_css_selector('[class="ipe-SoccerGridCell "]')
            item['team1' + name] = team[0].text
            item['team2' + name] = team[1].text

        parse_container('ICorner ', 'corners')
        parse_container('IYellowCard ', 'yellow_cards')
        parse_container('IRedCard ', 'red_cards')
        parse_container('IPenalty ', 'penalties')

        # table = driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[class="ipe-EventViewDetail_MarketGrid gl-MarketGrid "]'))
        table = driver.find_element_by_css_selector('[class="ipe-EventViewDetail_MarketGrid gl-MarketGrid "]')


        def parse_table_kv(header):
            # Fulltime Results
            try:
                # rows = table.driver.wait.until(EC.presence_of_element_located((By.XPATH, '[class="ipe-EventViewDetail_MarketGrid gl-MarketGrid "]'))
                rows = table.find_element_by_xpath('..//span[text()="{}"]/parent::div/parent::div'.format(header))
            except:
                return
            col_name = '_'.join(h.lower() for h in header.split())
            rows = rows.find_elements_by_css_selector('[class*=gl-Market_CN-3]')
            for index, fulltime_result in enumerate(rows):
                item[col_name + '_key_' + str(index+1)] = fulltime_result.find_element_by_class_name('gl-Participant_Name').text
                item[col_name + '_value_' + str(index+1)] = fulltime_result.find_element_by_class_name('gl-Participant_Odds').text

        parse_table_kv('Fulltime Result')
        parse_table_kv('Double Chance')

        # Goals
        headers = table.find_elements_by_class_name('gl-MarketGroupButton_Text')
        table_headers = [h.text for h in headers]
        r = re.compile(r'^\d.*Goal$')
        matches = list(filter(r.match, table_headers))
        for match in matches:
            parse_table_kv(match)

        print(item)
        items.append(item.copy())


for i in range(100):
    try:
        run()
    except (KeyboardInterrupt, SystemExit):
        print('Interupted')
        driver.close()


driver.close()


def create_fieldnames():
    item_keys = set()
    for item in items:
        for key in item:
            item_keys.add(key)
    return item_keys


with open('bet365.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=create_fieldnames())
    writer.writeheader()
    for item in items:
        writer.writerow(item)
