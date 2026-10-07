+++
title = "A site for the studio"
description = "F.R.E.D. has a web page now. Here is what it is for and what the first reports will cover."
date = 2026-10-02
draft = true

[taxonomies]
tags = ["meta"]
+++

Franzen Research, Engineering & Development has existed as a company since 2023 and as a bench for a good while longer. Until now it had no address on the web of its own. This site fixes that: a short description of what the studio does, the companies the work has been for, the public projects, and this blog.

<!-- more -->

The blog is for project reports. Not announcements, but the kind of write-up the studio would have liked to find when starting each of these:

- **Digitizing VHS with CXADC**: a capture rig built around a cheap PCIe TV tuner card, the clock modification it needs, and what VHS-Decode makes of the raw RF signal.
- **An airgapped key ceremony that fits on a USB stick**: how Mind the Gap boots, derives and provisions smart cards without ever touching a network, and what the test suite checks.
- **Validators on NixOS**: declaring a Substrate validator and its monitoring in one flake, rotating keys, and recovering from the failures that actually happen.

The site itself is static, built with Zola from a Nix flake, and ships no JavaScript. The source is on GitHub.
