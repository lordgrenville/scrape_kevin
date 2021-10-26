# provide an RSS feed for Kevin Lewis

from time import sleep

import requests
from bs4 import BeautifulSoup

ROOT = "https://www.nationalaffairs.com"

def get_latest_articles():
    r_root = requests.get(ROOT + "/authors/detail/kevin-lewis")
    soup_root = BeautifulSoup(r_root.text, "html.parser")
    return {
        link.text.strip(): ROOT + link["href"]
        for link in soup_root.find_all("a", attrs={"class": "article-title-link"})
    }


def htmlencode(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def create_feed(title, link, title_di):
    feed = []
    feed += (
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>\n  <title>'
        + htmlencode(title)
        + "</title>\n  <link>"
        + htmlencode(link)
        + "</link>\n  <description>Scraping Kevin Lewis to RSS for fun and profit"
        + "</description>"
        + '<atom:link href="localhost:8888/rss.xml" rel="self" type="application/rss+xml" />'
    )
    for item_title, item_link in title_di.items():
        insert_item(feed, item_link, item_title)
    feed += "</channel></rss>"
    return "".join(feed)


def insert_item(feed, item_link, item_title):
    if item_link in feed:
        print(f"item {item_title} is already in the feed")
        return feed
    soup = BeautifulSoup(requests.get(item_link).text, "html.parser")
    soup.find("div", {"class": "article-social-bar"}).clear()
    # find first item and insert just before
    ind = feed.find('<item>')
    post = "  <item>"
    post += f"  <title>{item_title} </title>"
    post += f"  <link>{ROOT + item_link} </link>"
    post += "  <description>"
    post += htmlencode(str(soup.find("div", attrs={"class": "article-content"})))
    post += "</description>  </item>"
    feed = feed[:ind] + post + feed[ind:]
    sleep(5)
    return feed


titles_di = get_latest_articles()
try:
    with open("kevin_lewis.rss", "r") as f:
        new_feed = f.read()
        for item_title_, item_link_ in titles_di.items():
            new_feed = insert_item(new_feed, item_link_, item_title_)
    with open("kevin_lewis.rss", "w") as f:
        f.write(new_feed)

except FileNotFoundError:
    basic_feed = create_feed("Kevin Lewis", ROOT + "/authors/detail/kevin-lewis", titles_di)
    with open("kevin_lewis.rss", "w+") as f:
        f.write(basic_feed)
