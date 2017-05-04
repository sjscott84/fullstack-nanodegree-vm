# "Database code" for the DB Forum.

import datetime
import psycopg2
import bleach

POSTS = [("This is the first post.", datetime.datetime.now())]

def get_posts():
  """Return all posts from the 'database', most recent first."""
  #return reversed(POSTS)
  pg = psycopg2.connect("dbname=forum")
  c = pg.cursor()
  c.execute("select content, time from posts order by time desc")
  posts = ({str(row[0]), str(row[1])}
  			for row in c.fetchall())
  pg.close()
  return posts



def add_post(content):
  """Add a post to the 'database' with the current timestamp."""
  pg = psycopg2.connect("dbname=forum")
  c = pg.cursor()
  c.execute("insert into posts (content) values (%s)", (bleach.clean(content),))
  pg.commit()
  pg.close()


