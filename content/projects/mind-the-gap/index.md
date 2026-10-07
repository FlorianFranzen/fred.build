+++
title = "Mind the Gap"
description = "Tools and a NixOS live image for painless airgapping of secrets and keys: smart-card keys derived from a 24-word mnemonic, entirely offline."
weight = 10

[taxonomies]
tags = ["mind-the-gap", "nix", "rust", "security"]

[extra]
repo = "https://github.com/gliology/mind-the-gap"
role = "Author"
status = "active"
period = "2021–"
tech = ["Rust", "Nix", "NixOS", "OpenPGP", "smart cards"]
featured = true
+++

Key ceremonies tend to fail in the boring places: a laptop that was online once too often, a backup nobody can restore, a card that was provisioned by hand and documented in someone's head. Mind the Gap turns the whole procedure into something you can boot.

The command-line tool derives a full OpenPGP key set from a 256-bit mnemonic: a primary key plus signing, decryption and authentication subkeys, each stretched with argon2id and a context string so the same words can safely feed several cards or applications. The keys are written straight to a smart card and never touch a disk.

Around the tool sits a NixOS live ISO (`nix build github:gliology/mind-the-gap#iso`) that boots without networking, carries the card tooling, and is reproducible bit for bit. A NixOS VM test exercises the derivation path on every change. Open work includes Solo 2 and Nitrokey 3 support and a PIV certificate flow.

<!-- Draft paragraph, publish once the fork is documented:
The OpenPGP side builds on a patched fork of the Sequoia library (gli.al/sequoia on GitLab) that prioritises certificate size, so a full key set fits on the cards it targets.
-->
