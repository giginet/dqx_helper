# -*- coding: utf-8 -*-
#
# character.py
# created by giginet on 2012/08/18
#

import re
import math
import urllib2
import datetime
import cStringIO
from PIL import Image
from BeautifulSoup import BeautifulSoup
import dqx_helper
from dqx_helper.photo import Photo

class PermissionException(Exception): pass
class NotFoundException(Exception): pass

class CharacterListMixin(object):
    def _get_characters(self, soup, table_class):
        members = []
        member_tables = soup.findAll('tr', {'class' : table_class})
        for tr in member_tables:
            link = tr.findAll('td')[0].find('a')
            cid = re.compile('[0-9]+').search(dict(link.attrs)['href']).group(0)
            name = link.string
            try:
                member = Character(cid, self.auth, name)
                members.append(member)
            except PermissionException:
                print "%s is not public." % name
                member = Character(cid, self.auth, name, fetch=False)
                members.append(member)
            except NotFoundException:
                pass
        return members

class Character(CharacterListMixin):
    CID_PATTERN = r'(?P<cid>[0-9]+)'
    CHARACTER_URL = r'%s/sc/character/%d/'
    CHARACTER_STATUS_URL = r'%s/sc/character/%d/status/'
    HOME_STATUS_URL = r'%s/sc/home/status/'
    PHOTO_INDEX_URL = r'%s/sc/character/%d/picture/page/%d'
    FRIEND_INDEX_URL = r'%s/sc/character/%d/friendlist/page/%d'
    FACEICON_URL = r'%s/dq_resource/faceicon2/%s/%s/%s/%s/%d.png'
    
    def __init__(self, cid, auth=None, name=None, fetch=True):
        match = re.search(self.CID_PATTERN, str(cid))
        if (match and match.group('cid')):
            self.cid = int(match.group('cid'))
        elif isinstance(cid, int) or (isinstance(cid, str) and cid.isdigit()):
            self.cid = int(cid)
        else:
            raise TypeError("""'cid' must be URL of character page or character id.""")
        self.auth = auth
        if name:
            self.name = name
        self._friends = None
        self.updated_at = None
        self._team = None
        if fetch: self.fetch()

    def __unicode__(self):
        return u"%s[%s](%s %s %s) Lv.%d" % (self.name, self.character_id, self.job, self.species, self.sex, self.level)

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __eq__(self, other):
        return type(other) == type(self) and other.cid == self.cid

    def fetch(self):
        # fetch from home
        soup = self._get_soup(self.url)
        name = soup.find(id='myCharacterName')
        if not name:
            if soup.findAll('div', {'class':re.compile('imgUnkchara')}):
                raise NotFoundException('cid = %d is not found.' % self.cid)
            self.is_public = False
            raise PermissionException("cid = %d is not public." % self.cid)
        self.is_public = True
        match = re.match(r'\[(?P<name>.+)\]', name.string)
        self.name = match.group('name')
        self.message = ''.join([tag.string for tag in soup.find('div', {'class':'message'}).find('p') if not tag.string is None])
        self.location = map(lambda dt: dt.string, soup.find('div', {'class':'where'}).findAll('dd'))
        equipment_table = soup.find('div', {'class':'equipment'})
        equip_index = 1 if self.is_mychara() else 0 # マイキャラと他のキャラでは挙動が違う
        self.equipments = dict([(key.contents[0].string, None if value.contents[equip_index].string.strip() == u"そうびなし" else value.contents[equip_index].string.strip()) for key, value in zip(equipment_table.findAll('th'), equipment_table.findAll('td'))])
        slist = map(lambda tag: tag.string.replace(u'：', '').replace(u'&nbsp;', ''), soup.find('div', id='myCharacterStatusList').findAll('dd'))
        if self.is_mychara():
            self.character_id, kind, self.job, self.level = slist[:4]
            self.species = kind[:-1]
            self.sex = kind[-1]
        else:
            self.character_id, self.species, self.sex, self.job, self.level = slist[:5]
        self.level = int(self.level)
        self.money, self.next_exp, self.charge = (None,) * 3
        if self.is_mychara():
            self.next_exp = int(slist[4][:-1])
            self.money = int(slist[5][:-1])
            self.charge = int(slist[6][:-2])

        team = soup.find('div', id='myTeamStatusList')
        self._team_id = None
        if team:
            self._team_id = int(re.compile('[0-9]+').search(dict(team.find('a').attrs)['href']).group(0))

        support_comment = soup.find(id="welcomeFriend").find('dd')
        self.is_support = support_comment is not None
        self.support_info = {}
        if self.is_support:
            support = soup.find('div', {'class' : 'support'})
            self.support_info['comment'] = support_comment.contents[0].string.strip()
            if self.is_mychara():
                self.support_info['exp'], self.support_info['gold'], self.support_info['honor'] = map(lambda dd: int(re.compile('^[0-9]+').match(dd.contents[0].string).group(0)), support.find('dl', {'class' : 'value'}).findAll('dd'))

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
        tds = spell_table.findAll('td')
        if tds[0].contents[0].string.strip() == '---':
            self.spells = []
        else:
            spell_index = 1 if self.is_auth() else 0
            self.spells = [td.contents[spell_index].string.strip() for td in spell_table.findAll('td')]
        self.updated_at = datetime.datetime.today()

    def get_photos(self):
        if not self.is_auth():
            raise PermissionException("you cannot execute get_photos without logged in.")
        photos = []
        soup = self._get_soup(self.PHOTO_INDEX_URL % (dqx_helper.BASE_URL, self.cid, 0))
        max_page = re.compile('[0-9]+').search(soup.find('div', {'class' : 'searchResult'}).contents[0].string).group(0)
        for page in range(int(math.ceil(int(max_page) / 9))):
            print "Fetching page %d..." % page
            soup = self._get_soup(self.PHOTO_INDEX_URL % (dqx_helper.BASE_URL, self.cid, page))
            table = soup.findAll('td', {'class' : 'contentsTable1TD1'})
            if len(table) is 0: break
            for photo in table:
                info = dict(photo.find('a', {'class' : 'showLargePict'}).attrs)
                comment = info.get('title', '')
                date, location = photo.find('p', {'class' : 'thumbLocationAndDate'}).contents[::2]
                photo_id = int(re.compile(r'[0-9]+').findall(info['rel'])[-1])
                p = Photo(photo_id, self, comment=comment, created_at=str(date.string), location=str(location.string))
                photos.append(p)
        return photos

    @property
    def status_url(self):
        if self.is_mychara():
            return self.HOME_STATUS_URL % dqx_helper.BASE_URL
        return self.CHARACTER_STATUS_URL % (dqx_helper.BASE_URL, self.cid)

    @property
    def url(self):
        return self.CHARACTER_URL % (dqx_helper.BASE_URL, self.cid)

    def _get_soup(self, url):
        if self.is_auth():
            r = self.auth.browser.open(url)
            return BeautifulSoup(r.read())
        else:
            page = urllib2.urlopen(url)
            return BeautifulSoup(page)

    def is_mychara(self):
        return self.is_auth() and self.cid in self.auth.cids

    def is_auth(self):
        return not self.auth is None

    @property
    def friends(self):
        if self._friends is None:
            self._friends = self.get_friends()
        return self._friends

    def get_friends(self):
        # fetch from friendlist
        if not self.is_auth():
            raise PermissionException("you cannot execute get_friends without logged in.")
        if not self._friends:
            self._friends = []
            soup = self._get_soup(self.FRIEND_INDEX_URL % (dqx_helper.BASE_URL, self.cid, 0))
            max_page = re.compile('[0-9]+').search(soup.find('div', {'class' : 'searchResult'}).string).group(0)
            for page in range(int(math.ceil(int(max_page) / 10.0))):
                soup = self._get_soup(self.FRIEND_INDEX_URL % (dqx_helper.BASE_URL, self.cid, page))
                friends = self._get_characters(soup, 'friendlistTableTd')
                if len(friends) == 0: break
                self._friends += friends
        return self._friends
        
    def get_faceicon(self):
        l = len(str(self.cid))
        url = self.FACEICON_URL % (dqx_helper.BASE_URL, str(self.cid)[:l - 9], str(self.cid)[:l - 8], str(self.cid)[:l - 7], str(self.cid)[:l - 6], self.cid)
        page = urllib2.urlopen(url)
        return Image.open(cStringIO.StringIO(page.read()))

    @property
    def team(self):
        if not self._team:
            from dqx_helper.team import Team
            self._team = Team(self._team_id, self.auth)
        return self._team
