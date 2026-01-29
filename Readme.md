# Paperless Empty Page Filter

This repository provides a **pre-consume script for Paperless-ngx** that
automatically removes **blank, white, or nearly empty pages** from PDF
files before they are stored in the Paperless-ngx document archive.

It is designed for scanned documents where blank back pages, scan
borders, or empty sheets are common.

------------------------------------------------------------------------

## 🚀 Features

-   Detects blank or nearly blank pages based on pixel analysis\
-   Works as a Paperless-ngx **pre-consume hook**\
-   Fully configurable via environment variables\
-   Optional cropping before detection\
-   Safe fallback: original PDF is kept if processing fails\
-   MIT licensed

------------------------------------------------------------------------

## 🧠 Algorithm Overview

1.  Each page is rendered to an image (configurable DPI).
2.  Image is optionally cropped.
3.  Image is downscaled for faster processing.
4.  Pixels above a brightness threshold are considered "white".
5.  The ratio of white pixels is calculated.
6.  If the ratio exceeds the configured limit, the page is removed.
7.  Remaining pages are merged into a new PDF.

------------------------------------------------------------------------

## 📦 Requirements

-   Python 3.9+
-   pillow
-   pypdf
-   pdf2image
-   numpy

Install dependencies manually:

``` bash
pip install pillow pypdf pdf2image numpy
```

------------------------------------------------------------------------

## ⚙️ Installation

1.  Clone this repository:

``` bash
git clone https://github.com/jhaertf/paperless-empty-page-filter.git
```

2.  Make the script executable:

``` bash
chmod +x preconsume_empty_pages.py
```

3.  Configure it as pre-consume script in Paperless-ngx.

Example (Docker Compose):

``` yaml
environment:
  PRE_CONSUME_SCRIPT: /scripts/preconsume_empty_pages.py
```

------------------------------------------------------------------------

## 🧪 Standalone Usage (CLI)

You can also use the script without Paperless-ngx:

``` bash
python preconsume_empty_pages.py input.pdf output.pdf
```

Example:

``` bash
python preconsume_empty_pages.py scan.pdf cleaned.pdf
```

------------------------------------------------------------------------

## 🔧 Configuration

All parameters can be set via environment variables:

``` bash
export PRE_CONSUME_WHITE_RATIO=0.985
export PRE_CONSUME_WHITE_CUTOFF=250
export PRE_CONSUME_DPI=150
export PRE_CONSUME_DOWNSCALE=6
export PRE_CONSUME_CROP_TOP=50
export PRE_CONSUME_CROP_BOTTOM=50
```


------------------------------------------------------------------------

### 4. **Log-File**

```bash
tail -f /tmp/preconsume.log
```

Example log file: 

```log
[2026-01-29 21:34:12] INFO: Seite 3: entfernt (leer)
[2026-01-29 21:34:12] INFO: Summary: behalten=5, entfernt=1
```

---

## 🎛️ Configuration Parameters (Explanation)

| Variable | Default | Description |
|--------|---------|-------------|
| `PRE_CONSUME_THRESHOLD` | 5 | How white must a page be? (0 = black, 255 = white) |
| `PRE_CONSUME_WHITE_RATIO` | 0.98 | Ratio of white pixels required to be considered "empty" |
| `PRE_CONSUME_DPI` | 150 | Image resolution for analysis (higher = more accurate, but slower) |
| `PRE_CONE_DOWNSCALE` | 6 | Reduces image size for performance (e.g. 150 DPI → 25 DPI) |
| `PRE_CONSUME_WHITE_CUTOFF` | 251 | Brightness threshold at which a pixel is considered "white" |
| `PRE_CONSUME_CROP_PERCENT` | 0.04 | Percentage cropped from all sides |
| `PRE_CONSUME_CROP_PX` | 0 | Pixels cropped from all sides |
| `PRE_CONSUME_CROP_LEFT_PX` | 15 | Specific left crop (overrides `CROP_PX`) |
| ... | ... | All `LEFT/RIGHT/TOP/BOTTOM` variables work analogously |

> ⚠️ **Tip**: For scanned documents with borders: `CROP_LEFT_PX=15`, `CROP_RIGHT_PX=15` → removes border artifacts.

------------------------------------------------------------------------

## 🔧 Troubleshooting

- **No changes?** → Check `/tmp/preconsume.log` – it shows exactly what happened.
- **Too many pages removed?** → Set `WHITE_RATIO` to 0.95 or lower.
- **No logging?** → Check the `PRE_CONSUME_LOG_FILE` path and write permissions.
- **Corrupted PDF?** → The script has a fallback: the original file is kept if something goes wrong.

------------------------------------------------------------------------

## 📜 License

This project is released under the **MIT License** – see [LICENSE](LICENSE).

You are free to use, modify, and distribute it – including for commercial purposes.

------------------------------------------------------------------------

## ❤️ Contributing

If you have improvements – e.g. OCR integration, image comparison, or batch mode – feel free to open a pull request!


------------------------------------------------------------------------

## 🛡️ Error Handling

If any exception occurs during processing: - The script logs the error -
The original PDF is returned unchanged

This ensures zero data loss.

------------------------------------------------------------------------

## 📄 Typical Use Cases

-   Duplex scans with single-sided content\
-   Large batch imports\
-   Scanners that add trailing blank pages\
-   Removing scan margins before OCR

------------------------------------------------------------------------

## 📜 License

MIT License

------------------------------------------------------------------------

> 💬 **Note**: This script runs as a **pre-consume hook** in Paperless-ngx. It is executed **before archiving** – right after upload.
