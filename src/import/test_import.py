#!/usr/bin/env python3

from article import Article
import os
from pathlib import Path
from elasticsearch import Elasticsearch, helpers
import tempfile
import zipfile
import concurrent.futures
import yaml


def create_mapping(name):
    """
    Create the ES index and mapping
    :return:
    """
    client = Elasticsearch("http://localhost:9200")

    if client.indices.exists(name):
        client.indices.delete(index=name)

    with open("../service/fields.yaml") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
            exit(1)

    properties = {}

    for field, props in data.items():
        if props['type'] == 'text':
            properties[field] = {
                'type': 'text',
                'fields': {
                    'keyword': {
                        'type': 'keyword',
                        'ignore_above': 256
                    }
                }
            }
        elif props['type'] == 'number':
            properties[field] = {
                'type': 'integer',
            }
        elif props['type'] == 'date':
            properties[field] = {
                'type': 'date',
            }

    settings = {
        "mappings": {
            "properties": properties
        }
    }

    client.indices.create(
        index=name,
        ignore=400,
        body=settings,
    )


def files_in_dir(dirname):
    """
    Import files from a directory.
    :param dirname:
    :return:
    """
    files = list(Path(dirname).rglob("*"))
    articles = []
    for file in files:
        if not os.path.isfile(file):
            continue
        articles.append(file)
    return articles


def split_bulk(total, size):
    """
    Split bulk articles into chunks.
    :param total: The list of article filenames
    :param size: The size of each chunk
    :return: A list of lists, chunks of size :size: from :total:
    """
    for i in range(0, len(total), size):
        yield total[i:i + size]


def process_bulk(filenames):
    """
    Process a bulk of filenames
    :param filenames:
    :return:
    """
    articles = []
    for filename in filenames:
        try:
            articles.append(Article.from_file(filename))
        except Exception as e:
            print(f"Failed to parse file '{filename}'")
            print(e)

    client = Elasticsearch("http://localhost:9200")
    bulk = [
        {
            "_index": "articles",
            "_id": article.id,
            "_source": article.to_json(),
        }
        for article in articles
    ]
    try:
        res = helpers.bulk(client, bulk)
    except BaseException as e:
        print("Error!")
        print(e.__class__.__name__)
        print(e)


def import_zip(file):
    """
    Import a single zipfile
    :param file:
    :return:
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Importing {file}")
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tmpdir)
        article_locations = files_in_dir(tmpdir)

        bulks = list(split_bulk(article_locations, 250))
        print(f"Processing {len(bulks)} bulks from {file}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(process_bulk, bulks)

        print(f"Imported {len(article_locations)} articles from {file}")
    return len(article_locations)


if __name__ == '__main__':
    create_mapping("articles")

    zipfiles = Path("data").rglob("*.zip")

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(import_zip, zipfiles)
