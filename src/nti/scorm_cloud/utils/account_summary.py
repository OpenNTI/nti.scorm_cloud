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

import calendar
from dateutil import parser as dt_parser

SESSIONS_ENDPOINT = u'/api/cloud/sessions'
USAGE_SUMMARY_ENDPOINT = u'/api/cloud/realm/usage-summary'

SCORM_CLOUD_PRICING = {
    'little': {
        'registrations': 50,
        'pricing': 75,
        'overage': 3
    },
    'medium': {
        'registrations': 100,
        'pricing': 150,
        'overage': 3
    },
    'big': {
        'registrations': 300,
        'pricing': 300,
        'overage': 0.33
    },
    'bigger': {
        'registrations': 3000,
        'pricing': 1000,
        'overage': 0.1
    },
    # TODO: confirm key name
    'evenBigger': {
        'registrations': 60000,
        'pricing': 5000,
        'overage': 0.075
    }
}


def establish_session(base_url, username, password):
    """
    Establishes session cookies for the provided username and password.

    Returns cookies suitable for subsequent requests
    """
    session_url = urljoin(base_url, SESSIONS_ENDPOINT)
    resp = requests.post(session_url, data={
                         u'email': username, u'password': password})
    resp.raise_for_status()
    return resp.cookies


def fetch_account_usage_summary(base_url, session):
    usage_url = urljoin(base_url, USAGE_SUMMARY_ENDPOINT)
    resp = requests.get(usage_url, cookies=session)
    resp.raise_for_status()
    return resp


def _to_epoch(date_str):
    dt = dt_parser.parse(date_str)
    return calendar.timegm(dt.utctimetuple())


def calculate_account_cost(account_type, registration_count):
    account_pricing = SCORM_CLOUD_PRICING[account_type]
    overages = registration_count - account_pricing['registrations']
    # Clamp to 0 if we have no overages
    overages = max(overages, 0)
    return account_pricing['pricing'] + overages * account_pricing['overage']


def _gauge(title, *args, **kwargs):
    from prometheus_client import Gauge

    # TODO is this the proper way to do this? We want to wrap the Guage
    # creation to prefix the title and send all other args kwargs through.
    # can our additional kwarg prefix not be defined in the function definition?
    prefix = kwargs.pop('prefix', 'scorm_cloud')
    return Gauge('%s_%s' % (prefix, title), *args, **kwargs)


def push_to_prometheus(usage, push_gateway, job):
    from prometheus_client import CollectorRegistry, push_to_gateway, Enum

    registry = CollectorRegistry()

    # Set some top level gauges based on our summary
    _gauge('job_last_success_unixtime',
           'Last time a batch job successfully finished',
           registry=registry).set_to_current_time()

    _gauge('billing_period_start_date',
           'When the current billing period started.',
           registry=registry).set(_to_epoch(usage['billingPeriodStartDate']))

    _gauge('billing_period_end_date',
           'When the current billing period ended.',
           registry=registry).set(_to_epoch(usage['billingPeriodEndDate']))

    _gauge('total_registration_count',
           'The total number of registrations in this billing cycle',
           registry=registry).set(usage['registrationCount'])

    _gauge('total_registration_limit',
           'The total registration limit for this billing cycle',
           registry=registry).set(usage['registrationLimit'])

    # Set up a labeled guage for each application name
    g = _gauge('registration_count',
               'The registration limit for each application in this billing cycle',
               labelnames=['scorm_cloud_application'],
               registry=registry)

    for application in usage.get('applications', ()):
        name = application['applicationName']
        count = application['registrationCount']
        g.labels(name).set(count)

    g = _gauge('account_costs',
               'The costs of each account type based on the current number of registrations',
               ['account_type'],
               registry=registry)

    for account_type in SCORM_CLOUD_PRICING.keys():
        g.labels(account_type).set(calculate_account_cost(
            account_type, usage['registrationCount']))

    _gauge('current_cost',
           'The cost of the current account type based on the current number of registrations',
           registry=registry
           ).set(calculate_account_cost(usage['accountType'], usage['registrationCount']))

    push_to_gateway(push_gateway, job=job, registry=registry)


def main():
    parser = argparse.ArgumentParser(
        description=u'Fetch account usage information from ScormCloud')

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

    # Optional arguments for pusing data to a prometheus monitoring system
    parser.add_argument(u'-t', u'--track',
                        type=str,
                        action=u'store',
                        dest=u'push_gateway',
                        required=False,
                        help=u'The host:port for a prometheus push gateway')
    parser.add_argument(u'-j', u'--job-name',
                        type=str,
                        action=u'store',
                        dest=u'job_name',
                        default=u'scorm_cloud_account_summary',
                        required=False,
                        help=u'The push_gateway job name to use')

    arguments = parser.parse_args()
    if arguments.password is None:
        arguments.password = getpass(u'ScormCloud Password: ')
    session = establish_session(arguments.base_url,
                                arguments.username,
                                arguments.password)
    usage = fetch_account_usage_summary(arguments.base_url, session).json()

    if arguments.push_gateway:
        push_to_prometheus(usage, arguments.push_gateway, arguments.job_name)

    return usage
