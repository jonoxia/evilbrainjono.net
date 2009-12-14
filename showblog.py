#!/usr/bin/python
import cgi
import cgitb
cgitb.enable()

from model import *
from common_utils import *
import math
import datetime
from sqlobject import AND

POSTS_PER_PAGE = 12

def make_month_links(showcomments):
    beginning_of_time = datetime.datetime( 2004, 7, 1 )
    endDate = datetime.datetime.now()
    startDate = datetime.datetime( endDate.year, endDate.month, 1 )
    
    archive_links = "<a name=\"#archivelinks\"><h4>Archive:</h4></a><ul>";
    while (endDate > beginning_of_time):
        numEntries = BlogEntry.select( AND( BlogEntry.q.date >= startDate, BlogEntry.q.date < endDate ) ).count()
        if (numEntries > 0):
            linkDestination = "/blog?showcomments=%s&year=%d&month=%d" % (showcomments, startDate.year, startDate.month)
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


def make_tag_links(showcomments):
    tags = BlogTag.select(orderBy="name")
    tag_links = ""
    tag_links += "<h4>Tags:</h4> <ul><li><a href=\"/blog?showcomments=%s\">Latest</a></li>" % showcomments
    for tag in tags:
        tag_links += "<li><a href=\"/blog?tag=%s&showcomments=%s\">" % (tag.name, showcomments)
        number = EntryToTagLink.selectBy(tag = tag.id).count()
        linktext = tag.name + " (%d)" % number
        tag_links += linktext 
        tag_links += "</a></li>"
    tag_links += "</ul>"
    return tag_links

def make_entry_action_links(username, entry):
    linkHtml = ""
    if username:
        linkHtml += "<a href=\"blog/new?type=comment&original=%d#form\">Leave a Comment</a>\n" % entry.id
        if username == 'Jono':
            linkHtml += " | <a href=\"blog/new?type=editentry&editid=%d\">Edit this Entry</a>\n" % entry.id
    else:
        linkHtml += "<a href=\"/blog/login\">Login to Leave a Comment</a>\n"
    return linkHtml

def make_action_links(username, showcomments):
    action_links = ""
    if  showcomments == 'false':
        action_links += "<li><a href=\"/blog?showcomments=true\">Show Comments</a></li>"
    else:
        action_links += "<li><a href=\"/blog?showcomments=false\">Hide Comments</a></li>"
    if not username:
        action_links += "<li><a href=\"/blog/login\">Login</a></li>"
    else:
        # TODO logout link never actually worked!  Add that feature.
        action_links += "<li><a href=\"/blog/login\">Logout</a></li>"

    if username == "Jono":
        action_links +=  "<li>Welcome back, Jono.  I have guarded your blog vigilantly while you were away.  Want to <a href=\"blog/new?type=entry\">make a new entry</a>?</li>"
    elif username:
        action_links += "<li>Hi %s!  How you doin?  Glad you could make it.  Jono would be right happy if you left him some comments.</li>" % username

    return action_links

def make_entry_tags_links(entry, showcomments):
    tagPicsHtml = ""
    rows = EntryToTagLink.selectBy(entry = entry.id)
    tags = []
    # TODO this would be easier if I used sqlobject relatedJoin.
    for row in rows:
        blogTags = BlogTag.selectBy(id = row.tag)
        if blogTags.count() > 0:
            tags.append( blogTags[0] )
            
    if len(tags) > 0:
        tagPicsHtml += "Tagged: "
    for tag in tags:
        linkText = "<a href=\"/blog?tag=%s&showcomments=%s\">" % (tag.name, showcomments)
        if tag.name in ["rpg", "politics", "music"]:    # add supported categories here
            imgSrc = "/images/tags/%s.jpg" % tag.name
            imgText = linkText + "<img src=\"%s\"></a>" % imgSrc
            tagPicsHtml += imgText
        else:
            tagPicsHtml += linkText + tag.name + "</a> "
    return tagPicsHtml


def renderMainBlogPage():
    q = cgi.FieldStorage()

    showcomments = 'false'
    tagName = None
    month = 0
    year = 0
    permalink = 0
    username = None
    pageContentLinks = ""

    # TODO: maybe put showcomments in a cookie so we don't have to pass it around in the url all the time?
    if q.has_key("showcomments"):
        showcomments = q["showcomments"].value

    if q.has_key("tag"):
        tagName = q["tag"].value

    if q.has_key("month"):
        month = int(q["month"].value)

    if q.has_key("year"):
        year = int(q["year"].value)

    if q.has_key("permalink"):
        permalink = q["permalink"].value

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
        entries = BlogEntry.select( AND( BlogEntry.q.date >= startDate, BlogEntry.q.date < endDate ) )
        pageContentLinks = "<h4>Articles from %s:</h4><ul>" % startDate.strftime("%B %Y")
    else:
        entries = BlogEntry.select(BlogEntry.q.public == True, orderBy = "-date")[0:POSTS_PER_PAGE]
        pageContentLinks = "<h4>Recent Articles:</h4><ul>"

   
    content = ""
    for entry in entries:
        if (showcomments == "true"):
            commentsHtml = show_comments_for_entry(entry.id)
            featureHtml = ""
        else:
            commentsHtml = ""
            numComments = BlogComment.selectBy(original_post = entry.id).count()
            featureHtml = "<a href=\"/blog?showcomments=true#%dc\">%d comments</a> | " % (entry.id, numComments)

        tagPicsHtml = make_entry_tags_links(entry, showcomments)
        featureHtml += make_entry_action_links(username, entry)
        entryHtml = render_template_file( "blog_entry.html", { "id": entry.id,
                                                               "title": entry.title,
                                                               "date": entry.date.strftime("%a, %d %b %Y %H:%M") ,
                                                               "words": entry.words,
                                                               "commentarea": commentsHtml,
                                                               "features": featureHtml,
                                                               "tagpics": tagPicsHtml})
        if (pageContentLinks != ""):
            pageContentLinks += "<li><a href=\"#%d\">%s</a></li>" % (entry.id, entry.title)
        content += entryHtml

    if (pageContentLinks != ""):
        pageContentLinks += "</ul>"

    substitution_dict["contents"] = content
    substitution_dict["navigation"] = ""
    substitution_dict["actionlinks"] = make_action_links(username, showcomments)
    substitution_dict["categorylinks"] = pageContentLinks + make_tag_links(showcomments)
    substitution_dict["archivelinks"] = make_month_links(showcomments)
    print render_template_file( "blog.html", substitution_dict )


if __name__ == "__main__":
    renderMainBlogPage()
