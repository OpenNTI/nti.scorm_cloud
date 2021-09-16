#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import uuid

from six.moves import urllib_parse

from zope import interface

from rustici_software_cloud_v2.api.registration_api import RegistrationApi as SCV2RegistrationApi

from rustici_software_cloud_v2.models.launch_auth_schema import LaunchAuthSchema

from rustici_software_cloud_v2.models.launch_link_request_schema import LaunchLinkRequestSchema

from rustici_software_cloud_v2.rest import ApiException

from nti.scorm_cloud.client.mixins import WithRepr
from nti.scorm_cloud.client.mixins import NodeMixin
from nti.scorm_cloud.client.mixins import RegistrationMixin

from nti.scorm_cloud.client.mixins import nodecapture

from nti.scorm_cloud.client.request import ScormCloudError

from nti.scorm_cloud.interfaces import IRegistrationService

from nti.scorm_cloud.minidom import getChildren
from nti.scorm_cloud.minidom import getChildText
from nti.scorm_cloud.minidom import getFirstChild
from nti.scorm_cloud.minidom import getTextOrCDATA
from nti.scorm_cloud.minidom import getAttributeValue
from nti.scorm_cloud.minidom import getChildTextOrCDATA

logger = __import__('logging').getLogger(__name__)


def _set_regid_on_redirecturl(redirect_url, regid):
    url_parts = list(urllib_parse.urlparse(redirect_url))
    query = dict(urllib_parse.parse_qsl(url_parts[4]))
    query.update({"regid": str(regid)})
    url_parts[4] = urllib_parse.urlencode(query)
    return urllib_parse.urlunparse(url_parts)


@interface.implementer(IRegistrationService)
class RegistrationService(object):

    def __init__(self, service):
        self.service = service

    def createRegistration(self, courseid, regid, fname, lname, learnerid,
                           email=None, postbackurl=None, authtype=None, urlname=None,
                           urlpass=None, resultsformat=None):
        regid = regid or str(uuid.uuid1())
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['fname'] = fname
        request.parameters['lname'] = lname
        request.parameters['courseid'] = courseid
        request.parameters['learnerid'] = learnerid
        request.parameters['appid'] = self.service.config.appid
        if email:
            request.parameters['email'] = email
        if postbackurl:
            request.parameters['postbackurl'] = postbackurl
        if authtype:
            request.parameters['authtype'] = authtype
        if urlname:
            request.parameters['urlname'] = urlname
        if urlpass:
            request.parameters['urlpass'] = urlpass
        if resultsformat:
            request.parameters['resultsformat'] = resultsformat
        xmldoc = request.call_service('rustici.registration.createRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Create Registration failed.")
        return regid
    create_registration = createRegistration

    def exists(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.exists')
        result = xmldoc.documentElement.firstChild.firstChild.nodeValue
        return result == 'true'

    def deleteRegistration(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service(
            'rustici.registration.deleteRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Delete Registration failed.")
    delete_registration = deleteRegistration

    def resetRegistration(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.resetRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Reset Registration failed.")
    reset_registration = resetRegistration

    def getRegistrationList(self, courseid=None, learnerid=None, after=None, until=None):
        request = self.service.request()
        request.parameters['appid'] = self.service.config.appid
        if courseid:
            request.parameters['courseid'] = courseid
        if learnerid:
            request.parameters['learnerid'] = learnerid
        if after:
            request.parameters['after'] = after
        if until:
            request.parameters['until'] = until
        xmldoc = request.call_service('rustici.registration.getRegistrationList')
        nodes = xmldoc.documentElement.getElementsByTagName('registration')
        return [Registration.fromMinidom(n) for n in nodes or ()]
    get_registration_list = getRegistrationList

    def getRegistrationDetail(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.getRegistrationDetail')
        nodes = xmldoc.getElementsByTagName('registration')
        return Registration.fromMinidom(nodes[0]) if nodes else None
    get_registration_detail = getRegistrationDetail

    def getRegistrationResult(self, regid, resultsformat=None, instanceid=None):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        if instanceid:
            request.parameters['instanceid'] = instanceid
        if resultsformat:
            request.parameters['resultsformat'] = resultsformat
        xmldoc = request.call_service('rustici.registration.getRegistrationResult')
        nodes = xmldoc.getElementsByTagName('registrationreport')
        return RegistrationReport.fromMinidom(nodes[0]) if nodes else None
    get_registration_result = getRegistrationResult

    def launch(self, regid, redirecturl, cssUrl=None, courseTags=None,
               learnerTags=None, registrationTags=None, disableTracking=False, culture=None,
               launchAuthType='vault', launchAuth=None):
        """
        Determine the launch url that can be used by the user agent to launch the provided
        registration.

        This has been migrated to the v2 api, notice some of the kwargs are translated
        based on the migration guide.

        https://cloud.scorm.com/docs/v2/reference/migration_guide/
        """
        if launchAuth is None:
            launchAuth = LaunchAuthSchema(type=launchAuthType)
        
        v2regservice = SCV2RegistrationApi(api_client=self.service.make_v2_api())
        redirecturl =  _set_regid_on_redirecturl(redirecturl, regid)

        launch_link_request = LaunchLinkRequestSchema(
            redirect_on_exit_url=redirecturl,
            tracking=not disableTracking,
            culture=culture,
            css_url=cssUrl,
            learner_tags=learnerTags,
            course_tags=courseTags,
            registration_tags=registrationTags,
            launch_auth=launchAuth
        )
        try:
            result = v2regservice.build_registration_launch_link(regid, 
                                                                 launch_link_request)
        except ApiException as exc:
            logger.exception("Error while getting scorm launch url")
            raise ScormCloudError('Cannot get scorm launch url')
        return result.launch_link
    get_launch_url = getLaunchURL = launch

    def getLaunchHistory(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.getLaunchHistory')
        nodes = xmldoc.getElementsByTagName('launchhistory')
        return LaunchHistory.fromMinidom(nodes[0]) if nodes else None
    get_launch_history = getLaunchHistory

    def getLaunchInfo(self, launchid):
        request = self.service.request()
        request.parameters['launchid'] = launchid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.getLaunchInfo')
        nodes = xmldoc.getElementsByTagName('launch')
        return Launch.fromMinidom(nodes[0]) if nodes else None
    get_launch_info = getLaunchInfo

    def resetGlobalObjectives(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.resetGlobalObjectives')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Reset global objectives failed.")
    reset_global_objectives = resetGlobalObjectives

    def updateLearnerInfo(self, learnerid, fname, lname, newid=None, email=None):
        request = self.service.request()
        request.parameters['learnerid'] = learnerid
        request.parameters['fname'] = fname
        request.parameters['lname'] = lname
        request.parameters['appid'] = self.service.config.appid
        if newid:
            request.parameters['newid'] = newid
        if email:
            request.parameters['email'] = email
        xmldoc = request.call_service('rustici.registration.updateLearnerInfo')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Update learner information failed.")
    update_learner_info = updateLearnerInfo

    def getPostbackInfo(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.getPostbackInfo')
        nodes = xmldoc.getElementsByTagName('postbackinfo')
        return PostbackInfo.fromMinidom(nodes[0]) if nodes else None
    get_postback_info = getPostbackInfo

    def updatePostbackInfo(self, regid, url, name=None, password=None,
                           authtype=None, resultsformat=None):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        if url:
            request.parameters['url'] = url
        if authtype:
            request.parameters['authtype'] = authtype
        if name:
            request.parameters['name'] = name
        if password:
            request.parameters['password'] = password
        if resultsformat:
            request.parameters['resultsformat'] = resultsformat
        xmldoc = request.call_service('rustici.registration.updatePostbackInfo')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Update Postback info failed.")
        return regid
    update_postback_info = updatePostbackInfo

    def deletePostbackInfo(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.deletePostbackInfo')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Postback info deletion failed.")
        return regid
    delete_postback_info = deletePostbackInfo

        
@WithRepr
class Comment(NodeMixin):

    def __init__(self, value=None, location=None, date_time=None):
        self.value = value
        self.location = location
        self.date_time = date_time

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        return cls(getChildTextOrCDATA(node, 'value'),
                   getChildTextOrCDATA(node, 'location'),
                   getChildTextOrCDATA(node, 'date_time'))


@WithRepr
class Response(NodeMixin):

    def __init__(self, id_=None, value=None):
        self.id = id_
        self.value = value

    @classmethod
    def fromMinidom(cls, node):
        return cls(getAttributeValue(node, 'id'),
                   getTextOrCDATA((node,)))


@WithRepr
class Interaction(NodeMixin):

    def __init__(self, id_, timestamp=None, weighting=None,
                 learner_response=None, result=None,
                 latency=None, description=None,
                 objectives=(), correct_responses=None):
        self.id = id_
        self.result = result
        self.latency = latency
        self.timestamp = timestamp
        self.weighting = weighting
        self.objectives = objectives
        self.description = description
        self.learner_response = learner_response
        self.correct_responses = correct_responses

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        objectives = []
        for n in getChildren(node, 'objectives', 'objective') or ():
            objectives.append(Objective.fromMinidom(n))
        correct_responses = []
        for n in getChildren(node, 'correct_responses', 'response') or ():
            correct_responses.append(Response.fromMinidom(n))
        return cls(getAttributeValue(node, 'id'),
                   getChildTextOrCDATA(node, 'timestamp'),
                   getChildTextOrCDATA(node, 'weighting'),
                   getChildTextOrCDATA(node, 'learner_response'),
                   getChildTextOrCDATA(node, 'result'),
                   getChildTextOrCDATA(node, 'latency'),
                   getChildTextOrCDATA(node, 'description'),
                   objectives or (),
                   correct_responses or ())


@WithRepr
class LearnerPreference(NodeMixin):

    def __init__(self, audio_level=None, language=None,
                 delivery_speed=None, audio_captioning=None):
        self.language = language
        self.audio_level = audio_level
        self.delivery_speed = delivery_speed
        self.audio_captioning = audio_captioning

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        return cls(getChildTextOrCDATA(node, 'audio_level'),
                   getChildTextOrCDATA(node, 'language'),
                   getChildTextOrCDATA(node, 'delivery_speed'),
                   getChildTextOrCDATA(node, 'audio_captioning'))


@WithRepr
class Static(NodeMixin):

    def __init__(self, completion_threshold=None, launch_data=None,
                 learner_id=None, learner_name=None, max_time_allowed=None,
                 scaled_passing_score=None, time_limit_action=None):
        self.learner_id = learner_id
        self.launch_data = launch_data
        self.learner_name = learner_name
        self.max_time_allowed = max_time_allowed
        self.time_limit_action = time_limit_action
        self.completion_threshold = completion_threshold
        self.scaled_passing_score = scaled_passing_score

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        return cls(getChildTextOrCDATA(node, 'completion_threshold'),
                   getChildTextOrCDATA(node, 'launch_data'),
                   getChildTextOrCDATA(node, 'learner_id'),
                   getChildTextOrCDATA(node, 'learner_name'),
                   getChildTextOrCDATA(node, 'max_time_allowed'),
                   getChildTextOrCDATA(node, 'scaled_passing_score'),
                   getChildTextOrCDATA(node, 'time_limit_action'))


@WithRepr
class Runtime(NodeMixin):

    def __init__(self, completion_status=None, credit=None, entry=None,
                 exit_=None, location=None, mode=None, progress_measure=None,
                 score_scaled=None, score_raw=None, total_time=None,
                 timetracked=None, success_status=None, suspend_data=None,
                 learnerpreference=None, static=None, comments_from_learner=(),
                 comments_from_lms=(), interactions=(), objectives=()):
        self.mode = mode
        self.exit = exit_
        self.entry = entry
        self.credit = credit
        self.static = static
        self.location = location
        self.score_raw = score_raw
        self.objectives = objectives
        self.total_time = total_time
        self.timetracked = timetracked
        self.interactions = interactions
        self.score_scaled = score_scaled
        self.suspend_data = suspend_data
        self.success_status = success_status
        self.progress_measure = progress_measure
        self.completion_status = completion_status
        self.learnerpreference = learnerpreference
        self.comments_from_lms = comments_from_lms
        self.comments_from_learner = comments_from_learner

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        pref = getFirstChild(node, 'learnerpreference')
        learnerpref = LearnerPreference.fromMinidom(pref) if pref else None
        static = getFirstChild(node, 'static')
        static = Static.fromMinidom(static) if pref else None
        comments_from_learner = []
        for n in getChildren(node, 'comments_from_learner', 'comment') or ():
            comments_from_learner.append(Comment.fromMinidom(n))
        comments_from_lms = []
        for n in getChildren(node, 'comments_from_lms', 'comment') or ():
            comments_from_lms.append(Comment.fromMinidom(n))
        interactions = []
        for n in getChildren(node, 'interactions', 'interaction') or ():
            interactions.append(Interaction.fromMinidom(n))
        objectives = []
        for n in getChildren(node, 'objectives', 'objective') or ():
            objectives.append(Objective.fromMinidom(n))
        return cls(getChildText(node, 'completion_status'),
                   getChildText(node, 'credit'),
                   getChildText(node, 'entry'),
                   getChildText(node, 'exit'),
                   getChildText(node, 'location'),
                   getChildText(node, 'mode'),
                   getChildText(node, 'progress_measure'),
                   getChildText(node, 'score_scaled'),
                   getChildText(node, 'score_raw'),
                   getChildText(node, 'total_time'),
                   getChildText(node, 'timetracked'),
                   getChildText(node, 'success_status'),
                   getChildTextOrCDATA(node, 'suspend_data'),
                   learnerpref,
                   static,
                   comments_from_learner or (),
                   comments_from_lms or (),
                   interactions or (),
                   objectives or ())


@WithRepr
class Instance(NodeMixin):

    def __init__(self, instanceId, courseVersion=None, updateDate=None):
        self.instanceId = instanceId
        self.updateDate = updateDate
        self.courseVersion = courseVersion

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        return cls(getChildTextOrCDATA(node, 'instanceId'),
                   getChildTextOrCDATA(node, 'courseVersion'),
                   getChildTextOrCDATA(node, 'updateDate'))


@WithRepr
class Registration(NodeMixin):

    def __init__(self, appId, registrationId, courseId,
                 courseTitle=None, lastCourseVersionLaunched=None,
                 learnerId=None, learnerFirstName=None, learnerLastName=None,
                 email=None, createDate=None, firstAccessDate=None, lastAccessDate=None,
                 completedDate=None, instances=()):
        self.appId = appId
        self.email = email
        self.courseId = courseId
        self.instances = instances
        self.learnerId = learnerId
        self.createDate = createDate
        self.courseTitle = courseTitle
        self.completedDate = completedDate
        self.lastAccessDate = lastAccessDate
        self.registrationId = registrationId
        self.firstAccessDate = firstAccessDate
        self.learnerLastName = learnerLastName
        self.learnerFirstName = learnerFirstName
        self.lastCourseVersionLaunched = lastCourseVersionLaunched

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        instances = []
        for n in getChildren(node, 'instances', 'instance') or ():
            instances.append(Instance.fromMinidom(n))
        return cls(getChildTextOrCDATA(node, 'appId'),
                   getChildTextOrCDATA(node, 'registrationId'),
                   getChildTextOrCDATA(node, 'courseId'),
                   getChildTextOrCDATA(node, 'courseTitle'),
                   getChildTextOrCDATA(node, 'lastCourseVersionLaunched'),
                   getChildTextOrCDATA(node, 'learnerId'),
                   getChildTextOrCDATA(node, 'learnerFirstName'),
                   getChildTextOrCDATA(node, 'learnerLastName'),
                   getChildTextOrCDATA(node, 'email'),
                   getChildTextOrCDATA(node, 'createDate'),
                   getChildTextOrCDATA(node, 'firstAccessDate'),
                   getChildTextOrCDATA(node, 'lastAccessDate'),
                   getChildTextOrCDATA(node, 'completedDate'),
                   instances or ())


@WithRepr
class RegistrationReport(RegistrationMixin):

    def __init__(self, format_, regid=None, instanceid=None,
                 complete=None, success=None, totaltime=0, score=None,
                 activity=None):
        RegistrationMixin.__init__(self, format_, regid, instanceid)
        self.score = score
        self.success = success
        self.activity = activity
        self.complete = complete
        self.totaltime = totaltime

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        activity = getFirstChild(node, 'activity')
        activity = Activity.fromMinidom(activity) if activity else None
        return cls(getAttributeValue(node, 'format'),
                   getAttributeValue(node, 'regid'),
                   getAttributeValue(node, 'instanceid'),
                   getChildText(node, 'complete'),
                   getChildText(node, 'success'),
                   getChildText(node, 'totaltime'),
                   getChildText(node, 'score'),
                   activity)


@WithRepr
class Objective(NodeMixin):

    def __init__(self, id_, measurestatus=False, normalizedmeasure=0.0,
                 progressstatus=False, satisfiedstatus=False,
                 score_scaled=None, score_min=None, score_raw=None,
                 success_status=None, completion_status=None, progress_measure=None,
                 description=None):
        self.id = id_
        self.score_min = score_min
        self.score_raw = score_raw
        self.description = description
        self.score_scaled = score_scaled
        self.measurestatus = measurestatus
        self.progressstatus = progressstatus
        self.success_status = success_status
        self.satisfiedstatus = satisfiedstatus
        self.progress_measure = progress_measure
        self.completion_status = completion_status
        self.normalizedmeasure = normalizedmeasure

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        return cls(getAttributeValue(node, 'id'),
                   getChildText(node, 'measurestatus') == 'true',
                   float(getChildText(node, 'normalizedmeasure') or '0.0'),
                   getChildText(node, 'progressstatus') == 'true',
                   getChildText(node, 'satisfiedstatus') == 'true',
                   getChildText(node, 'score_scaled'),
                   getChildText(node, 'score_min'),
                   getChildText(node, 'score_raw'),
                   getChildText(node, 'success_status'),
                   getChildText(node, 'completion_status'),
                   getChildText(node, 'progress_measure'),
                   getChildText(node, 'description'))


@WithRepr
class Activity(NodeMixin):

    def __init__(self, id_, title, complete=None, success=None,
                 satisfied=False, completed=False, progressstatus=False, attempts=1,
                 suspended=False, time_=None, score=None,
                 objectives=(), children=(), runtime=None):
        self.id = id_
        self.time = time_
        self.title = title
        self.score = score
        self.success = success
        self.runtime = runtime
        self.attempts = attempts
        self.children = children
        self.complete = complete
        self.suspended = suspended
        self.completed = completed
        self.satisfied = satisfied
        self.objectives = objectives
        self.progressstatus = progressstatus

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        objectives = []
        for n in getChildren(node, 'objectives', 'objective') or ():
            objectives.append(Objective.fromMinidom(n))
        children = []
        for n in getChildren(node, 'children', 'activity') or ():
            children.append(Activity.fromMinidom(n))
        runtime = getFirstChild(node, 'runtime')
        runtime = Runtime.fromMinidom(runtime) if runtime else None
        return cls(getAttributeValue(node, 'id'),
                   getChildText(node, 'title'),
                   getChildText(node, 'complete'),
                   getChildText(node, 'success'),
                   getChildText(node, 'satisfied') == 'true',
                   getChildText(node, 'completed') == 'true',
                   getChildText(node, 'progressstatus') == 'true',
                   int(getChildText(node, 'attempts') or '0'),
                   getChildText(node, 'suspended') == 'true',
                   getChildText(node, 'time'),
                   getChildText(node, 'score'),
                   objectives or (),
                   children or (),
                   runtime)


@WithRepr
class RuntimeEvent(NodeMixin):

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        values = {}
        for name, value in node.attributes.items():
            values[name] = value
        return cls(**values)


@WithRepr
class RuntimeLog(NodeMixin):

    def __init__(self, events=(), **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        self.events = events

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        values = {}
        for name, value in node.attributes.items():
            values[name] = value
        events = []
        for n in node.getElementsByTagName("RuntimeEvent") or ():
            events.append(RuntimeEvent.fromMinidom(n))
        return cls(events or (), **values)


@WithRepr
class Launch(NodeMixin):

    def __init__(self, id_, completion=None, satisfaction=None,
                 measure_status=None, normalized_measure=None, experienced_duration_tracked=None,
                 launch_time=None, exit_time=None, update_dt=None, runtimelog=None):
        self.id = id_
        self.exit_time = exit_time
        self.update_dt = update_dt
        self.completion = completion
        self.runtimelog = runtimelog
        self.launch_time = launch_time
        self.satisfaction = satisfaction
        self.measure_status = measure_status
        self.normalized_measure = normalized_measure
        self.experienced_duration_tracked = experienced_duration_tracked

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        log = getFirstChild(node, 'log')
        runtimelog = getFirstChild(log, 'RuntimeLog') if log else None
        runtimelog = RuntimeLog.fromMinidom(runtimelog) if runtimelog else None
        return cls(getAttributeValue(node, 'id'),
                   getChildText(node, 'completion'),
                   getChildText(node, 'satisfaction'),
                   getChildText(node, 'measure_status'),
                   getChildText(node, 'normalized_measure'),
                   getChildText(node, 'experienced_duration_tracked'),
                   getChildText(node, 'launch_time'),
                   getChildText(node, 'exit_time'),
                   getChildText(node, 'update_dt'),
                   runtimelog)


@WithRepr
class LaunchHistory(NodeMixin):

    def __init__(self, regid, launches=()):
        self.regid = regid
        self.launches = launches

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        launches = []
        for n in node.getElementsByTagName("launch") or ():
            launches.append(Launch.fromMinidom(n))
        return cls(getAttributeValue(node, 'regid'),
                   launches or ())


@WithRepr
class PostbackInfo(NodeMixin):

    def __init__(self, regid, url=None, authtype=None, login=None, password=None):
        self.url = url
        self.login = login
        self.regid = regid
        self.authtype = authtype
        self.password = password

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        return cls(getAttributeValue(node, 'regid'),
                   getChildText(node, 'url'),
                   getChildText(node, 'authtype'),
                   getChildText(node, 'login'),
                   getChildText(node, 'password'),)
