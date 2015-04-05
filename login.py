# coding: utf-8
import urllib, urllib2, Cookie
from google.appengine.api import urlfetch
from urlparse import urljoin
import logging

class GAEOpener(object):
    def __init__(self):
        self.cookie = Cookie.SimpleCookie()
        self.last_response = None

    def open(self, url, data = None):
        base_url = url
        if data is None:
            method = urlfetch.GET
        else:
            method = urlfetch.POST
        while url is not None:
            self.last_response = urlfetch.fetch(url = url,
                payload = data,
                method = method,
                headers = self._get_headers(self.cookie),
                allow_truncated = False,
                follow_redirects = False,
                deadline = 10
                )
            data = None # Next request will be a get, so no need to send the data again. 
            method = urlfetch.GET
            self.cookie.load(self.last_response.headers.get('set-cookie', '')) # Load the cookies from the response
            url = urljoin(base_url, self.last_response.headers.get('location'))
            if url == base_url:
                url = None
        return self.last_response

    def _get_headers(self, cookie):
        headers = {
            'Host' : 'www.secure.pixiv.net',
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2',
            'Cookie' : self._make_cookie_header(cookie)
             }
        return headers

    def _make_cookie_header(self, cookie):
        cookie_header = ""
        for value in cookie.values():
            cookie_header += "%s=%s; " % (value.key, value.value)
        return cookie_header

    def get_cookie_header(self):
        return self._make_cookie_header(self.cookie)
