#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import requests
import json
import os
import socket


def headers_to_dict(headers_raw):
    """
    >>> r = headers_to_dict("Host: localhost:8080\\nUser-Agent: curl/7.47.0\\n")
    >>> r['Host']
    'localhost:8080'
    >>> r['User-Agent']
    'curl/7.47.0'
    """
    headers = {}
    for h in str(headers_raw).split("\n")[:-1]:
        h_splitted = h.split(':')
        name = h[:h.find(':')].strip()
        if len(name) > 0:
            value = h[h.find(':') + 1:].strip()
            headers[name] = value
    return headers


def is_html(header):
    return 'Content-Type' in header and header['Content-Type'].find('text/html') > -1


def parse_html(html, base_href):
    # TODO : this replacement is ugly / errorprone. Contributions welcomed!
    html = html.replace("href='//", "href='http://")
    html = html.replace("src='//", "src='http://")
    html = html.replace('href="//', 'href="http://')
    html = html.replace('src="//', 'src="http://')

    html = html.replace("href='/", "href='" + base_href + "/")
    html = html.replace("src='/", "src='" + base_href + "/")
    html = html.replace('href="/', 'href="' + base_href + '/')
    html = html.replace('src="/', 'src="' + base_href + '/')

    p_head = html.find('<head')
    if p_head > -1:
        p_endtag = html.find('>', p_head)
        html = html[:p_endtag + 1] + '<base href="' + base_href + '">' + html[p_endtag:]
        return html


if __name__ == "__main__":
    PORT = 8765

    assert 'BASE_HREF' in os.environ, "Please provide a value as an env variable for BASE_HREF"
    assert 'TARGET_URL' in os.environ, "Please provide a value as an env variable for TARGET_URL"
    BASE_HREF = os.environ['BASE_HREF'].rstrip('/')
    TARGET_URL = os.environ['TARGET_URL']

    assert TARGET_URL.startswith('http'), "Please set a correct value for TARGET_URL."
    if not TARGET_URL.endswith('/'):
        TARGET_URL = TARGET_URL + '/'


    class request_handler(BaseHTTPRequestHandler):
        def handle_response(self, target_response):
            if is_html(target_response.headers):
                html = str(target_response.text)
                html = parse_html(html, BASE_HREF)
                body = html.encode()
            else:
                body = target_response.content

            self.send_response(target_response.status_code)
            for h in target_response.headers:
                if h in ['Content-Type', 'Content-Language']:
                    self.send_header(h, target_response.headers[h])
            self.end_headers()
            self.wfile.write(body)
            sys.stdout.flush()

        def do_POST(self):
            data = self.rfile.read(int(self.headers['Content-Length']))
            headers = headers_to_dict(self.headers)
            target_response = requests.post(
                TARGET_URL + self.path.lstrip('/'),
                headers=headers,
                data=data
            )
            self.handle_response(target_response)

        def do_GET(self):
            headers = headers_to_dict(self.headers)
            target_response = requests.get(
                TARGET_URL + self.path.lstrip('/'),
                headers=headers
            )
            self.handle_response(target_response)


    http = HTTPServer(
        ('', PORT),
        request_handler
    )

    print('proxy started...')
    sys.stdout.flush()
    http.serve_forever()
    sys.stdout.flush()
