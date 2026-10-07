+++
title = "Open Ephys plugins"
description = "Acquisition plugins for the Open Ephys GUI, built for White Matter's wireless recording hardware."
weight = 50

[taxonomies]
tags = ["neuroscience", "cpp", "open-ephys"]

[extra]
repo = "https://github.com/FlorianFranzen?tab=repositories&q=open-ephys"
homepage = "https://open-ephys.org"
role = "Contributor"
status = "archived"
period = "2018–2019"
tech = ["C++", "JUCE", "Asio", "binary network protocols"]
featured = false
+++

Open Ephys is the open-source acquisition platform much of systems neuroscience records with. For White Matter the studio built the bridge between their headstages and the GUI: a C++ acquisition plugin, the binary network protocol behind it, and a port of their SDK from Winsock to Asio so the same code ran on Linux and macOS. Along the way the throughput, latency and jitter of the whole path were measured and tuned until a dense multi-channel stream arrived cleanly in the GUI.
