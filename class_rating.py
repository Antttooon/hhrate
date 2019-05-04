import re

import requests
from bs4 import BeautifulSoup as bs

from settings import settings
from utils import get_digits


class ParseRating:
    def __init__(self, search_text=None):

        self.search_text = search_text.replace(' ', '+') or 'Python'
        self.url = 'https://spb.hh.ru/search/resume?area=2&clusters=true&exp_period=all_time&logic=normal&no_magic=false&order_by=relevance&pos=full_text&text={search}'.format(
            search=self.search_text)
        self.t_url = 'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}'
        self.t_message = ''

        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.79'
        })

    def get_all_pages(self):
        all_pages_list = []
        r = self.session.get(self.url)

        html = bs(r.text, 'html.parser')
        count_resumes = get_digits(html.find('h1').text)
        self.t_message += '\nAll results: {}'.format(count_resumes)
        count_pages = int(html.find_all('a', class_='HH-Pager-Control')[-2].text)
        for i in range(0, count_pages):
            all_pages_list.append(self.url + '&page={}'.format(str(i)))
        return all_pages_list

    def get_zp(self, page):
        zp_list = []
        html = bs(page, 'html.parser')
        resumes = html.find_all('div', class_='resume-search-item')

        for resume in resumes:
            zp_text = resume.find('div', class_='resume-search-item__compensation').text
            digits = get_digits(zp_text)
            if 'USD' in zp_text:
                zp = settings.USD * digits
            elif 'EUR' in zp_text:
                zp = settings.EUR * digits
            elif 'руб' in zp_text:
                zp = digits
            else:
                zp = 0
            zp_list.append(zp)
        return zp_list

    def run(self):
        all_zp_list = []
        pages = self.get_all_pages()
        for url in pages[:30]:
            page = self.session.get(url).text
            zp_list = self.get_zp(page)
            all_zp_list += zp_list
        self.t_message += '\nPages count: ' + str(len(pages)) + '\n'
        try:
            my_rating = str(all_zp_list.index(64500) + 1)
        except:
            my_rating = 'Not in results!!!'

        self.t_message += '\nMy resume rating: ' + my_rating
        self.t_message += '\nMax ZP:' + str(max(all_zp_list))
        self.t_message += '\nMin ZP:' + str(min([i for i in all_zp_list if i != 0]))

        if my_rating.isalnum() and int(my_rating) > settings.min_rating:
            self.t_message += '\n !!! Warning, rating is very low !!! {}\n'.format(my_rating)
            self.t_message += str(self.url.encode('utf-8'))

        print(self.t_message)

        try:
            send_message = requests.get(
                self.t_url.format(token=settings.TOKEN, chat_id=settings.CHAT_ID, text=self.t_message))
            print('Message send status: ', send_message.status_code)
        except Exception as e:
            print("ERROR : Message not send: ", e)
