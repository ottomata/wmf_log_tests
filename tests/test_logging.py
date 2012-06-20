#!/usr/bin/env python

import pytest
import urllib2
import re
import subprocess
import time

from palb.core import *


# always send these request headers when testing.
test_request_headers         = {
    'Accept-Language': 'da, en-gb;q=0.8, en;q=0.7',
    'X-Carrier':   'nonya'
}

# pattern is the following space separated fields:
#
# hostname
# seq
# timestamp
# request_time
# remote_addr
# status
# bytes_sent
# request_method
# uri
# proxy_host
# content_type
# referer
# x_forwarded_for
# user_agent
# accept_language
# x_carrier
log_format_pattern           = "^(?P<hostname>.+?)\t(?P<seq>\d+?)\t(?P<timestamp>.+?)\t(?P<request_time>.+?)\t(?P<remote_addr>.+?)\t(?P<status>.+?)\t(?P<bytes_sent>.+?)\t(?P<request_method>.+?)\t(?P<uri>.+?)\t(?P<proxy_host>.+?)\t(?P<content_type>.+?)\t(?P<referer>.+?)\t(?P<x_forwarded_for>.+?)\t(?P<user_agent>.+?)\t(?P<accept_language>.+?)\t(?P<x_carrier>.+)$"
log_format_regexp            = re.compile(log_format_pattern)


def send_requests(url, request_count):
    """Calls send_request request_count times."""
    for i in range(0,request_count):
        send_request(url)
    # pool = URLGetterPool(10)
    # pool.start()
    # producer = URLProducer(pool.url_queue, ["http://en.wikipedia.org:3128"], request_count)
    # stats = ResultStats()
    # producer.start()
    # pool.result_queue.get()
    # for _ in xrange(request_count):
    #     if not keep_processing:
    #         break
    #     stats.add(pool.result_queue.get())
    # stats.stop()    

def send_request(url):
    """Calls request_url with the test_request_headers."""
    return request_url(url, test_request_headers)

def request_url(url, headers = {}):
    """Sends a simple GET request to URL and returns the result."""
    req                      = urllib2.Request(url)
    for header, value in headers.items():
        req.add_header(header, value)
    res                      = urllib2.urlopen(req)
    return res.read()


def match_log_line(line):
	"""Matches log line against log_format_regexp and returns the match group dict."""

	match                    = log_format_regexp.match(line)
	if match:
	    return match.groupdict()
	else:
	    return False



# reads the last line from a file and returns it
# If you want to read the nth to last line from file, then set
# reverse_index to n
def read_last_line_from_file(file_path, reverse_index=1):
	"""Reads and returns  the last line from file_path using subprocess and tail -n 1."""
	proc                    = subprocess.Popen(['tail', '-n',  str((reverse_index)),  file_path], stdout=subprocess.PIPE)
	return proc.communicate()[0].split("\n")[0]





main_url       = 'http://en.wikipedia.org/index.php/Main_Page'

nginx_url          = 'https://en.wikipedia.org/index.php/Main_Page'
# nginx_url          = 'http://localhost:8080'
nginx_access_log   = '/var/log/nginx/access.log'

squid_url          = 'http://en.wikipedia.org:3128/index.php/Main_Page'
# squid_url          = 'http://localhost:8081'

squid_access_log   = '/var/log/squid/access.log'

varnish_url        = 'http://en.wikipedia.org:6081/index.php/Main_Page'

udp2log_port       = 8420
udp2log_file_log   = '/var/log/udp2log/file.log'
# udp2log_file_log   = '/a/log/all.log'

udp2log_filter_log = '/var/log/udp2log/filter.log'
# udp2log_filter_log = '/a/log/filter.log'



def verify_log_line(line):
	print "Verifying %s" % line
	matches              = match_log_line(line)
	
	assert matches 

	# verify hostname
	assert matches.has_key('hostname')
	assert len(matches['hostname']) > 0
	
	# verify seq
	assert matches.has_key('seq')
	assert matches['seq'] > 0
	
	# verify request_timestamp
	assert matches.has_key('timestamp')
	assert len(matches['timestamp']) > 0
	
	# verify remote_addr
	assert matches.has_key('remote_addr')
	assert len(matches['remote_addr']) > 0
	
	# verify status
	assert matches.has_key('status')
	assert len(matches['status']) > 0
	
	# verify bytes_sent
	assert matches.has_key('bytes_sent')
	assert len(matches['bytes_sent']) > 0
	
	# verify uri
	assert matches.has_key('uri')
	assert len(matches['uri']) > 0
	
	# verify proxy_host
	assert matches.has_key('proxy_host')
	assert len(matches['proxy_host']) > 0
	
	# verify content_type
	assert matches.has_key('content_type')
	assert matches['content_type'].startswith('text/html')
	
	# verify referer
	assert matches.has_key('referer')
	assert len(matches['referer']) > 0
	
	# verify x_forwarded_for
	assert matches.has_key('x_forwarded_for')
	assert len(matches['x_forwarded_for']) > 0
	
	# verify user_agent
	assert matches.has_key('user_agent')
	assert len(matches['user_agent']) > 0
	
	# verify accept_language
	assert matches.has_key('accept_language')
	assert len(matches['accept_language']) > 0
	
	# verify x_carrier
	assert matches.has_key('x_carrier')
	assert len(matches['x_carrier']) > 0




def request_and_verify(url, log_file, request_count=1, buffered=False):
	# make a request
	send_requests(url, request_count)
	time.sleep(1)
	
	# udp2log buffers its output.
	# if we are verifying a buffered request, 
	# then read the 2nd to last line in the file
	# to make sure we don't get a truncated line
	# due to buffering.
	if buffered:
		reverse_index = 2
	else:
		reverse_index = 1
	line = read_last_line_from_file(log_file, reverse_index)
	# verify that the line looks as it should
	verify_log_line(line)


# nginx
def test_nginx_access_log_format():
	request_and_verify(nginx_url, nginx_access_log)
	
# udp2log buffers lines, so we need
# to do a bunch of requests before it will output.
# 50 should do it.
def test_nginx_udp2log_file_format():
  request_and_verify(nginx_url, udp2log_file_log, 100, True)

def test_nginx_udp2log_filter_format():
  request_and_verify(nginx_url, udp2log_filter_log, 100, True)






# squid
def test_squid_access_log_format():
  request_and_verify(squid_url, squid_access_log)

def test_squid_udp2log_file_format():
  request_and_verify(squid_url, udp2log_file_log, 100, True)

def test_squid_udp2log_filter_format():
  request_and_verify(squid_url, udp2log_filter_log, 100, True)




# varnish doesn't have an access log, it only uses udp2log
def test_varnish_udp2log_file_format():
  request_and_verify(varnish_url, udp2log_file_log, 100, True)

def test_varnish_udp2log_filter_format():
  request_and_verify(varnish_url, udp2log_filter_log, 100, True)

