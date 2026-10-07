+++
title = "pseudocode-ruby"
description = "A Ruby gem that renders LaTeX pseudocode algorithms to HTML with pseudocode.js and KaTeX."
weight = 91

[taxonomies]
tags = ["ruby", "asciidoc"]

[extra]
repo = "https://github.com/FlorianFranzen/pseudocode-ruby"
role = "Author"
status = "maintained"
period = "2022"
tech = ["Ruby", "pseudocode.js", "KaTeX", "ExecJS"]
featured = false
+++

Written alongside the AsciiDoc toolchain of the Polkadot specification, which needed algorithms typeset the way papers do. The gem wraps pseudocode.js and KaTeX through ExecJS, in the style of katex-ruby: `Pseudocode.render(algorithm)` returns HTML, and the pseudocode stylesheet makes it look right. Published as the `pseudocode` gem under the MIT licence.
