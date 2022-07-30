import requests
from bs4 import BeautifulSoup
import time
import re
import os
import csv
from termcolor import colored, cprint

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

EXE_PATH = r'webdriver\chromedriver.exe' #Chrome 92v



def parse_link(link, sessia):
    req = sessia.get(link)
    if req.status_code == requests.codes.ok:

        soup = BeautifulSoup(req.text, "html.parser")
        uid = link.split('/')[-1]

        try:
            company_name = re.sub(r"\s+", " ", soup.find(['div'], class_='j-d-h__company').text)
        except:
            company_name = None

        try:
            vacancy_name = re.sub(r"\s+", " ", soup.find('h3', class_='j-d-h__title').text)
        except:
            vacancy_name = None

        try:
            employment_type = re.sub(r"\s+", " ", soup.find(['div'], class_='j-d-h__info').text)
        except:
            employment_type = None

        try:
            salary = re.sub(r"\s+", " ", soup.find('div', class_='j-d-salary__bl').text)
        except:
            salary = None

        try:
            text = re.sub(r"\s+", " ", soup.find('div', class_='j-d-desc').text)
        except:
            text = None

    parse_params = {'name': vacancy_name,
                    'salary': salary,
                    # 'experience': experience,
                    'employment_type': employment_type,
                    'company_name': company_name,
                    # 'adress': adress,
                    'text': text,
                    # 'skills': skills,
                    'uid': uid
                    }

    return parse_params

def make_tmp_dataset(total_vac_list):
    """
    :param total_vac_list: List of dictionary
    :return: tmp.csv in data

    encoded in utf-8
    """
    keys = total_vac_list[0].keys()
    with open("data/cs_tmp.csv", "w", encoding='utf-8') as file:
        csvwriter = csv.DictWriter(file, keys)
        csvwriter.writeheader()
        csvwriter.writerows(total_vac_list)

def main():
    total_vac_list = []

    sessia = requests.Session()

    driver = webdriver.Chrome(executable_path=EXE_PATH)
    driver.get('https://careerspace.app/jobs')
    delay = 3  # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__layout"]/div/div[1]/div[2]/form/div/div[2]/div/div[3]/div/div/div[2]/input')))
        print("Page is ready!")
    except TimeoutException:
        print("Loading took too much time!")

    checkbox = driver.find_element_by_xpath(
        '//*[@id="__layout"]/div/div[1]/div[2]/form/div/div[2]/div/div[3]/div/div/div[1]')
    checkbox.click()

    checkbox_element = driver.find_element_by_xpath(
        '//*[@id="__layout"]/div/div[1]/div[2]/form/div/div[2]/div/div[3]/div/div/div[3]/ul/li[3]')
    checkbox_element.click()

    checkbox.click()

    button = driver.find_element_by_xpath('//*[@id="__layout"]/div/div[1]/div[2]/form/div/div[2]/div/div[6]/button[1]')
    button.click()

    count_vac_in_button = int(driver.find_element_by_xpath(
        '//*[@id="__layout"]/div/div[1]/div[2]/form/div/div[2]/div/div[6]/button[1]/span/span').text)
    print(colored('[INFO]', 'magenta', attrs=['bold']), count_vac_in_button)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # infinite-status-prompt

    count_vacs_status = 0
    while count_vacs_status < count_vac_in_button:
        try:
            vacs = driver.find_elements_by_class_name('job-card')
            count_vacs_status = len(vacs)
            # print(count_vacs_status)

        except:
            print('Error')

    print(colored('[INFO]', 'magenta', attrs=['bold']) + f' Count Vacancys: {count_vacs_status}')

    for el in vacs:
        try:
            _link = el.find_element_by_class_name('job-card__i').get_attribute('href')
            params = parse_link(_link, sessia)
            print(colored('[INFO]', 'magenta', attrs=['bold']) + f' vacancy name: {params["name"]} | href: {_link}')
            print(colored(f'[Salary]', 'magenta', attrs=['bold']) + f' {params["salary"]}')
            print(colored(f'[ET]', 'magenta', attrs=['bold']) + f' {params["employment_type"]}')
            print()
            total_vac_list.append(params)
        except:
            pass

    driver.quit()

    make_tmp_dataset(total_vac_list)

if __name__ == '__main__':
    main()



    """
    run_no = 0

    payload = {
        'sortBy': 'new-desc',
        'functions': '13',
        'skip': f'{run_no}',
        'take': '50',
    }

    cookies = {
        '_ym_uid': '1659187953195001898',
        '_ym_d': '1659187953',
        '_ym_isad': '2',
    }

    headers = {
        'authority': 'careerspace.app',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        # Requests sorts cookies= alphabetically
        # 'cookie': '_ym_uid=1659187953195001898; _ym_d=1659187953; _ym_isad=2',
        'sec-ch-ua': '"Chromium";v="102", "Opera GX";v="88", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36 OPR/88.0.4412.85',
    }

    sessia = requests.Session()


    req = sessia.get('https://careerspace.app/jobs', params=payload, cookies=cookies, headers=headers)
    #req = sessia.get('https://careerspace.app/api/v1/jobs/filter/', params=params, cookies=cookies, headers=headers)
    for i in range(10):
        if req.status_code == requests.codes.ok:
            print(f'[info] {run_no}')
            #print(req)


            soup = BeautifulSoup(req.text, "html.parser")
            vacancy_list = soup.findAll(['div'], class_='job-card')
            run_no += 50
            #print(len(vacancy_list))
            for el in vacancy_list:
                try:
                    #cprint(el.h3.text)
                    _link = el.find('a', class_='job-card__i', href=True)["href"]
                    print(colored('[INFO]', 'magenta', attrs=['bold']) + f' vacancy name: {el.h3.text} | link: https://careerspace.app{_link}')
                    print(colored('[INFO]', 'magenta', attrs=['bold']) + f' run_no: {run_no}')
                except:
                    cprint(f'[Error] NoneType text', 'red', attrs=['bold'])
                #finally:
                #    cprint(f'Finish', 'blue', attrs=['bold'])
        """