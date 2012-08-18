# -*- coding: utf-8 -*-
#
# photo.py
# created by giginet on 2012/08/19
#
import os
import re
import urllib2
import cStringIO
from dateutil.parser import parser
from PIL import Image

class Photo(object):
    def __init__(self, url, author, **kwargs):
        self.url = url
        self.author = author
        self.place = kwargs.get('place', '')
        self.created_at = parser(kwargs.get('created_at'))
        self.comment = kwargs.get('comment')
        self.photo_id = re.compile(r'[0-9]+').search(self.url).groups()[-1]

    def save(self, path=os.getcwd()):
        dirname = os.path.dirname(path)
        data = urllib2.openurl(self.url).read()
        img = Image.open(cStringIO.cStringIO(data))
        img.save(os.path.join(dirname, self.filename))

    @property
    def filename(self):
        return r"%d_%d.png" % (self.author.cid, self.photo_id)
