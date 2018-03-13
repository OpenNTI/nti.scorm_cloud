#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that

import unittest

import fudge

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestDebugService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_service(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        debug = service.get_debug_service()

        # ping / authping
        for method in ('ping', 'authping'):
            reply = '<rsp stat="ok"><pong /></rsp>'
            data = fudge.Fake().has_attr(content=reply)
            session = fudge.Fake().expects('get').returns(data)
            mock_ss.is_callable().returns(session)

            method = getattr(debug, method)
            assert_that(method(), is_(True))

            session = fudge.Fake().expects('get').raises(ValueError())
            mock_ss.is_callable().returns(session)
            assert_that(method(), is_(False))

        # gettime
        reply = '<rsp stat="ok"><currenttime tz="UTC">20171130152345</currenttime></rsp>'
        data = fudge.Fake().has_attr(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        assert_that(debug.gettime(), is_('20171130152345'))

        session = fudge.Fake().expects('get').raises(ValueError())
        mock_ss.is_callable().returns(session)
        assert_that(debug.gettime(), is_(none()))
