+++
title = "Wii U GamePad on Linux"
description = "Early work on talking to the Wii U GamePad from Linux: an out-of-tree mac80211 module with DKMS packaging, firmware-dump tooling, and documentation for libdrc."
weight = 86

[taxonomies]
tags = ["linux", "reverse-engineering", "c", "kernel"]

[extra]
repo = "https://bitbucket.org/FlorianFranzen/drc-mac80211"
homepage = "https://github.com/GaryOderNichts/libdrc"
role = "Contributor"
status = "archived"
period = "2014"
tech = ["C", "Linux kernel", "DKMS", "Python"]
featured = false
cover_alt = "A gamepad with a screen"
+++

In 2014 the Wii U GamePad's wireless link was being reverse-engineered by the libdrc project. The GamePad speaks a modified Wi-Fi, so using it from a PC needed a patched `mac80211`. The studio's founder took that patch out of the kernel tree: backported to 3.11, then 3.13, built as a standalone module so nobody had to recompile a kernel, and packaged with a DKMS configuration so it survived kernel updates. The module lives in the `drc-mac80211` repository on Bitbucket.

Alongside it came a Python tool that parses GamePad firmware flash dumps and splits them into their parts for analysis in IDA, contributed to `drc-re-scripts`, and the boot and image-resource documentation of libdrc itself (seven commits, preserved in the GitHub import of the library).
