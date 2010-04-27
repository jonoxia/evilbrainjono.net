import re
import cgi
import cgitb
import datetime
from common_utils import *
from model import *

cgitb.enable()

def make_form(type, original, editid, username):
    default_text = ""
    default_title = ""
    if type == "editentry":
        oldEntry = get_old_entry(editid)
        default_text = oldEntry.words
        default_title = oldEntry.title
    dict = {"type": type,
            "original": original,
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

def add_submission(q, username, type, original):
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
            tagNames = q["tags"].value.split(",")
            for tagName in tagNames:
                tagName = tagName.strip(" ")
                blogTag = BlogTag.selectBy( name = tagName )
                if blogTag.count() == 0:
                    blogTag = BlogTag( name = tagName )
                else:
                    blogTag = blogTag[0]
                EntryToTagLink(entry = newEntry.id, tag = blogTag.id)

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


# TODO leaving comments is going to be handled by leave-blog-comment.py, so we can take out the
# comment-leaving options from this file.
def printBlogEntryForm():
    q = cgi.FieldStorage()

    cookie = getCookie()
    if cookie.has_key("blogin"):
        username = cookie["blogin"].value
    else:
        username = None

    if q.has_key("type"):
        type = q["type"].value
    else:
        type = None
    if q.has_key("original"):
        original = q["original"].value
    else:
        original = None
    if q.has_key("editid"):
        editid = q["editid"].value
    else:
        editid = None

    if not username:
        print_redirect(LOGIN_PAGE_URL)

    if q.has_key("submission"):
        if type == "editentry":
            commit_edit(q, username, editid)
        else:
            add_submission(q, username, type, original)
        print_redirect("/blog")

    if (type == "entry" or type == "editentry") and username != "Jono":
        print_redirect("/blog")

    contentHtml = ""
    if type == "comment":
        contentHtml += "<h2>" + username + " is adding a comment.  Below is the original blog entry.  Below that is the comment form.</h2>"
        contentHtml += print_original_entry(original)
    elif type == "editentry":
        contentHtml +=  "Jono is editing old entry id " + editid + " : "
    else:
        contentHtml += "Jono is making a new entry: "

    contentHtml += make_form(type, original, editid, username)
    
    print render_template_file("blog.html", {"title": "Jono's Natural Log -- Leave Comments",
                                             "contents": contentHtml,
                                             "navigation": "",
                                             "archivelinks": "",
                                             "actionlinks": "",
                                             "categorylinks": ""
                                             })


if __name__ == "__main__":
    printBlogEntryForm()
