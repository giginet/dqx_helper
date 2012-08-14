# -*- coding: utf-8 -*-
#
# main.py
# created by giginet on 2012/08/14
#
import re
import sys
import itertools
import urllib
import cookielib
import mechanize
import yaml
from BeautifulSoup import BeautifulSoup

class Product(object):
    def __init__(self, item_id="", name="", price=0, quantity=1, place=""):
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.price = price / self.quantity
        self.place = place
        self.total = self.price * self.quantity

    def __unicode__(self):
        return u"%(name)s(%(id)s)@%(place)s" % {'name':self.name, 'id':self.item_id, 'place':self.place}

class BazaarBot(object):
    BASE_URL = r'http://hiroba.dqx.jp'
    LOGIN_PAGE = r'%s/sc/login' % BASE_URL
    SEARCH_PAGE = r'%s/sc/search' % BASE_URL
    BAZAAR_PAGE = r'%s/sc/search/bazaar/%s/page/%d'
    ID_NAME = '_pr_confData_sqexid'
    PASSWD_NAME ='_pr_confData_passwd'

    def __init__(self, username='', passwd=''):
        self.br = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        self.br.set_cookiejar(cj)
        self.br.set_handle_equiv(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.login(username, passwd)
        
    def login(self, username, passwd):
        br = self.br 
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

    def search_item(self, q=''):
        products = []
        r = self.br.open("%s/%s/item" % (self.SEARCH_PAGE, urllib.quote(q)))
        soup = BeautifulSoup(r.read())
        items = soup.findAll('a', {'href':re.compile('/sc/game/item/.+')})
        if len(items) is 0:
            return []
        href = dict(items[0].attrs)['href']
        item_id = href.split('/')[-2]
        for page in itertools.count():
            print "Searchng... page %d" % page
            r = self.br.open(self.BAZAAR_PAGE % (self.BASE_URL, item_id, page))
            soup = BeautifulSoup(r.read())
            columns = soup.findAll('tr', 'bazaarTableTd')
            if len(columns) is 0: break
            for column in columns:
                quantity = column.find('td', {'class':'col12Td'}).string
                price = column.find('td', {'class':'col14Td'}).contents[0]
                place = column.find('td', {'class':'col16Td'}).string
                quantity = re.match(r'^[0-9]+', quantity).group(0)
                price = re.match(r'^[0-9]+', price).group(0)
                product = Product(name=q, item_id=item_id, price=int(price), quantity=int(quantity), place=place)
                products.append(product)
        return sorted(products, key=lambda product: product.price)

SETTING_FILE = 'setting.yaml'

if __name__ == '__main__':
    setting = yaml.load(open(SETTING_FILE).read())
    if len(sys.argv) == 2:
        b = BazaarBot(setting['sqex_id'], setting['passwd'])
        products = b.search_item(sys.argv[1])
        print "%sの検索結果" % sys.argv[1]
        for product in products[:10]:
            print u"%dG %d個 総額%dG @%s" % (product.price, product.quantity, product.total, product.place)
        print "%d品中" % len(products)
    else:
        print "%s must be called as %s <itemname>" % (sys.argv[0], sys.argv[0])
    
