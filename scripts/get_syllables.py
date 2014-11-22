#!/usr/bin/env python
import wordfunc
import sys

if len(sys.argv) == 1:
	print "No arguments"
	exit()

## read a stream first
try:
	with open(sys.argv[1]) as entrywound:
		for line in entrywound:
			words = wordfunc.parse_line(line)

			## print word and number of syllables per word
			for w in words:
				nos=wordfunc.ns(w)
				if nos==-1: break
				print 'Word: '+w
				print nos
except IOError:
	print "Unable to open file. Exiting!"
	exit(1)
