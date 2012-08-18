# -*- coding: utf-8 -*-
#
# auth.py
# created by giginet on 2012/08/18
#
import re
import cookielib
import mechanize
from BeautifulSoup import BeautifulSoup
import dqx_helper

class AuthException(Exception):
    def __str__(self):
        return "Exception raised for errors in authenticate to DQX portal."

class Auth(object):
    LOGIN_PAGE = r'%s/sc/login' % dqx_helper.BASE_URL
    SEARCH_PAGE = r'%s/sc/search' % dqx_helper.BASE_URL
    BAZAAR_PAGE = r'%s/sc/search/bazaar/%s/page/%d'

    def __init__(self, username='', passwd=''):
        self.browser = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        self.browser.set_cookiejar(cj)
        self.browser.set_handle_equiv(True)
        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)
        self.browser.set_handle_robots(False)
        self.login(username, passwd)
        
    def login(self, username, passwd):
        browser = self.browser 
        browser.open(self.LOGIN_PAGE)

        browser.select_form(name='mainForm')
        for f in browser.form.controls: f.readonly = False
        browser.form['_pr_confData_sqexid'] = username
        browser.form['_pr_confData_passwd'] = passwd
        browser.form['_event'] = 'Submit'
        r = browser.submit()
        
        browser.select_form(name='mainForm')
        r = browser.submit()
        r = browser.open(self.SEARCH_PAGE)
        soup = BeautifulSoup(r)
        rel = dict(soup.findAll('a', {'class':re.compile('charselect')})[0].attrs)['rel']
        if not rel:
            raise AuthException()
        browser.select_form(name='loginActionForm')
        for f in browser.form.controls: f.readonly = False
        browser.form['cid'] = rel
        browser.submit()