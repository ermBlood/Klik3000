# Klik3000

Utilita pro automatické vyhledání tlačítka na obrazovce (template matching + multi-scale) a klikání v intervalu.

## Požadavky
- Python 3.10+
- `pip install -r requirements.txt`
- Obrázek šablony: `arrow.png`

## Použití
```bash
python main.py

    ESC ukončí běh.

    Interval zadáš při startu.

    Pokud se tlačítko nenajde, nabídne manuální výběr pozice.

    V průběhu smyčky validuje přítomnost tlačítka (malá ROI).

Poznámky

    Multi-scale seznam je v kódu (viz scale_list), lze upravit.

    Pokud DPI/zoom zlobí, zvaž rozšíření škál a ROI.


README by ChatGPT