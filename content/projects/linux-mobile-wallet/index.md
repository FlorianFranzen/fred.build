+++
title = "Linux mobile wallet"
description = "A transaction signer for Substrate chains built on mobile-nixos: an old phone as an offline signing device, declared like any other NixOS system."
weight = 55

[taxonomies]
tags = ["nix", "nixos", "security", "polkadot"]

[extra]
repo = "https://github.com/gliology/linux-mobile-wallet"
role = "Author"
status = "archived"
period = "2021"
tech = ["Nix", "mobile-nixos", "Substrate"]
featured = false
+++

An experiment from the same line of thinking as [Mind the Gap](/projects/mind-the-gap/): a phone that never goes online, running a NixOS image built with mobile-nixos, signing transactions for Polkadot-family chains and handing them back as QR codes. Declaring the whole device in Nix means the image can be rebuilt from source years later, which is the point of a signing device you have to trust.

The project reached a working prototype in 2021 and is kept as a reference; the hardware-key approach of Mind the Gap took over from it.
