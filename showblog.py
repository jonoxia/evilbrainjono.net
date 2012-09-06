#!/usr/bin/python
import cgi
import cgitb
cgitb.enable()

from model import *
from common_utils import *
import math
import datetime
from sqlobject import AND
from blog_config import ADMIN_USERNAME

POSTS_PER_PAGE = 20

def make_month_links():
    beginning_of_time = datetime.datetime( 2004, 7, 1 )
    endDate = datetime.datetime.now()
    startDate = datetime.datetime( endDate.year, endDate.month, 1 )
    
    archive_links = "<a name=\"#archivelinks\"><h4>Archive:</h4></a><ul>";
    while (endDate > beginning_of_time):
        numEntries = BlogEntry.select( AND( BlogEntry.q.date >= startDate, BlogEntry.q.date < endDate ) ).count()
        if (numEntries > 0):
            linkDestination = "/blog?year=%d&month=%d" % (startDate.year, startDate.month)
            archive_links += "<li><a href=\"%s\">%s (%d)</a></li>" % ( linkDestination, 
                                                                       startDate.strftime("%B %Y"), 
                                                                       numEntries )
        endDate = startDate
        month = startDate.month - 1
        year = startDate.year
        if (month < 1):
            month = 12
            year = startDate.year - 1
        startDate = datetime.datetime(year, month, 1)
    archive_links += "</ul>"
    return archive_links


def make_tag_links():
    tags = BlogTag.select(orderBy="name")
    tag_links = ""
    tag_links += "<h4>Tags:</h4> <ul><li><a href=\"/blog\">Latest</a></li>"
    for tag in tags:
        tag_links += "<li><a href=\"/blog?tag=%s\">" % tag.name
        number = EntryToTagLink.selectBy(tag = tag.id).count()
        # When showing tag name as link, replace underscores with spaces.
        tag_name = tag.name.replace("_", " ")
        linktext = tag_name + " (%d)" % number
        tag_links += linktext 
        tag_links += "</a></li>"
    tag_links += "</ul>"
    return tag_links

def make_entry_action_links(username, entry):
    linkHtml = ""
    if username == 'Jono':
        linkHtml += " <a href=\"blog/new?type=editentry&editid=%d\">Edit this Entry</a>\n" % entry.id

    if not username:
        linkHtml += "<a href=\"blog/login\">Register to leave comments</a>\n"


    return linkHtml

def make_action_links(username, q):
    action_links = ""
    if not username:
        action_links += "<li><a href=\"/blog/login\">Login</a></li>"
    else:
        # TODO logout link never actually worked!  Add that feature.
        action_links += "<li><a href=\"/blog/login\">Logout</a></li>"

    if username == ADMIN_USERNAME:
        action_links +=  "<li>Welcome back, Jono. <a href=\"blog/new?type=entry\">New entry</a> | <a href=\"/pic-uploader.html\">Pic Upload</a> | <a href=\"\">Drafts</a></li>"
    elif username:
        action_links += "<li>Hi %s!</li>" % username

    return action_links

def make_entry_tags_links(entry):
    tagsHtml = ""
    rows = EntryToTagLink.selectBy(entry = entry.id)
    tags = []
    # TODO this would be easier if I used sqlobject relatedJoin.
    for row in rows:
        blogTags = BlogTag.selectBy(id = row.tag)
        if blogTags.count() > 0:
            tags.append( blogTags[0] )
            
    if len(tags) > 0:
        tagsHtml += "Tagged: "
    for tag in tags:
        linkText = "<a href=\"/blog?tag=%s\">" % tag.name
        tagsHtml += linkText + tag.name + "</a> "
    return tagsHtml


def renderMainBlogPage():
    q = cgi.FieldStorage()

    tagName = None
    month = 0
    year = 0
    permalink = 0
    showcomments = False
    username = None
    pageContentLinks = ""

    if q.has_key("tag"):
        tagName = q["tag"].value

    if q.has_key("month"):
        month = int(q["month"].value)

    if q.has_key("year"):
        year = int(q["year"].value)

    if q.has_key("permalink"):
        permalink = q["permalink"].value

    if q.has_key("showcomments"):
        showcomments = q["showcomments"].value

    cookie = getCookie()
    if cookie.has_key("blogin"):
        username = cookie["blogin"].value
    else:
        username = None

    substitution_dict = {"title": "Evil Brain Jono's Natural Log"}

    #Do the query to get all the blog entries.  Sort newest first; show POSTS_PER_PAGE
    #at a time; if the params say this is an archive page, go back that many
    #using OFFSET; if params say this is a permalink, just get that one entry...

    #and if params say this is a category selection, get all entries fitting that
    #category.
    entries = []
    if permalink != 0:
        entries = BlogEntry.selectBy(public=True, id=permalink)
        pageContentLinks = ""
    elif tagName:
        tagObj = BlogTag.selectBy(name = tagName)[0]
        # TODO this part here would be easier if I had used sqlobject's RelatedJoin
        rows = EntryToTagLink.selectBy(tag = tagObj.id)
        entries = []
        for row in rows:
            someEntries = BlogEntry.selectBy(public=True, id=row.entry)
            if someEntries.count() > 0:
                entries.append( someEntries[0] )
        pageContentLinks = "<h4>Articles tagged with %s:</h4><ul>" % tagName
    elif month > 0 and year > 0:
        endmonth = month + 1
        if endmonth > 12:
            endmonth = 1
            endyear = year + 1
        else:
            endyear = year
        startDate = datetime.datetime( year, month, 1)
        endDate = datetime.datetime( endyear, endmonth, 1)
        entries = BlogEntry.select( AND( BlogEntry.q.date >= startDate, BlogEntry.q.date < endDate,
                                         BlogEntry.q.public == True ) )
        pageContentLinks = "<h4>Articles from %s:</h4><ul>" % startDate.strftime("%B %Y")
    else:
        entries = BlogEntry.select(BlogEntry.q.public == True, orderBy = "-date")[0:POSTS_PER_PAGE]
        pageContentLinks = "<h4>Recent Articles:</h4><ul>"

   
    content = ""
    for entry in entries:
        # Prepare comment area. It should default shown if we got here by permalink or
        # URL fragment anchor, otherwise default hidden.
        if permalink != 0 or showcomments == "true":
            defaultCommentsShown = True
        else:
            defaultCommentsShown = False
        commentsHtml = show_comments_for_entry(entry.id, defaultCommentsShown, q)
        numComments = BlogComment.selectBy(original_post = entry.id).count()
        if defaultCommentsShown:
            featureHtml = "<a class=\"comment-link\">Hide Comments</a> | "
        else:
            featureHtml = "<a class=\"comment-link\">%d comments</a> | " % numComments

        tagsHtml = make_entry_tags_links(entry)
        featureHtml += make_entry_action_links(username, entry)

        # Is this a long entry, i.e. there's below-the-fold-content?
        words = entry.words
        belowTheFold = ""
        if (entry.more_words != None) and (entry.more_words != ""):
            if (permalink != 0):
                # If we're looking at a permalink i.e. single-page view, just show all contents:
                words += entry.more_words
            else:
                # Otherwise hide them below a "read more" link:
                belowTheFold = render_template_file( "more_words.html", { "morewords": entry.more_words })
        entryHtml = render_template_file( "blog_entry.html", { "id": entry.id,
                                                               "title": entry.title,
                                                               "date": entry.date.strftime("%a, %d %b %Y %H:%M") ,
                                                               "words": words,
                                                               "morewords": belowTheFold,
                                                               "commentarea": commentsHtml,
                                                               "features": featureHtml,
                                                               "tags": tagsHtml})
        if (pageContentLinks != ""):
            pageContentLinks += "<li><a href=\"#%d\">%s</a></li>" % (entry.id, entry.title)
        content += entryHtml

    if (pageContentLinks != ""):
        pageContentLinks += "</ul>"

    substitution_dict["contents"] = content
    substitution_dict["navigation"] = ""
    substitution_dict["actionlinks"] = make_action_links(username, q)
    substitution_dict["categorylinks"] = pageContentLinks + make_tag_links()
    substitution_dict["archivelinks"] = make_month_links()
    substitution_dict["twitterlinks"] = links_from_rss_feed(TWITTER_FEED)
    substitution_dict["jonoscriptlinks"] = links_from_rss_feed(JONOSCRIPT_FEED)
    print render_template_file( "blog.html", substitution_dict )


if __name__ == "__main__":
    renderMainBlogPage()
