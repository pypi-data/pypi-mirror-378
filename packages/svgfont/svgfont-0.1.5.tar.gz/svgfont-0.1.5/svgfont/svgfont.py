"""
Simple SVG Font loader

© Daniel Berio (@colormotor) 2025 - ...

Some SVG loading code adpated from:
https://github.com/AnatomicMaps/flatmap-maker
SVGFont parsing code partially created with ChatGPT
"""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

import numpy as np
import svgpathtools as svg
from svgpathtools import Path, Line, QuadraticBezier, CubicBezier, Arc
from functools import reduce
import numbers

import os


class Glyph:
    """Glyph of a SVG font"""
    def __init__(self, ch, adv, beziers):
        self.ch = ch
        self.adv = float(adv)
        #self.polylines = polylines
        self.beziers = beziers


class Font:
    """A SVG font"""
    def __init__(self, family, units_per_em, glyphs, missing):
        self.family = family or ""
        self.units_per_em = float(units_per_em)
        self.scale = 1.0 / self.units_per_em
        self.glyphs = glyphs or {}
        self.missing = missing

    def get(self, ch):
        g = self.glyphs.get(ch)
        if g is not None:
            return g
        return self.missing if self.missing is not None else Glyph(None, 0.0, [])


def load_font(svg_font_file, tol=0.5):
    """
    Load an SVG `<font>` and convert each glyph outline into sequences of cubic Bezier curves.
    If `svg_font_file` does not end with “.svg”, it is resolved to a bundled font
    under `…/hershey/<name>.svg`.

    Args:
      svg_font_file: Path or short name of the SVG font file.
      tol: Maximum geometric deviation used when flattening curves to polylines,
        expressed in **font units** (smaller = more segments, higher fidelity).

    Returns:
      Font: An object with metadata and glyphs, where each `Glyph` has:
        - `ch`: unicode character (or `None` for missing-glyph)
        - `adv`: horizontal advance (font units)
        - `polylines`: list of NumPy arrays of shape (N, 2), one per subpath
    """

    if not svg_font_file.endswith(".svg"):
        svg_font_file = os.path.join(
            os.path.dirname(__file__), "hershey", svg_font_file + ".svg"
        )

    tree = ET.parse(svg_font_file)
    root = tree.getroot()
    ns_uri = root.tag.split("}")[0].strip("{")
    ns = {"svg": ns_uri} if ns_uri else {}

    font_elem = root.find(".//svg:font", ns) if ns else root.find(".//font")
    if font_elem is None:
        raise ValueError("No <font> element found in SVG.")

    default_adv = float(font_elem.get("horiz-adv-x", "1000"))

    ff = font_elem.find("svg:font-face", ns) if ns else font_elem.find("font-face")
    family = ff.get("font-family") if ff is not None else ""
    units_per_em = float(
        (ff.get("units-per-em") if ff is not None else "1000") or "1000"
    )

    glyphs = {}
    missing = None

    mg = (
        font_elem.find("svg:missing-glyph", ns)
        if ns
        else font_elem.find("missing-glyph")
    )
    if mg is not None:
        d = mg.get("d")
        if d is not None:
            path = svg.parse_path(d)
            paths = split_compound_path(path)
            adv = float(mg.get("horiz-adv-x", str(default_adv)))
            beziers = [path_to_bezier_chain(path) for path in paths]
            #polylines = [sample_bezier_chain(Cp, tol) for Cp in beziers]
            missing = Glyph(None, adv, beziers)

    glyph_elems = (
        font_elem.findall("svg:glyph", ns) if ns else font_elem.findall("glyph")
    )
    for g in glyph_elems:
        uni = g.get("unicode")
        d = g.get("d")
        if uni is None or d is None:
            continue
        adv = float(g.get("horiz-adv-x", str(default_adv)))
        polylines = []
        if d:
            path = svg.parse_path(d)
            paths = split_compound_path(path)
            beziers = [path_to_bezier_chain(path) for path in paths]
            #polylines = [sample_bezier_chain(Cp, tol) for Cp in beziers]

        glyphs[uni] = Glyph(uni, adv, beziers)

    return Font(family, units_per_em, glyphs, missing)



def text_width(text, font, size=1.0, letter_spacing=0.0, line_height=1.25):
    if type(font) == str:
        font = load_font(font, **kwargs)

    s = size / font.units_per_em
    x, y = 0, 0
    out = []
    w = 0
    for ch in text:
        if ch == "\n":
            x = pos[0]
            y -= line_height * size
            continue

        g = font.get(ch)
        x += (g.adv * s) + letter_spacing
        w = max(w, x - letter_spacing)
    return w


def text_paths(
    text,
    font,
    size=1.0,
    pos=[0, 0],
    box=None,
    padding=0,
    align="left",
    letter_spacing=0.0,
    line_height=1.0,
    tol=0.1,
    **kwargs,
):
    """Geneate text as a list of polylines

    Renders each glyph of `text` from an SVG font into one or more polylines.
    Characters are scaled to the requested `size` and optionally position at a
    starting position `pos`. If `box` is given, the resulting polylines are
    uniformly transformed to fit inside the rectangle (optionally padded
    according to `padding`).

    By default this function does adaptive sampling of the glyph Bezier curves,
    which will give straight segments for initially linear segments. If the
    `tol` parameter is set to zero, the function will return Bezier chains, i.e.
    sequences of cubic Bezier control points.

    Args:
        text (str):
            Unicode string to render. Newlines (`\\n`) start a new line.
        font (Font | str):
            A loaded `Font` object (from `load_font`) or a font name/path.
            If a string is provided, `load_font(font, **kwargs)` is called.
        size (float, default 1.0):
            Glyph scale in user units. Effective scale factor is
            `size / font.units_per_em`.
        pos (array-like of 2, default [0, 0]):
            Starting baseline position `[x0, y0]` in user units for the first line.
        box (array-like or None, default None):
            Optional target rectangle for the composed text; if provided,
            `transform_to_rect(polylines, box, padding)` is applied to the output.
        padding (float, default 0):
            Padding to apply when fitting into `box` (passed to `transform_to_rect`).
        letter_spacing (float, default 0.0):
            Additional advance added after each glyph, in user units.
        line_height (float, default 1.25):
            Line spacing as a multiple of `size`. Each newline moves the baseline
            by `line_height * size` in the negative Y direction.
        tol (float, default 0.5): Maximum geometric deviation used when flattening
            curves to polylines, expressed in **font units** (smaller = more segments, higher fidelity).
            If `0.0`, returns Bezier control points

        **kwargs:
            Extra keyword arguments forwarded to `load_font` when `font` is a string
            (e.g., `tol=...`).

    Returns:
        list[np.ndarray]:
            A list of polylines; each polyline is an `(N, 2)` NumPy array of
            `float64` in user units. Polylines are *open* (no duplicate
            start/end point).

    """
    if type(font) == str:
        font = load_font(font, **kwargs)

    s = size / font.units_per_em
    x, y = pos
    out = []

    lines = text.splitlines()

    for i, line in enumerate(lines):
        if align == "left":
            x = pos[0]
        else:
            w = text_width(line, font, size, letter_spacing, line_height)
            if align == "center":
                x = pos[0] - w / 2
            else:
                x = pos[0] - w

        y = pos[1] + (line_height * size) * i
        for ch in line:
            g = font.get(ch)
            if g.beziers:
                for P in g.beziers:
                    PP = P * s
                    PP = PP + [x, y]
                    if tol > 0:
                        out.append(sample_bezier_chain(PP, tol))
                    else:
                        out.append(PP)

            x += (g.adv * s) + letter_spacing

    if box is not None:
        out = transform_to_rect(out, box, padding)

    return out


def path_to_bezier_chain(path):
    """convert SVG path to a Bezier control points"""
    pieces = sum([to_bezier(piece) for piece in path], [])
    bezier = [pieces[0][0]] + sum([piece[1:] for piece in pieces], [])
    return np.vstack(bezier)


def path_to_polyline(path, tol):
    Cp = path_to_bezier_chain(path)
    return sample_bezier_chain(Cp, tol)


def split_compound_path(path):
    """Split compound paths, since svgpathtools does not do that by default"""
    import re

    split_paths = []
    s = path.d()
    # split at occurrences of moveto commands
    sub_d = filter(None, re.split("[Mm]", s))
    # indices (without moveto) of splits
    lens = [len(list(filter(None, re.split("[A-z]", d)))) - 1 for d in sub_d]
    # cum sum
    split_inds = [0] + reduce(lambda c, x: c + [c[-1] + x], lens, [0])[1:]
    split_paths += [svg.Path(*path[a:b]) for a, b in zip(split_inds, split_inds[1:])]
    return split_paths


def beziers_to_chain(beziers):
    """Convert list of Bezier curve segments to a piecewise bezier chain (shares vertices)"""
    n = len(beziers)
    chain = []
    for i in range(n):
        chain.append(list(beziers[i][:-1]))
    chain.append([beziers[-1][-1]])
    return np.array(sum(chain, []))


def to_bezier(piece):
    """convert a line or Bezier segment to control points"""
    one3d = 1.0 / 3
    if type(piece) == svg.path.Line:
        a, b = to_pt(piece.start), to_pt(piece.end)
        return [[a, a + (b - a) * one3d, b + (a - b) * one3d, b]]
    elif type(piece) == svg.path.CubicBezier:
        return [
            [
                to_pt(piece.start),
                to_pt(piece.control1),
                to_pt(piece.control2),
                to_pt(piece.end),
            ]
        ]
    elif type(piece) == svg.path.QuadraticBezier:
        QP0 = to_pt(piece.start)
        QP1 = to_pt(piece.control)
        QP2 = to_pt(piece.end)
        CP1 = QP0 + 2 / 3 * (QP1 - QP0)
        CP2 = QP2 + 2 / 3 * (QP1 - QP2)
        return [[QP0, CP1, CP2, QP2]]
    elif type(piece) == svg.path.Arc:
        bezs = sum([to_bezier(ap) for ap in cubic_beziers_from_arc(piece)], [])
        return bezs

    raise ValueError


def point_segment_distance(p, a, b):
    d = b - a
    # relative projection length
    u = np.dot(p - a, d) / np.dot(d, d)
    u = np.clip(u, 0, 1)

    proj = a + u * d
    return np.linalg.norm(proj - p)


def decasteljau(pts, bez, tol, level=0):
    if level > 12:
        return
    p1, p2, p3, p4 = bez
    p12 = (p1 + p2) * 0.5
    p23 = (p2 + p3) * 0.5
    p34 = (p3 + p4) * 0.5
    p123 = (p12 + p23) * 0.5
    p234 = (p23 + p34) * 0.5
    p1234 = (p123 + p234) * 0.5
    d = point_segment_distance(p1234[:2], p1[:2], p4[:2])
    if d > tol * tol:
        decasteljau(pts, [p1, p12, p123, p1234], tol, level + 1)
        decasteljau(pts, [p1234, p234, p34, p4], tol, level + 1)
    else:
        pts.append(p4)


def sample_bezier_chain(Cp, tol):
    ''' Sample a Bezier chain using Decasteljau's method'''
    Cp = np.array(Cp)
    pts = [Cp[0]]
    for i in range(0, len(Cp) - 1, 3):
        decasteljau(pts, Cp[i : i + 4], tol)
    return np.array(pts)


def to_segment(piece):
    """convert a line or Bezier segment to control points"""
    return [to_pt(piece.start), to_pt(piece.end)]


def to_pt(c):
    """convert complex number to np vector and flip Y"""
    return np.array([c.real, -c.imag])


def elliptic_arc_point(c, r, phi, eta):
    return complex(
        c.real
        + r.real * np.cos(phi) * np.cos(eta)
        - r.imag * np.sin(phi) * np.sin(eta),
        c.imag
        + r.real * np.sin(phi) * np.cos(eta)
        + r.imag * np.cos(phi) * np.sin(eta),
    )


def elliptic_arc_derivative(r, phi, eta):
    return complex(
        -r.real * np.cos(phi) * np.sin(eta) - r.imag * np.sin(phi) * np.cos(eta),
        -r.real * np.sin(phi) * np.sin(eta) + r.imag * np.cos(phi) * np.cos(eta),
    )


def cubic_bezier_control_points(c, r, phi, eta1, eta2):
    alpha = (
        np.sin(eta2 - eta1)
        * (np.sqrt(4 + 3 * np.power(np.tan((eta2 - eta1) / 2), 2)) - 1)
        / 3
    )
    P1 = elliptic_arc_point(c, r, phi, eta1)
    d1 = elliptic_arc_derivative(r, phi, eta1)
    Q1 = complex(P1.real + alpha * d1.real, P1.imag + alpha * d1.imag)
    P2 = elliptic_arc_point(c, r, phi, eta2)
    d2 = elliptic_arc_derivative(r, phi, eta2)
    Q2 = complex(P2.real - alpha * d2.real, P2.imag - alpha * d2.imag)
    return (P1, Q1, Q2, P2)


def cubic_beziers_from_arc(arc):
    r = arc.radius
    p1 = arc.start
    p2 = arc.end
    phi = geom.radians(arc.rotation)
    flagA = False  # arc.large_arc
    flagS = True  # arc.sweep
    # irint(arc)
    r_abs = complex(abs(r.real), abs(r.imag))
    d = complex((p1.real - p2.real), (p1.imag - p2.imag))
    p = complex(
        np.cos(phi) * d.real / 2 + np.sin(phi) * d.imag / 2,
        -np.sin(phi) * d.real / 2 + np.cos(phi) * d.imag / 2,
    )
    p_sq = complex(p.real**2, p.imag**2)
    r_sq = complex(r_abs.real**2, r_abs.imag**2)

    ratio = p_sq.real / r_sq.real + p_sq.imag / r_sq.imag
    if ratio > 1:
        scale = np.sqrt(ratio)
        r_abs = complex(scale * r_abs.real, scale * r_abs.imag)
        r_sq = complex(r_abs.real**2, r_abs.imag**2)

    dq = r_sq.real * p_sq.imag + r_sq.imag * p_sq.real
    pq = (r_sq.real * r_sq.imag - dq) / dq
    q = np.sqrt(max(0, pq))
    if flagA == flagS:
        q = -q

    cp = complex(
        q * r_abs.real * p.imag / r_abs.imag, -q * r_abs.imag * p.real / r_abs.real
    )
    c = complex(
        cp.real * np.cos(phi) - cp.imag * np.sin(phi) + (p1.real + p2.real) / 2.0,
        cp.real * np.sin(phi) + cp.imag * np.cos(phi) + (p1.imag + p2.imag) / 2.0,
    )

    lambda1 = svg_angle(
        complex(1, 0),
        complex((p.real - cp.real) / r_abs.real, (p.imag - cp.imag) / r_abs.imag),
    )
    delta = svg_angle(
        complex((p.real - cp.real) / r_abs.real, (p.imag - cp.imag) / r_abs.imag),
        complex((-p.real - cp.real) / r_abs.real, (-p.imag - cp.imag) / r_abs.imag),
    )
    delta = delta - 2 * np.pi * np.floor(delta / (2 * np.pi))
    if not flagS:
        delta -= 2 * np.pi
    lambda2 = lambda1 + delta

    t = lambda1
    dt = np.pi / 4
    curves = []
    while (t + dt) < lambda2:
        control_points = (
            cp for cp in cubic_bezier_control_points(c, r_abs, phi, t, t + dt)
        )
        curves.append(svg.CubicBezier(*control_points))
        t += dt
    control_points = (
        cp for cp in cubic_bezier_control_points(c, r_abs, phi, t, lambda2)
    )
    curves.append(svg.CubicBezier(*(tuple(control_points)[:3]), p2))
    return curves


def bounding_box(S, padding=0):
    """Axis ligned bounding box for a list of polylines
    Returns [min,max] list"""
    if not S:
        return np.array([0, 0]), np.array([0, 0])

    bmin = np.min([np.min(V, axis=0) for V in S if len(V)], axis=0)
    bmax = np.max([np.max(V, axis=0) for V in S if len(V)], axis=0)
    return [bmin - padding, bmax + padding]


def rect_in_rect(src, dst, padding=0.0, axis=None):
    """Fit src rect into dst rect, preserving aspect ratio of src, with optional padding"""
    dst = pad_rect(dst, padding)

    dst_w, dst_h = dst[1] - dst[0]
    src_w, src_h = src[1] - src[0]

    ratiow = dst_w / src_w
    ratioh = dst_h / src_h
    if axis == None:
        if ratiow <= ratioh:
            axis = 1
        else:
            axis = 0
    if axis == 1:  # fit vertically [==]
        w = dst_w
        h = src_h * ratiow
        x = dst[0][0]
        y = dst[0][1] + dst_h * 0.5 - h * 0.5
    else:  # fit horizontally [ || ]
        w = src_w * ratioh
        h = dst_h

        y = dst[0][1]
        x = dst[0][0] + dst_w * 0.5 - w * 0.5

    return rect(x, y, w, h)


def rect(x, y, w, h):
    return [np.array([x, y]), np.array([x + w, y + h])]


def rect_center(rect):
    return rect[0] + (rect[1] - rect[0]) / 2


def pad_rect(rect, pad):
    return np.array(rect[0]) + pad, np.array(rect[1]) - pad


def rect_size(rect):
    return np.array(rect[1]) - np.array(rect[0])


def rect_in_rect_transform(src, dst, padding=0.0, axis=None):
    """Return homogeneous transformation matrix that fits src rect into dst"""
    fitted = rect_in_rect(src, dst, padding, axis)

    cenp_src = rect_center(src)
    cenp_dst = rect_center(fitted)

    M = np.eye(3)
    M = np.dot(M, trans_2d(cenp_dst - cenp_src))
    M = np.dot(M, trans_2d(cenp_src))
    M = np.dot(M, scaling_2d(rect_size(fitted) / rect_size(src)))
    M = np.dot(M, trans_2d(-cenp_src))
    return M


def transform_to_rect(shape, rect, padding=0.0, offset=[0, 0], axis=None):
    """transform a shape or polyline to dest rect"""
    src_rect = bounding_box(shape)
    mat = trans_2d(offset) @ rect_in_rect_transform(src_rect, rect, padding, axis)
    return [affine_transform_polyline(mat, P) for P in shape]


def affine_transform_polyline(mat, P):
    dim = P.shape[1]
    P = np.vstack([np.array(P).T, np.ones(len(P))])
    P = mat @ P
    return P[:dim, :].T


def rot_2d(theta, affine=True):
    d = 3 if affine else 2
    m = np.eye(d)
    ct = np.cos(theta)
    st = np.sin(theta)
    m[0, 0] = ct
    m[0, 1] = -st
    m[1, 0] = st
    m[1, 1] = ct

    return m


def trans_2d(xy):
    m = np.eye(3)
    m[0, 2] = xy[0]
    m[1, 2] = xy[1]
    return m


def scaling_2d(xy, affine=True):
    d = 3 if affine else 2

    if is_number(xy):
        xy = [xy, xy]

    m = np.eye(d)
    m[0, 0] = xy[0]
    m[1, 1] = xy[1]


def rect_in_rect_transform(src, dst, padding=0.0, axis=None):
    """Return homogeneous transformation matrix that fits src rect into dst"""
    fitted = rect_in_rect(src, dst, padding, axis)

    cenp_src = rect_center(src)
    cenp_dst = rect_center(fitted)

    M = np.eye(3)
    M = np.dot(M, trans_2d(cenp_dst - cenp_src))
    M = np.dot(M, trans_2d(cenp_src))
    M = np.dot(M, scaling_2d(rect_size(fitted) / rect_size(src)))
    M = np.dot(M, trans_2d(-cenp_src))
    return M


def transform_to_rect(shape, rect, padding=0.0, offset=[0, 0], axis=None):
    """transform a shape or polyline to dest rect"""
    src_rect = bounding_box(shape)
    mat = trans_2d(offset) @ rect_in_rect_transform(src_rect, rect, padding, axis)
    return [affine_transform_polyline(mat, P) for P in shape]


def affine_transform_polyline(mat, P):
    dim = P.shape[1]
    P = np.vstack([np.array(P).T, np.ones(len(P))])
    P = mat @ P
    return P[:dim, :].T


def rot_2d(theta, affine=True):
    d = 3 if affine else 2
    m = np.eye(d)
    ct = np.cos(theta)
    st = np.sin(theta)
    m[0, 0] = ct
    m[0, 1] = -st
    m[1, 0] = st
    m[1, 1] = ct

    return m


def trans_2d(xy):
    m = np.eye(3)
    m[0, 2] = xy[0]
    m[1, 2] = xy[1]
    return m


def scaling_2d(xy, affine=True):
    d = 3 if affine else 2

    if is_number(xy):
        xy = [xy, xy]

    m = np.eye(d)
    m[0, 0] = xy[0]
    m[1, 1] = xy[1]
    return m


def is_number(x):
    return isinstance(x, numbers.Number)


def is_number(x):
    return isinstance(x, numbers.Number)
    return isinstance(x, numbers.Number)
