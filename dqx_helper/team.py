# -*- coding: utf-8 -*-
#
# dqx_helper/team.py
# created by giginet on 2012/09/04
#
import re
import itertools
import cStringIO
from PIL import Image
from BeautifulSoup import BeautifulSoup
import dqx_helper
from dqx_helper.character import Character, PermissionException, CharacterListMixin

class Team(CharacterListMixin):
    TEAM_PAGE = r'%s/sc/team/%d/top/'
    TEAM_MEMBERLIST_PAGE = r'%s/sc/team/%d/memberlist/page/%d/'

    def __init__(self, team_id, auth):
        self.team_id = team_id
        self.auth = auth
        self._emblem = None
        self._members = None
        self.fetch()

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def fetch(self):
        page = self.auth.browser.open(self.TEAM_PAGE % (dqx_helper.BASE_URL, self.team_id))
        soup = BeautifulSoup(page.read())
        error = soup.find('span', {'class' : 'error_red'})
        if error:
            error_str = error.contents[1].string
            print error_str
            raise PermissionException('Permission Denied for fetching Team %d', self.team_id)
        team_name = soup.find('div', {'class' : re.compile('tt_teamName')})
        self.name = team_name.contents[1].string
        team_slogan = soup.find('p', {'class' : re.compile('tt_slogan')})
        self.slogan = team_slogan.string
        team_reader = soup.find('p', {'class' : re.compile('charaName_idLeader')}).find('a')
        cid = dict(team_reader.attrs)['href'].split('/')[-2]
        self.reader = Character(cid, self.auth)
        self._emblem_url = dict(soup.find('div', {'class' : 'img_teamMark'}).find('img').attrs)['src']

    @property
    def emblem(self):
        if not self._emblem:
            page = self.auth.browser.open(dqx_helper.BASE_URL + self._emblem_url)
            self._emblem = Image.open(cStringIO.StringIO(page.read()))
        return self._emblem

    @property
    def members(self):
        return self.get_members()

    def get_members(self):
        # fetch from memberlist
        if not self._members:
            self._members = []
            prev = None
            for page in itertools.count():
                page = self.auth.browser.open(self.TEAM_MEMBERLIST_PAGE % (dqx_helper.BASE_URL, self.team_id, page))
                soup = BeautifulSoup(page.read())
                members = self._get_characters(soup, 'memberlistTableTd')
                if prev and prev[0].cid == members[0].cid: break
                prev = members
                self._members += members
        return self._members
