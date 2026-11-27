#!/usr/bin/env python3
"""Export F.Cu, In1.Cu, In2.Cu, B.Cu PDF->PNG renders and measure exact In1.Cu GND solidity (100% stdlib)."""

import subprocess
import sys
from pathlib import Path


def read_pgm(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    idx = 0

    def next_token() -> bytes:
        nonlocal idx
        while idx < len(data) and data[idx : idx + 1] in (b" ", b"\t", b"\r", b"\n", b"#"):
            if data[idx : idx + 1] == b"#":
                while idx < len(data) and data[idx : idx + 1] != b"\n":
                    idx += 1
            else:
                idx += 1
        start = idx
        while idx < len(data) and data[idx : idx + 1] not in (b" ", b"\t", b"\r", b"\n"):
            idx += 1
        return data[start:idx]

    magic = next_token()
    if magic != b"P5":
        raise ValueError(f"Expected P5 PGM, got {magic!r}")
    w = int(next_token())
    h = int(next_token())
    maxv = int(next_token())
    if maxv != 255:
        raise ValueError(f"Unexpected maxv {maxv}")
    idx += 1  # single whitespace byte after maxval
    return w, h, data[idx : idx + w * h]


def main():
    pcb_path = Path(sys.argv[1])
    out_dir = Path(".copperpilot/tmp/unit3_renders")
    out_dir.mkdir(parents=True, exist_ok=True)

    for lyr in ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]:
        pdf_p = out_dir / f"{lyr}.pdf"
        png_pfx = out_dir / lyr
        subprocess.run(
            [
                "/usr/bin/kicad-cli",
                "pcb",
                "export",
                "pdf",
                "--layers",
                f"{lyr},Edge.Cuts",
                "--mode-single",
                "-o",
                str(pdf_p),
                str(pcb_path),
            ],
            check=True,
        )
        # Crop directly to 180x115mm board [x=0..180mm, y=15..130mm] at 203.2 DPI (8 px/mm -> 1440 x 920 px)
        subprocess.run(
            [
                "/usr/bin/pdftoppm",
                "-png",
                "-singlefile",
                "-r",
                "203.2",
                "-x",
                "0",
                "-y",
                "120",
                "-W",
                "1440",
                "-H",
                "920",
                str(pdf_p),
                str(png_pfx),
            ],
            check=True,
        )

    bw_pdf = out_dir / "In1_bw.pdf"
    bw_pfx = out_dir / "In1_bw"
    subprocess.run(
        [
            "/usr/bin/kicad-cli",
            "pcb",
            "export",
            "pdf",
            "--layers",
            "In1.Cu",
            "--black-and-white",
            "--mode-single",
            "-o",
            str(bw_pdf),
            str(pcb_path),
        ],
        check=True,
    )
    # 508 DPI = exact 20.0 px/mm (0.05 mm/px)
    subprocess.run(
        ["/usr/bin/pdftoppm", "-gray", "-singlefile", "-r", "508", str(bw_pdf), str(bw_pfx)],
        check=True,
    )
    w, h, buf = read_pgm(out_dir / "In1_bw.pgm")
    print(f"In1_bw.pgm dimensions at 508 DPI (20 px/mm): {w} x {h}")

    def box_fill(x1: float, y1: float, x2: float, y2: float) -> float:
        c1, c2 = int(round(x1 * 20)), int(round(x2 * 20))
        r1, r2 = int(round(y1 * 20)), int(round(y2 * 20))
        total = (r2 - r1) * (c2 - c1)
        dark = 0
        for r in range(r1, r2):
            row = buf[r * w + c1 : r * w + c2]
            dark += sum(1 for px in row if px < 128)
        return 100.0 * dark / total

    def circle_fill(cx: float, cy: float, rad: float) -> float:
        r1, r2 = int((cy - rad - 0.5) * 20), int((cy + rad + 0.5) * 20)
        c1, c2 = int((cx - rad - 0.5) * 20), int((cx + rad + 0.5) * 20)
        rad2 = rad * rad
        total = 0
        dark = 0
        for r in range(r1, r2):
            dy2 = (r / 20.0 - cy) ** 2
            if dy2 > rad2:
                continue
            base = r * w
            for c in range(c1, c2):
                if (c / 20.0 - cx) ** 2 + dy2 <= rad2:
                    total += 1
                    if buf[base + c] < 128:
                        dark += 1
        return 100.0 * dark / total

    print(f"In1.Cu plane [2..178, 17..128] overall fill: {box_fill(2.0, 17.0, 178.0, 128.0):.2f}%")
    print(f"M1 FET row [13.5..66.5, 86.0..97.5] In1.Cu GND solidity: {box_fill(13.5, 86.0, 66.5, 97.5):.2f}%")
    print(f"M0 FET row [113.5..166.5, 86.0..97.5] In1.Cu GND solidity: {box_fill(113.5, 86.0, 166.5, 97.5):.2f}%")
    for name, (cx, cy) in [
        ("C_HF1", (158.4, 95.2)),
        ("C_HF2", (140.2, 95.2)),
        ("C_HF3", (121.4, 95.2)),
        ("C_HF4", (58.4, 95.2)),
        ("C_HF5", (40.2, 95.2)),
        ("C_HF6", (21.4, 95.2)),
    ]:
        print(
            f"{name} ({cx},{cy}) r=3.0mm solidity: {circle_fill(cx, cy, 3.0):.2f}%, "
            f"r=3.5mm solidity: {circle_fill(cx, cy, 3.5):.2f}%"
        )


if __name__ == "__main__":
    main()
