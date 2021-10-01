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
# ctrl-u -> start the show at "H" of Hallihallo
# ctrl-j -> next chapter
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
```bash
virtualenv -m venv .
. bin/activate
pip install -r requirements.txt

```
