import os
from PIL import Image, ImageEnhance, ImageStat
from tqdm import tqdm
import numpy as np

# ==================================================
# FUNZIONE DI CONVERSIONE DA COLORE A B&W
# ==================================================
def convert_bw(img, mode):
    # Conversione base in luminanza
    gray = img.convert("L")
    np_img = np.array(gray).astype(np.float32)

    if mode == 1:
        # Range naturale (solo normalizzazione soft)
        min_l, max_l = np.min(np_img), np.max(np_img)
        if max_l > min_l:
            np_img = (np_img - min_l) / (max_l - min_l) * 255

    elif mode == 2:
        # Nero e bianco forzati
        min_l, max_l = np.min(np_img), np.max(np_img)
        np_img = (np_img - min_l) / max(max_l - min_l, 1) * 255

    elif mode == 3:
        # Percentili 10% - 90%
        low = np.percentile(np_img, 10)
        high = np.percentile(np_img, 90)
        np_img = (np_img - low) / max(high - low, 1) * 255

    np_img = np.clip(np_img, 0, 255).astype(np.uint8)
    return Image.fromarray(np_img)

# ==================================================
# FUNZIONE PRINCIPALE DI MIGLIORAMENTO (NON TOCCATA)
# ==================================================
def auto_migliora(img_path, out_path, tipo_foto,
                  do_brightness, do_contrast, do_saturation, do_whitebalance,
                  do_bw=False, bw_mode=1):

    img = Image.open(img_path)

    # --- Conversione di sicurezza ---
    if img.mode not in ["L", "RGB"]:
        img = img.convert("RGB")

    # 1️⃣ Bilanciamento del bianco (solo se RGB)
    if do_whitebalance and img.mode == "RGB":
        np_img = np.array(img).astype(np.float32)
        means = np.mean(np_img, axis=(0, 1))
        means = np.maximum(means, 1)
        scale = means.mean() / means
        np_img *= scale
        np_img = np.clip(np_img, 0, 255).astype(np.uint8)
        img = Image.fromarray(np_img)

    # 2️⃣ Luminosità
    if do_brightness:
        stat = ImageStat.Stat(img)
        mean_lum = stat.mean[0] if img.mode == "L" else sum(stat.mean[:3]) / 3
        factor = 128 / max(mean_lum, 1)
        factor = min(max(factor, 0.8), 1.5)
        img = ImageEnhance.Brightness(img).enhance(factor)

    # 3️⃣ Contrasto
    if do_contrast:
        min_pix, max_pix = img.getextrema()
        if isinstance(min_pix, tuple):  # RGB
            ranges = [(mx - mn) for mn, mx in zip(min_pix, max_pix)]
            contrast_factor = sum(255 / max(r, 1) for r in ranges) / 3
        else:  # L
            contrast_factor = 255 / max(max_pix - min_pix, 1)

        contrast_factor = min(max(contrast_factor, 0.8), 2.0)
        img = ImageEnhance.Contrast(img).enhance(contrast_factor)

    # 4️⃣ Saturazione (solo se rimane a colori)
    if do_saturation and not do_bw and img.mode == "RGB":
        hsv = img.convert("HSV")
        s_channel = hsv.split()[1]
        mean_s = ImageStat.Stat(s_channel).mean[0]
        if mean_s > 0:
            sat_factor = min(max(128 / mean_s, 1.0), 2.0)
            img = ImageEnhance.Color(img).enhance(sat_factor)

    # 5️⃣ Conversione finale in Bianco e Nero
    if do_bw:
        img = convert_bw(img, bw_mode)

    img.save(out_path)

# ==================================================
# INTERFACCIA UTENTE RINNOVATA
# ==================================================
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("===========================================")
    print("           AUTO-MIGLIORAMENTO IMMAGINI")
    print("===========================================\n")

    print("Questo programma ottimizza automaticamente una o più foto,")
    print("bilanciando colori, luminosità e contrasto in modo intelligente.\n")

    # --- Scelta cartelle ---
    folder_src = input("Inserisci il percorso della cartella SORGENTE (foto originali): ").strip('"')
    folder_dst = input("Inserisci il percorso della cartella DESTINAZIONE (foto corrette): ").strip('"')

    if not os.path.exists(folder_src):
        print("\Cartella sorgente non trovata. Controlla il percorso e riprova.")
        return

    if not os.path.exists(folder_dst):
        os.makedirs(folder_dst)
        print("Cartella di destinazione creata automaticamente.\n")

    # --- Tipo di foto ---
    print("\n   Le immagini sono a colori o in bianco e nero?")
    tipo_foto = input("   Digita 'c' per colori oppure 'b' per bianco/nero: ").strip().lower()

    # --- Scelte di miglioramento ---
    print("\n OPERAZIONI DISPONIBILI")
    print("   (puoi combinarle liberamente)\n")
    
    do_whitebalance = input("Correzione dominanti colore (white balance)? [s/n]: ").lower() == "s"
    do_brightness   = input("Migliora luminosità generale? [s/n]: ").lower() == "s"
    do_contrast     = input("Aumenta il contrasto? [s/n]: ").lower() == "s"
    do_saturation   = input("Migliora saturazione colori? [s/n]: ").lower() == "s"
    
    do_bw = input("\nConvertire il risultato finale in BIANCO E NERO? [s/n]: ").lower() == "s"
    
    bw_mode = 1
    if do_bw:
        print("\n STILE BIANCO E NERO:")
        print("  1) Naturale → morbido, realistico")
        print("  2) Forte     → nero e bianco puri")
        print("  3) Bilanciato→ ignora estremi (10%-90%)")
        bw_mode = int(input("  Scelta [1/2/3]: "))

    # --- Selezione file ---
    files = [f for f in os.listdir(folder_src)
             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.bmp'))]

    if not files:
        print("\n   Nessuna immagine trovata nella cartella sorgente.")
        return

    print(f"\n📸 Trovate {len(files)} immagini da elaborare.")
    print("  Inizio elaborazione...\n")

    # --- Elaborazione batch ---
    for f in tqdm(files, ncols=100, desc="Elaborazione"):
        in_file = os.path.join(folder_src, f)
        name, ext = os.path.splitext(f)
        out_file = os.path.join(folder_dst, f"{name} - edit{ext}")
        auto_migliora(in_file, out_file, tipo_foto,
            do_brightness, do_contrast, do_saturation, do_whitebalance,
            do_bw, bw_mode)

    print("\nTutte le immagini sono state elaborate con successo!")
    print(f"I file corretti si trovano in: {folder_dst}")
    print("\nGrazie per aver usato il miglioratore automatico di Matteo™")

# ==================================================
if __name__ == "__main__":
    main()

