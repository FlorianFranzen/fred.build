+++
title = "NeuroSuite"
description = "NeuroScope, Klusters and NDManager: desktop tools for viewing, sorting and managing electrophysiology recordings."
weight = 20

[taxonomies]
tags = ["neurosuite", "neuroscience", "cpp"]

[extra]
repo = "https://github.com/neurosuite"
homepage = "https://neurosuite.github.io"
role = "Major contributor"
status = "active"
period = "2015–2020"
tech = ["C++", "Qt", "CMake"]
featured = true
+++

NeuroSuite is a family of Qt applications that a good part of the systems-neuroscience community still runs daily: **NeuroScope** for browsing raw electrophysiological and behavioural data, **Klusters** for cluster cutting during spike sorting, and **NDManager** for keeping an experiment's recordings and pre-processing pipeline in order.

The studio's contributions cover the core of NeuroScope and the shared `libneurosuite` library: a modern Qt port, file-format plugins, live data streaming, and a long tail of stability fixes, together with CI for the whole suite. For Blackrock Microsystems this included import of their file formats and live streaming from Cerebus systems, which meant extending the `libcbsdk` SDK that is now part of the organisation too.

{{ figure(src="screenshot.png", alt="NeuroScope, Klusters and NDManager side by side", caption="NeuroScope, Klusters and NDManager, from the NeuroSuite website.") }}
