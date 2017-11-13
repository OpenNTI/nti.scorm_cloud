#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that

import unittest
from io import BytesIO

import fudge

from nti.scorm_cloud.client import ScormCloudService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestDebugService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.urlopen')
    def test_service(self, mock_up):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        debug = service.get_debug_service()

        # ping / authping
        for method in ('ping', 'authping'):
            reply = '<?xml version="1.0" encoding="utf-8" ?><rsp stat="ok"><pong /></rsp>'
            buff = BytesIO(reply)
            mock_up.is_callable().returns(buff)

            method = getattr(debug, method)
            assert_that(method(), is_(True))

            mock_up.is_callable().raises(ValueError())
            assert_that(method(), is_(False))

        # gettime
        reply = '<?xml version="1.0" encoding="utf-8" ?><rsp stat="ok"><currenttime tz="UTC">20171130152345</currenttime></rsp>'
        buff = BytesIO(reply)
        mock_up.is_callable().returns(buff)
        assert_that(debug.gettime(), is_('20171130152345'))

        mock_up.is_callable().raises(ValueError())
        assert_that(debug.gettime(), is_(none()))
