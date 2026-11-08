#!/usr/bin/env python3
"""Validate img-rev JSON reports (stdlib only).

Checks structure against references/report-schema.json by hand, plus the
skill's evidence rules: every inferred-capable group carries a basis grade,
palette has exactly 5 HEX colors with an honest palette_basis, inferred
optics or Kelvin readings must be written as a tilde or a range, a
style_only report must carry a subject-free style_profile, and a
person_swap report must carry a complete swap_spec (identity source,
named face panel, measured canvas size, at least two referential feature
points, expression handling, and a QA block with score and carried/lost
lists).
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
    if d.get("mode") not in ("report", "recreation", "style_only", "person_swap"):
        fail("mode must be report, recreation, style_only or person_swap")
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

    if d["mode"] == "person_swap":
        swap = d.get("swap_spec")
        if not isinstance(swap, dict):
            fail("person_swap mode requires a swap_spec object")
        for key in ("identity_source", "face_reference", "canvas_size"):
            if not (swap.get(key) or "").strip():
                fail(f"swap_spec.{key} is required in person_swap mode")
        points = swap.get("feature_points")
        if not isinstance(points, list) or len(points) < 2:
            fail("swap_spec.feature_points needs at least 2 referential feature points")
        if swap.get("expression_handling") not in ("with_face", "from_canvas"):
            fail("swap_spec.expression_handling must be with_face or from_canvas")
        attempt = swap.get("attempt")
        if not isinstance(attempt, int) or attempt < 1:
            fail("swap_spec.attempt must be a positive integer")
        qa = swap.get("qa")
        if not isinstance(qa, dict):
            fail("swap_spec.qa object is required in person_swap mode")
        score = qa.get("score")
        if not isinstance(score, (int, float)) or not (0 <= score <= 10):
            fail("swap_spec.qa.score must be a number between 0 and 10")
        for key in ("carried", "lost"):
            if not isinstance(qa.get(key), list) or not qa[key]:
                fail(f"swap_spec.qa.{key} needs at least one entry")

    print(f"[OK] {path} passed (mode={d['mode']}, palette_basis={d['palette_basis']}, "
          f"{len(anchors)} anchors, {len(report['textures'])} textures)")


if __name__ == "__main__":
    main()
