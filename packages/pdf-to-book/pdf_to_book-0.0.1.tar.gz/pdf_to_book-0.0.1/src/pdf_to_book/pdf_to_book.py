"""
pdf_to_book.py

Produce a 2-up, duplex-ready booklet PDF from an input PDF.

Usage:
    python pdf_to_book.py input.pdf output.pdf [options]

Options:
    --paper {auto,letter,a4}    Output paper size. 'auto' (default) uses the input page rotated to landscape.
    --gutter-mm N              Inner gutter (mm) to leave for binding (default 6 mm).
    --margin-mm N              Outer/top/bottom margin in mm (default 4 mm).
    --zoom FACTOR              Page zoom factor (e.g. 1.2 = 120%). Default 1.0 (fit).
    --line                     Draw a vertical line down the middle of each sheet (fold/cut guide).
"""
import fitz # pymupdf
import argparse

def mm_to_pt(mm): 
    return mm * 72.0 / 25.4

def paper_size_from_name(name):
    name = name.lower()
    if name == "letter":
        return (11.0 * 72.0, 8.5 * 72.0)   # landscape (w,h)
    if name == "a4":
        w = mm_to_pt(297.0)
        h = mm_to_pt(210.0)
        return (w, h)
    raise ValueError("unknown paper")

def place_page(out_page, rect, src, pgnum, zoom):
    """Place one source page into a rect, with optional zoom"""
    if pgnum < 0 or pgnum >= src.page_count:
        return
    src_page = src[pgnum]
    src_rect = src_page.rect

    # scale factor to fit, then apply zoom
    scale_x = rect.width / src_rect.width
    scale_y = rect.height / src_rect.height
    scale = min(scale_x, scale_y) * zoom

    w = src_rect.width * scale
    h = src_rect.height * scale

    dx = rect.x0 + (rect.width - w) / 2
    dy = rect.y0 + (rect.height - h) / 2
    target = fitz.Rect(dx, dy, dx + w, dy + h)

    out_page.show_pdf_page(target, src, pgnum)

def draw_center_line(page, out_w, out_h):
    """Draw a vertical guide line at the center"""
    center_x = out_w / 2.0
    shape = page.new_shape()
    shape.draw_line((center_x, 0), (center_x, out_h))
    shape.finish(color=(0, 0, 0), width=0.5, fill=None)
    shape.commit()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="input PDF")
    p.add_argument("output", help="output PDF (2-up, duplex-ready)")
    p.add_argument("--paper", default="auto",
                   help="paper size: 'auto' (default), 'letter', or 'a4'")
    p.add_argument("--gutter-mm", type=float, default=6.0,
                   help="inner gutter in mm (default 6 mm)")
    p.add_argument("--margin-mm", type=float, default=4.0,
                   help="outer/top/bottom margin in mm (default 4 mm)")
    p.add_argument("--zoom", type=float, default=1.0,
                   help="page zoom factor (e.g. 1.2 = 120%%). Default 1.0")
    p.add_argument("--line", action="store_true",
                   help="draw vertical fold/cut guide line at center")
    args = p.parse_args()

    src = fitz.open(args.input)
    if src.page_count == 0:
        raise SystemExit("Input PDF has no pages.")

    orig_rect = src[0].rect
    orig_w, orig_h = orig_rect.width, orig_rect.height

    if args.paper == "auto":
        out_w, out_h = orig_h, orig_w
    else:
        out_w, out_h = paper_size_from_name(args.paper)

    gutter = mm_to_pt(args.gutter_mm)
    margin = mm_to_pt(args.margin_mm)

    # pad to multiple of 4
    while src.page_count % 4 != 0:
        src.new_page(width=orig_w, height=orig_h)

    n = src.page_count
    sheets = n // 4
    slot_w = out_w / 2.0

    out = fitz.open()

    for s in range(sheets):
        a = n - 1 - 2*s
        b = 0 + 2*s
        c = 0 + 2*s + 1
        d = n - 1 - (2*s + 1)

        # FRONT
        p_front = out.new_page(width=out_w, height=out_h)
        left_rect = fitz.Rect(margin, margin, slot_w - margin, out_h - margin)
        right_rect = fitz.Rect(slot_w + margin, margin, out_w - margin, out_h - margin)
        left_rect.x1 -= (gutter/2.0)
        right_rect.x0 += (gutter/2.0)
        place_page(p_front, left_rect, src, a, args.zoom)
        place_page(p_front, right_rect, src, b, args.zoom)
        if args.line:
            draw_center_line(p_front, out_w, out_h)

        # BACK
        p_back = out.new_page(width=out_w, height=out_h)
        left_rect_b = fitz.Rect(margin, margin, slot_w - margin - (gutter/2.0), out_h - margin)
        right_rect_b = fitz.Rect(slot_w + margin + (gutter/2.0), margin, out_w - margin, out_h - margin)
        place_page(p_back, left_rect_b, src, c, args.zoom)
        place_page(p_back, right_rect_b, src, d, args.zoom)
        if args.line:
            draw_center_line(p_back, out_w, out_h)

    out.save(args.output)
    out.close()
    src.close()
    print("Finished! Saved booklet 2-up PDF to:", args.output)
    print("Print duplex, 100% scale, no '2 pages per sheet'.")
    print("If backs flip wrong, switch 'flip on short edge' vs 'long edge'.")
    if args.line:
        print("Guide line drawn at center of each sheet.")

if __name__ == "__main__":
    main()

# Entry point for console_scripts (pip-installed usage)
def cli():
    """Console entry-point wrapper for setuptools/pyproject console_scripts."""
    main()