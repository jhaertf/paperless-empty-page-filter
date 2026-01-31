#!/usr/bin/env python3
import os
import sys
import logging
import tempfile
from pdf2image import convert_from_path
try:
    from pypdf import PdfReader, PdfWriter
except ModuleNotFoundError:
    from PyPDF2 import PdfReader, PdfWriter

PREFIX = "PRE_CONSUME_SCRIPT_"

def getenv_int(name: str, default: int, min_v=None, max_v=None) -> int:
    raw = os.getenv(PREFIX + name)
    if raw is None or raw == "":
        return default
    try:
        v = int(raw)
    except ValueError:
        logging.warning(f"ENV {PREFIX}{name}='{raw}' ist keine int-Zahl. Nutze Default={default}.")
        return default
    if min_v is not None and v < min_v:
        logging.warning(f"ENV {PREFIX}{name}={v} < {min_v}. Klemme auf {min_v}.")
        v = min_v
    if max_v is not None and v > max_v:
        logging.warning(f"ENV {PREFIX}{name}={v} > {max_v}. Klemme auf {max_v}.")
        v = max_v
    return v

def getenv_float(name: str, default: float, min_v=None, max_v=None) -> float:
    raw = os.getenv(PREFIX + name)
    if raw is None or raw == "":
        return default
    try:
        v = float(raw)
    except ValueError:
        logging.warning(f"ENV {PREFIX}{name}='{raw}' ist keine float-Zahl. Nutze Default={default}.")
        return default
    if min_v is not None and v < min_v:
        logging.warning(f"ENV {PREFIX}{name}={v} < {min_v}. Klemme auf {min_v}.")
        v = min_v
    if max_v is not None and v > max_v:
        logging.warning(f"ENV {PREFIX}{name}={v} > {max_v}. Klemme auf {max_v}.")
        v = max_v
    return v

def setup_logging():
    log_file = os.getenv(PREFIX + "LOG_FILE", "/tmp/preconsume.log")
    log_level_str = os.getenv(PREFIX + "LOG_LEVEL", "INFO").upper()
    level = getattr(logging, log_level_str, logging.INFO)
    log_dir = os.path.dirname(log_file) or "."
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
    )
    logging.info(f"Logging aktiv: level={log_level_str}, file={log_file}")

def crop_for_analysis(img, crop_percent: float, crop_px: int, crop_left_px: int, crop_right_px: int, crop_top_px: int, crop_bottom_px: int):
    """ Cropt nur für Analysezwecke. Priorität: 1) spezifische Seitenränder (LEFT/RIGHT/TOP/BOTTOM)_PX wenn gesetzt 2) CROP_PX (wenn > 0) 3) CROP_PERCENT (wenn > 0) """
    w, h = img.size
    # 1) Per-Side overrides
    if any(v > 0 for v in (crop_left_px, crop_right_px, crop_top_px, crop_bottom_px)):
        l = max(0, min(w - 1, crop_left_px))
        r = max(0, min(w - 1, crop_right_px))
        t = max(0, min(h - 1, crop_top_px))
        b = max(0, min(h - 1, crop_bottom_px))
        x0 = l
        y0 = t
        x1 = w - r
        y1 = h - b
    # 2) Fixed px crop
    elif crop_px > 0:
        c = max(0, crop_px)
        x0 = c
        y0 = c
        x1 = w - c
        y1 = h - c
    # 3) Percent crop
    else:
        p = max(0.0, crop_percent)
        cx = int(w * p)
        cy = int(h * p)
        x0 = cx
        y0 = cy
        x1 = w - cx
        y1 = h - cy

    # Fallback: wenn Crop zu aggressiv ist, nehme Original
    if x1 <= x0 + 1 or y1 <= y0 + 1:
        logging.warning(f"Crop zu aggressiv (box=({x0},{y0},{x1},{y1}) bei size={w}x{h}). Nutze Originalbild.")
        return img
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug(f" Crop-Box: ({x0},{y0},{x1},{y1}) von {w}x{h}")
    return img.crop((x0, y0, x1, y1))

def is_page_empty(image, threshold: int, white_ratio_min: float, downscale: int, white_cutoff: int, crop_percent: float, crop_px: int, crop_left_px: int, crop_right_px: int, crop_top_px: int, crop_bottom_px: int) -> bool:
    """ Prüft ob Seite nahezu leer ist: - optional Rand-Cropping (gegen Scannerrahmen / Schatten / Lochung) - Downsampling zur Performance - Histogramm zur Statistik """
    img = image.convert("L")
    # Rand-Cropping nur für Analyse
    if crop_percent > 0.0 or crop_px > 0 or any(v > 0 for v in (crop_left_px, crop_right_px, crop_top_px, crop_bottom_px)):
        img = crop_for_analysis(img, crop_percent, crop_px, crop_left_px, crop_right_px, crop_top_px, crop_bottom_px)
    # Downscale
    ds = max(1, downscale)
    w = max(1, img.width // ds)
    h = max(1, img.height // ds)
    img = img.resize((w, h))
    hist = img.histogram()
    total = sum(hist)
    if total == 0:
        return True
    avg = sum(i * c for i, c in enumerate(hist)) / total
    cutoff = max(0, min(255, white_cutoff))
    white_ratio = sum(hist[cutoff:256]) / total
    logging.debug(f" Analyse: avg={avg:.2f}, white_ratio={white_ratio:.3f}, cutoff={cutoff}, ds={ds}")
    return avg > (255 - threshold) and white_ratio > white_ratio_min

def main():
    setup_logging()
    input_pdf = os.getenv("DOCUMENT_WORKING_PATH")
    if not input_pdf:
        logging.error("Umgebungsvariable DOCUMENT_WORKING_PATH nicht gesetzt.")
        return 1
    if not os.path.exists(input_pdf):
        logging.error(f"Eingabedatei nicht gefunden: {input_pdf}")
        return 1

    # Core settings
    threshold = getenv_int("THRESHOLD", 5, min_v=0, max_v=255)
    white_ratio_min = getenv_float("WHITE_RATIO", 0.98, min_v=0.0, max_v=1.0)
    dpi = getenv_int("DPI", 150, min_v=50, max_v=600)
    downscale = getenv_int("DOWNSCALE", 6, min_v=1, max_v=50)
    white_cutoff = getenv_int("WHITE_CUTOFF", 251, min_v=0, max_v=255)

    # Crop settings
    crop_percent = getenv_float("CROP_PERCENT", 0.04, min_v=0.0, max_v=0.49)
    crop_px = getenv_int("CROP_PX", 0, min_v=0, max_v=2000)
    crop_left_px = getenv_int("CROP_LEFT_PX", 0, min_v=0, max_v=2000)
    crop_right_px = getenv_int("CROP_RIGHT_PX", 0, min_v=0, max_v=2000)
    crop_top_px = getenv_int("CROP_TOP_PX", 0, min_v=0, max_v=2000)
    crop_bottom_px = getenv_int("CROP_BOTTOM_PX", 0, min_v=0, max_v=2000)

    logging.info("Starte Verarbeitung (v3: Rand-Cropping)")
    logging.info(f" Datei: {input_pdf}")
    logging.info(
        f" Settings: dpi={dpi}, threshold={threshold}, white_ratio_min={white_ratio_min}, "
        f"downscale={downscale}, white_cutoff={white_cutoff}"
    )
    logging.info(
        f" Crop: crop_percent={crop_percent}, crop_px={crop_px}, "
        f"per-side(px) L/R/T/B={crop_left_px}/{crop_right_px}/{crop_top_px}/{crop_bottom_px}"
    )

    try:
        reader = PdfReader(input_pdf)
        images = convert_from_path(input_pdf, dpi=dpi)
        if len(images) != len(reader.pages):
            logging.warning(f"Seitenanzahl mismatch: images={len(images)} vs pdf_pages={len(reader.pages)}")
        logging.info(f"Gefundene Seiten: {len(images)}")

        writer = PdfWriter()
        kept_pages = 0
        removed_pages = 0

        for i, img in enumerate(images):
            page_num = i + 1
            empty = is_page_empty(
                img,
                threshold=threshold,
                white_ratio_min=white_ratio_min,
                downscale=downscale,
                white_cutoff=white_cutoff,
                crop_percent=crop_percent,
                crop_px=crop_px,
                crop_left_px=crop_left_px,
                crop_right_px=crop_right_px,
                crop_top_px=crop_top_px,
                crop_bottom_px=crop_bottom_px
            )
            if empty:
                removed_pages += 1
                logging.info(f" Seite {page_num}: entfernt (leer)")
            else:
                if i < len(reader.pages):
                    writer.add_page(reader.pages[i])
                    kept_pages += 1
                    logging.info(f" Seite {page_num}: behalten")
                else:
                    logging.warning(f" Seite {page_num}: nicht übernommen (Indexfehler)")

        logging.info(f"Summary: behalten={kept_pages}, entfernt={removed_pages}")

        if kept_pages == 0:
            logging.warning("Alle Seiten wurden als leer erkannt. Original bleibt unverändert.")
            return 0

        # Atomar ersetzen
        with tempfile.NamedTemporaryFile("wb", suffix=".pdf", delete=False, dir=os.path.dirname(input_pdf)) as tmp:
            writer.write(tmp)
            tmp_path = tmp.name
        os.replace(tmp_path, input_pdf)

        logging.info(f"PDF aktualisiert: {input_pdf}")
        logging.info("Verarbeitung abgeschlossen (Erfolg).")
        return 0

    except Exception as e:
        logging.error(f"Fehler bei Verarbeitung: {e}", exc_info=True)
        logging.warning("Fallback: Original-PDF unverändert belassen.")
        return 0

if __name__ == "__main__":
    sys.exit(main())