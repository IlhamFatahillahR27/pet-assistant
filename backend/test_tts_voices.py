import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))

from tts import get_available_voices
from settings_manager import settings_manager

class TestTTSVoiceFeatures(unittest.TestCase):
    def test_get_available_voices(self):
        voices = get_available_voices()
        self.assertIsInstance(voices, list)
        if len(voices) > 0:
            self.assertIn('id', voices[0])
            self.assertIn('name', voices[0])

    def test_update_tts_voice_setting(self):
        original_settings = settings_manager.get_settings()
        updated = settings_manager.update_settings({
            "tts": {
                "voice_id": "test_voice_sample",
                "volume": 0.8
            }
        })
        self.assertEqual(updated["tts"]["voice_id"], "test_voice_sample")
        self.assertEqual(updated["tts"]["volume"], 0.8)
        
        # Restore original settings
        settings_manager.update_settings(original_settings)

if __name__ == "__main__":
    unittest.main()
