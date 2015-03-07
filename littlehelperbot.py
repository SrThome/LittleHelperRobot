#!/usr/bin/python2.7 -u

import bs4
import praw
import re
import requests

from littlehelper_config import *


def start():
        reddit = praw.Reddit(user_agent = USER_AGENT)
        reddit.login(REDDIT_USERNAME, REDDIT_PASS)
        comment_stream = praw.helpers.comment_stream(reddit, "all", verbosity=1)
        n = 0
        for comment in comment_stream:
                n += 1
                if not n % 1000:
                        print n

                if comment.body.lower().find("m.wikipedia.org") != -1 or \
                   comment.body.lower().find("amazon.com/gp/aw/d") != -1 or \
                   comment.body.lower().find("m.facebook.com") != -1:
                        got_one(comment)



def demobile(expression, substitute, href, text):
	new_href = re.sub(expression, substitute, href)
	new_text = re.sub(expression, substitute, text)

	new_href = re.sub("\(", "\\\(", new_href)
	new_href = re.sub("\)", "\\\)", new_href)

	new_text = re.sub("\[", "\\\[", new_text)
	new_text = re.sub("\]", "\\\]", new_text)

	return (new_text, new_href)


def got_one(comment):

	print "==============="

	print comment.permalink.encode('utf-8')

	# body_html is escaped html. Unescape it here.
	soup = bs4.BeautifulSoup(comment.body_html)
	unescaped = soup.get_text()

	print unescaped.encode('utf-8')

	# And now actually parse it.
	soup = bs4.BeautifulSoup(unescaped)

	links = []
	for link in soup.find_all('a'):
		href = link.get('href')
		text = link.text
		if href.find("m.wikipedia.org") != -1:
			new_text, new_href = demobile("m.wikipedia.org", "wikipedia.org", href, text)
			links.append((new_text, new_href))
			print ">>>>> %s %s -> %s %s" % (href.encode('utf-8'), text.encode('utf-8'),
				new_href.encode('utf-8'), new_text.encode('utf-8'))

		if href.find("m.facebook.com") != -1:
			new_text, new_href = demobile("m.facebook.com", "facebook.com", href, text)
			links.append((new_text, new_href))
			print ">>>>> %s %s -> %s %s" % (href.encode('utf-8'), text.encode('utf-8'),
				new_href.encode('utf-8'), new_text.encode('utf-8'))

		if href.find('amazon.com/gp/aw/d') != -1:
			new_text, new_href = demobile("amazon.com/gp/aw/d/", "amazon.com/dp/", href, text)
			links.append((new_text, new_href))
			print ">>>>> %s %s -> %s %s" % (href.encode('utf-8'), text.encode('utf-8'),
				new_href.encode('utf-8'), new_text.encode('utf-8'))

	if comment.author.name != "LittleHelperRobot" and len(links) > 0:
		if len(links) == 1:
			text = "Non-mobile: [%s](%s)\n\n" % links[0]
		else: # len(links) > 1
			text = "Non-mobile:\n\n"
			for link in links:
				text += " * [%s](%s)\n" % (link)
			text += "\n"
		text += "^That's ^why ^I'm ^here, ^I ^don't ^judge ^you. ^PM ^/u/xl0 ^if ^I'm ^causing ^any ^trouble. [^WUT?](https://github.com/xl0/LittleHelperRobot/wiki/What's-this-all-about%3F)"

		print "I'm commenting:\n", text.encode('utf-8')
		try:
			c = comment.reply(text);
			print c.permalink.encode('utf-8')
		except praw.errors.RateLimitExceeded as e:
			print "Nope, rate limit exceded:", str(e)
		except praw.errors.APIException as e:
			print "Some other exception:", str(e)
		except requests.exceptions.HTTPError as e:
			print "Looks like we are banned here"

if __name__ == "__main__":
        start()
