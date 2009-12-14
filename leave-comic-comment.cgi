#!/usr/local/bin/python

import os
import cgi
import cgitb; cgitb.enable()
import sqlobject
import datetime
from urllib import urlencode
from Cookie import SimpleCookie


from model import ComicComment, User

"""
 Arguments should look like this:
 pageId   -> the number of the page being commented on
 title    -> the title of your comment
 message  -> the text of your comment
 username -> your username
 password -> your password
"""

NEED_FIELD_ERR = "You left a required field blank."
NO_SUCH_USER_ERR = "There is no user by that name."
WRONG_PASSWORD_ERR = "Password is in the wrong!"

COMIC_READER_URL = "/cgi-bin/yuki/comic-reader.cgi"

def returnWithError( form, errorMsg ):
    args = { "errorMsg": errorMsg }
    if form.has_key("pageSequence"):
	args["page"] = int(form["pageSequence"].value)
    anchor="comment_form"
    print "Location: %s?%s#%s" % ( COMIC_READER_URL, urlencode(args), anchor )
    print


def redirectToPage( form, cookie ):
    """
    Redirect you to whence you came...
    """
    print cookie
    returnWithError( form, "" )

def getCookie( initialvalues = {} ):
    """
    Return a SimpleCookie.  If some of the cookie values haven't
    been set, we'll plunk them into the cookie with the initialValues
    dict.
    """
    if os.environ.has_key('HTTP_COOKIE'):
        C = SimpleCookie(os.environ['HTTP_COOKIE'])
    else:
        C = SimpleCookie()
    for key in initialvalues.keys():
        if not C.has_key(key): C[key] = initialvalues[key]
    return C

def newCommentFromForm( form, cookie ):

    for requiredField in ["pageId", "message", "pageSequence"]:
	if not form.has_key( requiredField ):
	    returnWithError( form, NEED_FIELD_ERR )
	    return False

    if cookie.has_key( "blogin" ):
	username = cookie["blogin"].value
	alreadyLoggedIn = True
    else:
	alreadyLoggedIn = False
	if form.has_key( "username" ):
	    username = form["username"].value
	else:
	    returnWithError( form, NEED_FIELD_ERR )
	    return False

	if form.has_key( "password" ):
	    password = form["password"].value
	else:
	    returnWithError( form, NEED_FIELD_ERR )
	    return False
	
    if not form.has_key( "title" ):
	subject = ""
    else:
	subject = form["title"].value

    matchingUsers = User.selectBy( username = username )
    if matchingUsers.count() == 0:
	returnWithError( form, NO_SUCH_USER_ERR )
	return False

    user = matchingUsers[0]

    if not alreadyLoggedIn:
	if password == user.password:
	    # give me a login cookie then:
	    cookie["blogin"] = username
	else:
	    returnWithError( form, WRONG_PASSWORD_ERR )
	    return False

    newComment = ComicComment( pageRef = int( form["pageId"].value ),
			       commenter = username,
			       subject = subject,
			       words = form["message"].value )
    return cookie

if __name__ == "__main__":
    form = cgi.FieldStorage()
    cookie = getCookie()
    result = newCommentFromForm( form, cookie )
    if result:
	redirectToPage( form, result )
