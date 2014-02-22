#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Live Band Photos Mobile - Main page')

class BandHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Live Band Photos Mobile - band view')

class VenueHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Live Band Photos Mobile - venue view')

app = webapp2.WSGIApplication([
    ('/venue/[\w\-]*/', VenueHandler),
    ('/band/[\w\-]*/', BandHandler),
    ('/', MainHandler)
], debug=True)
