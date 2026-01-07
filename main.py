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

    # 1️⃣ Bilanciamento del bianco (prima di tutto)
    if do_whitebalance and img.mode == "RGB":
        np_img = np.array(img).astype(np.float32)
        means = np.mean(np_img, axis=(0, 1))
        means = np.maximum(means, 1)
        scale = means.mean() / means
        np_img *= scale
        np_img = np.clip(np_img, 0, 255).astype(np.uint8)
        img = Image.fromarray(np_img)

    # 🔲 Conversione Bianco e Nero
    if do_bw:
        img = convert_bw(img, bw_mode)

    # 2️⃣ Regolazione della luminosità
    if do_brightness:
        stat = ImageStat.Stat(img)
        if img.mode == "L":
            mean_lum = stat.mean[0]
        else:
            mean_lum = sum(stat.mean[:3]) / 3
        brightness_factor = 128 / max(mean_lum, 1)
        brightness_factor = min(max(brightness_factor, 0.8), 1.5)
        img = ImageEnhance.Brightness(img).enhance(brightness_factor)

    # 3️⃣ Regolazione del contrasto
    if do_contrast:
        if img.mode == "L":
            min_pix, max_pix = img.getextrema()
            contrast_factor = 255 / max(max_pix - min_pix, 1)
        else:
            channels = img.split()
            factors = []
            for ch in channels:
                min_pix, max_pix = ch.getextrema()
                factors.append(255 / max(max_pix - min_pix, 1))
            contrast_factor = sum(factors) / 3
            contrast_factor = min(max(contrast_factor, 0.8), 2.0)
        img = ImageEnhance.Contrast(img).enhance(contrast_factor)

    # 4️⃣ Saturazione (ultimo tocco)
    if do_saturation and tipo_foto == "c" and img.mode == "RGB":
        hsv = img.convert('HSV')
        s_channel = hsv.split()[1]
        mean_s = ImageStat.Stat(s_channel).mean[0]
        if mean_s > 0:
            saturation_factor = min(max(128 / mean_s, 1.0), 2.0)
            img = ImageEnhance.Color(img).enhance(saturation_factor)

    img.save(out_path)

# ==================================================
# INTERFACCIA UTENTE RINNOVATA
# ==================================================
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🎨 ===========================================")
    print("           AUTO-MIGLIORAMENTO IMMAGINI")
    print("=========================================== 🎨\n")

    print("Questo programma ottimizza automaticamente una o più foto,")
    print("bilanciando colori, luminosità e contrasto in modo intelligente.\n")

    # --- Scelta cartelle ---
    folder_src = input("📂 Inserisci il percorso della cartella SORGENTE (foto originali): ").strip('"')
    folder_dst = input("💾 Inserisci il percorso della cartella DESTINAZIONE (foto corrette): ").strip('"')

    if not os.path.exists(folder_src):
        print("\n❌ Cartella sorgente non trovata. Controlla il percorso e riprova.")
        return

    if not os.path.exists(folder_dst):
        os.makedirs(folder_dst)
        print("📁 Cartella di destinazione creata automaticamente.\n")

    # --- Tipo di foto ---
    print("\n   Le immagini sono a colori o in bianco e nero?")
    tipo_foto = input("   Digita 'c' per colori oppure 'b' per bianco/nero: ").strip().lower()

    # --- Scelte di miglioramento ---
    print("\n🔧 Scegli quali correzioni applicare (rispondi 's' o 'n'):\n")
    print("💡 Suggerimento: l’ordine ottimale è già gestito automaticamente!")

    do_whitebalance = input("   ➤ Bilanciare il bianco? [s/n]: ").strip().lower() == "s"
    do_brightness    = input("   ➤ Regolare la luminosità? [s/n]: ").strip().lower() == "s"
    do_contrast      = input("   ➤ Regolare il contrasto? [s/n]: ").strip().lower() == "s"
    do_saturation    = input("   ➤ Regolare la saturazione? [s/n]: ").strip().lower() == "s"
  
    do_bw = input("\n🔲 Convertire le immagini in Bianco e Nero? [s/n]: ").strip().lower() == "s"

    bw_mode = 1
    if do_bw:
        print("\n🖤 Scegli il tipo di Bianco e Nero:")
        print("   1️⃣ Naturale (range reale della foto)")
        print("   2️⃣ Contrastato (nero e bianco perfetti)")
        print("   3️⃣ Intelligente (10% - 90%)")
        bw_mode = int(input("   Selezione [1/2/3]: ").strip())

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

    print("\n✅ Tutte le immagini sono state elaborate con successo!")
    print(f"📁 I file corretti si trovano in: {folder_dst}")
    print("\nGrazie per aver usato il miglioratore automatico di Matteo™ 😎")

# ==================================================
if __name__ == "__main__":
    main()

