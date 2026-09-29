/**
 * 🐾 Tamagotchi Life: Yuyus Cozy Apartment & The Traveling Merchant
 * Core Game Engine (Canvas 60 FPS, Isometric Rooms, Care Vitals, Merchant & Economy)
 */

// 1. ZIMMER-DEFINITIONEN (Aus den 6 isometrischen WebP-Dateien)
const ROOMS = [
    { id: "zimmer5", name: "🎮 Cyber Gaming Lounge", file: "assets/zimmer5.webp", desc: "Neon, Dual-Monitor PC, Gamer-Sessel & RGB Lights" },
    { id: "zimmer6_xxx", name: "✨ Cozy Pastel Studio", file: "assets/zimmer6_xxx.webp", desc: "Pastelltöne, Lichterketten, Plüschtiere & Kuschelecke" },
    { id: "zimmer2", name: "🛋️ Warm Loft & Relax Corner", file: "assets/zimmer2.webp", desc: "Rustikales Holz, Kaminofen & gemütliche Sofas" },
    { id: "zimmer3", name: "🧸 Chill Oasis & Bookshelf", file: "assets/zimmer3.webp", desc: "Bücherregale, Zimmerpflanzen & Leseecke" },
    { id: "zimmer4", name: "🌆 Sunset Studio & Retro Desk", file: "assets/zimmer4.webp", desc: "Abendstimmung, warmes goldenes Licht & Nostalgie" },
    { id: "zimmer", name: "🌸 Chibi Dream Bedroom", file: "assets/zimmer.webp", desc: "Traumhaftes Schlafzimmer mit weichen Decken" }
];

// 2. HÄNDLER-REGAL-SLOTS (Aus händler_wagen_makierung Template)
const MERCHANT_SLOTS = [
    { id: 1, left: 23.0, top: 44.1, width: 13.9, height: 24.8 },
    { id: 2, left: 3.8, top: 45.5, width: 17.1, height: 24.2 },
    { id: 3, left: 65.1, top: 45.7, width: 16.2, height: 21.5 },
    { id: 4, left: 84.3, top: 46.7, width: 10.7, height: 21.3 },
    { id: 5, left: 11.9, top: 61.6, width: 5.7, height: 11.4 },
    { id: 6, left: 30.1, top: 60.6, width: 6.7, height: 15.2 },
    { id: 7, left: 73.3, top: 60.6, width: 6.8, height: 12.2 },
    { id: 8, left: 91.0, top: 59.8, width: 5.1, height: 11.2 }
];

// 3. WAREN-KATALOG DES REISENDEN HÄNDLERS
const CATALOG_ITEMS = [
    { id: "bed_deluxe", name: "🛏️ Kuscheliges Plüschbett", type: "furniture", price: 45, currency: "coin", desc: "Erhöht die Schlaferholung von Yuyu", icon: "🛏️" },
    { id: "neon_lamp", name: "💡 Cyberpunk Schreibtischlampe", type: "decor", price: 30, currency: "coin", desc: "Spendet warmes Fokuslicht", icon: "💡" },
    { id: "monstera_plant", name: "🪴 Frische Monstera-Pflanze", type: "decor", price: 25, currency: "coin", desc: "Verbessert die Raumluft & Vitalität", icon: "🪴" },
    { id: "fairy_lights", name: "✨ Magische Lichterkette", type: "decor", price: 5, currency: "heart", desc: "Wunderschönes Glitzern für die Wände", icon: "✨" },
    { id: "magic_yarn", name: "🧶 Buntes Glöckchen-Garn", type: "kitty", price: 3, currency: "heart", desc: "Das Kätzchen liebt es heiß und innig!", icon: "🧶" },
    { id: "donut_tower", name: "🍩 Goldener Glasur-Donut", type: "snack", price: 15, currency: "coin", desc: "+35% Hunger & Sofort-Zuneigung", icon: "🍩" },
    { id: "espresso_mug", name: "☕ Feiner Espresso-Krug", type: "snack", price: 12, currency: "coin", desc: "+45% Energie für Yuyu", icon: "☕" },
    { id: "fountain_water", name: "🥤 Reines Bergquellwasser", type: "snack", price: 8, currency: "coin", desc: "+55% Hydration & Frische", icon: "🥤" },
    { id: "ps5_console", name: "🎮 Next-Gen Spielkonsole", type: "furniture", price: 12, currency: "heart", desc: "Yuyus Traum für die Gaming-Lounge", icon: "🎮" },
    { id: "cat_tree", name: "🐾 Luxus-Kratzbaum", type: "furniture", price: 8, currency: "heart", desc: "Perfekter Aussichtsplatz fürs Kätzchen", icon: "🐾" }
];

class GameEngine {
    constructor() {
        this.canvas = document.getElementById("game-canvas");
        this.ctx = this.canvas.getContext("2d");
        
        // Interner virtueller Canvas für gestochen scharfe Skalierung
        this.vWidth = 1200;
        this.vHeight = 750;
        this.canvas.width = this.vWidth;
        this.canvas.height = this.vHeight;

        // Spiel-Zustand & Ökonomie
        this.coins = 25;
        this.hearts = 8;
        this.vitals = {
            hunger: 88,
            thirst: 85,
            energy: 92,
            affection: 90
        };
        this.level = 1;
        this.xp = 0;
        this.currentRoom = "zimmer5";
        this.weather = "sunny"; // sunny, rain, night
        this.isSleeping = false;
        
        // Yuyu & Kitty State
        this.yuyu = {
            x: 600,
            y: 530,
            targetX: 600,
            targetY: 530,
            anim: "idle",
            frame: 0,
            dir: 1, // 1 = rechts, -1 = links
            speed: 2.2,
            blush: 0,
            blink: 0,
            eatingTimer: 0,
            currentSnack: null,
            speech: "Moin! Willkommen in unserem gemütlichen Zuhause! 🌸",
            speechTimer: 5.0
        };

        this.kitty = {
            x: 670,
            y: 540,
            targetX: 670,
            targetY: 540,
            anim: "idle",
            frame: 0,
            dir: 1,
            speed: 1.8,
            actionTimer: 0
        };

        // Inventar & Möbel
        this.inventory = ["bed_deluxe", "neon_lamp", "monstera_plant"];
        this.placedFurniture = [
            { id: "water_crate", x: 420, y: 560, w: 70, h: 70, icon: "🥤" },
            { id: "monstera_plant", x: 790, y: 530, w: 80, h: 90, icon: "🪴" },
            { id: "neon_lamp", x: 730, y: 480, w: 60, h: 75, icon: "💡" }
        ];

        // Partikel
        this.particles = [];
        this.dustMotes = [];
        this._initDustMotes();

        // Assets
        this.images = {};
        this.loadedCount = 0;
        this.totalAssets = 0;

        // Händler State
        this.merchantPoses = [
            "assets/händler_vor_dem_wagen1.webp",
            "assets/händler_vor_dem_wagen2.webp",
            "assets/händler_vor_dem_wagen3.webp",
            "assets/händler_vor_dem_wagen4.webp"
        ];
        this.currentMerchantPoseIdx = 0;
        this.currentShopStock = [];

        // Zeitgeber
        this.lastTime = performance.now();
        this.coinAccTime = 0;
        this.heartAccTime = 0;
        this.giftCheckTime = 0;

        this._loadSaveData();
        this._preloadAssets();
        this._initEvents();
        this._refreshShopStock();
    }

    _initDustMotes() {
        for (let i = 0; i < 28; i++) {
            this.dustMotes.push({
                x: Math.random() * this.vWidth,
                y: Math.random() * this.vHeight,
                size: Math.random() * 2.8 + 1.2,
                speedY: Math.random() * 0.25 + 0.1,
                phase: Math.random() * Math.PI * 2
            });
        }
    }

    _preloadAssets() {
        const assetList = [
            // Zimmer
            { key: "zimmer", src: "assets/zimmer.webp" },
            { key: "zimmer2", src: "assets/zimmer2.webp" },
            { key: "zimmer3", src: "assets/zimmer3.webp" },
            { key: "zimmer4", src: "assets/zimmer4.webp" },
            { key: "zimmer5", src: "assets/zimmer5.webp" },
            { key: "zimmer6_xxx", src: "assets/zimmer6_xxx.webp" },
            // Pet & Aktionen
            { key: "yuyu_spritesheet", src: "assets/yuyu_spritesheet.webp" },
            { key: "trinken_essen", src: "assets/trinken_essen.webp" },
            { key: "schlafen", src: "assets/schlafen.webp" },
            { key: "hinfallen", src: "assets/hinfallen.webp" },
            { key: "party_ball", src: "assets/party_ball.webp" },
            { key: "sauer", src: "assets/sauer.webp" },
            // Props & Kätzchen
            { key: "Katze_zubehör", src: "assets/Katze_zubehör.webp" },
            { key: "bett_lape_wasser_v2", src: "assets/bett_lape_wasser_v2.webp" },
            { key: "plfanzen_patikel_lichter", src: "assets/plfanzen_patikel_lichter.webp" },
            { key: "wind_wetter", src: "assets/wind_wetter.webp" },
            // Händler
            { key: "händler_wagen", src: "assets/händler_wagen.webp" },
            { key: "händler_1", src: "assets/händler_vor_dem_wagen1.webp" },
            { key: "händler_2", src: "assets/händler_vor_dem_wagen2.webp" },
            { key: "händler_3", src: "assets/händler_vor_dem_wagen3.webp" },
            { key: "händler_4", src: "assets/händler_vor_dem_wagen4.webp" }
        ];

        this.totalAssets = assetList.length;
        assetList.forEach(item => {
            const img = new Image();
            img.onload = () => {
                this.loadedCount++;
                if (this.loadedCount >= this.totalAssets) {
                    console.log("🐾 Alle WebP-Assets geladen! Spiel startet.");
                    document.getElementById("loading-overlay")?.classList.add("hidden");
                    requestAnimationFrame(this.gameLoop.bind(this));
                }
            };
            img.onerror = () => {
                console.warn("Fehler beim Laden von:", item.src);
                this.loadedCount++;
            };
            img.src = item.src;
            this.images[item.key] = img;
        });
    }

    _initEvents() {
        // Klick in den Raum -> Yuyu hinlaufen lassen oder Objekte anklicken
        this.canvas.addEventListener("click", (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const scaleX = this.vWidth / rect.width;
            const scaleY = this.vHeight / rect.height;
            const clickX = (e.clientX - rect.left) * scaleX;
            const clickY = (e.clientY - rect.top) * scaleY;

            // Klick auf das Kätzchen?
            const kDist = Math.hypot(clickX - this.kitty.x, clickY - this.kitty.y);
            if (kDist < 50) {
                this.petKitty();
                return;
            }

            // Klick auf Yuyu?
            const yDist = Math.hypot(clickX - this.yuyu.x, clickY - this.yuyu.y);
            if (yDist < 60) {
                this.petYuyu();
                return;
            }

            // Klick auf ein platziertes Möbelstück?
            for (const prop of this.placedFurniture) {
                if (Math.abs(clickX - prop.x) < 40 && Math.abs(clickY - prop.y) < 40) {
                    if (prop.id === "water_crate") {
                        this.feedSnack("water");
                        return;
                    }
                }
            }

            // Im Raum bewegen (Innerhalb des isometrischen Fußbodens)
            const clampedY = Math.max(480, Math.min(680, clickY));
            const clampedX = Math.max(220, Math.min(980, clickX));
            this.yuyu.targetX = clampedX;
            this.yuyu.targetY = clampedY;
            this.yuyu.dir = clampedX > this.yuyu.x ? 1 : -1;
            this.yuyu.anim = "walk";
            this.addParticle(clampedX, clampedY, "✨", "#38bdf8");
            window.soundEngine?.playStep();
        });
    }

    _loadSaveData() {
        try {
            const saved = localStorage.getItem("yuyu_tamagotchi_save");
            if (saved) {
                const data = JSON.parse(saved);
                this.coins = data.coins ?? 25;
                this.hearts = data.hearts ?? 8;
                this.vitals = data.vitals ?? this.vitals;
                this.level = data.level ?? 1;
                this.xp = data.xp ?? 0;
                this.currentRoom = data.currentRoom ?? "zimmer5";
                this.inventory = data.inventory ?? this.inventory;
                this.placedFurniture = data.placedFurniture ?? this.placedFurniture;
            }
        } catch (e) {
            console.error("Speicherstand konnte nicht geladen werden:", e);
        }
    }

    _saveData() {
        const data = {
            coins: this.coins,
            hearts: this.hearts,
            vitals: this.vitals,
            level: this.level,
            xp: this.xp,
            currentRoom: this.currentRoom,
            inventory: this.inventory,
            placedFurniture: this.placedFurniture
        };
        localStorage.setItem("yuyu_tamagotchi_save", JSON.stringify(data));
    }

    // =========================================================================
    // GAME LOOP (60 FPS)
    // =========================================================================
    gameLoop(now) {
        const dt = (now - this.lastTime) / 1000.0;
        this.lastTime = now;

        this.update(dt);
        this.render();

        requestAnimationFrame(this.gameLoop.bind(this));
    }

    update(dt) {
        // 1. Ökonomie: Münzen langsam anhäufen (alle 45 Sekunden +1 Münze)
        this.coinAccTime += dt;
        if (this.coinAccTime >= 45.0) {
            this.coinAccTime = 0;
            this.coins += 1;
            this.addParticle(this.yuyu.x + 20, this.yuyu.y - 80, "+1 🪙", "#fbbf24");
            window.soundEngine?.playCoin();
            this.showBanner("🪙 +1 Münze erhalten (Passiver Ertrag)");
        }

        // 2. Ökonomie: Herzen verdienen bei optimaler Pflege (> 80% Vitals)
        this.heartAccTime += dt;
        const avgVitals = (this.vitals.hunger + this.vitals.thirst + this.vitals.energy + this.vitals.affection) / 4;
        if (this.heartAccTime >= 90.0) {
            this.heartAccTime = 0;
            if (avgVitals >= 80) {
                this.hearts += 1;
                this.addParticle(this.yuyu.x - 20, this.yuyu.y - 80, "+1 ❤️", "#f43f5e");
                window.soundEngine?.playHeart();
                this.showBanner("❤️ +1 Herz verdient! (Exzellente Fürsorge)");
            }
        }

        // 3. Zufällige Geschenk-Drops von Yuyu fürs Zimmer
        this.giftCheckTime += dt;
        if (this.giftCheckTime >= 180.0) {
            this.giftCheckTime = 0;
            if (Math.random() < 0.40 && this.vitals.affection > 75) {
                this.triggerRoomGift();
            }
        }

        // 4. Vitals Zerfall (sehr sanft)
        this.vitals.hunger = Math.max(0, this.vitals.hunger - dt * 0.05);
        this.vitals.thirst = Math.max(0, this.vitals.thirst - dt * 0.08);
        this.vitals.energy = this.isSleeping ? Math.min(100, this.vitals.energy + dt * 0.6) : Math.max(0, this.vitals.energy - dt * 0.04);

        // 5. Yuyu Bewegung & Pfadfindung
        const dx = this.yuyu.targetX - this.yuyu.x;
        const dy = this.yuyu.targetY - this.yuyu.y;
        const dist = Math.hypot(dx, dy);

        if (dist > 5 && !this.isSleeping && this.yuyu.eatingTimer <= 0) {
            this.yuyu.x += (dx / dist) * this.yuyu.speed;
            this.yuyu.y += (dy / dist) * this.yuyu.speed;
            this.yuyu.anim = "walk";
            this.yuyu.frame += dt * 7.5;
        } else {
            if (this.yuyu.anim === "walk") {
                this.yuyu.anim = "idle";
            }
            this.yuyu.frame += dt * 3.5;
            // Zufälliges Spazierengehen
            if (Math.random() < 0.003 && !this.isSleeping && this.yuyu.eatingTimer <= 0) {
                this.yuyu.targetX = 260 + Math.random() * 680;
                this.yuyu.targetY = 500 + Math.random() * 160;
                this.yuyu.dir = this.yuyu.targetX > this.yuyu.x ? 1 : -1;
            }
        }

        // 6. Kätzchen folgt Yuyu mit sanftem Abstand
        const cdx = (this.yuyu.x + (this.yuyu.dir === 1 ? -60 : 60)) - this.kitty.x;
        const cdy = this.yuyu.y - this.kitty.y;
        const cDist = Math.hypot(cdx, cdy);

        if (cDist > 70 && !this.isSleeping) {
            this.kitty.x += (cdx / cDist) * this.kitty.speed;
            this.kitty.y += (cdy / cDist) * this.kitty.speed;
            this.kitty.anim = cdx > 0 ? "walk_right" : "walk_left";
            this.kitty.frame += dt * 6.5;
        } else {
            this.kitty.frame += dt * 2.8;
            this.kitty.actionTimer += dt;
            if (this.kitty.actionTimer > 6.0) {
                this.kitty.actionTimer = 0;
                const r = Math.random();
                this.kitty.anim = r < 0.4 ? "idle" : (r < 0.7 ? "groom" : "play_yarn");
            }
        }

        if (this.isSleeping) {
            this.kitty.anim = "sleep";
        }

        // 7. Timer & Effekte
        if (this.yuyu.eatingTimer > 0) {
            this.yuyu.eatingTimer -= dt;
        }
        if (this.yuyu.speechTimer > 0) {
            this.yuyu.speechTimer -= dt;
        }
        if (this.yuyu.blush > 0) {
            this.yuyu.blush -= dt;
        }

        // 8. Partikel updaten
        this.particles = this.particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.alpha -= dt * 0.9;
            return p.alpha > 0;
        });

        // 9. Staubpartikel / Lichtstaub
        this.dustMotes.forEach(m => {
            m.y -= m.speedY;
            if (m.y < 0) {
                m.y = this.vHeight;
                m.x = Math.random() * this.vWidth;
            }
        });

        // HUD updaten
        this._updateHUD();
    }

    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.vWidth, this.vHeight);

        // 1. Isometrisches Zimmer zeichnen
        const roomImg = this.images[this.currentRoom];
        if (roomImg && roomImg.complete) {
            ctx.drawImage(roomImg, 0, 0, this.vWidth, this.vHeight);
        } else {
            ctx.fillStyle = "#0f172a";
            ctx.fillRect(0, 0, this.vWidth, this.vHeight);
        }

        // 2. Wetter-Overlay & Lichtstimmung
        this._renderWeather();

        // 3. Platzierte Möbel im Zimmer
        this.placedFurniture.forEach(prop => {
            ctx.save();
            ctx.font = "42px sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            // Weicher Bodenschatten
            ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
            ctx.beginPath();
            ctx.ellipse(prop.x, prop.y + 20, 26, 9, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillText(prop.icon, prop.x, prop.y);
            ctx.restore();
        });

        // 4. Schlafendes Kuschelbett rendern (wenn Yuyu schläft)
        if (this.isSleeping) {
            const propsImg = this.images["bett_lape_wasser_v2"];
            if (propsImg && propsImg.complete) {
                const cw = propsImg.width / 8;
                const ch = propsImg.height / 11;
                ctx.drawImage(propsImg, 4 * cw, 1 * ch, 2 * cw, ch, this.yuyu.x - 70, this.yuyu.y - 25, 140, 75);
            }
        }

        // 5. Yuyu Chibi rendern
        this._renderYuyu();

        // 6. Kätzchen-Begleiter rendern
        this._renderKitty();

        // 7. Schwebende Partikel (Herzen, Münzen, Sterne)
        this.particles.forEach(p => {
            ctx.save();
            ctx.globalAlpha = Math.max(0, p.alpha);
            ctx.font = "bold 18px sans-serif";
            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 8;
            ctx.fillText(p.text, p.x, p.y);
            ctx.restore();
        });

        // 8. Schwebende Lichtstaub-Partikel (Ambient Cozy Glow)
        ctx.save();
        this.dustMotes.forEach(m => {
            const glow = (Math.sin(performance.now() * 0.002 + m.phase) + 1) / 2;
            ctx.fillStyle = `rgba(255, 240, 200, ${0.2 + glow * 0.4})`;
            ctx.beginPath();
            ctx.arc(m.x, m.y, m.size, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.restore();

        // 9. Sprechblase von Yuyu
        if (this.yuyu.speechTimer > 0 && !this.isSleeping) {
            this._renderSpeechBubble(this.yuyu.x, this.yuyu.y - 145, this.yuyu.speech);
        }
    }

    _renderYuyu() {
        const ctx = this.ctx;
        const sheet = this.images["yuyu_spritesheet"];
        if (!sheet || !sheet.complete) return;

        const FRAME_W = 192;
        const FRAME_H = 208;
        const scale = 0.65;
        const dw = FRAME_W * scale;
        const dh = FRAME_H * scale;
        const dx = this.yuyu.x - dw / 2;
        const dy = this.yuyu.y - dh;

        // Bodenschatten
        ctx.save();
        ctx.fillStyle = "rgba(0, 0, 0, 0.45)";
        ctx.beginPath();
        ctx.ellipse(this.yuyu.x, this.yuyu.y - 6, dw * 0.32, 10, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // Row/Col im Spritesheet
        let row = 0;
        let frames = 4;
        if (this.yuyu.anim === "walk") {
            row = this.yuyu.dir === 1 ? 1 : 2;
            frames = 4;
        } else if (this.isSleeping) {
            row = 3;
            frames = 2;
        }

        const col = Math.floor(this.yuyu.frame) % frames;
        const sx = col * FRAME_W;
        const sy = row * FRAME_H;

        ctx.drawImage(sheet, sx, sy, FRAME_W, FRAME_H, dx, dy, dw, dh);

        // Errötete Bäckchen beim Streicheln
        if (this.yuyu.blush > 0) {
            ctx.save();
            ctx.fillStyle = "rgba(244, 63, 94, 0.45)";
            ctx.beginPath();
            ctx.arc(this.yuyu.x - 14, dy + dh * 0.48, 7, 0, Math.PI * 2);
            ctx.arc(this.yuyu.x + 14, dy + dh * 0.48, 7, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Snack Munching Overlay
        if (this.yuyu.eatingTimer > 0 && this.yuyu.currentSnack) {
            ctx.save();
            ctx.font = "24px sans-serif";
            const bob = Math.sin(performance.now() * 0.015) * 4;
            ctx.fillText(this.yuyu.currentSnack, this.yuyu.x - 12, dy + dh * 0.65 + bob);
            ctx.restore();
        }
    }

    _renderKitty() {
        const ctx = this.ctx;
        const kSheet = this.images["Katze_zubehör"];
        if (!kSheet || !kSheet.complete) return;

        const cw = kSheet.width / 8;
        const ch = kSheet.height / 11;
        const kw = 64;
        const kh = 68;
        const kx = this.kitty.x - kw / 2;
        const ky = this.kitty.y - kh;

        // Kätzchen-Bodenschatten
        ctx.save();
        ctx.fillStyle = "rgba(0, 0, 0, 0.35)";
        ctx.beginPath();
        ctx.ellipse(this.kitty.x, this.kitty.y - 4, kw * 0.35, 7, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        let row = 3;
        let startCol = 0;
        let frames = 3;

        if (this.kitty.anim === "walk_right") {
            row = 2; startCol = 0; frames = 4;
        } else if (this.kitty.anim === "walk_left") {
            row = 2; startCol = 4; frames = 4;
        } else if (this.kitty.anim === "sleep") {
            row = 0; startCol = 2; frames = 2;
        } else if (this.kitty.anim === "groom") {
            row = 5; startCol = 0; frames = 4;
        } else if (this.kitty.anim === "play_yarn") {
            row = 4; startCol = 0; frames = 4;
        }

        const col = startCol + (Math.floor(this.kitty.frame) % frames);
        ctx.drawImage(kSheet, col * cw, row * ch, cw, ch, kx, ky, kw, kh);
    }

    _renderWeather() {
        const ctx = this.ctx;
        if (this.weather === "night") {
            ctx.fillStyle = "rgba(10, 15, 30, 0.45)";
            ctx.fillRect(0, 0, this.vWidth, this.vHeight);
        } else if (this.weather === "rain") {
            ctx.fillStyle = "rgba(15, 23, 42, 0.25)";
            ctx.fillRect(0, 0, this.vWidth, this.vHeight);
            // Sanfte Regenstriche
            ctx.strokeStyle = "rgba(56, 189, 248, 0.25)";
            ctx.lineWidth = 1.5;
            const now = performance.now() * 0.8;
            for (let i = 0; i < 40; i++) {
                const rx = (i * 32 + now * 2) % this.vWidth;
                const ry = (i * 24 + now * 5) % this.vHeight;
                ctx.beginPath();
                ctx.moveTo(rx, ry);
                ctx.lineTo(rx - 8, ry + 16);
                ctx.stroke();
            }
        }
    }

    _renderSpeechBubble(x, y, text) {
        const ctx = this.ctx;
        ctx.save();
        ctx.font = "bold 13px sans-serif";
        const metrics = ctx.measureText(text);
        const bw = Math.min(320, metrics.width + 24);
        const bh = 38;
        const bx = Math.max(20, Math.min(this.vWidth - bw - 20, x - bw / 2));
        const by = y;

        ctx.fillStyle = "rgba(15, 23, 42, 0.94)";
        ctx.strokeStyle = "#00d4ff";
        ctx.lineWidth = 1.8;
        ctx.shadowColor = "rgba(0, 212, 255, 0.4)";
        ctx.shadowBlur = 10;

        ctx.beginPath();
        ctx.roundRect(bx, by, bw, bh, 8);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.shadowBlur = 0;
        ctx.fillText(text, bx + bw / 2, by + bh / 2);
        ctx.restore();
    }

    // =========================================================================
    // SPIEL-AKTIONEN & INTERAKTIONEN
    // =========================================================================
    petYuyu() {
        this.yuyu.blush = 4.0;
        this.vitals.affection = Math.min(100, this.vitals.affection + 6);
        this.xp += 15;
        this._checkLevelUp();
        this.addParticle(this.yuyu.x, this.yuyu.y - 100, "💖 +15 XP", "#f43f5e");
        window.soundEngine?.playHeart();
        const quotes = [
            "Du bist so lieb zu mir! 💕",
            "Mhm, das kraulen tut gut! ✨",
            "Beste Pflege der Welt! 🌸"
        ];
        this.yuyu.speech = quotes[Math.floor(Math.random() * quotes.length)];
        this.yuyu.speechTimer = 3.5;
        this._saveData();
    }

    petKitty() {
        this.kitty.anim = "groom";
        this.kitty.actionTimer = 0;
        this.addParticle(this.kitty.x, this.kitty.y - 50, "🐾 Schnurr!", "#fbbf24");
        this.addParticle(this.kitty.x + 15, this.kitty.y - 70, "💖", "#f43f5e");
        window.soundEngine?.playPurr();
        this.vitals.affection = Math.min(100, this.vitals.affection + 4);
        this._saveData();
    }

    feedSnack(type) {
        if (type === "water") {
            this.vitals.thirst = Math.min(100, this.vitals.thirst + 45);
            this.yuyu.currentSnack = "🥤";
            this.yuyu.speech = "Aah, herrlich frisches Wasser! 💧";
            window.soundEngine?.playDrink();
            this.addParticle(this.yuyu.x, this.yuyu.y - 80, "+45% 💧", "#38bdf8");
        } else if (type === "coffee") {
            this.vitals.energy = Math.min(100, this.vitals.energy + 40);
            this.yuyu.currentSnack = "☕";
            this.yuyu.speech = "Kaffee-Boost aktiviert! Wach & fit! ⚡";
            window.soundEngine?.playDrink();
            this.addParticle(this.yuyu.x, this.yuyu.y - 80, "+40% ⚡", "#eab308");
        } else {
            this.vitals.hunger = Math.min(100, this.vitals.hunger + 40);
            this.yuyu.currentSnack = "🥪";
            this.yuyu.speech = "Mjam, köstlicher Snack! Danke dir! 😋";
            window.soundEngine?.playEat();
            this.addParticle(this.yuyu.x, this.yuyu.y - 80, "+40% 🥪", "#22c55e");
        }
        this.yuyu.eatingTimer = 2.5;
        this.yuyu.speechTimer = 3.5;
        this.xp += 10;
        this._checkLevelUp();
        this._saveData();
    }

    toggleSleep() {
        this.isSleeping = !this.isSleeping;
        if (this.isSleeping) {
            this.yuyu.speech = "Gute Nacht... Zzz... 💤";
            this.showBanner("💤 Yuyu schläft tief und fest (Energie lädt)");
        } else {
            this.yuyu.speech = "Guten Morgen! Fit für neue Abenteuer! ☀️";
            this.showBanner("☀️ Yuyu ist aufgewacht!");
            window.soundEngine?.playLevelUp();
        }
        this.yuyu.speechTimer = 3.0;
        this._saveData();
    }

    triggerRoomGift() {
        const giftPool = [
            { id: "fairy_lights", name: "✨ Magische Lichterkette", icon: "✨" },
            { id: "magic_yarn", name: "🧶 Buntes Glöckchen-Garn", icon: "🧶" },
            { id: "monstera_plant", name: "🪴 Frische Monstera-Pflanze", icon: "🪴" },
            { id: "neon_lamp", name: "💡 Cyberpunk Schreibtischlampe", icon: "💡" }
        ];
        const gift = giftPool[Math.floor(Math.random() * giftPool.length)];
        if (!this.inventory.includes(gift.id)) {
            this.inventory.push(gift.id);
        }
        this.yuyu.speech = `Schau mal! Ich habe ${gift.name} für unser Zimmer gefunden! 🎁✨`;
        this.yuyu.speechTimer = 5.0;
        this.addParticle(this.yuyu.x, this.yuyu.y - 100, `🎁 ${gift.name}`, "#d8b4fe");
        window.soundEngine?.playGift();
        this.showBanner(`🎁 Yuyu hat dir ein Geschenk fürs Zimmer gemacht: ${gift.name}!`);
        this._saveData();
    }

    switchRoom(roomId) {
        this.currentRoom = roomId;
        window.soundEngine?.playHappy?.();
        this.showBanner(`🏠 Umgezogen in: ${ROOMS.find(r => r.id === roomId)?.name}`);
        this._saveData();
    }

    _checkLevelUp() {
        const neededXp = this.level * 100;
        if (this.xp >= neededXp) {
            this.xp -= neededXp;
            this.level += 1;
            this.coins += 15;
            this.hearts += 5;
            this.addParticle(this.yuyu.x, this.yuyu.y - 120, `⭐ LEVEL ${this.level}!`, "#fbbf24");
            window.soundEngine?.playLevelUp();
            this.showBanner(`🎉 LEVEL UP! Du bist jetzt Level ${this.level}! (+15 🪙, +5 ❤️)`);
        }
    }

    // =========================================================================
    // HÄNDLER WAGEN & SHOP
    // =========================================================================
    _refreshShopStock() {
        // Wähle 8 zufällige Artikel für die 8 Slots
        const shuffled = [...CATALOG_ITEMS].sort(() => 0.5 - Math.random());
        this.currentShopStock = MERCHANT_SLOTS.map((slot, idx) => {
            const item = shuffled[idx % shuffled.length];
            return { slot, item };
        });
    }

    openMerchantWagon() {
        window.soundEngine?.playMerchantChime();
        this.currentMerchantPoseIdx = (this.currentMerchantPoseIdx + 1) % this.merchantPoses.length;
        const modal = document.getElementById("merchant-modal");
        modal?.classList.add("active");
        this.renderMerchantView();
    }

    renderMerchantView() {
        const container = document.getElementById("merchant-shelves-container");
        const charImg = document.getElementById("merchant-char-img");
        if (charImg) {
            charImg.src = this.merchantPoses[this.currentMerchantPoseIdx];
        }

        if (container) {
            container.innerHTML = "";
            this.currentShopStock.forEach(({ slot, item }) => {
                const el = document.createElement("div");
                el.className = "merchant-shelf-slot";
                el.style.left = `${slot.left}%`;
                el.style.top = `${slot.top}%`;
                el.style.width = `${slot.width}%`;
                el.style.height = `${slot.height}%`;
                el.title = `${item.name} (${item.price} ${item.currency === "coin" ? "Münzen" : "Herzen"})`;

                const currIcon = item.currency === "coin" ? "🪙" : "❤️";
                el.innerHTML = `
                    <div style="font-size: 1.3rem;">${item.icon}</div>
                    <div style="font-size: 0.65rem; font-weight: bold; color: #fbbf24;">${item.price} ${currIcon}</div>
                `;

                el.onclick = () => this.buyItem(item);
                container.appendChild(el);
            });
        }
    }

    buyItem(item) {
        if (item.currency === "coin") {
            if (this.coins < item.price) {
                alert(`Nicht genügend Münzen! Du benötigst ${item.price} 🪙.`);
                return;
            }
            this.coins -= item.price;
        } else {
            if (this.hearts < item.price) {
                alert(`Nicht genügend Herzen! Du benötigst ${item.price} ❤️.`);
                return;
            }
            this.hearts -= item.price;
        }

        if (!this.inventory.includes(item.id)) {
            this.inventory.push(item.id);
        }

        window.soundEngine?.playCoin();
        this.showBanner(`✓ Gekauft: ${item.name}!`);
        this.renderMerchantView();
        this._saveData();
    }

    // =========================================================================
    // UI HILFSMETHODEN
    // =========================================================================
    addParticle(x, y, text, color) {
        this.particles.push({
            x, y, text, color,
            vx: (Math.random() - 0.5) * 1.5,
            vy: -1.8,
            alpha: 1.0
        });
    }

    showBanner(text) {
        const b = document.getElementById("floating-banner");
        if (b) {
            b.innerText = text;
            b.classList.add("show");
            clearTimeout(this._bannerTimeout);
            this._bannerTimeout = setTimeout(() => b.classList.remove("show"), 3200);
        }
    }

    _updateHUD() {
        const coinEl = document.getElementById("hud-coins");
        const heartEl = document.getElementById("hud-hearts");
        const levelEl = document.getElementById("hud-level");
        const hungerFill = document.getElementById("vital-hunger");
        const thirstFill = document.getElementById("vital-thirst");
        const energyFill = document.getElementById("vital-energy");

        if (coinEl) coinEl.innerText = this.coins;
        if (heartEl) heartEl.innerText = this.hearts;
        if (levelEl) levelEl.innerText = `Lv. ${this.level}`;

        if (hungerFill) hungerFill.style.width = `${Math.floor(this.vitals.hunger)}%`;
        if (thirstFill) thirstFill.style.width = `${Math.floor(this.vitals.thirst)}%`;
        if (energyFill) energyFill.style.width = `${Math.floor(this.vitals.energy)}%`;
    }
}

// Globaler Spielstart
window.addEventListener("DOMContentLoaded", () => {
    window.game = new GameEngine();
});
