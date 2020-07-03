import json, random, requests, os
import ruamel.yaml as yaml
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from time import perf_counter, sleep

try: config_file = os.environ['POLLINATOR_CONFIG']
except KeyError: config_file = 'config.yaml'
try:
    with open(config_file, "r") as file:
        configs = yaml.safe_load(file)
except Exception as error:
    print(f"Failed to load configs {error}")
vote_config, proxy_config = configs['votes'], configs['proxy']
url = proxy_config['url']
params = dict(
    apiKey=proxy_config['api_key'],
    country="US",
)
def get_proxy():
    while True:
        resp = requests.get(url=url, params=params)
        data = json.loads(resp.text)
        try:
            print(f"Location: {data['city']}, {data['state']}, {data['country']}\nRemaining: {data['requestsRemaining']}")
        except KeyError:
            print(data)
            continue
        PROXY = data["proxy"]
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType": "MANUAL",
        }
        webdriver.DesiredCapabilities.CHROME['timeouts'] = {
            "pageLoad": 3000,
        }
        webdriver.DesiredCapabilities.CHROME['pageLoadStrategy'] = 'eager'
        tic = perf_counter()
        driver = webdriver.Chrome()
        try:
            driver.get("https://google.com/")
            WebDriverWait(driver, timeout=2).until(EC.title_is("Google"))
            return PROXY
            break
        except TimeoutException as error:
            continue
        finally:
            toc = perf_counter()
            dur = toc - tic
            print(f"Proxy validation time {dur:0.2f} seconds")
            driver.quit()

for i in range(configs['votes']['number_of_votes']):
    PROXY = get_proxy()
    try:
        tally = {}
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType": "MANUAL",
        }
        webdriver.DesiredCapabilities.CHROME['pageLoadStrategy'] = 'normal'
        tick = perf_counter()
        webdriver.DesiredCapabilities.CHROME['timeouts'] = { "pageLoad": 15000 }
        driver = webdriver.Chrome()
        driver.set_window_size(1024, 768)
        driver.delete_all_cookies()
        driver.get(vote_config['vote_url'])
        WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.ID, 'pollvote'))).click()
        random_vote = random.randrange(100)
        if random_vote < vote_config['bias_to_first_option']:
            vote_option = vote_config['vote_options'][0]['option']
            print(f"Voting for {vote_config['vote_options'][0]['text']} {vote_option}")
        else:
            vote_option = vote_config['vote_options'][1]['option']
            print(f"Voting for {vote_config['vote_options'][1]['text']} {vote_option}")
        WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.ID, vote_option))).click()
        try:
            WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.ID, vote_config['vote_button_id']))).click()
            WebDriverWait(driver, timeout=5).until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'pds-question-top'),'Thank you for voting'))
        except UnexpectedAlertPresentException as error:
            try:
                please_vote = driver.switch_to_alert()
                please_vote.accept()
                WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.ID, vote_option))).click()
            except:
                pass
            WebDriverWait(driver, timeout=10).until(EC.element_to_be_clickable((By.ID, vote_config['vote_button_id']))).click()
        answers = driver.find_elements_by_class_name('pds-feedback-group')
        for answer in answers:
            for option in vote_config['vote_options']:
                if answer.find_element_by_class_name("pds-answer-text").text == option['text']:
                    tally[option['text']] = answer.find_element_by_class_name("pds-feedback-result").text
    except (NoSuchElementException, TimeoutException) as error:
        print(error)
        continue
    finally:
        tock = perf_counter()
        if tally:
            print(f"Vote completed in {tock - tick:0.2f} seconds\nScore: {tally}")
            sleeper = random.randrange(5, 20)
            print(f"Dwell for {sleeper} seconds")
            sleep(sleeper)
        else: print(f"No vote tally found in {tock-tick:0.2f}")
        driver.quit()
        pass
