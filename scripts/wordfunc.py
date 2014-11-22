from nltk.corpus import cmudict as cmud
import nltk

d=cmud.dict()

# break up the line into words etc.,
def parse_line(line):
	return nltk.word_tokenize(line)

# return -1 if the word is not in the dictionary
def ns(word):
	if word.lower() not in d:
     		return -1
# if not just return the syllables. sometimes there can be two or more answer.
# just return the first one [0]
  	else:
		return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
