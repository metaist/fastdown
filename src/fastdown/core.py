#!/usr/bin/python
# coding: utf-8

from binascii import hexlify, unhexlify
from os import path as osp
import copy
import json

from argh import arg
from simplecrypt import encrypt, decrypt
import argh
import requests

DEFAULT_PATH = 'config.json'
DEFAULT_CONFIG = {
    'proxies': None,
    'sites': {}
}
DEFAULT_HEADERS = {
    'User-Agent':  ('Mozilla/5.0 (Windows NT 6.3; rv:36.0)'
                    'Gecko/20100101 Firefox/36.0')
}


def json_encrypt(password, obj):
    '''Serialize and encrypt a plain object.'''
    plaintext = json.dumps(obj)
    return hexlify(encrypt(password, plaintext))


def json_decrypt(password, ciphertext):
    '''Decrypt and deserialize an encrypted object.'''
    plaintext = decrypt(password, unhexlify(ciphertext))
    return json.loads(plaintext)


class BaseScraper(object):
    '''Common scraper methods.'''
    BASE_URL = 'http://example.com/'

    config = {}
    proxies = None
    session = None

    def baseurl(self, path):
        '''Construct a URL based on the BASE_URL.'''
        return self.BASE_URL + path

    def get(self, url, params=None):
        '''Simplified fetching of URLs.'''
        return self.session.get(url, params=params, proxies=self.proxies,
                                headers=DEFAULT_HEADERS)

    def post(self, url, params=None):
        '''Simplified posting of URLs.'''
        return self.session.post(url, data=params, proxies=self.proxies,
                                 headers=DEFAULT_HEADERS)


class Engine(object):
    '''Core engine.'''
    config = None

    def __init__(self, path=None, password=None):
        '''Construct a new engine.'''
        self.config = DEFAULT_CONFIG
        if path:
            self.load(path, password)

    def load(self, path=None, password=None):
        '''Load configuration, decrypting as needed.'''
        path = path or DEFAULT_PATH
        config = copy.deepcopy(DEFAULT_CONFIG)
        config.update(json.load(file(path)))

        for site, site_config in config.get('sites', {}).items():
            if type(site_config) in [str, unicode]:  # decrypt
                config['sites'][site] = json_decrypt(password, site_config)
                config['sites'][site]['encrypt'] = True

        self.path = path
        self.config = config
        return self

    def save(self, path=None, password=None):
        '''Save configuration, encrypting as needed.'''
        path = path or self.path or DEFAULT_PATH
        config = copy.deepcopy(self.config)
        for site, site_config in config.get('sites', {}).items():
            if site_config.get('encrypt', False) and password:  # encrypt
                config['sites'][site] = json_encrypt(password, site_config)
            else:  # plain copy
                config['sites'][site] = site_config

        with open(path, 'w') as configfile:
            json.dump(config, configfile, sort_keys=True, indent=2,
                      separators=(',', ': '))
        return self

    def run(self, site):
        '''Run a module.'''
        config = self.config.get('sites', {}).get(site, {})
        proxies = self.config.get('proxies', None)
        session = requests.Session()

        module = __import__(site.replace('.', '_'))
        module.Scraper(config, proxies, session).run()
        return self


@arg('-s', '--site', help='site to scrape')
@arg('-c', '--config', help='path to config file')
@arg('-p', '--password', help='password for config file')
@arg('-e', '--encrypt', help='encrypt config file after run')
@arg('-d', '--decrypt', help='decrypt config file after run')
def main(site=None, config='config.json', password=None,
         encrypt=False, decrypt=False):
    '''Main entry point.'''
    engine = Engine()
    engine.load(config, password=password)

    if site:
        engine.run(site)

    if encrypt:
        engine.save(password=password)
    elif decrypt:
        engine.save(password=None)

if '__main__' == __name__:
    argh.dispatch_command(main)
