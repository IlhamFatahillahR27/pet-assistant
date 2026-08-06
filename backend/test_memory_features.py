import os
import sys
import unittest

# Tambahkan direktori backend ke sys.path
sys.path.append(os.path.dirname(__file__))

from user_memory import UserMemoryManager
from settings_manager import settings_manager

class TestMemoryFeatures(unittest.TestCase):
    def setUp(self):
        # Menggunakan file memori terisolasi untuk pengujian
        self.test_file = os.path.join(os.path.dirname(__file__), "test_user_memory.json")
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.manager = UserMemoryManager(file_path=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_get_memories(self):
        mem1 = self.manager.add_memory("Pengguna biasa dipanggil Ilham", "identity")
        self.assertEqual(mem1["category"], "identity")
        self.assertEqual(mem1["fact"], "Pengguna biasa dipanggil Ilham")

        mem2 = self.manager.add_memory("Makanan favorit adalah Nasi Goreng", "preference")
        self.assertEqual(len(self.manager.get_all_memories()), 2)

    def test_duplicate_prevention(self):
        self.manager.add_memory("Hobi coding dan bermusik", "habit")
        self.manager.add_memory("Hobi coding dan bermusik", "habit")
        self.assertEqual(len(self.manager.get_all_memories()), 1)

    def test_delete_memory(self):
        mem = self.manager.add_memory("Bisa berbahasa Jepang", "general")
        self.assertEqual(len(self.manager.get_all_memories()), 1)
        deleted = self.manager.delete_memory(mem["id"])
        self.assertTrue(deleted)
        self.assertEqual(len(self.manager.get_all_memories()), 0)

    def test_clear_all_memories(self):
        self.manager.add_memory("Fakta 1", "general")
        self.manager.add_memory("Fakta 2", "general")
        self.manager.clear_all_memories()
        self.assertEqual(len(self.manager.get_all_memories()), 0)

    def test_context_string_formatting(self):
        self.manager.add_memory("Pengguna bernama Ilham", "identity")
        context_str = self.manager.get_memory_context_string()
        self.assertIn("MEMORI & KETAHUAN LOKAL PENGGUNA", context_str)
        self.assertIn("IDENTITY", context_str)
        self.assertIn("Pengguna bernama Ilham", context_str)

if __name__ == "__main__":
    unittest.main()
