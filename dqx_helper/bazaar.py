# -*- coding: utf-8 -*-
#
# bazzar.py
# created by giginet on 2012/08/14
#
import re
import itertools
import urllib
from BeautifulSoup import BeautifulSoup
import dqx_helper

class Product(object):
    def __init__(self, **kwargs):
        self.item_id = kwargs.get('item_id')
        self.name = kwargs.get('name')
        self.quantity = kwargs.get('quantity', 1)
        self.rank = kwargs.get('rank', None)
        self.price = float(kwargs.get('price', 0)) / float(self.quantity)
        self.place = kwargs.get('place', '')
        self.total = self.price * self.quantity

    def __unicode__(self):
        return u"%(name)s(%(id)s)@%(place)s" % {'name':self.name, 'id':self.item_id, 'place':self.place}

class Bazaar(object):
    SEARCH_PAGE = r'%s/sc/search' % dqx_helper.BASE_URL
    BAZAAR_PAGE = r'%s/sc/search/bazaar/%s/page/%d'

    def __init__(self, auth):
        self.auth = auth
        
    def search_item(self, q=''):
        products = []
        r = self.auth.browser.open("%s/%s/item" % (self.SEARCH_PAGE, urllib.quote(q)))
        soup = BeautifulSoup(r.read())
        items = soup.findAll('a', {'href':re.compile('/sc/game/item/.+')})
        if len(items) is 0:
            return []
        href = dict(items[0].attrs)['href']
        item_id = href.split('/')[-2]
        for page in itertools.count():
            print "page %d fetching..." % page
            r = self.auth.browser.open(self.BAZAAR_PAGE % (dqx_helper.BASE_URL, item_id, page))
            soup = BeautifulSoup(r.read())
            columns = soup.findAll('tr', 'bazaarTableTd')
            if len(columns) is 0: break
            for column in columns:
                quantity = column.find('td', {'class':'col12Td'}).string
                price = column.find('td', {'class':'col14Td'}).contents[0]
                place = column.find('td', {'class':'col16Td'}).string
                rank_row = column.find('td', {'class':'col13Td'})
                font = rank_row.find('font')
                if font:
                    # fontタグがあるとき、ランク0 ~ 2
                    rank = 3 - len(font.string)
                else:
                    # fontタグがないとき、ランクなしかランク3
                    rank = None if rank_row.contents[0].string == '---' else 3
                quantity = re.match(r'^[0-9]+', quantity).group(0)
                price = re.match(r'^[0-9]+', price).group(0)
                product = Product(name=q, item_id=item_id, price=int(price), quantity=int(quantity), place=place, rank=rank)
                products.append(product)
        return sorted(products, key=lambda product: product.price)
