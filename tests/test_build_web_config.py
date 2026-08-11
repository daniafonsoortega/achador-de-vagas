import unittest

from scripts.build_web_config import validated_config


class ConfigTests(unittest.TestCase):
    def test_normalizes_valid_config(self):
        config = validated_config({
            "SUPABASE_URL": "https://abc-123.supabase.co/",
            "SUPABASE_ANON_KEY": "x" * 30,
            "TELEGRAM_BOT_USERNAME": "@MeuBot_123",
            "SUPPORT_EMAIL": "oi@example.com",
        })
        self.assertEqual(config["supabaseUrl"], "https://abc-123.supabase.co")
        self.assertEqual(config["telegramBotUsername"], "MeuBot_123")

    def test_rejects_placeholder_values(self):
        with self.assertRaises(ValueError):
            validated_config({})


if __name__ == "__main__":
    unittest.main()

