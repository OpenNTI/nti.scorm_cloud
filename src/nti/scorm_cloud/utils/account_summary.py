#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Provides functions for getting account summary information from scormcloud.

*IMPORTANT* This module uses undocumented apis and shouldn't be relied on in
production systems. It is meant to be an ops tool
"""

import argparse
from getpass import getpass
import requests
from urlparse import urljoin

SESSIONS_ENDPOINT = u'/api/cloud/sessions'
USAGE_SUMMARY_ENDPOINT = u'/api/cloud/realm/usage-summary'

def establish_session(base_url, username, password):
    """
    Establishes session cookies for the provided username and password.

    Returns cookies suitable for subsequent requests
    """
    session_url = urljoin(base_url, SESSIONS_ENDPOINT)
    resp = requests.post(session_url, data={u'email': username, u'password': password})
    resp.raise_for_status()
    return resp.cookies

def fetch_account_usage_summary(base_url, session):
    usage_url = urljoin(base_url, USAGE_SUMMARY_ENDPOINT)
    resp = requests.get(usage_url, cookies=session)
    resp.raise_for_status()
    return resp

def main():
    parser = argparse.ArgumentParser(description=u'Fetch account usage information from ScormCloud')
    
    parser.add_argument(u'--base-url',
                        type=str,
                        action=u'store',
                        dest=u'base_url',
                        help=u'The base url for scorm cloud',
                        default=u'https://cloud.scorm.com/',
                        required=False)
    parser.add_argument(u'-u', u'--username',
                        dest=u'username',
                        type=str,
                        action=u'store',
                        help=u'The scorm cloud username',
                        required=True)
    parser.add_argument(u'-p', u'--password',
                        nargs=u'?',
                        action=u'store',
                        dest=u'password',
                        required=True,
                        help=u'The scorm cloud password or blank to be prompted')

    arguments = parser.parse_args()
    if arguments.password is None:
        arguments.password = getpass(u'ScormCloud Password: ')
    session = establish_session(arguments.base_url,
                                arguments.username,
                                arguments.password)
    print fetch_account_usage_summary(arguments.base_url, session).text
