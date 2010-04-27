#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()
import sys
import Cookie
from common_utils import *
from model import *

LOGIN_PAGE_URL = "/blog-cgi/login.py" # was /cgi-bin/blog/login.cgi
ALREADY_USER_ERR = """<h2>There is already a user called %s!</h2>
<p>Pick another name and try again.</p>"""
SHORT_PASSWD_ERR = """<h2>Passwords must be at least 5 characters.</h2>
<p>Pick a longer password and try again.</p>"""
PASSWD_MISMATCH_ERR = """<h2>The two password fields don't match.</h2>
<p>Try it again, and make sure to enter the same thing in both fields.</p>"""
PASSWD_WRONG_ERR = """<h2>Wrong Password for user %s!</h2>
<p>Try again.</p>"""
NO_USER_ERR = """<h2>There is no account called %s!</h2>
<p>Try again.</p>"""
NO_USERNAME_GIVEN_ERR = """<h2>You didn't supply a username.</h2>
<p>Try again.</p>"""
NO_PASSWD_GIVEN_ERR = """<h2>You didn't supply a password.</h2>
<p>Try again.</p>"""
NO_PASSWD2_GIVEN_ERR = """<h2>You didn't confirm the password.</h2>
<p>Try again.</p>"""
NO_CRUMPETS_ERR ="""<h2>You didn't type 'crumpets'.  Are you sure you're not a spambot?</h2>"""

# TODO implement open_id so people don't have to create an account.

def check_create_ok(q):
    if not q.has_key('username'):
        return NO_USERNAME_GIVEN_ERR
    username = q['username'].value
    if not q.has_key('password'):
        return NO_PASSWD_GIVEN_ERR
    password = q['password'].value
    if not q.has_key('password2'):
        return NO_PASSWD2_GIVEN_ERR
    password2 = q['password2'].value
    if q.has_key('email'):
        email = q['email'].value
    else:
        email = ""
    if not q.has_key('turing'):
        return NO_CRUMPETS_ERR
    if q['turing'].value != "crumpets":
        return NO_CRUMPETS_ERR

    matchingUsers = User.selectBy( username = username )
    if matchingUsers.count() != 0:
        return ALREADY_USER_ERR % username
    if len(password) < 5:
        return SHORT_PASSWD_ERR
    if password != password2:
        return PASSWD_MISMATCH_ERR
    newUser = User(username = username, password = password, email = email,
                   icon = "", link = "" )
    # TODO no way for user to set user icon or link back to their site...
    set_cookie(q)

def check_login_ok(q):
    username = q['username'].value
    password = q['password'].value
    matchingUsers = User.selectBy( username = username )
    if matchingUsers.count() == 0:
        return NO_USER_ERR % username
    if password != matchingUsers[0].password:
        return PASSWD_WRONG_ERR
    set_cookie(q)

def set_cookie(q):
    # TODO superseded by commonpants.py: print_redirect
    #Call this when login is successful.  Sets cookie with username
    #and redirects to blog.
    username = q["username"].value
    password = q["password"].value
    C = Cookie.SimpleCookie()
    C["blogin"] = username
    C["password"] = password # TODO how to set path, expiration?
    C["blogin"]["path"] = "/"
    C["password"]["path"] = "/"
    print "Status: 302" # temporary redirect
    print C
    # TODO this redirect loses showcomments setting
    print "Location: " + "/blog"
    print
    sys.exit(1)


# Main: 
q = cgi.FieldStorage()
error_message = ''

if q.has_key('submission'):
    if q['submission'].value == 'Create':
        error_message = check_create_ok(q)
    if q['submission'].value == 'Login':
        error_message = check_login_ok(q)

dict = {"title": "Jono's Natural Login",
        "navigation": "",
        "actionlinks": "",
        "categorylinks": "",
        "archivelinks": ""}

dict["contents"] = render_template_file( "login_form.html", {"error": error_message,
                                                             "action": "/blog/login"} )

print render_template_file("blog.html", dict )
