#!/usr/bin/env python3
"""
🧪 Automated Feature Test Suite for Desktop Pet Companion
Prüft alle Core-Module auf fehlerfreie Ausführung.
"""

import os
import sys
import unittest
import time
from pathlib import Path

# Add current directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import pet modules
from pet_desktop import (
    ConfigManager, RetroSoundSynthesizer, VoiceEngine, LLMEngine,
    TamagotchiEngine, PomodoroManager, BallGame, VOICES, HUD_THEMES
)

class TestDesktopPetSuite(unittest.TestCase):

    def setUp(self):
        self.config = ConfigManager()
        self.sfx = RetroSoundSynthesizer()
        self.voice = VoiceEngine(self.config, self.sfx)
        self.llm = LLMEngine(self.config)
        self.tamagotchi = TamagotchiEngine(self.config, self.llm, self.voice, self.sfx)

    def test_voices_config(self):
        self.assertEqual(len(VOICES), 4)
        for key in ["lola", "buster", "mimi", "klaus"]:
            self.assertIn(key, VOICES)
            self.assertIn("pitch", VOICES[key])
            self.assertIn("rate", VOICES[key])
            self.assertIn("espeak", VOICES[key])

    def test_hud_themes(self):
        self.assertEqual(len(HUD_THEMES), 4)
        for key in ["cyberpunk", "gameboy", "kawaii", "minimal"]:
            self.assertIn(key, HUD_THEMES)

    def test_sfx_generation(self):
        for name in ["happy", "level_up", "alert", "ball_catch", "sleep", "pomodoro", "purr", "dice", "fortune"]:
            path = RetroSoundSynthesizer.CACHE_DIR / f"{name}.wav"
            self.assertTrue(path.exists(), f"SFX {name}.wav was not generated")
            self.assertGreater(path.stat().st_size, 500)

    def test_progression_and_xp(self):
        old_xp = self.config.data.get("progression", {}).get("xp", 0)
        self.config.add_xp(50)
        new_xp = self.config.data.get("progression", {}).get("xp", 0)
        self.assertEqual(new_xp, old_xp + 50)

    def test_affection_progression(self):
        old_aff = self.config.data.get("progression", {}).get("affection", 50)
        self.tamagotchi.increase_affection(15)
        new_aff = self.config.data.get("progression", {}).get("affection", 50)
        self.assertEqual(new_aff, min(100, old_aff + 15))

    def test_mute_flags(self):
        self.config.set("sfx_muted", True)
        self.assertTrue(self.config.get("sfx_muted", False))
        self.config.set("voice_muted", True)
        self.assertTrue(self.config.get("voice_muted", False))

    def test_snacks_feeding(self):
        self.tamagotchi.hunger = 40.0
        msg, icon = self.tamagotchi.feed_snack("sandwich")
        self.assertGreaterEqual(self.tamagotchi.hunger, 80.0)
        self.assertEqual(icon, "🥪")

        self.tamagotchi.thirst = 30.0
        msg, icon = self.tamagotchi.feed_snack("water")
        self.assertGreaterEqual(self.tamagotchi.thirst, 75.0)
        self.assertEqual(icon, "🥤")

    def test_sleep_mode(self):
        self.assertFalse(self.tamagotchi.is_sleeping)
        is_sleeping = self.tamagotchi.toggle_sleep()
        self.assertTrue(is_sleeping)
        self.assertTrue(self.tamagotchi.is_sleeping)
        # Aufwecken
        is_sleeping = self.tamagotchi.toggle_sleep()
        self.assertFalse(is_sleeping)

    def test_ball_game_physics(self):
        ball = BallGame()
        self.assertFalse(ball.active)
        ball.throw(100.0, 100.0, 300.0)
        self.assertTrue(ball.active)
        initial_y = ball.y
        ball.update_physics(300.0)
        self.assertNotEqual(ball.y, initial_y)

    def test_llm_provider_detection(self):
        self.assertEqual(self.llm.detect_provider("AIzaSy123456789"), "gemini")
        self.assertEqual(self.llm.detect_provider("sk-123456789"), "openai")
        self.assertEqual(self.llm.detect_provider("sk-or-123456789"), "openrouter")
        self.assertEqual(self.llm.detect_provider("gsk_123456789"), "groq")

if __name__ == "__main__":
    unittest.main()
