"""
elastic_index.py
This includes class Index for dealing with Elasticsearch.
Contains methods for finding articles.
"""

import yaml
from elasticsearch import Elasticsearch
import math
from werkzeug.exceptions import NotFound


class Index:
    """
    An elasticsearch index of articles.
    """

    def __init__(self, config):
        self.config = config
        self.client = Elasticsearch([{"host": self.config["url"]}])

    @staticmethod
    def no_case(str_in):
        """
        Create query from string, case-insensitive.
        :param str_in:
        :return:
        """
        string = str_in.strip()
        ret_str = ""
        if string != "":
            for char in string:
                ret_str = ret_str + "[" + char.upper() + char.lower() + "]"
        return ret_str + ".*"

    @staticmethod
    def make_matches(searchvalues):
        """
        Create match queries.
        :param searchvalues:
        :return:
        """
        must_collection = []
        for item in searchvalues:
            if item["field"] == "FREE_TEXT":
                for value in item["values"]:
                    must_collection.append({"multi_match": {"query": value, "fields": ["*"]}})
            elif item["field"] in ["year", "lines"]:
                range_values = item["values"][0]
                r_array = range_values.split('-')
                must_collection.append(
                    {"range": {item["field"]: {"gte": r_array[0], "lte": r_array[1]}}}
                )
            else:
                for value in item["values"]:
                    must_collection.append({"match": {item["field"] + ".keyword": value}})
        return must_collection

    def get_facet(self, field, amount, facet_filter, search_values):
        """
        Get a facet.
        :param field:
        :param amount:
        :param facet_filter:
        :param search_values:
        :return:
        """
        terms = {
            "field": field + ".keyword",
            "size": amount,
            "order": {
                "_count": "desc"
            }
        }

        if facet_filter:
            filtered_filter = ''.join([f"[{char.upper()}{char.lower()}]" for char in facet_filter])
            terms["include"] = f'.*{filtered_filter}.*'

        body = {
            "size": 0,
            "aggs": {
                "names": {
                    "terms": terms
                }
            }
        }

        if search_values:
            body["query"] = {
                "bool": {
                    "must": self.make_matches(search_values)
                }
            }
        response = self.client.search(index='articles', body=body)

        return [{"key": hits["key"], "doc_count": hits["doc_count"]}
                for hits in response["aggregations"]["names"]["buckets"]]

    def get_filter_facet(self, field, facet_filter):
        """
        Get a filter facet.
        :param field:
        :param facet_filter:
        :return:
        """
        ret_array = []
        response = self.client.search(
            index="articles",
            body=
            {
                "query": {
                    "regexp": {
                        field: self.no_case(facet_filter)
                    }
                },
                "size": 0,
                "aggs": {
                    "names": {
                        "terms": {
                            "field": field,
                            "size": 20,
                            "order": {
                                "_count": "desc"
                            }
                        }
                    }
                }
            }
        )
        for hits in response["aggregations"]["names"]["buckets"]:
            buffer = {"key": hits["key"], "doc_count": hits["doc_count"]}
            if facet_filter.lower() in buffer["key"].lower():
                ret_array.append(buffer)
        return ret_array

    def get_nested_facet(self, field, amount):
        """
        Get a nested facet.
        :param field:
        :param amount:
        :return:
        """
        ret_array = []
        path = field.split('.')[0]
        response = self.client.search(
            index="articles",
            body=
            {
                "size": 0,
                "aggs": {
                    "nested_terms": {
                        "nested": {
                            "path": path
                        },
                        "aggs": {
                            "filter": {
                                "filter": {
                                    "regexp": {
                                        "$field.raw": "$filter.*"
                                    }
                                },
                                "aggs": {
                                    "names": {
                                        "terms": {
                                            "field": "$field.raw",
                                            "size": amount
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
        for hits in response["aggregations"]["nested_terms"]["filter"]["names"]["buckets"]:
            buffer = {"key": hits["key"], "doc_count": hits["doc_count"]}
            ret_array.append(buffer)
        return ret_array

    def get_min_max(self, fields):
        """
        Get the minimum and maximum value for fields in :fields:
        :param fields: A list of fields to get the min/max for
        :return:
        """
        aggs = {}
        tmp = {}

        for field in fields:
            aggs[f"min-{field}"] = {
                "min": {
                    "field": field,
                },
            }
            aggs[f"max-{field}"] = {
                "max": {
                    "field": field,
                },
            }
            tmp[field] = {}

        response = self.client.search(
            index="articles",
            body={
                "size": 0,
                "aggs": aggs
            }
        )['aggregations']

        for key, value in response.items():
            type, field = key.split('-')
            tmp[field][type] = value['value']

        return tmp

    def browse(self, page, length, search_values):
        """
        Search for articles.
        :param page:
        :param length:
        :param search_values:
        :return:
        """
        int_page = int(page)
        start = (int_page - 1) * length

        if search_values:
            query = {
                "bool": {
                    "must": self.make_matches(search_values)
                }
            }
        else:
            query = {
                "match_all": {}
            }

        response = self.client.search(index="articles", body={
            "query": query,
            "size": length,
            "from": start,
            "_source": ["id", "path", "from_name", "from_email", "newsgroups", "subject",
                        "message_id", "date", "x_gateway", "lines", "xref", "body", "references"],
            "sort": [
                {"date": {"order": "asc"}}
            ]
        })

        return {"amount": response["hits"]["total"]["value"],
                "pages": math.ceil(response["hits"]["total"]["value"] / length),
                "items": [item["_source"] for item in response["hits"]["hits"]]}

    def get_facets(self):
        """
        Get all facets. Parses the configuration YAML file for determining
        what facets are available.
        :return:
        """
        with open("fields.yaml", 'r') as stream:
            data = yaml.safe_load(stream)
        tmp = {}
        number_fields = []
        for field, props in data.items():
            if props['facet']:
                tmp[field] = {
                    'field': field,
                    'type': props['type'],
                    'name': props['name'],
                }
                if props['type'] == 'number':
                    number_fields.append(field)

        min_max = self.get_min_max(number_fields)
        for field in number_fields:
            tmp[field]['min'] = min_max[field]['min']
            tmp[field]['max'] = min_max[field]['max']
        return list(tmp.values())

    def by_message_id(self, message_id):
        """
        Find a message by message id.
        """
        query = {
            "term": {
                "message_id.keyword": {
                    "value": message_id,
                }
            }
        }
        response = self.client.search(index="articles", body={
            "query": query,
            "size": 1,
            "from": 0,
            "_source": ["id", "path", "from_name", "from_email", "newsgroups", "subject",
                        "message_id", "date", "x_gateway", "lines", "xref", "body", "references"],
            "sort": [
                {"date": {"order": "asc"}}
            ]
        })
        if response["hits"]["total"]["value"] > 0:
            return response['hits']['hits'][0]['_source']
        return None

    def get_replies(self, message_id):
        """
        Find all replies to message with id :message_id:
        :param message_id: The id of the original post
        :return:
        """
        query = {
            "term": {
                "references.keyword": {
                    "value": message_id,
                }
            }
        }
        response = self.client.search(index="articles", body={
            "query": query,
            "_source": ["id", "path", "from_name", "from_email", "newsgroups", "subject",
                        "message_id", "date", "x_gateway", "lines", "xref", "body", "references",
                        "body"],
            "sort": [
                {"date": {"order": "asc"}}
            ]
        })
        return response["hits"]['hits']

    def by_id(self, article_id):
        """
        Get an article by id
        :param article_id:
        :return:
        """
        res = self.client.get(index='articles', id=article_id)
        if not res['found']:
            raise NotFound('Article not found')

        data = res['_source']
        if data['references'] != '':
            ref = self.by_message_id(data['references'])
            data['thread_reply'] = ref

        replies = self.get_replies(data['message_id'])
        if len(replies) > 0:
            data['replies'] = [i['_source'] for i in replies]

        return data
