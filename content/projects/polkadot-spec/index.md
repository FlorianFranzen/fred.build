+++
title = "Polkadot Protocol Specification"
description = "The implementable specification of the Polkadot host, written so that independent teams could build compatible clients from the document alone."
weight = 40

[taxonomies]
tags = ["polkadot", "specification", "blockchain"]

[extra]
repo = "https://github.com/w3f/polkadot-spec"
homepage = "https://spec.polkadot.network"
role = "Lead author"
status = "archived"
period = "2020–2023"
tech = ["AsciiDoc", "Julia", "conformance testing"]
featured = true
+++

A protocol is only decentralised once more than one implementation of it exists. As Polkadot Specification Lead at the Web3 Foundation, the studio's founder led the work of turning the reference implementation's behaviour into a specification that Gossamer (Go), Kagome (C++) and the Rust host could all be checked against.

That meant three things in practice: a readable, versioned document covering the host, networking, consensus and runtime interfaces; a conformance test suite that exercised each client against the same fixtures; and the slow diplomatic work of getting multiple teams to agree on what the protocol actually was where the code disagreed with itself. The multi-client ecosystem the network runs on today grew out of that process.

The specification's binary formats were described in Kaitai Struct, rendered into the document by [asciidoctor-kaitai](/projects/asciidoctor-kaitai/), an extension written for this purpose.
