import json
import os
from pathlib import Path
from time import sleep

import requests
import selenium
import seleniumwire.undetected_chromedriver as uc
from selenium.webdriver.common.by import By

brave_path = '/usr/bin/brave-browser'
option = uc.ChromeOptions()
option.binary_location = brave_path
option.accept_insecure_certs = True  # necessary just because seleniumwire is needed for accessing
# the requests and it cert system is apparently broken and no longer maintained


AUDIO_FQDN = os.environ['AUDIO_FQDN']
BASE_URL = os.environ['BASE_URL']
USER_AGENT = os.environ['USER_AGENT']


def get_requests(driver):
    return [request for request in driver.requests if request.host == AUDIO_FQDN]


def request_detected(driver):
    while len(get_requests(driver)) == 0:
        sleep(5)


def search_for_word(driver, section_indx, section, word_indx, word):
    search_url = f'{base_url}{word}'
    access_link = True
    while access_link:
        driver.get(search_url)
        try:
            print(f"looking for {word}")
            driver.find_element(by=By.CLASS_NAME, value="play").click()
            request_detected(driver)
            sleep(3)
            forvo_requests = get_requests(driver)
            url = forvo_requests[len(forvo_requests) - 1].url
            response = requests.get(url, headers={"User-Agent": USER_AGENT})
            Path(f"pronunciation/{section_indx}_{section}").mkdir(parents=True, exist_ok=True)
            with open(f"pronunciation/{section_indx}_{section}/{word_indx}_{word}.mp3", "wb") as fout:
                fout.write(response.content)
            access_link = False
            print(f"downloaded audio for {word} from {url}")
        except selenium.common.exceptions.NoSuchElementException:
            print(f"{word} not found")
            access_link = False
        except selenium.common.exceptions.ElementClickInterceptedException:
            sleep(5)


def go_through_file():
    driver = uc.Chrome(options=option, version_main=125)
    words = json.loads(open("words.json").read())
    for section_indx, section in enumerate(words.items()):
        section_key = section[0]
        section = section[1]
        if type(section[0]) is str:
            for word_indx, words in enumerate(section):
                search_for_word(driver, section_indx, section_key, word_indx, words.replace("\n", ""))
    driver.close()


go_through_file()
