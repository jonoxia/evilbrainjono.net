#!/usr/bin/python

import os
import re
import sys
import model
import string
from Cookie import SimpleCookie

RSS_URL = "/jono.rss"
RSS_FILE = "/var/www/jono.rss"
RSS_COMMENTS_URL = "/comments.rss"
RSS_COMMENTS_FILE = "/var/www/comments.rss"
LOGIN_PAGE_URL = "/blog/login"
BASE_BLOG_URL = "http://evilbrainjono.net/blog"
CSS_URL = "/jono.css"
TEMPLATE_DIR = "/var/www/templates"


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

def print_redirect(url, cookie=None):
    print "Status: 302" # temporary redirect
    if cookie:
        print cookie
    # TODO this redirect loses showcomments setting
    print "Location: " + url
    print
    sys.exit(1)

def render_template_file( filename, substitutionDict ):
    file = open( os.path.join( TEMPLATE_DIR, filename ), "r")
    template = string.Template(file.read())
    file.close()
    return template.substitute( substitutionDict )

def show_comments_for_entry(id):
    comments = model.BlogComment.select(model.BlogComment.q.original_post == id, orderBy = "date")
    numComments = comments.count()
    commentHtml = ""
    if numComments > 0:
        for comment in comments:
            commentAuthors = model.User.selectBy( username = comment.author)
            author = commentAuthors[0]
            dict = {"linktext": "",
                    "author": author.username,
                    "date": comment.date.strftime("%a, %d %b %Y %H:%M"),
                    "title": comment.title,
                    "words": comment.words,
                    "icon": "",
                    "endlink": "" }
            if author.link:
                dict["linktext"] = "<a href=\"%s\">" % author.link
                dict["endlink"] = "</a>"

            if author.icon:
                src = "/images/commenters/%s" % author.icon
                alt = comment.author + "'s pic"
                dict["icon"] = "<img src=\"%s\" class=\"commenter\" alt=\"%s\" width=\"100\" height=\"100\">" % (src, alt)


            commentHtml += render_template_file("blog_comment.html", dict)
        return render_template_file("comment_area.html", { "id": id, "comments": commentHtml})
    else:
        return render_template_file("comment_area.html", {"id":id, "comments": "No Comments Yet"})
