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

### Available Variables

  ---------------------------------------------------------------------------
  Variable                   Default             Description
  -------------------------- ------------------- ----------------------------
  PRE_CONSUME_THRESHOLD      5                   Tolerance for near-white
                                                 pixels

  PRE_CONSUME_WHITE_RATIO    0.98                Minimum white area ratio to
                                                 classify page as empty

  PRE_CONSUME_WHITE_CUTOFF   251                 Brightness threshold

  PRE_CONSUME_DPI            150                 Render DPI

  PRE_CONSUME_DOWNSCALE      6                   Downscale factor

  PRE_CONSUME_CROP_LEFT      0                   Crop left

  PRE_CONSUME_CROP_RIGHT     0                   Crop right

  PRE_CONSUME_CROP_TOP       0                   Crop top

  PRE_CONSUME_CROP_BOTTOM    0                   Crop bottom
  ---------------------------------------------------------------------------

------------------------------------------------------------------------

## 🧩 Code Example (Detection Logic)

``` python
white_pixels = np.sum(img_array >= white_cutoff)
total_pixels = img_array.size
white_ratio = white_pixels / total_pixels

if white_ratio > white_ratio_threshold:
    # page is considered empty and removed
```

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
