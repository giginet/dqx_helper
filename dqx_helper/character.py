# -*- coding: utf-8 -*-
#
# character.py
# created by giginet on 2012/08/18
#

import re
import urllib2
from BeautifulSoup import BeautifulSoup
import dqx_helper

class PermissionException(Exception): pass

class Character(object):
    CID_PATTERN = r'(?P<cid>[0-9]+)'
    CHARACTER_URL = '%s/sc/character/%d/'
    CHARACTER_STATUS_URL = '%s/sc/character/%d/status/'
    HOME_STATUS_URL = '%s/sc/home/status/'
    
    def __init__(self, cid, auth=None):
        match = re.search(self.CID_PATTERN, str(cid))
        if (match and match.group('cid')):
            self.cid = int(match.group('cid'))
        elif isinstance(cid, int) or (isinstance(cid, str) and cid.isdigit()):
            self.cid = int(cid)
        else:
            raise TypeError("""'cid' must be URL of character page or character id.""")
        self.auth = auth
        self.fetch(cid)

    def fetch(self, url):
        # fetch from home
        soup = self._get_soup(self.url)
        name = soup.find(id='myCharacterName').string
        match = re.match(r'\[(?P<name>.+)\]', name)
        if not match:
            raise PermissionException("cid = %d is not found or private. " % self.cid)
        self.name = match.group('name')
        self.message = ''.join([tag.string for tag in soup.find('div', {'class':'message'}).find('p') if not tag.string is None])
        self.location = map(lambda dt: dt.string, soup.find('div', {'class':'where'}).findAll('dd'))
        equipment_table = soup.find('div', {'class':'equipment'})
        equip_index = 1 if self.is_mychara() else 0 # マイキャラと他のキャラでは挙動が違う
        self.equipments = dict([(key.contents[0].string, None if value.contents[equip_index].string.strip() == u"そうびなし" else value.contents[equip_index].string.strip()) for key, value in zip(equipment_table.findAll('th'), equipment_table.findAll('td'))])
        slist = map(lambda tag: tag.string.replace(u'：', '').replace(u'&nbsp;', ''), soup.find('div', id='myCharacterStatusList').findAll('dd'))
        self.character_id, self.brood, self.sex, self.job, self.level = slist[:5]
        self.level = int(self.level)
        self.charge = None
        if self.is_mychara():
            self.charge = int(slist[5].replace(u'時間', ''))

        # fetch from status
        soup = self._get_soup(self.status_url)
        parameter_table = soup.find('div', {'class':'parameter'})
        self.parameters = dict([(key.contents[0].string, int(value.contents[0])) for key, value in zip(parameter_table.findAll('th'), parameter_table.findAll('td'))])
        skill_table = soup.find('div', {'class':'skill'})
        self.skills = dict([(key.contents[0].string, int(value.contents[0])) for key, value in zip(skill_table.findAll('th'), skill_table.findAll('td'))])
        sp_skill_table = soup.find('div', {'class':'specialSkill'})
        self.special_skills = dict([(tr.find('th').contents[0].string, map(lambda tag: tag.contents[0].string, tr.find('td').contents[1::2])) for tr in sp_skill_table.findAll('tr')])
        effect_table = soup.find('div', {'class':'skillEffect'})
        self.skill_effects = dict([(tr.find('th').contents[0].string, map(lambda tag: tag, tr.find('td').contents[1::2])) for tr in effect_table.findAll('tr')])
        spell_table = soup.find('div', {'class':'spell'})
        self.spells = [td.contents[0].string.strip() for td in spell_table.findAll('td')]
        if self.spells[0] == '---': self.spells = []

    @property
    def status_url(self):
        if self.is_mychara():
            return self.HOME_STATUS_URL % dqx_helper.BASE_URL
        return self.CHARACTER_STATUS_URL % (dqx_helper.BASE_URL, self.cid)

    @property
    def url(self):
        return self.CHARACTER_URL % (dqx_helper.BASE_URL, self.cid)

    def _get_soup(self, url):
        if self.is_mychara():
            r = self.auth.browser.open(url)
            return BeautifulSoup(r.read())
        else:
            page = urllib2.urlopen(url)
            return BeautifulSoup(page)

    def is_mychara(self):
        return self.auth and self.auth.cid == self.cid
