# 🐾 Tamagotchi Life: Yuyus Cozy Apartment & The Traveling Merchant

## 1. Vision & Projektziel (Version 1 / Web-App & Spiel)
Aus dem ursprünglichen reinen Desktop-Overlay entsteht ein eigenständiges, immersives Tamagotchi-Wohnungsspiel im Browser. Yuyu lebt in ihrem eigenen gemütlichen Apartment, läuft autonom im Raum umher, interagiert mit Möbeln und ihrem Kätzchen-Begleiter.
Draußen hält regelmäßig der reisende Händler mit seinem Wagen, bei dem seltene Einrichtungsgegenstände, Lichter und Snacks gekauft werden können.

---

## 2. Systemarchitektur & Datenfluss

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        BROWSER CANVAS ENGINE                           │
│  ┌──────────────────────┐  ┌─────────────────┐  ┌───────────────────┐  │
│  │ 🏠 Apartment Room    │  │ 🐾 Chibi Yuyu   │  │ 🐱 Kitty          │  │
│  │  - 6 Isometrische    │  │  - 81-Frame     │  │  - Follow / Sleep │  │
│  │    Zimmer (WebP)     │  │    Zustands-    │  │  - Garnknäuel     │  │
│  │  - Wetter-Overlay    │  │    maschine     │  │  - Schnurr-Audio  │  │
│  │  - Licht-Partikel    │  │  - Pathfinding  │  │  - Streicheln     │  │
│  └──────────────────────┘  └─────────────────┘  └───────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        GAME STATE & PROGRESSION                        │
│  ┌──────────────────────────────────┐ ┌──────────────────────────────┐ │
│  │ 🪙 Münzen (Coins)                │ │ ❤️ Herzen (Hearts)           │ │
│  │  - Sehr langsame, stetige        │ │  - Pflege-Währung            │ │
│  │    Generierung über Zeit (Idle)  │ │  - Verdient durch gute       │ │
│  │  - Belohnung für Minispiele      │ │    Versorgung (>80% Vitals), │ │
│  │  - Kauf von Basis-Snacks & Deko  │ │    Streicheln & Pausen       │ │
│  └──────────────────────────────────┘ └──────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 🎁 Zufällige Geschenk-Drops                                       │ │
│  │  - Bei hoher Zuneigung schenkt Yuyu ab und zu seltene Zimmer-Deko │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 🛒 DER REISENDE HÄNDLER (MERCHANT WAGON)               │
│  - Händler-Wagen & 4 animierte Posen (händler_vor_dem_wagen1..4.webp)  │
│  - Regal-Slots (basierend auf Markierungs-Template)                   │
│  - Wechselndes Sortiment: Zimmer-Möbel, Lampen, Pflanzen, Snacks      │
│  - Einkauf gegen Münzen 🪙 und Herzen ❤️                               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Asset-Verzeichnis (Assents/)
- **Zimmer (6 Hintergründe):** `zimmer.webp`, `zimmer2.webp`, `zimmer3.webp`, `zimmer4.webp`, `zimmer5.webp`, `zimmer6_xxx.webp`
- **Yuyu Chibi Sprites:** `yuyu_spritesheet.webp` (81 Frames), `hinfallen.webp`, `party_ball.webp`, `sauer.webp`, `schlafen.webp`, `trinken_essen.webp`
- **Kätzchen & Props:** `Katze_zubehör.webp`, `bett_lape_wasser_v2.webp`, `bett_lape_wasser.webp`
- **Lichter & Natur:** `plfanzen_patikel_lichter.webp`, `plfanzen_patikel_lichter_v2.webp`
- **Wetter:** `wind_wetter.webp`
- **Händler:** `händler_wagen.webp`, `händler_vor_dem_wagen1..4.webp`, `händler_wagen_makierung_...jpeg`

---

## 4. Meilensteine (Status)
- [x] Entfernung der alten Desktop-Overlay OS-Installation aus `~/.local`
- [x] 20-Minuten-Entwicklungs-Timer im Hintergrund gestartet
- [x] Alle 24 Sprites & Assets im Ordner `Assents/` bereitgestellt
- [ ] HTML5/Canvas Web-Game Client & Engine aufbauen
- [ ] Wohnungssystem mit isometrischer Begehbarkeit & Möbel-Anpassung
- [ ] Kätzchen-Begleiter mit KI, Interaktionen & Audio
- [ ] Tamagotchi-Kreislauf (Vitals, Füttern, Schlafen, Pausen)
- [ ] 2-Währungs-Ökonomie (🪙 langsame Münzen, ❤️ verdiente Herzen)
- [ ] Händler-Reisewagen mit zufällig wechselndem Warenangebot & Einkaufsmenü
- [ ] Geschenksystem für Zimmer-Deko
- [ ] Lokaler Webserver & One-Click Starter-Skript
