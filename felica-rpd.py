#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import requests
import json
import time
import Felica
from logging import getLogger, Formatter, DEBUG
from logging.handlers import TimedRotatingFileHandler


def setLogging(logfile, bktime, bkcount):
    handler = TimedRotatingFileHandler(
        filename=logfile,
        when=bktime,
        backupCount=bkcount
    )
    handler.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def check_process(pidFile, logger=None):
    if os.path.isfile(pidFile):
        logger.error('the process is already exist')
        sys.exit(1)
    else:
        logger.info('check_process OK')


def postDataToJS(data, url, headers, logger=None):
    data = json.dumps(data)
    logger.debug(data)
    try:
        response = requests.post(url, data=data, headers=headers)
        logger.debug(response.status_code)
        logger.debug(response.text)
    except requests.exceptions.ConnectionError as e:
        logger.error(str(e))


def callback(idm):
    url = 'http://localhost:3000/card_data_post'
    headers = {'content-type': 'application/json'}
    data = {'IDm': idm}
    postDataToJS(data, url, headers, logger)


def main(logger=None):
    # Read and Post IDm to node.js
    media = '/opt/felica_app/python/media/se_maoudamashii_system46.wav'
    cr = Felica.CardReader(logger, media)
    logger.info('felica-rpd is started...')
    while True:
        try:
            cr.read_id(callback)
        except Exception as e:
            logger.error(str(e))
            time.sleep(10)


def fork(pidFile, logger=None):
    pid = os.fork()

    if pid > 0:
        # Write pid file
        f = open(pidFile, 'w')
        f.write(str(pid)+"\n")
        f.close()
        sys.exit(0)

    if pid == 0:
        main(logger)


if __name__ == '__main__':
    # pid file
    pidFile = '/var/run/felica_app/felica-rpd.pid'

    # Logging
    logger = setLogging('/var/log/felica_app/felica-rpd.log', 'W0', 10)

    # Double start-up prevention
    check_process(pidFile, logger)

    # Fork
    fork(pidFile, logger)
