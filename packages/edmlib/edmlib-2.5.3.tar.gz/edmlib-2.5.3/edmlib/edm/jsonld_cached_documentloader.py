"""
Remote document loader for pyld. Based on requests_document_loader but with very simple in-memory caching
"""

from pyld.documentloader.requests import requests_document_loader


def cached_requests_document_loader(secure=False, **kwargs):
    loader = requests_document_loader(secure=secure, **kwargs)
    cache = {}

    def cached_loader(url, options={}):
        if url in cache:
            return cache[url]
        doc = loader(url, options)
        cache[url] = doc
        return doc

    return cached_loader
