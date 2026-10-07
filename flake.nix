{
  description = "fred.build - website of F.R.E.D., the prototype studio of Florian Franzen";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-26.05";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];
      forAll = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAll (pkgs: rec {
        default = site;

        site = pkgs.stdenvNoCC.mkDerivation {
          pname = "fred-site";
          version = self.shortRev or self.dirtyShortRev or "dev";
          src = nixpkgs.lib.cleanSource ./.;
          nativeBuildInputs = [ pkgs.zola ];
          buildPhase = ''
            runHook preBuild
            zola build -o $out
            runHook postBuild
          '';
          dontInstall = true;
        };
      });

      checks = forAll (pkgs: {
        # Internal links and anchors only; external checks need the network.
        links = pkgs.runCommand "fred-site-check" { nativeBuildInputs = [ pkgs.zola ]; } ''
          cp -r ${nixpkgs.lib.cleanSource ./.} src
          chmod -R u+w src
          cd src
          zola check --skip-external-links
          touch $out
        '';
      });

      devShells = forAll (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            zola
            svgo
            oxipng
            resvg
            imagemagick
            python3Packages.fonttools
            python3Packages.brotli # woff2 output of the fontTools subsetter
            python3Packages.uharfbuzz # shaping for the wordmark paths
            python3Packages.skia-pathops # overlap removal for the favicon cut-outs
            python3Packages.segno # QR code on the business card
            librsvg # rsvg-convert: business card PDFs (design/build-cards.py)
          ];
          # Source fonts for design/build-assets.py and design/build-plates.py
          FONT_INTER = "${pkgs.inter}";
          FONT_JBMONO = "${pkgs.jetbrains-mono}";
        };
      });

      apps = forAll (pkgs: {
        serve = {
          type = "app";
          program = toString (pkgs.writeShellScript "serve" ''
            exec ${pkgs.zola}/bin/zola serve --drafts "$@"
          '');
        };
      });
    };
}
