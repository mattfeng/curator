#!/usr/bin/env python

import argparse
import os
import sys
import json
import time
import dotenv
import yaml
import openai

dotenv.load_dotenv()

def get_environment_variable(varname):
    if not (ret := os.environ.get(varname)):
        print(f"error: env variable `{varname}` was not supplied.")
        sys.exit(1)
    return ret


def get_articles_from_file(articles_json):
    with open(articles_json) as f:
        articles = json.load(f)
    return articles


def get_openai_response(article, interests, model):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "Your job is to determine whether or not a PhD student should read a paper, given their interests."},
        {"role": "user", "content": f"The PhD student is interested in [{interests[0]}]."},
        *([
        {"role": "user", "content": f"The PhD student is also interested in [{interest}]."} for interest in interests[1:]]),
        {"role": "user", "content": f"The paper's title is: {article['title']}."},
        {"role": "user", "content": f"The paper's authors are: {article['authors']}."},
        {"role": "user", "content": f"A brief description of the paper is: {article['description']}."},
        {"role": "user", "content": f"Given the above information about a new research paper, would you recommend the user read the paper? Reply with either 'yes' or 'no' in only lowercase and give a reason on the next line. The information about the paper is: {json.dumps(article)}."}
    ]

    # print(messages)

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        )
    return response


def get_user_interests(interests_yaml):
    with open(interests_yaml) as f:
        interests = yaml.safe_load(f)

    valid_interests = []
    for interest in interests:
        match interest:
            case {"topic": topic}:
                valid_interests.append(topic)
            case _:
                print("user provided interest missing one or more of: ['topic', 'keywords'].")

    return valid_interests


def main(*, articles_json, output_file, interests_yaml, openai_model):
    openai.api_key = get_environment_variable("OPENAI_API_KEY")
    # print(openai.Model.list())

    articles = get_articles_from_file(articles_json)
    interests = get_user_interests(interests_yaml)
    print(interests)

    for journal, articles_list in articles.items():
        print(f"=== Journal: {journal} ===")
        for article in articles_list:
            resp = get_openai_response(article, interests, openai_model)
            ans = resp["choices"][0]["message"]["content"]

            recommend, reason = map(lambda f: f.strip(), ans.split("\n"))
            print(article["title"])
            print(ans)
            print()

            article["recommendation"] = recommend
            article["reason"] = reason
            time.sleep(20)
    
    with open(output_file, "w") as fout:
        json.dump(articles, fout)
    print("[i] finished curation.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--articles-json", default="articles.json")
    parser.add_argument("--output-file", default="curated.json")
    parser.add_argument("--interests-yaml", default="interests.yaml")
    parser.add_argument("--openai-model", default="gpt-4")

    args = parser.parse_args()

    main(
        articles_json=args.articles_json,
        output_file=args.output_file,
        interests_yaml=args.interests_yaml,
        openai_model=args.openai_model
        )
