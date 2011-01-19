#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Estrae mnemonici da numeri
#

import re
import functools

mnemos = {
        '0': "s|x|z|ss|zz",
        '1': "d|t|dd|tt",
        '2': "n|nn|gn",
        '3': "m|mm",
        '4': "r|rr",
        '5': "l|ll|gli",
        '6': "(?:c|cc|g|gg)[ei]",
        '7': "k|q|(?:[cg][aou])|(?:[cg]h[ei])",
        '8': "f|ff|v|vv",
        '9': "b|bb|p|pp",
        }
vocabulary_ext = tuple(w.rstrip("\n\r") for w in file("enilab2.voc", "r").readlines())
vocabulary = tuple(w.rstrip("\n\r") for w in file("enilab2.ana", "r").readlines())

class memoized(object):
    """Decorator that caches a function's return value each time it is called.
       If called later with the same arguments, the cached value is returned, and
       not re-evaluated.
       """
    def __init__(self, func):
          self.func = func
          self.cache = {}
    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

@memoized
def buildregex(number):
    regex = middle = "[aeiou]"
    middle += "+"
    regex += "*"
    for letter in number:
        regex += "(?:" + mnemos[letter] + ")" + middle
    regex = regex[:-1] + "*$"
    return re.compile(regex)

@memoized
def find(regex, extended):
    words = []
    for word in (vocabulary_ext if extended else vocabulary):
        if regex.match(word):
            words.append(word)
    return words

@memoized
def memo(number, stop_first=True, extended=False):
    number = unicode(number)
    if not number.isdigit():
        raise Exception("'{0}' isn't a number".format(number))
    results = []
    for l in xrange(len(number), (1 if len(number) > 1 else 0), -1):
        first, rest = number[:l], number[l:]
        regex = buildregex(first)
        words = find(regex, extended)
        if not rest:
            results += list((word,) for word in words)
        else:
            for word in words:
                for others in memo(rest, stop_first, extended):
                    results.append((word,) + others)
        if results and stop_first:
            break
    return results

if __name__ == "__main__":
    import sys
    stop_first = not ('-a' in sys.argv)
    extended = ('-e' in sys.argv)
    for number in sys.argv[1:]:
        if number.isdigit():
            print("{0}:".format(number))
            for m in memo(number, stop_first, extended):
                print("\t{0}".format(" ".join(m)))
