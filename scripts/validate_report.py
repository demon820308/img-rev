#!/usr/bin/env python3
"""Validate img-rev JSON reports (stdlib only).

Checks structure against references/report-schema.json by hand, plus the
skill's evidence rules: every inferred-capable group carries a basis grade,
palette has exactly 5 HEX colors with an honest palette_basis, inferred
optics or Kelvin readings must be written as a tilde or a range, and a
style_only report must carry a subject-free style_profile.
"""
import json
import re
import sys

GRADES = ("observed", "inferred", "unknown")


def fail(msg):
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_report.py <report.json>")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        fail(f"invalid JSON: {e}")

    meta = d.get("meta", {})
    if meta.get("skill") != "img-rev":
        fail("meta.skill must be 'img-rev'")
    if d.get("mode") not in ("report", "recreation", "style_only"):
        fail("mode must be report, recreation or style_only")
    if d.get("palette_basis") not in ("eyeballed", "measured"):
        fail("palette_basis must be eyeballed or measured")

    report = d.get("report")
    if not isinstance(report, dict):
        fail("report object is required")
    for key in ("medium", "composition", "optics", "lighting", "palette", "grade", "textures"):
        if key not in report:
            fail(f"report.{key} is required")

    palette = report["palette"]
    if len(palette) != 5 or any(not re.fullmatch(r"#[0-9A-Fa-f]{6}", p.get("hex", "")) for p in palette):
        fail("report.palette must be exactly 5 entries with #RRGGBB hex values")
    if len(report["textures"]) < 3:
        fail("report.textures needs at least 3 tactile entries")

    for group in ("optics", "lighting", "grade"):
        basis = report[group].get("basis")
        if basis not in GRADES:
            fail(f"report.{group}.basis must be one of {GRADES}")

    reading = report["optics"].get("reading", "")
    if reading and report["optics"]["basis"] == "inferred":
        if "~" not in reading and "-" not in reading and "–" not in reading:
            fail("inferred optics.reading must be a tilde estimate or a range, never a bare exact value")
    kelvin = report["lighting"].get("temperature_kelvin", "")
    if kelvin and report["lighting"]["basis"] == "inferred":
        if "~" not in kelvin and "-" not in kelvin and "–" not in kelvin:
            fail("inferred lighting.temperature_kelvin must be a tilde estimate or a range, never a bare exact value")

    anchors = d.get("visual_anchors")
    if not isinstance(anchors, list) or not (3 <= len(anchors) <= 5):
        fail("visual_anchors must contain 3 to 5 entries")
    for a in anchors:
        if a.get("basis") not in GRADES or not a.get("anchor"):
            fail("every visual anchor needs text and a basis grade")

    if d["mode"] == "style_only" and not (d.get("style_profile") or "").strip():
        fail("style_only mode requires a non-empty style_profile")

    print(f"[OK] {path} passed (mode={d['mode']}, palette_basis={d['palette_basis']}, "
          f"{len(anchors)} anchors, {len(report['textures'])} textures)")


if __name__ == "__main__":
    main()
