# -*- coding: utf-8 -*-
#
# /Users/giginet/Desktop/dqx-helper/dqx_helper.py
# created by giginet on 2012/08/18
#

import nose
import yaml
from nose.tools import ok_, eq_, raises
from dqx_helper.auth import Auth, AuthException
from dqx_helper.character import Character, PermissionException
from dqx_helper.bazaar import Bazaar
from dqx_helper.team import Team

SETTING_FILE = 'setting.yaml'

class TestAuth(object):
    def setup(self):
        setting = yaml.load(open(SETTING_FILE).read())
        self.sqex_id = setting['sqex_id']
        self.passwd = setting['passwd']

    def test_auth(self):
        u"""正しいID, パスワードでログインできる"""
        a = Auth(self.sqex_id, self.passwd)
        ok_(a)

    def test_character(self):
        u"""キャラクタを取得できる"""
        a = Auth(self.sqex_id, self.passwd)
        ok_(a.characters)

    @raises(AuthException)
    def test_error(self):
        u"""適当なID, パスワードでエラーが返ってくる"""
        Auth('hoge', 'hoge')

class TestCharacter(object):
    FIXTURE_ID = '111362909909'
    def setup(self):
        setting = yaml.load(open(SETTING_FILE).read())
        self.sqex_id = setting['sqex_id']
        self.passwd = setting['passwd']
        self.auth = Auth(self.sqex_id, self.passwd) 
        self.character = Character(self.FIXTURE_ID)
        self.my_chara = self.auth.characters[0]
    
    def test_name(self):
        u"""キャラクター名が取得できる"""
        eq_(self.character.name, u'ぎぎにゃん', '名前が取得できる')

    def test_info(self):
        u"""それぞれの情報を取得できる"""
        ok_(self.character.species)
        eq_(self.character.sex, u'男')
        ok_(self.character.level)

    @raises(PermissionException)
    def test_photo_permission(self):
        u"""ログインしてないと写真を取得できない"""
        ok_(self.character.get_photos())

    @raises(PermissionException)
    def test_friend_permission(self):
        u"""ログインしてないとフレンドを取得できない"""
        ok_(self.character.get_friends())

    def test_photo(self):
        u"""自分の写真が取得できる"""
        ok_(self.my_chara.get_photos())

    def test_friends(self):
        u"""自分のフレンドが取得できる"""
        ok_(self.my_chara.get_friends())

class TestTeam(object):
    FIXTURE_ID = 2420682692

    def setup(self):
        setting = yaml.load(open(SETTING_FILE).read())
        self.sqex_id = setting['sqex_id']
        self.passwd = setting['passwd']
        self.auth = Auth(self.sqex_id, self.passwd) 
        self.team = Team(self.FIXTURE_ID, self.auth)

    def test_name(self):
        u"""チーム名が取得できる"""
        ok_(self.team.name, u'ガマデウス')

    def test_member(self):
        u"""チームメンバーが取得できる"""
        ok_(self.team.members)

    def test_emblem(self):
        u"""エンブレムが取得できる"""
        ok_(self.team.emblem)

if __name__ == '__main__':
    nose.main(argv=['dummy', '-v'])
