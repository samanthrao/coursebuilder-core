# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests that walk through Course Builder pages."""

__author__ = 'Sean Lip'

import os
import unittest

import webapp2
import webtest

from google.appengine.ext import testbed


def FakeLogin(email):
  os.environ['USER_EMAIL'] = email
  os.environ['USER_ID'] = 'user1'


def EmptyEnviron():
  os.environ['AUTH_DOMAIN'] = 'example.com'
  os.environ['SERVER_NAME'] = 'localhost'
  os.environ['SERVER_PORT'] = '8080'
  os.environ['USER_EMAIL'] = ''
  os.environ['USER_ID'] = ''


class BaseTestClass(unittest.TestCase):
  """Base class for setting up and tearing down test cases."""

  def setUp(self):
    EmptyEnviron()
    import main
    main.debug = True
    app = main.app
    self.testapp = webtest.TestApp(app)
    self.testbed = testbed.Testbed()
    self.testbed.activate()

    # Declare any relevant App Engine service stubs here.
    self.testbed.init_user_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.testbed.deactivate()


class GetRequestTest(BaseTestClass):
  """A class for testing GET requests."""

  def testGetRequests(self):
    """Test GET requests on individual pages."""
    FakeLogin('test@example.com')
    response = self.testapp.get('/')
    self.assertEqual(response.status_int, 302)
    self.assertEqual(
        response.location, 'http://%s/register' % os.environ['SERVER_NAME'])

    response = self.testapp.get('/register')
    assert len(response.forms) == 1
    response.form.set('form01', 'Student1')
    response = response.form.submit()
    assert 'Thank you for registering for' in response.body
    self.assertEqual(response.status_int, 200)

    response = self.testapp.get('/announcements')
    assert 'Example Announcement' in response.body
    self.assertEqual(response.status_int, 200)

    response = self.testapp.get('/course')
    assert 'Google Search makes it amazingly easy to find information' in response.body
    self.assertEqual(response.status_int, 200)

    response = self.testapp.get('/forum')
    assert 'forum_embed' in response.body
    self.assertEqual(response.status_int, 200)

    response = self.testapp.get('/student/home')
    assert 'Course progress related information' in response.body
    self.assertEqual(response.status_int, 200)

    # Test assessment pages
    response = self.testapp.get('/assessment?name=Pre')
    assert '/assets/js/assessment-Pre.js' in response.body
    self.assertEqual(response.status_int, 200)

    response = self.testapp.get('/assessment?name=Mid')
    assert '/assets/js/assessment-Mid.js' in response.body
    self.assertEqual(response.status_int, 200)

    response = self.testapp.get('/assessment?name=Fin')
    assert '/assets/js/assessment-Fin.js' in response.body
    self.assertEqual(response.status_int, 200)

