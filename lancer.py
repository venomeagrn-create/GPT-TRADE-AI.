"""Double-cliquez sur ce fichier pour lancer la démo (paper trading, aucun ordre réel).

Il lance la démo puis attend que vous appuyiez sur Entrée avant de fermer.
"""
import runpy
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    try:
        runpy.run_module("bot", run_name="__main__")
    except Exception as exc:  # affiche l'erreur au lieu de fermer la fenêtre
        print("Erreur :", exc)
    input("\nAppuyez sur Entrée pour fermer...")
