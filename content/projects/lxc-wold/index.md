+++
title = "lxc_wold"
description = "Wake-on-LAN for Linux containers: a daemon that starts an LXC container when a magic packet for its MAC address arrives."
weight = 92

[taxonomies]
tags = ["c", "linux"]

[extra]
repo = "https://github.com/FlorianFranzen/lxc_wold"
role = "Author"
status = "archived"
period = "2013–2015"
tech = ["C", "LXC", "CMake"]
featured = false
+++

Stopped containers should behave like sleeping machines. lxc_wold watches the network for Wake-on-LAN magic packets, matches the MAC address against the configured containers and starts the right one through liblxc, so anything that can wake a computer can wake a container too.
