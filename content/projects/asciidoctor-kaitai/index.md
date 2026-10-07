+++
title = "asciidoctor-kaitai"
description = "An Asciidoctor extension that lets a document carry its own Kaitai Struct binary format definitions, compiled and drawn as diagrams on the page."
weight = 45

[taxonomies]
tags = ["asciidoc", "kaitai", "ruby", "specification"]

[extra]
repo = "https://github.com/FlorianFranzen/asciidoctor-kaitai"
role = "Author"
status = "maintained"
period = "2022–"
tech = ["Ruby", "Asciidoctor", "Kaitai Struct", "Graphviz", "Nix"]
featured = true
+++

A `kaitai` block in an AsciiDoc document holds the `seq`, `types`, `enums` and `instances` sections of a Kaitai Struct definition as YAML. The extension compiles each block with the Kaitai Struct compiler, renders it with Graphviz and embeds the result as an inline SVG diagram. The same blocks can be exported again as standalone `.ksy` files, so the document stays the single source of truth for a machine-readable description of the format. External `.ksy` files next to the document can be imported and their types reused.

It was written for the [Polkadot Protocol Specification](/projects/polkadot-spec/), where it documented the SCALE codec, the runtime metadata and the block formats until the specification moved to a different toolchain in 2023. The repository preserves that history and makes the extension usable on its own, with CI and a Nix dev shell that provides Ruby, `ksc` and `dot`.
