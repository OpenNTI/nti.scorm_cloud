#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that

import unittest

import fudge

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer

XML_HEADER = '<?xml version="1.0" encoding="utf-8" ?>'


class TestInvitationService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_create_invitation(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        invitation = service.get_invitation_service()
        
        reply = XML_HEADER + '<rsp stat="ok">937296cb-ae79-4190-bb6f-9a39b97785ac</rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        for method in ('createInvitation', 'createInvitationAsync'):
            method = getattr(invitation, method)
            iden = method("mycourseid", True, True, 
                          "myemail@sample.com", 
                          "email subject", "email body",
                          True, 1, 
                          "http://mysite.org", 
                          "httpbasic", "myname", "mypassword", 
                          "activity", "20171130152345")
            assert_that(iden, is_('937296cb-ae79-4190-bb6f-9a39b97785ac'))
