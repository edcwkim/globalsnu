from haystack.backends.elasticsearch5_backend import (
    Elasticsearch5SearchBackend, Elasticsearch5SearchEngine)
from haystack.signals import BaseSignalProcessor


class ElasticsearchSearchBackend(Elasticsearch5SearchBackend):

    DEFAULT_SETTINGS = {
        'settings': {
            "analysis": {
                "analyzer": {
                    "ngram_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["haystack_ngram", "lowercase"]
                    },
                    "edgengram_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["haystack_edgengram", "lowercase"]
                    }
                },
                "tokenizer": {
                    "haystack_ngram_tokenizer": {
                        "type": "nGram",
                        "min_gram": 2,
                        "max_gram": 15,
                    },
                    "haystack_edgengram_tokenizer": {
                        "type": "edgeNGram",
                        "min_gram": 2,
                        "max_gram": 15,
                        "side": "front"
                    }
                },
                "filter": {
                    "haystack_ngram": {
                        "type": "nGram",
                        "min_gram": 2,
                        "max_gram": 15
                    },
                    "haystack_edgengram": {
                        "type": "edgeNGram",
                        "min_gram": 2,
                        "max_gram": 15
                    }
                }
            }
        }
    }

    def build_schema(self, fields):
        content_field_name, mapping = super().build_schema(fields)
        for field_name, field_mapping in mapping.items():
            if field_mapping.get('analyzer') == "snowball":
                mapping[field_name]['analyzer'] = "cjk"
        return (content_field_name, mapping)


class ElasticsearchSearchEngine(Elasticsearch5SearchEngine):

    backend = ElasticsearchSearchBackend
