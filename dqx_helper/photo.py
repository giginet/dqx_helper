# -*- coding: utf-8 -*-
#
# photo.py
# created by giginet on 2012/08/19
#
import os
import cStringIO
from dateutil.parser import parser
from PIL import Image

class Photo(object):

    PHOTO_URL = r'http://img.dqx.jp/smpicture/download/webpicture/%d/original/%d/'

    def __init__(self, photo_id, author, **kwargs):
        self.photo_id = photo_id
        self.author = author
        self.place = kwargs.get('place', '')
        self.created_at = parser(kwargs.get('created_at'))
        self.comment = kwargs.get('comment')
        self.url = self.PHOTO_URL % (self.author.cid, self.photo_id)

    def save(self, path=os.getcwd()):
        if not self.author.is_auth: return
        r = self.author.auth.browser.open(self.url)
        img = Image.open(cStringIO.StringIO(r.read()))
        if os.path.isdir(path):
            img.save(os.path.join(path, self.filename))
            print "save %s" % self.filename
        else:
            print "%s is not found." % path

    @property
    def filename(self):
        return r"%d_%d.png" % (self.author.cid, self.photo_id)
