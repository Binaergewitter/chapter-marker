#!/usr/bin/env python
""" usage: bgt-get-titles [--out=FILE] [SHOW]

requires PAD_APIKEY to be set

returns the id of the next bgt show
"""

# 'https://etherpad.euer.krebsco.de/api/1.2.15/getText?apikey=9lYFcvKX7udkrjxM03UMMBysn&padID=bgt275'
import requests
import urllib.request
import os

url = 'https://etherpad.euer.krebsco.de/api/1.2.15/getText?apikey={}&padID={}'

def current_show():
    url = "https://pad.binaergewitter.de/"
    ret = urllib.request.urlopen(url)
    return ret.geturl().split("/")[-1]

def main():
    from docopt import docopt
    args = docopt(__doc__)
    apikey = os.environ.get('PAD_APIKEY',None)
    show = args['SHOW']
    out = args['--out']

    if not apikey:
        print(__doc__)
        exit(1)
    if not show:
        show = current_show()
    ret = requests.get(url.format(apikey,show)).json()["data"]["text"]
    header = True

    titles = []
    for line in ret.split("\n"):
        if line == '---':
            header = False
        if not header and line.startswith("## "):
            titles.append(line.replace("## ","").strip())

    if not out:
        print("\n".join(titles))
    else:
        with open(out,'w+') as f:
            print("\n".join(titles),file=f)




if __name__ == "__main__":
    main()
