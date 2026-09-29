#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenPets / Codex V2 Pet Catalog Manager & Downloader
Ermöglicht das Auflisten, Suchen und automatische Herunterladen von
offiziellen Companions aus dem OpenPets-Katalog (https://openpets.dev).
"""

import json
import urllib.request
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

CATALOG_URL = "https://openpets.dev/pets/catalog.v2.json"

def fetch_catalog() -> List[Dict[str, Any]]:
    """Lädt den offiziellen OpenPets V2 Katalog herunter"""
    req = urllib.request.Request(
        CATALOG_URL,
        headers={"User-Agent": "YuyuDesktopPet/2.0 (Linux; x86_64)"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("pets", [])

def download_and_install_pet(pet_id: str, target_dir: Optional[Path] = None) -> bool:
    """Lädt ein Pet herunter und installiert es in pets/<pet_id>"""
    if target_dir is None:
        target_dir = Path(__file__).resolve().parent / "pets" / pet_id
    
    pets = fetch_catalog()
    pet_meta = None
    for p in pets:
        if p.get("id") == pet_id:
            pet_meta = p
            break
            
    if not pet_meta:
        raise ValueError(f"Pet mit ID '{pet_id}' wurde im Katalog nicht gefunden.")
        
    zip_url = pet_meta.get("zip")
    if not zip_url:
        raise ValueError(f"Pet '{pet_id}' besitzt keine gültige Download-URL.")
        
    tmp_zip = target_dir.parent / f"{pet_id}_temp.zip"
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        req = urllib.request.Request(
            zip_url,
            headers={"User-Agent": "YuyuDesktopPet/2.0 (Linux; x86_64)"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp, open(tmp_zip, "wb") as f:
            f.write(resp.read())
            
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(tmp_zip, "r") as z:
            for member in z.namelist():
                filename = Path(member).name
                if filename in ["pet.json", "spritesheet.webp", "thumb.webp", "preview.webp"]:
                    with z.open(member) as src, open(target_dir / filename, "wb") as dst:
                        dst.write(src.read())
                        
        # Falls kein pet.json entpackt wurde, erzeuge ein valides
        meta_file = target_dir / "pet.json"
        if not meta_file.exists():
            clean_meta = {
                "id": pet_id,
                "displayName": pet_meta.get("displayName", pet_id.title()),
                "description": pet_meta.get("description", ""),
                "spriteVersionNumber": pet_meta.get("spriteVersionNumber", 2),
                "spritesheetPath": "spritesheet.webp"
            }
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(clean_meta, f, indent=2, ensure_ascii=False)
                
        return True
    finally:
        if tmp_zip.exists():
            try:
                tmp_zip.unlink()
            except Exception:
                pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        try:
            pets = fetch_catalog()
            print(f"Gefundene Pets im Katalog ({len(pets)} verfügbar):")
            for p in pets:
                print(f" - {p.get('id'):<25} | {p.get('displayName'):<20} | {p.get('description', '')[:50]}...")
        except Exception as e:
            print(f"Fehler beim Laden des Katalogs: {e}")
    elif len(sys.argv) > 2 and sys.argv[1] == "install":
        pid = sys.argv[2]
        print(f"Lade Pet '{pid}' herunter...")
        try:
            ok = download_and_install_pet(pid)
            print(f"Erfolgreich installiert in pets/{pid}!" if ok else "Installation fehlgeschlagen.")
        except Exception as e:
            print(f"Fehler: {e}")
    else:
        print("Verwendung: python3 catalog_downloader.py [list | install <pet_id>]")
