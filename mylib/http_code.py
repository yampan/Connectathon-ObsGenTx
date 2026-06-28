# -*- coding: utf-8 -*-

# =====================================================================
# Original: Pi5a:/home/jupyter/work/Oauth/common_lib/http_code.py
# 2025-02-04
# 使用方法：
#     sys.path.append('/home/jovyan/work/OAuth/common_lib')
#     from http_code import HTTPcode, HTTP2S
# =====================================================================



################################################################
# HTTP レスポンスステータスコード https://developer.mozilla.org/ja/docs/Web/HTTP/Status

HTTPcode = {200: "OK", 201: "Created", 202: "Accepted", 
            203: "Non-Authoritative Information",
            204: "No Content", 205:"Reset Content",
            301: "Moved Permanently: リソースが永続的に移動しました。",
            302: "Found: リソースが一時的に別の場所に移動しました。",
            304: "Not Modified: リソースに変更なし。",
            400: "Bad Request", 401:"Unauthorized",
            403: "Forbiden", 404:"Not Found",
            405: "Method Not Allowed", 406:"Not Acceptable", 
            407: "Proxy Authentication Required", 408: "Request Timeout", 
            409: "Conflict", 410: "Gone", 411: "Length Required", 
            412: "Precondition Failed", 413: "Payload Too Large", 
            414: "URI Too Long", 415: "Unsupported Media Type",
            416: "Range Not Satisfiable", 417: "Expectation Failed", 
            418: "I'm a teapot", 421: "Misdirected Request",
            500: "Internal Server Error", 501: "Not Implemented",
            530: "undefined error" }
################################################################

def HTTP2S(code):
    return HTTPcode[code]
