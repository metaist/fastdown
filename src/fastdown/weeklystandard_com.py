#!/usr/bin/python
# coding: utf-8

from os import path as osp
import copy
import re

from bs4 import BeautifulSoup
import requests

from core import BaseScraper

DEFAULT_CONFIG = {
    'username': '',
    'password': '',
    'folder': '.'
}

class Scraper(BaseScraper):
    '''Scraping engine for weeklystandard.com'''
    BASE_URL = 'http://www.weeklystandard.com'

    config = {}
    proxies = None
    session = None

    def __init__(self, config, proxies=None, session=None):
        '''Construct the site object.'''
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self.config.update(config)
        self.proxies = proxies
        self.session = session or requests.Session()

    def run(self):
        '''Scrape this site.'''
        username = self.config.get('username', '')
        password = self.config.get('password', '')
        self.login(username, password)

        path = self.config.get('folder', '.')
        self.latest(path)

        return self

    def login(self, username, password):
        '''Get login page, fill out the form, and submit.'''
        next_url = self.baseurl('/users/login')
        print 'FETCH {0}'.format(next_url)
        soup = BeautifulSoup(self.get(next_url).text)
        # have login form

        form = soup.find(id='user-login-form')
        next_url = self.baseurl(form['action'])
        params = dict([(tag['name'], tag.get('value', ''))
                        for tag in form.find_all('input')])
        params['name'] = username
        params['pass'] = password
        print 'FETCH {0}'.format(next_url)
        self.post(next_url, params).text
        # logged in

        return self

    def latest(self, path='.'):
        '''Download the latest issue.'''
        next_url = self.baseurl('/issue/current')
        print 'FETCH {0}'.format(next_url)
        soup = BeautifulSoup(self.get(next_url).text)
        link = soup.find(lambda t: 'a' == t.name and
                         t.get('href', '').startswith('/download'))
        next_url = self.baseurl(link['href'])
        # have download url

        issue_name = ''.join(soup.find(class_='mag-title').stripped_strings)
        matches = re.match(r'.*Vol. ([0-9]*), No. ([0-9]*)', issue_name)
        issue_name = 'Vol-{0[0]}-No-{0[1]}'.format(matches.groups()) + '.pdf'
        # have issue volume / issue number

        print 'FETCH {0}'.format(next_url)
        response = self.get(next_url)
        with open(osp.join(path, issue_name), 'wb') as outfile:
            outfile.write(response.content)

        return self
