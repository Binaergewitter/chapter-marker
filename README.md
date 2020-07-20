# Chapter-marker

Write the current time delta to your screen. To be used with hotkeys or with
the sleep interval

## Workflow

```
chapter-start   # wenn Ingo sagt "halli hallo und herzlich willkommen"
chapter-mark  5 # maus in den browser neben die titelzeile oder mittels hotkey
```

## Hotkey in your window manager
To achieve full potential of chapter-marker, make sure to add the tool as a
hotkey to your window manager

### AwesomeWM


* `Ctrl-j`: start timer
* `Ctrl-k`: add marker

Add to your `rc.conf`:

```lua
globalkeys = awful.util.table.join(
  ...
  -- chapter-marker
  awful.key({ "Control" }, "j", function () awful.spawn("/usr/bin/chapter-start") end,
            {description = "start the chapter marker",}),
  awful.key({ "Control" }, "k", function () awful.spawn("/usr/bin/chapter-mark") end,
            {description = "create a chapter mark",}),
  ...
)
root.keys(globalkeys)
```

## Installation

### NixOS

```nix
environment.systemPackages = [ (pkgs.callPackage /here/default.nix {}) ];
# or with nur
environment.systemPackages = [ nur.repos.makefu.chapter-marker ];
```

Build manually:
```bash
nix-build -E 'with import <nixpkgs> {};pkgs.callPackage ./default.nix {}'
result/bin/chapter-mark # run it
```

### Legacy OS
Please note that these installation instructions are untested and extremely
fragile, you must use your own brain unfortunately.
```bash
cp chapter-* /usr/bin/
chmod 755 /usr/bin/chapter-*
# also install xdotool somehow ¯\_( ͡° ͜ʖ ͡°)_/¯
```
