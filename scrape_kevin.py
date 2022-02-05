# provide an RSS feed for Kevin Lewis

from time import sleep

import requests
from bs4 import BeautifulSoup

ROOT = "https://www.nationalaffairs.com"


def extract_article(article):
    title = article.h2.text.strip()
    excerpt = article.find("p", attrs={"class": "excerpt"}).text.strip()
    link = article.find("a", attrs={"class": "article-title-link"})["href"]
    return title + " (" + excerpt + ")", link


def get_latest_articles():
    r_root = requests.get(ROOT + "/authors/detail/kevin-lewis")
    soup = BeautifulSoup(r_root.text, "html.parser")
    return {
        title: ROOT + link
        for (title, link) in map(extract_article, soup.find_all("article"))
    }


def htmlencode(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def create_feed(title, link):
    feed = ""
    feed += (
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>\n  <title>'
        + htmlencode(title)
        + "</title>\n  <link>"
        + htmlencode(link)
        + "</link>\n  <description>Scraping Kevin Lewis to RSS for fun and profit"
        + "</description>"
        + '<atom:link href="localhost:8888/rss.xml" rel="self" type="application/rss+xml" />'
    )
    feed += "</channel></rss>"
    return "".join(feed)


def get_item(item_link, item_title):
    print(f"New post: {item_title}")
    soup = BeautifulSoup(requests.get(item_link).text, "html.parser")
    soup.find("div", {"class": "article-social-bar"}).clear()
    post = "  <item>"
    post += f"  <title>{item_title} </title>"
    post += f"  <link>{item_link} </link>"
    post += "  <description>"
    post += htmlencode(str(soup.find("div", attrs={"class": "article-content"})))
    post += "</description>  </item>"
    sleep(5)
    return post


def insert_item(feed, item):
    # find first item and insert just before
    to_find = 'application/rss+xml" />'
    ind = feed.find(to_find) + len(to_find)
    feed = feed[:ind] + item + feed[ind:]
    return feed


if __name__ == "__main__":
    feed_location = "/Users/josh/Documents/research/dev/make_rss_kevin_lewis/kevin_lewis.rss"
    titles_di = get_latest_articles()
    try:
        with open(feed_location, "r") as f:
            existing_feed = f.read()

    except FileNotFoundError:
        print("No feed exists. Creating new feed.")
        existing_feed = create_feed("Kevin Lewis", ROOT + "/authors/detail/kevin-lewis")

    new_items = []
    ALL_NEW = True
    for item_title_, item_link_ in titles_di.items():
        if item_link_ in existing_feed:
            print(f"item {item_title_} is already in the feed")
            ALL_NEW = False
            continue
        new_items.append(get_item(item_link_, item_title_))
    existing_feed = insert_item(existing_feed, " ".join(new_items))
    if ALL_NEW:
        pass  # TODO go on to next page and keep looping until existing content found?
    with open(feed_location, "w") as f:
        f.write(existing_feed)
