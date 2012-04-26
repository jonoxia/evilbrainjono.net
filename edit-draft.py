#!/usr/bin/python

BASE_PATH = "/var/www/images"

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

title = q.getfirst("title", "")
tags = q.getfirst("tags", "")
if title != "":
  draft.title = title
if tags != "":
  make_tags_for_entry(draft, tags)

if q.getfirst("publish", "") == "true":
  draft.public = True
  link = "http://evilbrainjono.net/blog#%d" % draft.id
  update_rss( draft.title, draft.words, link, RSS_FILE )

print "Content-type: text/html"
print

if draft.public:
  print "<p>Published!!</p>"
else:
  print render_template_file("publish_form.html", {})

print "<h2>%s</h2>" % draft.title
print draft.words
