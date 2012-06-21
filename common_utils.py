#!/usr/bin/python

import os
import re
import sys
import model
import datetime
import string
import base64
import feedparser
from urllib import urlencode
from Cookie import SimpleCookie

RSS_URL = "/jono.rss"
RSS_FILE = "/var/www/jono.rss"
RSS_COMMENTS_URL = "/comments.rss"
RSS_COMMENTS_FILE = "/var/www/comments.rss"
LOGIN_PAGE_URL = "/blog/login"
BASE_BLOG_URL = "http://evilbrainjono.net/blog"
CSS_URL = "/jono.css"
TEMPLATE_DIR = "/var/www/templates"

TWITTER_FEED = "http://twitter.com/statuses/user_timeline/164093116.rss"
JONOSCRIPT_FEED = "http://jonoscript.wordpress.com/feed/"

# Error messages:
NEED_FIELD_ERR = "You left a required field blank."
NO_SUCH_USER_ERR = "There is no user by that name."
WRONG_PASSWORD_ERR = "Password is in the wrong!"


def getCookie( initialvalues = {} ):
    # TODO This is duplicated in leave-comic-comment.py getCookie(); delete that one.
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
    # TODO This is duplicated in leave-comic-comment.py; delete that one.
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

def render_comment_entry_form( id, form ):
    # TODO this overlaps a lot with printCommentForm in comicread.py.
    # Let's try to merge them.
    cookie = getCookie()
    welcome = ""
    errorMsg = form.getfirst("errorMsg", "")
    defaultTitle = form.getfirst("title", "")
    defaultText = form.getfirst("message", "")
    defaultUsername = form.getfirst("username", "")
    
    if cookie.has_key("blogin"):
        # You are logged in.
        welcome = "Hi, %s! " % cookie["blogin"].value
        loginFields = ""
    else:
        # Not logged in.
        welcome = ""
        loginFields = render_template_file("new_comment_identity_fields.html",
                                           {"defaultUsername": defaultUsername})

    # Figure out returnUrl from form stuff
    returnArgs = {"showcomments": "true"}
    for key in ["tag", "month", "year", "permalink"]:
        if form.has_key(key):
            returnArgs[key] = form[key].value
    returnUrl = "/blog?%s#%dc" %  (urlencode(returnArgs), id)

    return render_template_file("new_comment_form.html", {"welcome": welcome,
                                                          "errorMsg" : errorMsg,
                                                          "postId": str(id),
                                                          "returnUrl": base64.b64encode(returnUrl),
                                                          "defaultTitle": defaultTitle,
                                                          "defaultText": defaultText,
                                                          "loginFields": loginFields} )

def show_comments_for_entry(id, form):
    posts = model.BlogEntry.selectBy(id = id)
    post = posts[0]
    if post.comments_disabled:
        return "<i>Comments Disabled</i>"

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
    else:
        commentHtml = "No Comments Yet"

    entryFormHtml = render_comment_entry_form(id, form)

    return render_template_file("comment_area.html", {"id":id,
                                                      "comments": commentHtml,
                                                      "new_comment_entry": entryFormHtml
                                                      })


def clean_commenter_html(text):
    text = re.sub(r"<(/?[^bi/].*?)>", r"&lt;\g<1>!&lt;", text)
    regexp = re.sub(r"(http://[\w\./%=&\?\-#]+)\b", 
                    r'<a href="\g<1>">\g<1></a>', 
                    text)
    
    numBoldStarts = len(re.findall("<b>", text)) - len(re.findall("</b>", text))
    numItalicStarts = len(re.findall("<b>", text)) - len(re.findall("</b>", text))

    while numBoldStarts > 0:
        text = text + "</b>"
        numBoldStarts -= 1
    while numItalicStarts > 0:
        text = text + "</i>"
        numItalicStarts -= 1
    return text

def html_clean(text):
    text = re.sub( r"\r?\n\r?\n", r"</p><p>", text)
    # TODO The following hack is supposed to replace " with &quot; except
    # inside html tags, but is known to interact weirdly with my
    # relative/absolute link handling code to sometimes break external links
    # that come after quotes in the input.
    #text = re.sub(r'<(.*?)"(.*?)"(.*?)>',
    #              r"<\1QUOT_INSIDE_TAG_HAXXOR\2QUOT_INSIDE_TAG_HAXXOR\3>", 
    #              text)
    #text = re.sub(r'"', r'&quot;', text)
    #text = re.sub(r'QUOT_INSIDE_TAG_HAXXOR', r'"', text)
    return text


def get_current_arpadate():
    date = datetime.datetime.now()
    # Must produce time in a string like this:
    #  <pubDate>Sun, 4 Jan 2009 03:00:00 GMT</pubDate>
    # TODO account for daylight savings time (PDT instead of PST).
    return date.strftime("%a, %d %b %Y %H:%M:%S GMT") 


def update_rss(title, description, link, rssFile, escapeContents = True):
    # TODO note this function depends on having the rss file skeleton in place already -- it can't
    # regenerate it from scratch.  That seems like a poor choice.
    title = rssclean(title)
    arpadate = get_current_arpadate()

    if escapeContents:
        description = "<![CDATA[%s]]>" % rssclean(description)
    
    xml = """
<item><title>%s</title>
<description>%s</description>
<link>%s</link>
<pubDate>%s</pubDate></item>""" % (title, description, link, arpadate)
    infile = open(rssFile, "r")
    outputFeed = ""
    numItems = 0
    for line in infile.readlines():
        if "<lastBuildDate>" in line:
            outputFeed += "      <lastBuildDate>%s</lastBuildDate>\n" % arpadate
        else:
            outputFeed += line
        if "</webMaster>" in line:
            outputFeed += xml
        if "</item>" in line:
            numItems += 1
            if numItems == 12:
                outputFeed += "\n</channel></rss>\n"
                break
    infile.close()
    outfile = open(rssFile, "w")
    outfile.write(outputFeed)
    outfile.close()

def rssclean(input):
    # TODO try keeping links intact in RSS, actually?
    urlprefix = "http://evilbrainjono.net/"
    # replace external links with urls
    regexp = re.compile("""<(a href|img src)="(http:.+?)">""")
    input = regexp.sub("(\g<2>) ", input)
    # replace internal links with absolute urls
    regexp = re.compile("""<(a href|img src)="(.+?)">""")
    input = regexp.sub("(" + urlprefix + "\g<2>) ", input)
    # replce literal quotes with &quot.
    input = re.compile('"').sub("&quot;", input)
    # Strip out all remaining html tags, replace with spaces.
    input = re.compile("<[^>]+?>").sub(" ", input) 
    return input

def links_from_rss_feed(url):
    try:
        f = feedparser.parse(url)
        rss_links = "<h4><a href=\"%s\">%s</a></h4><ul>" % (f.feed.link, f.feed.title)
    except:
        return ""
    entries = [e for e in f.entries if not ("evilbrainjono.net" in e.title)]
    for entry in entries[0:5]:
        if "twitter.com" in url:
            rss_links += "<li>%s</li>" % re.sub(r'^jonoxia: ', "", entry.title)
        else:
            rss_links += "<li><a href=\"%s\">%s</a></li>" % (entry.link, entry.title)
    rss_links += "</ul>"
    return rss_links.encode("utf-8")

def make_tags_for_entry(newEntry, tags):
    tagNames = tags.split(",")
    for tagName in tagNames:
        tagName = tagName.strip(" ")
        blogTag = model.BlogTag.selectBy( name = tagName )
        if blogTag.count() == 0:
            blogTag = model.BlogTag( name = tagName )
        else:
            blogTag = blogTag[0]
        model.EntryToTagLink(entry = newEntry.id, tag = blogTag.id)
