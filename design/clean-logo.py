#!/usr/bin/env python3
"""Normalise a logo SVG for the companies wall: one path colour (currentColor), no size
attributes, no gradients, no scripts or titles. Usage: clean-logo.py in.svg out.svg"""
import os, re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8", errors="ignore").read()
s = s[s.index("<svg"):]                                      # drop xml prolog / doctype
s = re.sub(r"<(title|desc|metadata|script|style)\b.*?</\1>", "", s, flags=re.S)
s = re.sub(r"<defs\b.*?</defs>", "", s, flags=re.S)          # gradients, clip paths, masks
s = re.sub(r"<(sodipodi|inkscape):[\w-]+\b[^>]*?/>", "", s)      # editor metadata
s = re.sub(r"<(sodipodi|inkscape):([\w-]+)\b.*?</\1:\2>", "", s, flags=re.S)
s = re.sub(r'\s(sodipodi|inkscape|xmlns:sodipodi|xmlns:inkscape):?[\w-]*="[^"]*"', "", s)
s = re.sub(r'\s(clip-path|mask|filter)="[^"]*"', "", s)
s = re.sub(r'\sfill="(?!none)[^"]*"', ' fill="currentColor"', s)
s = re.sub(r'\sstroke="(?!none)[^"]*"', ' stroke="currentColor"', s)
s = re.sub(r'\sstyle="[^"]*"', "", s)
s = re.sub(r'\s(class|id|data-[\w-]+|xml:space|preserveAspectRatio)="[^"]*"', "", s)
head = re.match(r"<svg[^>]*>", s).group(0)
vb = re.search(r'viewBox="([^"]+)"', head)
if not vb:
    w = re.search(r'width="([\d.]+)', head); h = re.search(r'height="([\d.]+)', head)
    vbv = f"0 0 {w.group(1)} {h.group(1)}"
else:
    vbv = vb.group(1)
new_head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vbv}" fill="currentColor" preserveAspectRatio="xMinYMid meet" aria-hidden="true" focusable="false">'
s = new_head + s[len(head):]
s = re.sub(r"\s+", " ", s).replace("> <", "><").strip()
open(dst, "w").write(s + "\n")
# minify when svgo is on PATH (it is in the dev shell)
import shutil, subprocess
if shutil.which("svgo"):
    subprocess.run(["svgo", "--multipass", "-q", dst], check=True)
print(f"{dst}: {os.path.getsize(dst)} bytes, viewBox {vbv}")
