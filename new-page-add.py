#!/usr/local/bin/python

from model import ComicPage, CustomPanel, BlogEntry
from common_utils import update_rss
import datetime

# Config: Edit this stuff.  TODO: Replace with web form.
TITLE = "Monday"
IMG_FILE_NAME = "chapter1/monday_final"
SUFFIX = ".jpg"

# Determine sequence number for comic
lastPage = ComicPage.select(orderBy = "-sequence")[0]
seq = lastPage.sequence + 1
print "Adding comic number %d." % seq

# Enter comic into database.
ComicPage( sequence = seq,
      title = TITLE,
      internalDate = datetime.date( 2018, 10, 25 ),
      fullText = """
todo
""",
      customHtml = "<img src=\"/images/yuki/chapter1/monday_final.jpg\" width=\"1155\" height=\"1452\"/>",
      baseImageFile = IMG_FILE_NAME,
      suffix = SUFFIX
)

# Put first panel into RSS feed.
rssLink = "http://evilbrainjono.net/yuki/%d" % seq
RSSFILE = "yuki.rss"
FIRST_PANEL = "http://www.evilbrainjono.net/images/yuki/%s_001%s" % (IMG_FILE_NAME, SUFFIX)
description = "&lt;img src=\"%s\" border\"2\"&gt;" % FIRST_PANEL
update_rss("Yuki Hoshigawa #%d: %s" % (seq, TITLE), description, rssLink, RSSFILE, False)

# Make a non-commentable linking post.
BlogEntry( date = datetime.datetime.now(),
           title = TITLE,
           public = True,
           comments_disabled = True,
           words = "New comic posted: <a href=\"%s\">%s</a>" % (rssLink, TITLE)
)
