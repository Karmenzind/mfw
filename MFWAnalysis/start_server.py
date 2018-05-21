#!/usr/bin/env python
# -*- coding: utf-8 -*-

import http.server
import socketserver
import sys
import os

os.chdir('./heatmap')

if __name__ == "__main__":

    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])
    else:
        PORT = 8000

    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
