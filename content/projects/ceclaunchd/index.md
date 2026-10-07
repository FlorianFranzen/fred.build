+++
title = "ceclaunchd"
description = "A daemon that listens on HDMI-CEC through libcec and runs scripts when the television or receiver sends a command."
weight = 90

[taxonomies]
tags = ["c", "linux"]

[extra]
repo = "https://github.com/FlorianFranzen/ceclaunchd"
role = "Author"
status = "archived"
period = "2013"
tech = ["C", "libcec", "HDMI-CEC"]
featured = false
+++

The television remote already talks to every device on the HDMI bus. ceclaunchd sits on that bus through libcec, and a small config file maps each button to a binary or script, so a remote becomes a trigger for anything a Linux box behind the screen can do. It ships with its own init script and builds with a plain `make`.
