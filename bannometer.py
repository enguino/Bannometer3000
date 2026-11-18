import os
import re
import subprocess
import sys
import tempfile
import wave
import ctypes
import pygame

import numpy as np

# Konstanter
MODELL = "base"        # Prøv "small" dersom maskinen er rask nok
SPRAAK = "no"          # "no" for norsk, "en" for engelsk
OPPTAK_SEKUNDER = 10   # Endres til 30 når alt er klart
SAMPLERATE = 16000
MAC_MIKROFON = ":0"    # AVFoundation-nummer; endres ved behov

# Mikrofon og AI
_modell = None


def hent_modell():
    # Dette kan ta litt tid første gang
    global _modell
    if _modell is None:
        from faster_whisper import WhisperModel
        print("Laster Faster-Whisper...")
        _modell = WhisperModel(MODELL, device="cpu", compute_type="int8")
    return _modell


def transkriber(sekunder=OPPTAK_SEKUNDER):
    # Tar opp lyd og returnerer gjenkjent tekst
    print(f"Opptak starter nå ({sekunder} sekunder). Snakk normalt.")

    if sys.platform == "darwin":
        # macOS: FFmpeg bruker AVFoundation i stedet for PortAudio
        with tempfile.TemporaryDirectory() as mappe:
            lydfil = os.path.join(mappe, "opptak.wav")
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loglevel", "error",
                    "-f", "avfoundation", "-i", MAC_MIKROFON,
                    "-t", str(sekunder),
                    "-ar", str(SAMPLERATE), "-ac", "1",
                    "-c:a", "pcm_s16le", lydfil,
                ],
                check=True,
            )

            # Les WAV uten PyAV: unngår metadata_errors-feilen
            with wave.open(lydfil, "rb") as wav:
                if (wav.getframerate() != SAMPLERATE
                        or wav.getnchannels() != 1
                        or wav.getsampwidth() != 2
                        or wav.getcomptype() != "NONE"):
                    raise ValueError("Forventer WAV: mono, 16 kHz, 16-bit PCM")
                lyddata = wav.readframes(wav.getnframes())

            lyd = np.frombuffer(lyddata, dtype="<i2").astype(np.float32) / 32768.0
    else:
        # Windows og Linux: lyddata sendes direkte som NumPy-array
        import sounddevice as sd
        opptak = sd.rec(
            int(sekunder * SAMPLERATE),
            samplerate=SAMPLERATE,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        lyd = opptak[:, 0].copy()

    print("Analyserer tale ...")
    segmenter, _ = hent_modell().transcribe(
        lyd,
        language=SPRAAK,
        beam_size=5,
        condition_on_previous_text=False,
        vad_filter=False,
    )
    return " ".join(segment.text.strip() for segment in segmenter).strip()


# Liste med norske og engelske banneord – utvid selv!
BANNEORD = ["faen", "helvete", "dritt", "jævla", "satan", "fuck", "shit"]


def finn_banneord(tekst):
    # OPPGAVE 1:
    # Fullfør denne funksjonen.
    # Tips: re.findall(r"\b\w+\b", tekst.lower()) gir enkeltord.

    ordliste = re.findall(r"\b\w+\b", tekst.lower())
    treff = []
    for ord in ordliste:
        if ord in BANNEORD:
            treff.append(ord)
    return treff
    
def beregn_poeng(treff):
    # OPPGAVE 2:
    # Fullfør denne funksjonen.
    # Gi banneordene poeng.

    # return treff[0].count("*")

    telte_ord = set()
    poeng = 0

    for ord in treff:
        if ord not in telte_ord:
            poeng += len(ord)
            telte_ord.add(ord)

    return poeng


# def vis_resultat(navn, tekst, treff, poeng):
#     # OPPGAVE 3:ø
#     # Forbedre resultatvisningen.

#     # print("\n--- RESULTAT ---")
#     # print("Deltaker:", navn)
#     # print("Tekst:", tekst)
#     # print("Treff:", treff)
#     # print("Poeng:", poeng)
#     ctypes.windll.user32.MessageBoxW(0, f"Deltaker: {navn}\n" f"Tekst: {tekst}\n" f"Treff: {treff}\n" f"Poeng: {poeng}\n\n" f"Poeng er basert på antall bokstaver i et unikt banneord", "Resultat", 0
# )

# def vis_resultatet_pygame(navn, tekst, treff, poeng): 

#     pygame.init()

#     bredde = 800
#     høyde = 500
#     skjerm = pygame.display.set_mode((bredde, høyde))
#     pygame.display.set_caption("Test")
#     font = pygame.font.SysFont("Arial", 24)

#     linjer = [f"Deltaker: {navn}", "", f"Tekst: {tekst}", "", f"Treff: {treff}", "", f"Poeng: {poeng}" ]

#     while True: 
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#         skjerm.fill((240, 240, 240))

#         y = 20
#         for linje in linjer:
#             tekst_surface = font.render(linje, True, (0, 0, 0))
#             skjerm.blit(tekst_surface, (20, y))
#             y += 35

#         pygame.display.flip()

def vis_resultatet_pygame(navn, tekst, treff, poeng):

    pygame.init()

    skjerm = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("BANNOMETER 3000")

    klokke = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 28)
    stor_font = pygame.font.SysFont("Arial", 52, bold=True)

    # Dartskive
    senter_x = 640
    senter_y = 360

    maks_poeng = 25
    prosent = min(poeng / maks_poeng, 1)

    treff_radius = 220 * (1 - prosent)

    mål_x = senter_x + treff_radius
    mål_y = senter_y

    # Startposisjon til pilen
    pil_x = -200
    pil_y = 200

    pil_truffet = False

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Mørk bakgrunn
        skjerm.fill((35, 35, 40))

        # -----------------------------
        # VENSTRE PANEL
        # -----------------------------

        pygame.draw.rect(
            skjerm,
            (20, 20, 20),
            (30, 120, 250, 500),
            border_radius=15,
        )

        pygame.draw.rect(
            skjerm,
            (220, 180, 50),
            (30, 120, 250, 500),
            4,
            border_radius=15,
        )

        # -----------------------------
        # HØYRE PANEL
        # -----------------------------

        pygame.draw.rect(
            skjerm,
            (20, 20, 20),
            (1000, 120, 250, 500),
            border_radius=15,
        )

        pygame.draw.rect(
            skjerm,
            (220, 180, 50),
            (1000, 120, 250, 500),
            4,
            border_radius=15,
        )

        # -----------------------------
        # DARTSKIVE
        # -----------------------------

        pygame.draw.circle(skjem := skjerm, (25, 25, 25), (senter_x, senter_y), 220)

        pygame.draw.circle(skjem, (240, 240, 230), (senter_x, senter_y), 180)
        pygame.draw.circle(skjem, (40, 40, 40), (senter_x, senter_y), 140)

        pygame.draw.circle(skjem, (240, 240, 230), (senter_x, senter_y), 100)
        pygame.draw.circle(skjem, (180, 0, 0), (senter_x, senter_y), 50)

        pygame.draw.circle(skjem, (0, 150, 0), (senter_x, senter_y), 20)

        
        # -----------------------------
        # ANIMER PILEN
        # -----------------------------

        if not pil_truffet:

            pil_x += (mål_x - pil_x) * 0.03
            pil_y += (mål_y - pil_y) * 0.03

            if abs(pil_x - mål_x) < 1:
                pil_truffet = True

        if not pil_truffet:

            pygame.draw.line(
                skjerm,
                (180, 180, 180),
                (int(pil_x - 60), int(pil_y)),
                (int(pil_x), int(pil_y)),
                5,
            )

            pygame.draw.polygon(
                skjerm,
                (0, 120, 255),
                [
                    (pil_x + 10, pil_y),
                    (pil_x - 10, pil_y - 8),
                    (pil_x - 10, pil_y + 8),
                ],
            )

        if pil_truffet:

            pygame.draw.circle(
                skjerm,
                (25, 25, 25),
                (int(mål_x), int(mål_y)),
                5
            )

            pygame.draw.circle(
                skjerm,
                (180, 30, 30),
                (int(mål_x), int(mål_y)),
                2
            )

        # -----------------------------
        # TITTEL
        # -----------------------------

        tittel = stor_font.render(
            "BANNOMETER 3000",
            True,
            (220, 40, 40),
        )

        skjerm.blit(tittel, (420, 30))

        # -----------------------------
        # VENSTRE INFO
        # -----------------------------

        overskrift = font.render("DELTAKER", True, (255, 255, 255))
        skjerm.blit(overskrift, (50, 150))

        navn_txt = font.render(navn, True, (220, 220, 220))
        skjerm.blit(navn_txt, (50, 190))

        treff_overskrift = font.render("TREFF", True, (255, 255, 255))
        skjerm.blit(treff_overskrift, (50, 280))

        y = 325

        for ord in treff:
            txt = font.render(f"• {ord}", True, (220, 220, 220))
            skjerm.blit(txt, (50, y))
            y += 35

        if not treff:
            txt = font.render("Ingen treff", True, (220, 220, 220))
            skjerm.blit(txt, (50, y))

        # -----------------------------
        # POENGRANG
        # -----------------------------

        if poeng < 5:
            rang = "Mors beste barn"
            farge = (0, 255, 0)

        elif poeng < 10:
            rang = "Litt frustrert"
            farge = (255, 255, 0)

        elif poeng < 15:
            rang = "Sinnataggen"
            farge = (255, 140, 0)

        else:
            rang = "Jævelen"
            farge = (255, 0, 0)

        poeng_txt = stor_font.render(
            str(poeng),
            True,
            farge,
        )

        rang_txt = font.render(
            rang,
            True,
            farge,
        )

        skjerm.blit(poeng_txt, (1080, 220))
        skjerm.blit(rang_txt, (1030, 320))

        # -----------------------------
        # LITEN FORKLARING
        # -----------------------------

        forklaring = font.render(
            "Unike banneord gir poeng etter ordlengde",
            True,
            (220, 220, 220),
        )

        skjerm.blit(forklaring, (350, 660))

        pygame.display.flip()
        klokke.tick(60)

def test_better_profanity(tekst):
    # Sammenlign den engelske detektoren med egen ordliste
    from better_profanity import profanity
    print("\n--- BETTER-PROFANITY ---")
    print("Engelsk bibliotek oppdaget banning:", profanity.contains_profanity(tekst))
    print("Sensurert versjon:", profanity.censor(tekst))


def hovedprogram():
    print("=== BANNOMETER 3000 ===")
    print("1: Skriv inn testtekst (uten mikrofon)")
    print("2: Snakk i mikrofonen")
    valg = input("Velg 1 eller 2: ").strip()
    if valg not in ("1", "2"):
        print("Ugyldig valg.")
        return

    navn = input("Deltakernavn (frivillig/pseudonym): ").strip() or "Testperson"
    if valg == "1":
        tekst = input("Skriv testtekst: ").strip()
    else:
        input("Trykk ENTER når du er klar ...")
        try:
            tekst = transkriber()
        except Exception as feil:
            print("Mikrofon eller AI kunne ikke brukes:", feil)
            print("På Mac må FFmpeg være installert og mikrofonnummeret være riktig.")
            print("Sjekk mikrofontillatelse, eller test tekstmodus i mellomtiden.")
            return

    print("\nGjenkjent tekst:", tekst or "(ingen tale gjenkjent)")
    treff = finn_banneord(tekst)
    poeng = beregn_poeng(treff)
    vis_resultatet_pygame(navn, tekst, treff, poeng)
    print("\nOBS: 0 poeng er forventet før du har løst elevoppgavene.")

    # Kjøres automatisk etter hver analyse
    try:
        test_better_profanity(tekst)
    except ImportError:
        print("\nbetter-profanity er ikke installert. Kjør: pip install better-profanity")


if __name__ == "__main__":
    hovedprogram()
