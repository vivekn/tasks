from eventlet.green import urllib2
import tasks

def fetch(url):
	body  = urllib2.urlopen(url).read()
	tasks.logger.debug("%s - %s" % (url, body))

if __name__ == '__main__':
	tasks.set_func(fetch)
	tasks.main()
