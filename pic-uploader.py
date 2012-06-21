#!/usr/bin/python

BASE_PATH = "/var/www/images"

import os
import base64
import cgi
import cgitb
import time
from model import *
from common_utils import *

def writeFile(path, data):
  file = open( path, "wb")
  data = data.split(",")[1] # everything after comma
  # Get an "incorrect padding" error on trying to decode.
  # Correct b64 padding:
  while len(data) % 4 != 0:
    data = data + "="
  file.write(base64.b64decode(data))
  file.close()

cgitb.enable()
q = cgi.FieldStorage()

data = q.getfirst("img", "")
directory = q.getfirst("directory", "")
filename = q.getfirst("filename", "0")
width = q.getfirst("width", "0")
height = q.getfirst("height", "0")
caption = q.getfirst("caption", "")
altText = q.getfirst("altText", "")

dirPath = os.path.join(BASE_PATH, directory)
if not os.path.exists(dirPath):
  os.mkdir(dirPath)
filename = "%s.jpg" % filename
filePath = os.path.join(dirPath, filename)
url = "/images/%s/%s" % (directory, filename)

writeFile(filePath, data)

html = render_template_file("pic.html", {"url": url,
                                   "alt": altText,
                                   "height": height,
                                   "width": width,
                                   "caption": caption})

# create a preview-posts table in database; on each upload,
# append the html oputput of the templating operation into that preview
# use directory as name of new preview; if matching name exists append to it, if not
# create it.
draft = BlogEntry.selectBy( title = directory, public = False )
if draft.count() == 0:
  kwargs = {"date": datetime.datetime.now(),
            "title": directory,
            "public": False,
            "words": "This is a photo gallery.",
            "more_words": html}
  draft = BlogEntry(**kwargs)
else:
  draft = draft[0]
  draft.more_words = draft.more_words + html
  

# TODO create a page where the preview can be viewed and edited before publishing

print "Content-type: text/html"
print
print "Saved post as %d" % draft.id
