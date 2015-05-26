#!/usr/bin/env python3
"""Retrieve a sitemap from given URL and list dublication and not accessible problems

Usage:

	python3 sitemap_diag.py http://www.example.com/sitemap.xml
"""
import sys
import requests
from bs4 import BeautifulSoup
try:
	from urllib import parse as urlparse
except ImportError:
	# Python 2
	import urlparse

def main(sitemapUrl):
	"""Main module execution logic

	Args:
		sitemap.xml Url
	"""
	sitemap_url = extract_url(sitemapUrl)
	sitemap = sitemap_fetch(sitemap_url)

	sitemapLocations = fetch_locations_from_sitemap(sitemap)

	if len(sitemapLocations) <= 0:
		print ("No location found in the sitemap!")
		sys.exit()

	problematicLocations = [] #List of problems

	sitemapLocations, problematicLocations = sitemap_check_dublicate(sitemapLocations)
	problematicLocations += sitemap_check_accessibility(sitemapLocations)

	print_sitemap_issues(problematicLocations, sitemap_url)


def extract_url(url):
	"""Format the Url to http://example.com/sitemap.xml

	Args:
		Given sitemap url from console

	Returns:
		Formated sitemap url
	"""
	parts = urlparse.urlsplit(url)

	if parts.scheme == '':
		scheme = 'http'
	else:
		scheme = parts.scheme

	urlpath = parts.path.split('/')
	if parts.netloc == '':
		netloc = urlpath[0]
	else:
		netloc = parts.netloc

	if len(urlpath) == 1:
		path = "sitemap.xml"
	else:
		path = urlpath[1]

	needed_parts = urlparse.SplitResult(scheme=scheme, netloc=netloc, path=path, 
	    query='', fragment='')

	return needed_parts.geturl()


def sitemap_fetch(sitemapUrl):
	"""Fetch sitemap from given URL.

	Args:
		sitemapUrl: The URL of the sitemap.

	Returns:
		Fetched sitemap.xml.
	"""
	try:
		r = requests.get(sitemapUrl)
		soup = BeautifulSoup(r.text)

		return soup
	except:
		print("Cannot fetch sitemap ", sitemapUrl)
		sys.exit()


def fetch_locations_from_sitemap(sitemap):
	"""Fetch locations from given sitemap.xml

	Args:
		sitemap.xml

	Returns:
		Fetched sitemap locations <loc> xml nodes
	"""	
	sitemapLocations = []

	for loc in sitemap.find_all('loc'):
		sitemapLocations.append(str(loc.text))

	return sitemapLocations


def sitemap_check_dublicate(sitemapLocations):
	"""Finds dublicated locations in the given sitemap location list

	Args:
		sitemapLocations: List of sitemap locations

	Returns:
		Sorted unique locations to check accessiblity
		problematicLocations: Problematic location list to append
	"""
	problematicLocations = []
	uniq = set()
	for loc in sitemapLocations:
		if loc not in uniq:
			uniq.add(loc)
		else:
			problematicLocations.append("Dublicated Url: {}".format(loc))

	return sorted(uniq), problematicLocations


def sitemap_check_accessibility(locations):
	"""Hits every given URL and gets HTTP status Code

	Args:
		List of URLs to test

	Returns:
		List of URL doesn't return 200 HTTP status code
	"""
	problematicLocations = []
	for loc in locations:
		print (loc)
		r = requests.head(loc)

		if r.status_code != 200:
			if r.status_code == 404: #maybe the URL doesn't response to HEAD request
				tmp = requests.get(loc) #let's try GET request
				if tmp.status_code != 200:
					problematicLocations.append("Status Code: {0} Url:{1}".format(r.status_code, loc))
			else:
				problematicLocations.append("Status Code: {0} Url:{1}".format(r.status_code, loc))

	return problematicLocations


def print_sitemap_issues(problematicLocations, domainname):
	"""Prints tested URLs which don't return 200

	Args:
		Iterable URLs which were tested and don't return 200
	"""
	if len(problematicLocations) == 0:
		print("Good Job! There is no problem on your sitemap")
		return

	print("\n~~List of problems~~")
	with open(domainname + "-sitemap-problems.txt", "w") as f:
		for problem in problematicLocations:
			print (problem)
			f.write(problem + "\n")


if __name__ == '__main__':
	if len(sys.argv) == 1: # The 0th arg is the module filename
		print ('Format should be "python3 sitemap_diag.py [Sitemap URL]"')
		sys.exit()

	main(sys.argv[1])