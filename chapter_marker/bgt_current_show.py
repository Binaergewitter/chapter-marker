#!/usr/bin/env python
""" usage: bgt-current-show

returns the id of the next bgt show
"""

import urllib.request


def main():
    url = "https://pad.binaergewitter.de/"
    ret = urllib.request.urlopen(url)
    print(ret.geturl().split("/")[-1])


if __name__ == "__main__":
    main()
