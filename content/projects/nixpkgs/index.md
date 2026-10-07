+++
title = "nixpkgs"
description = "Package maintenance in the Nix ecosystem: a hundred-odd pull requests since 2019, a dozen packages and a NixOS module under the studio's name."
weight = 30

[taxonomies]
tags = ["nix", "nixos", "packaging"]

[extra]
repo = "https://github.com/NixOS/nixpkgs/pulls?q=author%3AFlorianFranzen"
homepage = "https://github.com/NixOS/nixpkgs"
role = "Maintainer"
status = "active"
period = "2019–"
tech = ["Nix", "NixOS"]
featured = true
+++

Nix is how the studio ships anything reproducibly, so keeping the packages it relies on healthy is part of the job. In nixpkgs the studio maintains **jp2a**, **workstyle**, the **waybar** NixOS module and a group of Python packages around Sphinx (`sphinx-markdown-parser`, `sphinx-material`, `sphinx-serve`, `scikit-build`, `css-html-js-minify`, `unify`, `untokenize`), and co-maintains **bacon**, **flip-link**, **polkadot**, **subxt**, **segger-jlink**, **waybar** and **reuse**.

Beyond the packages themselves the pull requests range from kernel, BlueZ and Waydroid fixes to the initial packaging of tools the Rust and Polkadot ecosystems needed in nixpkgs. The current batch restores a set of GTK themes after the removal of the GTK 2 engine they depended on.
