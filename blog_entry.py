#!/usr/bin/python
import re
import cgi
import cgitb
import datetime
from tweet import updateTwitterStatus
from common_utils import *
from model import *
from blog_config import ADMIN_USERNAME

cgitb.enable()

def make_form(type, editid, username, newText):
    default_text = newText
    default_title = ""
    moreWords = ""
    publicChecked = "checked"
    if type == "editentry":
        oldEntry = get_old_entry(editid)
        default_text = oldEntry.words
        default_title = oldEntry.title
        if not oldEntry.public:
            publicChecked = ""
        if oldEntry.more_words != None:
            moreWords = oldEntry.more_words
    dict = {"type": type,
            "editid": editid,
            "title": default_title,
            "text": default_text,
            "extras": ""}
    extrasHtml = ""
    # This part is only for when I'm making an entry, not for comments:
    if (type == "entry" or type== "editentry") and username == ADMIN_USERNAME:
        # Get list of tags for autocompletion:
        allTags = BlogTag.select()
        tagList = ",".join([tag.name for tag in allTags])
        # add the 'more words' area and the publishing checkboxes:
        extrasHtml += render_template_file( "more_message.html", {"more_words": moreWords,
                                                                  "tag_list": tagList,
                                                                  "public_checked": publicChecked} )
        dict["extras"] = extrasHtml
    return render_template_file ( "entry_form.html", dict )

def get_old_entry(id):
    return BlogEntry.selectBy(id = id)[0]

def print_original_entry(id):
    # Slight duplication of code here.
    entry = get_old_entry(id)
    commentsHtml = show_comments_for_entry(id)
    entryHtml = render_template_file( "blog_entry.html", { "id": entry.id,
                                                          "title": entry.title,
                                                          "date": entry.date.strftime("%a, %d %b %Y %H:%M") ,
                                                          "words": entry.words,
                                                          "commentarea": commentsHtml,
                                                          "features": "",
                                                          "tags": ""})
    return entryHtml


def publicize(q, entry):
    link = "http://evilbrainjono.net/blog#%d" % entry.id
    doRss = q.getfirst("dorss", "")
    tweet = q.getfirst("tweet", "")

    if doRss == "yes":
        if len(entry.more_words) > 0:
            message = "\n\n This post was really long, so I snipped it.  Read the rest at http://evilbrainjono.net."
        else:
            message = "\n\n<a href=\"http://www.evilbrainjono.net/blog/new?type=comment&original=%d#form\">Leave a comment</a>" % entry.id
        update_rss( entry.title, entry.words + message, link, RSS_FILE )
    if tweet == "yes":
        message = "New blog post: %s %s" % (entry.title, link)
        if len(message) <= 140:
            updateTwitterStatus(message)

def add_submission(q, username, type):
    words = q.getfirst("message", "")
    more_words = q.getfirst("more_message", "")
    title = q.getfirst("title", "")
    public = q.getfirst("public", "")

    if username == ADMIN_USERNAME and type == "entry":
        words = html_clean(words)
        if more_words != "":
            more_words = html_clean(more_words)
        kwargs = {"date": datetime.datetime.now(),
                  "title": title,
                  "public": (public == "yes"),
                  "words": words,
                  "more_words": more_words}
        newEntry = BlogEntry(**kwargs)
        if q.has_key("tags"):
            make_tags_for_entry(newEntry, q["tags"].value)

        # Let RSS and twitter know about the new post:
        if public == "yes":
            publicize(q, newEntry)

    else:
        # Can't happen?
        pass

def commit_edit(q, username, editid):
    # TODO allow this to set/clear tags, too
    if username == ADMIN_USERNAME:
        theEntry = get_old_entry(editid)
        theEntry.words = html_clean(q.getfirst("message", ""))
        theEntry.title = q.getfirst("title", "")
        theEntry.more_words = html_clean(q.getfirst("more_message", ""))
        public = q.getfirst("public", "")

        # If we take a private post and turn it public, announce it! (if i don't want this, uncheck the rss/twitter boxes)
        if (theEntry.public == False) and (public == "yes"):
            publicize(q, theEntry)
        theEntry.public = (public == "yes")

def printBlogEntryForm():
    q = cgi.FieldStorage()

    cookie = getCookie()
    if cookie.has_key("blogin"):
        username = cookie["blogin"].value
    else:
        username = None

    # Only admin can make posts!
    if username != ADMIN_USERNAME:
        print_redirect("/blog")

    type = q.getfirst("type", "")
    editid = q.getfirst("editid", "")

    if q.has_key("submission"):
        if type == "editentry":
            commit_edit(q, username, editid)
        else:
            add_submission(q, username, type)
        print_redirect("/blog")

    newText = ""
    contentHtml = ""
    if type == "editentry":
        contentHtml +=  "Jono is editing old entry id " + editid + " : "
    else:
        contentHtml += "Jono is making a new entry: "

    contentHtml += make_form(type, editid, username, newText)
    
    print render_template_file("blog.html", {"title": "Jono's Natural Log -- Make Entry",
                                             "contents": contentHtml,
                                             "navigation": "",
                                             "archivelinks": "",
                                             "actionlinks": "",
                                             "categorylinks": "",
                                             "jonoscriptlinks": "",
                                             "twitterlinks": ""
                                             })


if __name__ == "__main__":
    printBlogEntryForm()
