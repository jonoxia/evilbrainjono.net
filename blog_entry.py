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
    if type == "editentry":
        oldEntry = get_old_entry(editid)
        default_text = oldEntry.words
        default_title = oldEntry.title
    dict = {"type": type,
            "editid": editid,
            "title": default_title,
            "text": default_text,
            "extras": ""}
    extrasHtml = ""
    # This part is only for when I'm making an entry, not for comments:
    if type == "entry" and username == "Jono":
        extrasHtml += render_template_file( "more_message.html", {} )
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
    if q.has_key("message"):
        words = q["message"].value
    else:
        words = ""
    if q.has_key("more_message"):
        more_words = q["more_message"].value
    else:
        more_words = ""
    if q.has_key("title"):
        title = q["title"].value
    else:
        title = ""

    if username == "Jono" and type == "entry":
        fullText = html_clean(words) + html_clean(more_words)
        kwargs = {"date": datetime.datetime.now(),
                  "title": title,
                  "public": True,
                  "words": fullText}
        newEntry = BlogEntry(**kwargs)
        if q.has_key("tags"):
            make_tags_for_entry(newEntry, q["tags"].value)

        link = "http://evilbrainjono.net/blog#%d" % newEntry.id
        if len(more_words) > 0:
            message = "\n\n This post was really long, so I snipped it.  Read the rest at http://evilbrainjono.net."
        else:
            message = "\n\n<a href=\"http://www.evilbrainjono.net/blog/new?type=comment&original=%d#form\">Leave a comment</a>" % newEntry.id

        update_rss( title, words + message, link, RSS_FILE )

    else:
        # Can't happen?
        pass

def commit_edit(q, username, editid):
    if username == "Jono":
        words = html_clean(q["message"].value)
        theEntry = get_old_entry(editid)
        theEntry.words = words

def do_upload(fileItem, username):
    dir = "expo2010" # TODO make this choice part of web interface
    if fileItem.filename and username == "Jono":
        name = os.path.basename(fileItem.filename)
        path = os.path.join("/var/www/images", dir)
        path = os.path.join(path, name)
        outfile = open(path, "wb")
        data = fileItem.file.read()
        outfile.write(data)
        outfile.close()
        return "<img src=\"/images/%s/%s\">" % (dir, name)
    else:
        if not fileItem.filename:
            return "Can't upload, file is null"
        if username != "Jono":
            return "Can't upload, invalid user"

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

    if q.has_key("upload") and q.has_key("file1"):
        dbug = q["file1"]
        newText = ""
        attrs = dir(dbug)
        for a in attrs:
            newText += "%s = %s; " % (a, getattr(dbug, a))
        #imgLink = do_upload(q["file1"], username)
        #newText = q.getfirst("text", "") + "\n\n" + imgLink
    else:
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
