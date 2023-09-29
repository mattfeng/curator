#!/usr/bin/env python

import feedparser
import yaml
import json
import argparse
import sys
import pathlib
import datetime


def get_journals_from_yaml(yaml_file):
    with open(yaml_file) as f:
        journals = yaml.safe_load(f)
    
    return journals


def get_feed_item_details(feed):
    items = []
    for item in feed.entries:
        items.append({
            "id": item.id,
            "title": item.title,
            "link": item.link,
            "description": item.description,
            "updated": item.updated_parsed,
            "authors": item.get("authors")
        })
    
    return items


def get_seen_article_ids(seen_file):
    if not pathlib.Path(seen_file).exists():
        return set()
    
    seen = set()
    with open(seen_file) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("##"):
                seen.add(line)
    
    return seen


def main(*, yaml_file, output_file, seen_file):
    journals = get_journals_from_yaml(yaml_file)
    seen_article_ids = get_seen_article_ids(seen_file)

    feeds = {}

    for journal in journals:
        match journal:
            case {"name": name, "rss": rss}:
                if name in feeds:
                    print(f"error: duplicate journal name `{name}`")
                    sys.exit(1)

                feeds[name] = feedparser.parse(rss)
            case _:
                print(f"error: entry in journals.yaml is missing at least one of [`name`, `rss`]")
                sys.exit(1)
    
    articles = {}
    new_article_ids = set()
    for journal, feed in feeds.items():
        feed_items = get_feed_item_details(feed)

        feed_items = list(filter(
            lambda item: item["id"] not in seen_article_ids, 
            feed_items))
        
        for new_feed_item in feed_items:
            new_article_ids.add(new_feed_item["id"])

        articles[journal] = feed_items
    
    with open(output_file, "w") as fout:
        json.dump(articles, fout)
    
    # track seen articles
    with open(seen_file, "a") as fout:
        fout.write(f"## new articles from: {datetime.datetime.now().isoformat()}\n")
        for article_id in new_article_ids:
            fout.write(f"{article_id}\n")

    print("[i] done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--journals-yaml", default="journals.yaml")
    parser.add_argument("--output-json", default="articles.json")
    parser.add_argument("--seen-file", default="seen.txt")

    args = parser.parse_args()
    main(
        yaml_file=args.journals_yaml,
        output_file=args.output_json,
        seen_file=args.seen_file
        )