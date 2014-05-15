#!/usr/bin/python

# The script for making a blog post using remote tools - jetpack, ubiquity, bookmarklet, whatever
# No cookie needed, but have to set username and password fields correctly.

import cgi
import cgitb
import blog_entry
from blog_config import ADMIN_USERNAME, ADMIN_PASSWORD
from model import BlogEntry

cgitb.enable()
q = cgi.FieldStorage()

username = q.getfirst("username", "")
password = q.getfirst("password", "")

# TODO don't hardcode these here, get from a config file or database:
if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
    # If public is false,
    # then see if there's already an unpublished post with this title
    # and if so, append message to it!
    # this way I can toolpost several links with publish now unchecked
    # then go to preview.py for final edits, and publish from there.

    if q.getfirst("public", "") != "yes":
        # look for matching draft
        draft = BlogEntry.selectBy( title = q.getfirst("title", ""),
                                    public = False )
        if draft.count() == 0:
            # new draft
            blog_entry.add_submission(q, username, "entry")
        else:
            # append to existing draft
            draft = draft[0]
            draft.words = draft.words + "\n\n" + q.getfirst("message", "")

    else:
        # new public post
        blog_entry.add_submission(q, username, "entry")


    # ALSO TODO: if post is short enough and tweet is true, then
    # tweetthe whole post body instead of link to the post.
    print "Content-type: text/html"
    print
    print "OK"
else:
    print "Content-type: text/html"
    print
    print "Password is in the wrong!"
