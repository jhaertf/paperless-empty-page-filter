# 📄 Paperless-ngx: Automatisches Entfernen leerer PDF-Seiten

> **Filtere automatisch leere, weiße oder fast-leere Seiten aus PDF-Dokumenten – bevor sie in Paperless-ngx archiviert werden.**

Mit diesem **Pre-consume Script** für Paperless-ngx entfernst du automatisch Seiten, die fast komplett weiß sind – z. B. leere Rückseiten von Dokumenten, Scan-Rahmen oder ungewollte Zwischenblätter.  
Das spart Speicherplatz, beschleunigt die Suche und verhindert unnötige Dokumente im Archiv.

---

## ✅ Warum das nützt

- **Keine leeren Seiten** im Archiv – saubere Dokumente.
- **Automatisch**: Läuft im Hintergrund, sobald ein PDF hochgeladen wird.
- **Konfigurierbar**: Thresholds, Crop-Ränder, Downsampling – perfekt für Scans.
- **Sicher**: Falls Fehler, bleibt das Original erhalten (Fallback).
- **Open Source & MIT-lizenziert** – frei nutzbar für Privat-, Firmen- und Bildungszwecke.

---

## ⚙️ Installation & Einbindung in Paperless-ngx

### 1. **Script speichern**

Lade das Script herunter und speichere es z. B. als:

```bash
/opt/docker/paperless/paperless-ngx/scripts/preconsume_empty_pages.py
```

Stelle sicher, dass es ausführbar ist:

```bash
chmod +x /opt/docker/paperless/paperless-ngx/scripts/preconsume_empty_pages.py
```

### 2. **Paperless-ngx Konfiguration (docker-compose.yml)**

Füge im `paperless-ngx`-Service die folgenden **Environment-Variablen** hinzu:

```yaml
environment:
  - PRE_CONSUME_SCRIPT=/opt/docker/paperless/paperless-ngx/scripts/preconsume_empty_pages.py
  - PRE_CONSUME_LOG_FILE=/tmp/preconsume.log
  - PRE_CONSUME_LOG_LEVEL=INFO

  # Anpassbare Parameter (Standardwerte)
  - PRE_CONSUME_THRESHOLD=5
  - PRE_CONSUME_WHITE_RATIO=0.98
  - PRE_CONSUME_DPI=150
  - PRE_CONSUME_DOWNSCALE=6
  - PRE_CONSUME_WHITE_CUTOFF=251

  # Optional: Rand-Cropping für Scan-Rahmen
  - PRE_CONSUME_CROP_PERCENT=0.04
  - PRE_CONSUME_CROP_PX=0
  - PRE_CONSUME_CROP_LEFT_PX=15
  - PRE_CONSUME_CROP_RIGHT_PX=15
  - PRE_CONSUME_CROP_TOP_PX=20
  - PRE_CONSUME_CROP_BOTTOM_PX=20
```

> 💡 **Tipp**: Die Variablen beginnen mit `PRE_CONSUME_` – damit sie nicht mit Paperless-Interne Variablen kollidieren.

### 3. **Neustart Paperless-ngx**

```bash
cd /opt/docker/paperless/paperless-ngx
docker-compose down && docker-compose up -d
```

### 4. **Log-Datei prüfen**

```bash
tail -f /tmp/preconsume.log
```

Nach dem Hochladen eines PDFs siehst du:

```log
[2026-01-29 21:34:12] INFO: Seite 3: entfernt (leer)
[2026-01-29 21:34:12] INFO: Summary: behalten=5, entfernt=1
```

---

## 🎛️ Konfigurations-Parameter (Erklärung)

| Variable | Default | Beschreibung |
|--------|---------|--------------|
| `PRE_CONSUME_THRESHOLD` | 5 | Wie weiß muss eine Seite sein? (0=black, 255=white) |
| `PRE_CONSUME_WHITE_RATIO` | 0.98 | Anteil weißer Pixel, um als "leer" zu gelten |
| `PRE_CONSUME_DPI` | 150 | Bildauflösung für Analyse (höher = genauer, aber langsamer) |
| `PRE_CONSUME_DOWNSCALE` | 6 | Reduziert Bildgröße zur Performance (z. B. 150 DPI → 25 DPI) |
| `PRE_CONSUME_WHITE_CUTOFF` | 251 | Ab welcher Helligkeit gilt ein Pixel als "weiß"? |
| `PRE_CONSUME_CROP_PERCENT` | 0.04 | Prozentsatz, der von allen Seiten abgeschnitten wird |
| `PRE_CONSUME_CROP_PX` | 0 | Pixel, die von allen Seiten abgeschnitten werden |
| `PRE_CONSUME_CROP_LEFT_PX` | 15 | Spezifischer linken Rand (überwiegt `CROP_PX`) |
| ... | ... | Alle `LEFT/RIGHT/TOP/BOTTOM`-Variablen funktionieren analog |

> ⚠️ **Tipp**: Bei gescannten Dokumenten mit Rahmen: `CROP_LEFT_PX=15`, `CROP_RIGHT_PX=15` → entfernt Rand-Abbildungen.

---

## 📂 Beispiel: Log-Ausgabe

```log
[2026-01-29 21:34:12] INFO: Starte Verarbeitung (v3: Rand-Cropping)
[2026-01-29 21:34:12] INFO: Datei: /opt/docker/paperless/paperless-ngx/data/documents/12345.pdf
[2026-01-29 21:34:12] INFO: Settings: dpi=150, threshold=5, white_ratio_min=0.98, downscale=6, white_cutoff=251
[2026-01-29 21:34:12] INFO: Crop: crop_percent=0.04, crop_px=0, per-side(px) L/R/T/B=15/15/20/20
[2026-01-29 21:34:13] INFO: Seite 1: behalten
[2026-01-29 21:34:13] INFO: Seite 2: entfernt (leer)
[2026-01-29 21:34:13] INFO: Summary: behalten=1, entfernt=1
[2026-01-29 21:34:13] INFO: PDF aktualisiert: /opt/docker/paperless/paperless-ngx/data/documents/12345.pdf
```

---

## 🔧 Troubleshooting

- **Keine Änderung?** → Prüfe `/tmp/preconsume.log` – dort steht genau, was passiert.
- **Zu viele Seiten entfernt?** → Setze `WHITE_RATIO` auf 0.95 oder niedriger.
- **Kein Logging?** → Prüfe `PRE_CONSUME_LOG_FILE`-Pfad und Schreibrechte.
- **PDF beschädigt?** → Das Script hat einen Fallback: Original bleibt unverändert, wenn etwas schiefgeht.

---

## 📜 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** veröffentlicht – siehe [LICENSE](LICENSE).

Du darfst es frei verwenden, modifizieren und verteilen – auch kommerziell.

---

## ❤️ Mitwirken

Falls du Verbesserungen hast – z. B. OCR-Integration, Bildvergleich oder Batch-Modus – erstelle einen Pull Request!

---

> 💬 **Hinweis**: Dieses Script läuft als **Pre-consume Hook** in Paperless-ngx. Es wird **vor der Archivierung** ausgeführt – also direkt nach dem Upload.