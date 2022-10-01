# Chapter-marker

Write a chaptermark file for your podcast. The focus is the [binaergewitter podcast](https://blog.binaergewitter.de)
Chapter-marker is to be used with hotkeys.


## Installation

```bash
pip install chapter-marker
```

## Workflow

### For Binärgewitter
```
export PAD_APIKEY=<add-apikey-for-pad-here> 

CURRENT_SHOW=$(bgt-current-show)
showtitles="titles${CURRENT_SHOW}.lst"
bgt-get-titles "${CURRENT_SHOW}" > "$showtitles"

chapter-marker "$showtitles" "${CURRENT_SHOW}"
# ctrl-j -> start the show at "H" of Hallihallo, also start next chapter
# check by clicking left on the tray icon which is the next chapter

# finish up the show by right clicking on the tray and choose [save] 
# the chapter mark file is now stored at ~/.local/share/chapter-marker/${CURRENT_SHOW}_chapters.txt
```

## Development

### NixOS

```bash
nix-shell
# or build and test the whole thing
nix-build
result/bin/chapter-marker
```


### Legacy OS

Requires python headers:

```bash
sudo dnf install python3-devel
sudo apt install python3-dev
```

```bash
poetry install
poetry run chapter-marker "$showtitles" "${CURRENT_SHOW}"
```

# License
Source Code under MIT (see `License`)

The Icons are Licensed under Apache 2.0, from https://github.com/Templarian/MaterialDesign/
