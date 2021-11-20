#!/usr/bin/env python
""" usage: bgt-get-titles [options] [SHOW]

options:
    --apikey=KEY        The etherpad APIKEY

requires either PAD_APIKEY to be set  or --apikey to be supplied

returns the id of the next bgt show
"""

import os
import urllib.request

import requests
from docopt import docopt

baseurl = "https://etherpad.euer.krebsco.de/api/1.2.15/{}?apikey={}&padID={}"


def current_show():
    url = "https://pad.binaergewitter.de/"
    ret = urllib.request.urlopen(url)
    return ret.geturl().split("/")[-1]


def main():

    args = docopt(__doc__)
    apikey = os.environ.get("PAD_APIKEY", None)
    if not apikey:
        print("PAD_APIKEY is not set, falling back to --apikey")
        apikey = args["--apikey"]

    show = args["SHOW"]

    if not apikey:
        print(__doc__)
        exit(1)
    if not show:
        show = current_show()
    try:
        print(f"Fetching show {show}")
        text = requests.get(baseurl.format("getText", apikey, show)).json()["data"]["text"]
        print(f"replacing <SENDUNGSNUMMER> with {show.upper()}")
        text = text.replace("<SENDUNGSNUMMER>", show.upper())
        print("updating shownotes")
        requests.post(baseurl.format("setText", apikey, show), data={"text": text})
    except:  # noqa E722
        print(f"for url: {baseurl.format(apikey, show)}")
        print(f"response: {requests.get(baseurl.format(apikey,show))}")


if __name__ == "__main__":
    main()
