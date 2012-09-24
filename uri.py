#!/usr/bin/python

import urllib2 as ul
import sys
import re
import time
import multiprocessing as mp
import getopt

time_results = []
total_time = time.time()
uri = None
count = None
timeout = 5
try:
    workers = mp.cpu_count() * 2
except:
    workers = 2

link_regexp = [
    re.compile('.*href="', re.I | re.M | re.S),
    re.compile('.*src="', re.I | re.M | re.S)
]


def usage():
    print "Usage: %s -c int -u uri -w int" % sys.argv[0]
    print "\t-c int, number of connections"
    print "\t-u string, uri"
    print "\t-t int, timeout (defaults to %d seconds)" % timeout
    print "\t-w int, number of workers processes (defaults to %d)" % workers
    sys.exit(0)


def fetch_uri(uri):
    try:
        data = ul.urlopen(uri, timeout=timeout).read()
        return data
    except (ul.HTTPError, ul.URLError, ValueError) as msg:
        print "Failed loading uri: %s" % uri
        print msg


def fake_eki(index_svg, proc_id):
    uris = []
    start = time.time()
    global time_results
    data = fetch_uri(index_svg)
    for line in data.split('\n'):
        for xp in link_regexp:
            if xp.search(line):
                uris.append(line.split('"')[1])

    for uri in uris:
        full_uri = '/'.join(index_svg.split('/')[:-1]) + "/" + uri
        fetch_uri(full_uri)

    time_elapsed = time.time() - start
    sys.stdout.write("\rProc %s finished in %.3f seconds" % (proc_id, time_elapsed))
    sys.stdout.flush()
    return time_elapsed

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hc:u:t:w:')
except getopt.GetoptError, msg:
    print "Error: %s" % msg
    usage()

for o, a in opts:
    if o == '-c':
        try:
            count = int(a)
        except:
            usage()
    elif o == '-u':
        uri = a
    elif o == '-t':
        try:
            timeout = int(a)
        except:
            print "Need an integer for timeout."
            usage()
    elif o == '-h':
        usage()
    elif o == '-w':
        workers = int(a)
    else:
        print "Error: unknown options %s" % o

if count is None or uri is None:
    usage()

p = mp.Pool(processes=workers)
for i in range(count):
    p.apply_async(fake_eki, (uri, i), callback=time_results.append)

p.close()
p.join()

time_results.sort()
print "\n"
print "Max time: %.3fs" % time_results[-1]
print "Min time: %.3fs" % time_results[0]
print "Avg time: %.3fs" % (sum(time_results) / len(time_results))
print
print "Total client time: %.3fs" % sum(time_results)
print "Total script time: %.3fs" % (time.time() - total_time)
