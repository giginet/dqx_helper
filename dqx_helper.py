# -*- coding: utf-8 -*-
#
# /Users/giginet/Desktop/dqx-helper/dqx_helper.py
# created by giginet on 2012/08/18
#

import sys
import yaml
from dqx_helper.auth import Auth
from dqx_helper.bazaar import Bazaar

SETTING_FILE = 'setting.yaml'

if __name__ == '__main__':
    setting = yaml.load(open(SETTING_FILE).read())
    if len(sys.argv) == 1:
        print "%s must be called as %s <command> arg0, arg1..." % (sys.argv[0], sys.argv[0])
    elif len(sys.argv) >= 2:
        command = sys.argv[1]
        args = []
        if len(sys.argv) > 2:
            args = sys.argv[2:]
        if command == 'bazzar':
            product = args[0]
            q = product.decode(sys.getfilesystemencoding())
            print u"%sの検索結果" % q
            a = Auth(setting['sqex_id'], setting['passwd'])
            b = Bazaar(a)
            products = b.search_item(product)
            for product in products[:100]:
                print u"%dG %d個 総額%dG @%s" % (product.price, product.quantity, product.total, product.place)
            print u"%d品中" % len(products)
        elif command == 'character':
            a = Auth(setting['sqex_id'], setting['passwd'])
            a.character
