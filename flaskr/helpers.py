from flask import abort

def get_or_403(query):
    if not query: abort(403)
    return query

