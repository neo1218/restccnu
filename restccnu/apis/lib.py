# coding: utf-8

import json
from . import api
from flask import request, jsonify
from ..spiders.lib import search_books, get_book, book_me
from .decorators import tojson, require_lib_login
from .paginate import _Pagination


@api.route('/lib/search/')
@tojson
def api_search_books():
    per_page = 20
    keyword = request.args.get('keyword')
    page = int(request.args.get('page') or '1')
    if keyword:
        book_info_list = search_books(keyword)
        pg_book_info_list = _Pagination(book_info_list, page, per_page)
        return {'meta': {
                'max': pg_book_info_list.max_page,
                'per_page': per_page },
            'results': book_info_list[(page-1)*per_page:page*per_page]}


@api.route('/lib/')
@tojson
def api_book_detail():
    id = request.args.get('id')
    book = request.args.get('book')
    author = request.args.get('author')
    return get_book(id, book, author)


@api.route('/lib/me/')
@require_lib_login
@tojson
def api_book_me(s, sid):
    return book_me(s)
