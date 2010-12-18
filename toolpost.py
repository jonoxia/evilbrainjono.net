#!/usr/bin/python

# The script for making a blog post using remote tools - jetpack, ubiquity, bookmarklet, whatever
# No cookie needed, but have to set username and password fields correctly.

import cgi
import cgitb
import blog_entry

cgitb.enable()
q = cgi.FieldStorage()

username = q.getfirst("username", "")
password = q.getfirst("password", "")
# TODO don't hardcode these here, get from a config file or database:
if username == "Jono" and password == "!Mizuno!":
    blog_entry.add_submission(q, username, "entry")
    print "Content-type: text/html"
    print
    print "OK"
else:
    print "Content-type: text/html"
    print
    print "Password is in the wrong!"
