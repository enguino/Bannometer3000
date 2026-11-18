 # Bannometer 3000

Oppgave 1 (finne banneord), oppgave 2 (beregne poeng) og oppgave 3 (forbedre resultatvisningen)
Utvid listen med dine selvvalgte banneord

## Filer

- `bannometer.py` 
- `requirements.txt` – Python-biblioteker som installeres med pip.

## Oppsett på Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python bannometer.py
```

Hvis PowerShell blokkerer aktivering, kan du bruke miljøets Python direkte:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe bannometer.py
```

## Oppsett på macOS

Mac-versjonen bruker FFmpeg med AVFoundation til mikrofonopptak. Installer FFmpeg først (krever Homebrew):

```bash
brew install ffmpeg
```

Opprett deretter Python-miljø og start programmet:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python bannometer.py
```

Gi Terminal (eller programmet som starter Python) mikrofontillatelse under **Systeminnstillinger → Personvern og sikkerhet → Mikrofon**. Mac-koden bruker lydinngang `:0` i FFmpeg; på andre Mac-er kan mikrofonnummeret være annerledes. Finn enhetene med:

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

Mac-opptaket lagres midlertidig som WAV, leses inn i NumPy og slettes automatisk etter bruk. Dette unngår en observert kompatibilitetsfeil mellom Faster-Whisper og PyAV ved direkte åpning av lydfil.

## Oppsett på Ubuntu/Linux

Installer eventuelt nødvendige systempakker:

```bash
sudo apt update
sudo apt install python3-venv libportaudio2
```

Deretter:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python bannometer.py
```

Windows og Linux bruker `sounddevice` til opptak. Mikrofon og lydoppsett kan variere mellom PC-er.

## Slik testes programmet

1. Velg **1** for tekstmodus. Prøv `faen og faen`. Programmet viser teksten, men gir **0 poeng** til oppgave 1 og 2 er løst.
2. Velg **2** for mikrofonopptak. Første gang må Faster-Whisper-modellen lastes ned fra internett. Etterpå kan talegjenkjenningen kjøres lokalt.
3. `better-profanity` kjøres **automatisk** etter analysen og viser om den engelske detektoren fant banning, samt en sensurert versjon av teksten. Den beregner ikke poeng.
4. Utvid listen `BANNEORD` med flere ord og skrivemåter.
5. Løs `finn_banneord()` (oppgave 1), `beregn_poeng()` (oppgave 2) og forbedre `vis_resultat()` (oppgave 3).
6. Endre `OPPTAK_SEKUNDER` fra 10 til 30 når alt fungerer.

## Viktig

- Bruk en støttet 64-bit Python-versjon. Python **3.13.16 er testet på macOS**; andre kombinasjoner av operativsystem og bibliotekversjoner kan kreve tilpasning.
- Whisper kan feilgjenkjenne eller utelate ord. Kontroller transkripsjonen ved testing.
- `better-profanity` er hovedsakelig engelskspråklig og er et bibliotek for deteksjon/sensur, ikke en norsk poengmotor.
- Bruk helst frivillige, lokale tester i små grupper. Innebygde mikrofoner kan fange opp andre personer.
- Programmet lagrer ikke opptak permanent. På Mac brukes en midlertidig lydfil som slettes; på Windows/Linux holdes opptaket i minnet. Programmet sender ikke navn eller transkribert tekst til en egen server, men modellnedlasting krever nettverk første gang.
