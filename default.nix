{ pkgs ? import <nixpkgs> {}}:

with pkgs;

pkgs.python3Packages.buildPythonPackage {
  pname = "chapter-marker";
  version = "1";
  src = lib.cleanSource ./.;
  propagatedBuildInputs = [
    qt5.full
    python3Packages.docopt
    python3Packages.pyqt5
    python3Packages.notify2
    python3Packages.requests
    python3Packages.pynput
    vscode
    qtcreator
  ];
  nativeBuildInputs = [ poetry ];
  checkInputs = [
    python3Packages.twine
  ];
}
