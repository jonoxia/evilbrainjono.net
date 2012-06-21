#!/usr/bin/python

import os
import base64
import cgi
import cgitb
import time
from model import *
from common_utils import *

cgitb.enable()
q = cgi.FieldStorage()

draft = BlogEntry.select(BlogEntry.q.public == False, orderBy = "-date")[0]

editLink = "http://evilbrainjono.net/blog/new?type=editentry&editid=%d" % draft.id

print "Content-type: text/html"
print

print "<a href=\"%s\">Edit This Post</a><br/>" % editLink
print "<h2>%s</h2>" % draft.title
print draft.words
print draft.more_words
