# -*- coding: utf-8 -*-

import collections
import functools
import httplib
import cStringIO
import core

from middleware.log import LogManager

class HttpRequest(object):
    """
        HTTPµÄÇëÇó
        method : GET, POST, etc
        url  : http://example.com/
        headers dict :  {'User-Agent': ['firefox']}
        body :  str
    """
    def __init__(self, host, method, url,  headers = None,  usessl = False, 
                       keyfile = None, certfile = None, port = None, body = None ):
        self.host = host
        self.port = port
        if usessl and self.port == None:
            self.port = 443
        self.method = method
        self.url = url
        self.headers = headers and headers or {}
        self.usessl = usessl
        self.keyfile = keyfile
        self.certfile = certfile
        self.body = body
    
    def __str__(self):
        return self.method + " " + self.host + " " + self.url

class HttpReply(object):
    def __init__(self,  header, body ):
        super(HttpReply,self).__init__()
        self.header = header
        self.body = body

    def __str__(self):
        return str(self.header) 

_logger = LogManager.get_logger("http_client")


class AsyncHTTPClient(object):
    def __init__(self, max_clients=10, max_buffer_size=10240):
        """
        max_buffer_size is the number of bytes that can be read by IOStream. It
        defaults to 10kB.
        """
        super(AsyncHTTPClient, self).__init__()
        self.max_clients = max_clients
        self.active = {}
        self.max_buffer_size = max_buffer_size
        _logger.info('__init__: max_clients %d, max_buffer_size %d ', max_clients, max_buffer_size )

    def http_request(self, request, timeout, callback):
        self.process_request(request, timeout, callback)
        if len(self.active) > self.max_clients:
            _logger.warn("max_clients(%s) limit reached, %d active http request." % (self.max_clients, len(self.active)))

    def process_request(self, request, timeout, callback):
        key = object()
        self.active[key] =  callback
        wrapper_callback = functools.partial(self._callback, key, request)
        HTTPConnection(request, timeout, wrapper_callback, self.max_buffer_size)

    def callback(self, key, request, err, reply):
        if self.active.has_key(key):
            callback =  self.active[key]
            del self.active[key]
            callback(request, reply)


class HTTPClient(core.http_client_proxy):
    def __init__(self, host, port, method, path, headers, timeout, usessl, content, keep_alive, handler):
        super(HTTPClient, self).__init__(host, port, method, path, headers, timeout, usessl, content, keep_alive)
        self.handler = handler
    
    def callback(self, err, headers, content):
        if not callable(self.handler):
            return

        if err == "":
            # yes, for compatible we have to hack here, just for an HTTPMessage's instance
            msg = httplib.HTTPMessage(cStringIO.StringIO())
            msg.status = ''
            msg.dict = headers
            reply = HttpReply(msg, content)
            self.handler(err, reply)
        else:
            _logger.error('HTTPClient - callback: err=%s', err)
            self.handler(err, None)


class HTTPConnection(object):
	
    HTTP_PORT = 80
    HTTPS_PORT = 443
    
    def __init__(self, request, timeout, wrapper_callback, max_buffer_size):
        super(HTTPConnection, self).__init__()
        # received data
        self.callback = wrapper_callback
        self.default_port = self.HTTPS_PORT if request.usessl else self.HTTP_PORT
        self.headers = ""
        self.set_hostport(request.host, request.port)
        self.putheaders(request.headers)
        body = request.body if request.body is not None else ""
        self.http_client = HTTPClient(self.host, self.port, request.method, request.url, self.headers, timeout, request.usessl, body, False, self.callback)
        self.http_client.start()

    def putheaders(self, headers):
        buf = []
        for hdr, value in headers.iteritems():
            hdr = '%s: %s' % (hdr, value)
            buf.append(hdr)
        self.headers = "\r\n".join(buf)

    def set_hostport(self, host, port):
        if port is None:
            i = host.rfind(':')
            j = host.rfind(']')     # ipv6 addresses have [...]
            if i > j:
                try:
                    port = int(host[i+1:])
                except ValueError:
                    if host[i+1:] == "":    # http://foo.com:/ == http://foo.com/
                        port = self.default_port
                    else:
                        raise httplib.InvalidURL("nonnumeric port: '%s'" % host[i+1:])
                host = host[:i]
            else:
                port = self.default_port
            if host and host[0] == '[' and host[-1] == ']':
                host = host[1:-1]
        self.host = host
        self.port = port


if __name__ == '__main__':	
    def callback(request, reply):
        print "entering http callback"
        if reply != None:
            print request, reply, reply.body
        else:
            print "failed to fetch the request", str(request)

    client = AsyncHTTPClient(10)
    request = HttpRequest("wordpress.org",  "GET", "/plugins/about/readme.txt")
    client.http_request(request, 10, callback)
