import os
import sys
import types
import unittest

os.environ.update({
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_SERVICE_ROLE_KEY": "test",
    "ADZUNA_APP_ID": "test",
    "ADZUNA_APP_KEY": "test",
    "ANTHROPIC_API_KEY": "test",
    "TELEGRAM_BOT_TOKEN": "test",
})

try:
    import anthropic  # noqa: F401
except ImportError:
    anthropic_stub = types.ModuleType("anthropic")
    anthropic_stub.Anthropic = object
    sys.modules["anthropic"] = anthropic_stub

try:
    import requests  # noqa: F401
except ImportError:
    sys.modules["requests"] = types.ModuleType("requests")

from scripts.daily_matcher import fails_hard_filters, search_terms  # noqa: E402


class MatcherTests(unittest.TestCase):
    def test_search_terms_are_deduplicated_and_limited(self):
        profile = {"cargo": "Marketing", "palavras_chave": "CRM, Marketing, Conteúdo, SEO"}
        self.assertEqual(search_terms(profile), ["Marketing", "CRM", "Conteúdo"])

    def test_salary_below_minimum_is_rejected(self):
        profile = {"salario_minimo": 25_000, "modelo_trabalho": "Qualquer"}
        job = {"salary_max": 22_000, "description": ""}
        self.assertEqual(fails_hard_filters(profile, job), "salário anunciado abaixo do mínimo")

    def test_remote_requires_remote_signal(self):
        profile = {"salario_minimo": None, "modelo_trabalho": "Remoto"}
        self.assertEqual(
            fails_hard_filters(profile, {"description": "Work in our Barcelona office"}),
            "não indica trabalho remoto",
        )
        self.assertIsNone(fails_hard_filters(profile, {"description": "100% teletrabajo"}))


if __name__ == "__main__":
    unittest.main()
