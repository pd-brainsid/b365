from selenium import webdriver
import time
import csv
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=options)
driver.implicitly_wait(10)


def login():
    driver.get('https://www.bet365.com/en/')

    try:
        driver.find_element_by_css_selector('[title="Live In-Play"]').click()
    except:
        pass
    driver.find_element_by_xpath('//*[text()="In-Play"]').click()
    driver.find_element_by_xpath('//*[text()="Event View"]').click()


items = []


def open_new_tab(category_index, subcategory_index, stat_index):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    login()
    categories = driver.find_elements_by_css_selector('[class="ipn-Classification ipn-Classification-open "]')
    category = categories[category_index]
    category.click()
    time.sleep(1)
    subcategories = category.find_elements_by_css_selector('[class="ipn-Competition "]')
    subcategory = subcategories[subcategory_index]
    stats = subcategory.find_elements_by_css_selector('[class="ipn-CompetitionContainer "]>div')
    stat = stats[stat_index]
    stat.click()
    time.sleep(1)
    return category, subcategory, stat


login()
categories = driver.find_elements_by_css_selector('[class="ipn-Classification ipn-Classification-open "]')
for cid in range(len(categories[:1])):
    category = categories[cid]
    category.click()
    time.sleep(1)
    # item['category_name'] = category.find_element_by_css_selector('[class="ipn-ClassificationButton_Label "]').text
    subcategories = category.find_elements_by_css_selector('[class="ipn-Competition "]')
    for sid in range(len(subcategories[:3])):
        # item = {}
        subcategories = category.find_elements_by_css_selector('[class="ipn-Competition "]')
        subcategory = subcategories[sid]
        # item['category_name'] = category.find_element_by_css_selector('[class="ipn-ClassificationButton_Label "]').text
        # item['subcategory_name'] = subcategory.find_element_by_css_selector('[class="ipn-CompetitionButton "]').text
        stats = subcategory.find_elements_by_css_selector('[class="ipn-CompetitionContainer "]>div')
        for stid in range(len(stats)):
            category, subcategory, stat = open_new_tab(cid, sid, stid)

windows = driver.window_handles


def run():
    for window in windows:
        item = {}
        driver.switch_to.window(window)
        stat = driver.find_element_by_css_selector('[class*="ipn-Fixture-selected"]')
        teams = stat.find_elements_by_class_name('ipn-TeamStack_Team')
        item['team1'] = teams[0].text
        item['team2'] = teams[1].text
        # print(item['team1'], item['team2'])
        item['timer'] = stat.find_element_by_class_name('ipn-ScoreDisplayStandard_Timer').text
        goals = stat.find_element_by_class_name('ipn-ScoreDisplayStandard_Score').text.split('-')
        item['team1_goals'] = goals[0]
        item['team2_goals'] = goals[1]

        container = driver.find_element_by_css_selector('[class="ipe-SoccerGridContainer "]')


        def parse_container(className, name):
            elem = container.find_element_by_css_selector('[class*="{}"]'.format(className))
            elem = elem.find_elements_by_css_selector('[class="ipe-SoccerGridCell "]')
            item['team1' + name] = elem[0].text
            item['team2' + name] = elem[1].text

        parse_container('ICorner ', 'corners')
        parse_container('IYellowCard ', 'yellow_cards')
        parse_container('IRedCard ', 'red_cards')
        parse_container('IPenalty ', 'penalties')

        table = driver.find_element_by_css_selector('[class="ipe-EventViewDetail_MarketGrid gl-MarketGrid "]')


        def parse_table_kv(header):
            # Fulltime Results
            try:
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


for i in range(50):
    run()

item_keys = set()
for item in items:
    for key in item:
        item_keys.add(key)


with open('bet365.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=sorted(item_keys))
    writer.writeheader()
    for item in items:
        writer.writerow(item)
