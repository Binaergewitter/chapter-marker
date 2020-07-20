{ coreutils, fetchFromGitHub, makeWrapper, xdotool, stdenv, ... }:

stdenv.mkDerivation rec {
  name = "chapter-marker-${version}";
  version = "master";
  src = fetchFromGitHub {
    owner = "makefu";
    repo = "chapter-marker";
    rev = "bff1dba47d40b00d32dca95262d339484c2ae5fb";
    sha256 = "01nl01kc4f3gync5xkjp0al752rilyyc4zvjjbv5hdvh38vgaml7";
  };

  buildInputs = [ makeWrapper ];

  installPhase =
    let
      path = stdenv.lib.makeBinPath [
        coreutils
        xdotool
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
