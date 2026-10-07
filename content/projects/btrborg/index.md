+++
title = "btrborg"
description = "Back up the latest btrbk snapshots into borg repositories: consistent, deduplicated, encrypted off-site archives of btrfs subvolumes."
weight = 46

[taxonomies]
tags = ["backup", "btrfs", "nix", "shell"]

[extra]
repo = "https://github.com/FlorianFranzen/btrborg"
role = "Author"
status = "maintained"
period = "2021–"
tech = ["Shell", "btrfs", "btrbk", "borg", "NixOS"]
featured = true
+++

btrbk is good at taking cheap, consistent btrfs snapshots and shipping them to other btrfs volumes. borg is good at deduplicated, encrypted archives on any storage. btrborg connects the two: for every subvolume btrbk manages, it takes the most recent snapshot and stores it in a borg repository of the same name. Because the archive is taken from a read-only snapshot, the backup is consistent even while the live subvolume keeps changing.

The tool has the commands you would expect from a backup job, `list`, `init`, `create`, `info`, `check`, `prune`, `compact`, and a `run` that chains them and only prunes if the check passed. Configuration is a shell snippet in `/etc/btrborg.conf`, so secrets can live in a separate root-only file that is sourced from it, and every variable can also come from the environment. It ships with a man page and is what backs up the studio's own machines.
