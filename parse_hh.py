import requests
from bs4 import BeautifulSoup
import time
import re
import os
import csv
from termcolor import colored, cprint

#search_vacancy_list = ['data scientist', 'аналитик данных', 'machine learning', 'data engineer', 'data analyst']
search_vacancy_list = ['data scientist', 'аналитик данных', 'machine learning']

def get_data(search_vacancy_list:list, search_period:int=14)->list:
    """
    :param search_vacancy_list: List vacancy names which one will be parsed
    :param search_period: filtred last n-days, default = 14 (2week)
    :return:
    """

    total_vac_list = []

    if not os.path.exists('data'):
        os.mkdir('data')

    run_no = 0
    for vacancy_name in search_vacancy_list:
        run_no = 0
        while True:
            payload = {'search_period': search_period,
                       'text': vacancy_name,
                       'ored_clusters': True,
                       'enable_snippets': True,
                       'clusters': True,
                       'area': 113,  # 113 - Russia
                       'hhtmFrom': 'vacancy_search_catalog',
                       'page': run_no}

            sessia = requests.Session()
            try:
                req = sessia.get('https://hh.ru/search/vacancy', headers={'User-Agent': 'Custom'}, data=payload)
                if req.status_code == requests.codes.ok:
                    soup = BeautifulSoup(req.text, "html.parser")

                    run_no += 1

                    if soup.findAll(['div'], class_='vacancy-serp-item__layout') != []:
                        print()
                        print()
                        cprint('===' * 50, 'cyan', attrs=['bold'])
                        cprint(f'[PAGE] {run_no} - {vacancy_name}', 'cyan', attrs=['bold'])
                        cprint('===' * 50, 'cyan', attrs=['bold'])
                        print()
                        print()
                        for el in soup.findAll(['div'], class_='vacancy-serp-item__layout'):
                            _name = el.find('a', class_='bloko-link', href=True).text
                            link = el.find('a', class_='bloko-link', href=True)["href"]
                            time.sleep(0.05)
                            parse_params = parse_page(link, sessia)
                            parse_params['link'] = link

                            print(colored('[INFO]', 'magenta', attrs=['bold'])+ f' vacancy name: {_name} | href: {link}')
                            print(colored(f'[Salary]', 'magenta', attrs=['bold'])+ f' {parse_params["salary"]}')
                            print(colored(f'[Skills]', 'magenta', attrs=['bold'])+ f' {parse_params["skills"]}')
                            print()
                            total_vac_list.append(parse_params)
                    else:
                        print()
                        cprint(f'[Error] start parse next vacancy', 'red', attrs=['bold'])
                        print()
                        continue
                else:
                    print()
                    cprint(f'[Error] code: {req.status_code}', 'red', attrs=['bold'])
                    print()
                    break
            except:
                print()
                cprint('[Error] Session crash', 'red', attrs=['bold'])
                print()
                break

    return total_vac_list
    
    

def parse_page(url, sessia):
    """
    Parsing Page, get params from html and convert to dict
    :param url:
    :param sessia:
    :return: dict
    """
    #print('hello world')
    req = sessia.get(url, headers={'User-Agent': 'Custom'})
    if req.status_code == requests.codes.ok:
        soup = BeautifulSoup(req.text, "html.parser")

        uid = re.search('\d+', url).group(0)

        try:
            name = soup.find(['div'], class_='vacancy-title').h1.text
        except:
            name = None

        try:
            salary = soup.find(attrs={'data-qa': 'vacancy-salary'}).text
        except:
            salary = None

        try:
            experience = soup.find(attrs={'data-qa': 'vacancy-experience'}).text
        except:
            experience = None

        try:
            employment_type = soup.find(attrs={'data-qa': 'vacancy-view-employment-mode'}).text
        except:
            employment_type = None

        try:
            company_name = soup.find(['span'], class_='vacancy-company-name').text
        except:
            company_name = None

        try:
            adress = soup.find(attrs={'data-qa': 'vacancy-view-raw-address'}).text
        except:
            adress = None

        try:
            text = soup.find(['div'], class_='vacancy-description').text
        except:
            text = None

        try:
            skills = str([el.text for el in soup.findAll(attrs={'data-qa': 'bloko-tag__text'})])
        except:
            skills = None

        parse_params = {'name': name,
                        'salary': salary,
                        'experience': experience,
                        'employment_type': employment_type,
                        'company_name': company_name,
                        'adress': adress,
                        'text': text,
                        'skills': skills,
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
    with open("data/hh_tmp.csv", "w", encoding='utf-8') as file:
        csvwriter = csv.DictWriter(file, keys)
        csvwriter.writeheader()
        csvwriter.writerows(total_vac_list)

if __name__ == '__main__':

    total_vac_list = get_data(search_vacancy_list, 14)
    print(len(total_vac_list))
    make_tmp_dataset(total_vac_list)