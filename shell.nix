{ pkgs ? import <nixpkgs> {}}:

with pkgs;

mkShell {
  buildInputs = [
    # put packages here.
    xdotool
  ];
}
