# Skidspår Väst AI Agent ❄️

En AI-driven agent som visar status och snödjup för skidspår i Västra Götaland (Billingen, Ulricehamn m.fl.) baserat på rapporter från Skidspår.se.

## Hur det fungerar
1. **Python-skriptet** (`scraper.py`) hämtar data från Skidspår.se.
2. Datat sparas i `data.json`.
3. **Frontend** (`index.html`) visar upp datat snyggt.
4. **GitHub Actions** (`.github/workflows/main.yml`) kör skriptet automatiskt var 4:e timme.

## Installation / Kör lokalt
1. Installera Python:
   ```bash
   pip install -r requirements.txt
   ```
2. Kör skrapan:
   ```bash
   python scraper.py
   ```
3. Öppna `index.html` i din webbläsare (obs: för att se data lokalt kan du behöva köra en lokal server pga webbläsares säkerhetsinställningar, t.ex. `python -m http.server`).

## Publicera på GitHub
Eftersom detta projekt ska hostas på GitHub Pages:

1. Ladda upp alla filer till ditt GitHub-repo.
2. Gå till **Settings** -> **Pages**.
3. Välj `main` branch och klicka Save.
4. Klart! Din sida uppdateras nu automatiskt.
