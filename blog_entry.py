#!/usr/bin/python
import re
import cgi
import cgitb
import datetime
from common_utils import *
from model import *

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
    if (type == "entry" or type== "editentry") and username == "Jono":
        extrasHtml += render_template_file( "more_message.html", {"more_words": moreWords,
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
                                                          "tagpics": ""})
    return entryHtml

def add_submission(q, username, type):
    words = q.getfirst("message", "")
    more_words = q.getfirst("more_message", "")
    title = q.getfirst("title", "")
    public = q.getfirst("public", "")
    doRss = q.getfirst("dorss", "")

    if username == "Jono" and type == "entry":
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

        link = "http://evilbrainjono.net/blog#%d" % newEntry.id

        if doRss == "yes":
            if len(more_words) > 0:
                message = "\n\n This post was really long, so I snipped it.  Read the rest at http://evilbrainjono.net."
            else:
                message = "\n\n<a href=\"http://www.evilbrainjono.net/blog/new?type=comment&original=%d#form\">Leave a comment</a>" % newEntry.id
            update_rss( title, words + message, link, RSS_FILE )

    else:
        # Can't happen?
        pass

def commit_edit(q, username, editid):
    # TODO allow this to set/clear tags, too
    if username == "Jono":
        theEntry = get_old_entry(editid)
        theEntry.words = html_clean(q.getfirst("message", ""))
        theEntry.title = q.getfirst("title", "")
        theEntry.more_words = html_clean(q.getfirst("more_message", ""))
        public = q.getfirst("public", "")
        theEntry.public = (public == "yes")

def printBlogEntryForm():
    q = cgi.FieldStorage()

    cookie = getCookie()
    if cookie.has_key("blogin"):
        username = cookie["blogin"].value
    else:
        username = None

    if username != "Jono":
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
