#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import nfc
from pygame import mixer


class CardReader(object):
    def __init__(self, logger, media):
        self.logger = logger
        # media
        mixer.init()
        mixer.music.load(media)
        self.music = mixer.music

    def output_log(self, c='', priority='debug'):
        if self.logger is not None:
            if priority == 'error':
                self.logger.error(c)
            elif priority == 'info':
                self.logger.info(c)
            elif priority == 'debug':
                self.logger.debug(c)
        else:
            print c

    def on_discover(self, target):
        self.output_log('FeliCa has been touch', 'info')
        self.music.play(1)
        return True

    def on_connect(self, tag):
        if isinstance(tag, nfc.tag.tt3.Type3Tag):
            self.idm = binascii.hexlify(tag.idm)
            self.callback(self.idm)
        return True

    def read_id(self, callback=None):
        self.callback = callback

        # nfc main class
        try:
            clf = nfc.ContactlessFrontend('usb')
            self.output_log(
                    'clf ContactlessFrontend has been connected', 'info')
        except Exception as e:
            self.output_log(str(e), 'error')
            raise Exception('clf ContactlessFrontend error')

        # FeliCa read
        rdwr_options = {
            'on-discover': self.on_discover,
            'on-connect': self.on_connect
        }
        try:
            clf.connect(rdwr=rdwr_options)
            self.output_log('FeliCa has been released', 'info')
        except Exception as e:
            self.output_log(str(e), 'error')
            raise Exception('clf connect error')
        finally:
            clf.close()
