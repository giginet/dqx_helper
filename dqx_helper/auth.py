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

    def __init__(self, username=None, passwd=None, chara_index=0):
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
        self.login(username, passwd, chara_index)
        self._characters = None
        
    def login(self, username, passwd, chara_index=0):
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
        rels = [dict(char.attrs)['rel'] for char in soup.findAll('a', {'class':re.compile('charselect')})]
        if len(rels) == 0:
            raise AuthException("Exception raised for errors in authenticate to DQX portal.")
        elif len(rels) <= chara_index:
            raise AuthException("chara_index %d is not found.", chara_index)
        browser.select_form(name='loginActionForm')
        for f in browser.form.controls: f.readonly = False
        self.cids = map(lambda rel: int(rel), rels)
        browser.form['cid'] = str(self.cids[chara_index])
        browser.submit()

    @property
    def characters(self):
        if not self._characters:
            self._characters = [Character(cid, self) for cid in self.cids]
        return self._characters
