/**
 * 🎵 RetroSoundEngine — Web Audio API Synthesizer
 * 100% Standalone (Pure Browser JS, no external audio files required)
 */
class RetroSoundEngine {
    constructor() {
        this.ctx = null;
        this.muted = false;
        this.volume = 0.6;
        this._initOnInteraction();
    }

    _initOnInteraction() {
        const unlock = () => {
            if (!this.ctx) {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                this.ctx = new AudioContext();
            }
            if (this.ctx.state === 'suspended') {
                this.ctx.resume();
            }
            window.removeEventListener('click', unlock);
            window.removeEventListener('keydown', unlock);
        };
        window.addEventListener('click', unlock);
        window.addEventListener('keydown', unlock);
    }

    _ensureCtx() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContext();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    playToneSequence(notes, type = 'sine') {
        if (this.muted) return;
        this._ensureCtx();
        if (!this.ctx) return;

        let startTime = this.ctx.currentTime;
        notes.forEach(({ freq, dur, vol = 0.3 }) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = type;
            osc.frequency.setValueAtTime(freq, startTime);

            gain.gain.setValueAtTime(vol * this.volume, startTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, startTime + dur);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(startTime);
            osc.stop(startTime + dur);

            startTime += dur * 0.85;
        });
    }

    // 🪙 Münzen-Klingen (Heller metallischer Doppelton)
    playCoin() {
        this.playToneSequence([
            { freq: 987.77, dur: 0.08, vol: 0.25 }, // B5
            { freq: 1318.51, dur: 0.22, vol: 0.35 } // E6
        ], 'sine');
    }

    // ❤️ Herzen-Glitzern (Magisches Arpeggio)
    playHeart() {
        this.playToneSequence([
            { freq: 523.25, dur: 0.07, vol: 0.25 }, // C5
            { freq: 659.25, dur: 0.07, vol: 0.30 }, // E5
            { freq: 783.99, dur: 0.08, vol: 0.35 }, // G5
            { freq: 1046.50, dur: 0.20, vol: 0.40 } // C6
        ], 'triangle');
    }

    // 🐱 Sanftes Schnurren & Kraulen (Vibrato-Welle)
    playPurr() {
        if (this.muted) return;
        this._ensureCtx();
        if (!this.ctx) return;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        const lfo = this.ctx.createOscillator();
        const lfoGain = this.ctx.createGain();

        const now = this.ctx.currentTime;
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(110, now);

        lfo.frequency.setValueAtTime(22, now); // 22 Hz Schnurr-Vibration
        lfoGain.gain.setValueAtTime(25, now);

        lfo.connect(osc.frequency);

        gain.gain.setValueAtTime(0.001, now);
        gain.gain.linearRampToValueAtTime(0.28 * this.volume, now + 0.15);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.85);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start(now);
        lfo.start(now);
        osc.stop(now + 0.85);
        lfo.stop(now + 0.85);
    }

    // 🥪 Knabbern / Munch
    playEat() {
        this.playToneSequence([
            { freq: 320, dur: 0.06, vol: 0.3 },
            { freq: 440, dur: 0.06, vol: 0.35 },
            { freq: 280, dur: 0.08, vol: 0.25 }
        ], 'square');
    }

    // 🥤 Schluck Wasser / Trinken
    playDrink() {
        this.playToneSequence([
            { freq: 600, dur: 0.07, vol: 0.2 },
            { freq: 750, dur: 0.08, vol: 0.25 },
            { freq: 900, dur: 0.12, vol: 0.3 }
        ], 'sine');
    }

    // ⭐ Level-Up / Jubel
    playLevelUp() {
        this.playToneSequence([
            { freq: 523.25, dur: 0.10, vol: 0.35 }, // C5
            { freq: 659.25, dur: 0.10, vol: 0.40 }, // E5
            { freq: 783.99, dur: 0.10, vol: 0.45 }, // G5
            { freq: 987.77, dur: 0.12, vol: 0.50 }, // B5
            { freq: 1046.50, dur: 0.14, vol: 0.55 }, // C6
            { freq: 1318.51, dur: 0.35, vol: 0.60 }  // E6
        ], 'triangle');
    }

    // 🎁 Geschenk öffnen (Glücksglocken)
    playGift() {
        this.playToneSequence([
            { freq: 880, dur: 0.10, vol: 0.3 },
            { freq: 1108.73, dur: 0.10, vol: 0.35 },
            { freq: 1318.51, dur: 0.12, vol: 0.4 },
            { freq: 1760, dur: 0.30, vol: 0.5 }
        ], 'sine');
    }

    // 🛒 Händler-Glocke (Ladenglocke)
    playMerchantChime() {
        this.playToneSequence([
            { freq: 1200, dur: 0.12, vol: 0.3 },
            { freq: 1600, dur: 0.25, vol: 0.4 }
        ], 'sine');
    }

    // 🐾 Schrittchen-Klick
    playStep() {
        this.playToneSequence([
            { freq: 240, dur: 0.025, vol: 0.08 }
        ], 'triangle');
    }
}

window.soundEngine = new RetroSoundEngine();
