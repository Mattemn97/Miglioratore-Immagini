# 🎨 Auto-Miglioramento Immagini
Uno script Python interattivo che ottimizza automaticamente foto singole o intere cartelle di immagini, regolando **bilanciamento del bianco**, **luminosità**, **contrasto** e **saturazione** in modo intelligente e non distruttivo.  
Sviluppato da **Matteo Filippini**.

---

## 🚀 Funzionalità principali
- ✅ Bilanciamento automatico del bianco (correzione delle dominanti di colore)  
- ✅ Regolazione dinamica della luminosità in base alla media dei pixel  
- ✅ Miglioramento del contrasto per immagini più nitide  
- ✅ Aumento controllato della saturazione (solo per foto a colori)  
- ✅ Elaborazione batch di intere cartelle con **barra di progresso** (tqdm)  
- ✅ Interfaccia da terminale chiara e guidata  

---

## 🧩 Requisiti
Assicurati di avere **Python 3.8+** installato.  
Installa le dipendenze richieste con:

```bash
pip install pillow tqdm numpy
```

## 📂 Come usare
1. Salva lo script come main.py
2. Apri il terminale nella cartella in cui si trova lo script
3. Esegui:
4. 
```bash
python main.py
```

5. Segui le istruzioni sullo schermo:
- Inserisci la cartella sorgente con le foto originali
- Inserisci la cartella destinazione dove verranno salvate le foto corrette
- Indica se le immagini sono a colori (c) o in bianco e nero (b)
- Scegli quali correzioni applicare (bilanciamento bianco, luminosità, contrasto, saturazione)

Durante l’elaborazione, una barra di avanzamento mostrerà il progresso di ciascun file.

---

## 💡 Output
Per ogni immagine nella cartella sorgente, verrà generato un nuovo file nella cartella destinazione con il suffisso - edit.

Esempio:
```
foto1.jpg  ➜  foto1 - edit.jpg
foto2.png  ➜  foto2 - edit.png
```

## ⚙️ Logica di miglioramento
L’algoritmo applica le correzioni in questo ordine ottimale:

1. Bilanciamento del bianco → rimuove dominanti di colore indesiderate
2. Luminosità → ottimizza la chiarezza generale
3. Contrasto → enfatizza differenze luminose
4. Saturazione → aggiunge vivacità alle foto a colori

Ogni regolazione è auto-adattiva, calcolata in base ai valori statistici dell’immagine.

---

## 📸 Esempio di utilizzo
```bash
📂 Inserisci il percorso della cartella SORGENTE (foto originali): ./input
💾 Inserisci il percorso della cartella DESTINAZIONE (foto corrette): ./output
Le immagini sono a colori o in bianco e nero? c
➤ Bilanciare il bianco? [s/n]: s
➤ Regolare la luminosità? [s/n]: s
➤ Regolare il contrasto? [s/n]: s
➤ Regolare la saturazione? [s/n]: s
📸 Trovate 27 immagini da elaborare.
Elaborazione: 100%|█████████████████████████████| 27/27
✅ Tutte le immagini sono state elaborate con successo!
```