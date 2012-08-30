evilbrainjono.net
=================

My blog code, for evilbrainjono.net. On the web since 2004!

Dependencies: Python, MySQL, SQLObject

Expects to find a file called blog_config.py defining the following constants (not in version control because it contains private credentials!)

python model.py to create the database tables.

DB_URL: url to connect to MySQL database
ADMIN_USERNAME, ADMIN_PASSWORD: set your own login credentials
TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET: for the feature that auto-tweets links of new blog posts

Main page is showblog.py. I set up my Lighttpd server to rewrite http://evilbrainjono.net to http://evilbrainjono.net/showblog.py.

Publishes an RSS feed of articles to jono.rss and a feed of comments to comments.rss.