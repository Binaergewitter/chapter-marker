{ coreutils, fetchFromGitHub, makeWrapper, xclip, libnotify, stdenv, ... }:

stdenv.mkDerivation rec {
  name = "chapter-marker-${version}";
  version = "master";
  src = ./.;
  buildInputs = [ makeWrapper ];

  installPhase =
    let
      path = stdenv.lib.makeBinPath [
        coreutils
        xclip
        libnotify
      ];
    in
    ''
      mkdir -p $out/bin
      cp chapter-mark chapter-start $out/bin/
      wrapProgram $out/bin/chapter-mark \
        --prefix PATH : ${path}
      wrapProgram $out/bin/chapter-start \
        --prefix PATH : ${path}
    '';
}
