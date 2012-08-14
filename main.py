# -*- coding: utf-8 -*-
#
# main.py
# created by giginet on 2012/08/14
#
import re
import cookielib
import mechanize
from BeautifulSoup import BeautifulSoup

class Product(object):
    def __init__(name="", price=0, quantity=1):
        pass

class BazaarBot(object):
    BASE_URL = r'https://secure.square-enix.com'
    LOGIN_PAGE = r'http://hiroba.dqx.jp/sc/login/'
    SEARCH_PAGE = r'http://hiroba.dqx.jp/sc/search/'
    ID_NAME = '_pr_confData_sqexid'
    PASSWD_NAME ='_pr_confData_passwd'

    def __init__(self, username='', passwd=''):
        self.login(username, passwd)

    def login(self, username, passwd):
        br = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        br.set_handle_equiv(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        br.open(self.LOGIN_PAGE)

        br.select_form(name='mainForm')
        br.form[self.ID_NAME] = username
        br.form[self.PASSWD_NAME] = passwd
        for f in br.form.controls:
            f.readonly = False
        br.form['_event'] = 'Submit'
        r = br.submit()
        br.select_form(name='mainForm')
        r = br.submit()
        r = br.open(self.SEARCH_PAGE)
        soup = BeautifulSoup(r)
        rel = dict(soup.findAll('a', {'class':re.compile('charselect')})[0].attrs)['rel']
        br.select_form(name='loginActionForm')
        for f in br.form.controls:
            f.readonly = False
        br.form['cid'] = rel
        br.submit()
        # r = br.open(self.SEARCH_PAGE)
        # print r.read()

if __name__ == '__main__':
    b = BazaarBot('giginet', '********')
