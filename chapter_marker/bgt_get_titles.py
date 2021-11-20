#!/usr/bin/env python
""" usage: bgt-get-titles [options] [SHOW]

options:
    --out=FILE          file to output the titles to (default is stdout)
    --apikey=KEY        The etherpad APIKEY

requires either PAD_APIKEY to be set  or --apikey to be supplied

returns the id of the next bgt show
"""

import os
import urllib.request

import requests
from docopt import docopt

url = "https://etherpad.euer.krebsco.de/api/1.2.15/getText?apikey={}&padID={}"


def current_show():
    url = "https://pad.binaergewitter.de/"
    ret = urllib.request.urlopen(url)
    return ret.geturl().split("/")[-1]


def main():

    args = docopt(__doc__)
    apikey = os.environ.get("PAD_APIKEY", args["--apikey"])
    show = args["SHOW"]
    out = args["--out"]

    if not apikey:
        print(__doc__)
        exit(1)
    if not show:
        show = current_show()
    try:
        ret = requests.get(url.format(apikey, show)).json()["data"]["text"]
    except:  # noqa E722
        # way to complicated to do right:
        # https://stackoverflow.com/questions/16511337
        print("for url:" + url.format(apikey, show))
        print(f"response: {requests.get(url.format(apikey,show))}")
    header = True

    titles = []
    for line in ret.split("\n"):
        if line == "---":
            header = False
        if not header and line.startswith("## "):
            titles.append(line.replace("## ", "").strip())

    if not out:
        print("\n".join(titles))
    else:
        with open(out, "w+") as f:
            print("\n".join(titles), file=f)


if __name__ == "__main__":
    main()
