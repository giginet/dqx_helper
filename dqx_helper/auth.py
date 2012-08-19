# -*- coding: utf-8 -*-
#
# auth.py
# created by giginet on 2012/08/18
#

import re
import sys
from getpass import getpass
import cookielib
import mechanize
from BeautifulSoup import BeautifulSoup
import dqx_helper
from character import Character

class AuthException(Exception): pass

class Auth(object):
    LOGIN_PAGE = r'%s/sc/login' % dqx_helper.BASE_URL
    SEARCH_PAGE = r'%s/sc/search' % dqx_helper.BASE_URL

    def __init__(self, username=None, passwd=None):
        self.browser = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        self.browser.set_cookiejar(cj)
        self.browser.set_handle_equiv(True)
        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)
        self.browser.set_handle_robots(False)
        if not username or not passwd:
            sys.stdout.write('Username: ')
            username = raw_input()
            passwd = getpass()
        self.login(username, passwd)
        self._character = None
        
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
        try:
            r = browser.submit()
        except:
            raise AuthException('Username or Password may be invalid.')
        r = browser.open(self.SEARCH_PAGE)
        soup = BeautifulSoup(r)
        rel = dict(soup.findAll('a', {'class':re.compile('charselect')})[0].attrs)['rel']
        if not rel:
            raise AuthException("Exception raised for errors in authenticate to DQX portal.")
        browser.select_form(name='loginActionForm')
        for f in browser.form.controls: f.readonly = False
        self.cid = int(rel)
        browser.form['cid'] = str(self.cid)
        browser.submit()

    @property
    def character(self):
        if not self._character:
            self._character = Character(self.cid, self)
        return self._character
