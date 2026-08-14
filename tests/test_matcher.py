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

from scripts.daily_matcher import (  # noqa: E402
    HEADERS,
    fails_hard_filters,
    job_fingerprint,
    linkedin_search_url,
    score_job_locally,
    search_terms,
)


class MatcherTests(unittest.TestCase):
    def test_new_supabase_secret_is_not_sent_as_jwt(self):
        self.assertNotIn("Authorization", HEADERS)

    def test_local_score_rewards_title_and_keyword_matches(self):
        profile = {"cargo": "Publishing Editor", "palavras_chave": "content, CMS"}
        matching = {"title": "Publishing Editor", "description": "Content work with a CMS"}
        unrelated = {"title": "Warehouse Assistant", "description": "Picking and packing"}
        self.assertGreater(score_job_locally(profile, matching)[0], score_job_locally(profile, unrelated)[0])

    def test_search_terms_are_deduplicated_and_limited(self):
        profile = {"cargo": "Marketing", "palavras_chave": "CRM, Marketing, Conteúdo, SEO"}
        self.assertEqual(search_terms(profile), ["Marketing", "CRM", "Conteúdo"])

    def test_search_terms_expand_multiword_role_without_keywords(self):
        profile = {"cargo": "Publishing Editor", "palavras_chave": ""}
        self.assertEqual(search_terms(profile), ["Publishing Editor", "Publishing", "Editor"])

    def test_linkedin_search_is_barcelona_last_24_hours(self):
        url = linkedin_search_url({"cargo": "Publishing Editor", "localizacao": "Barcelona"})
        self.assertIn("keywords=Publishing+Editor", url)
        self.assertIn("location=Barcelona", url)
        self.assertIn("f_TPR=r86400", url)

    def test_job_fingerprint_deduplicates_case_and_punctuation(self):
        first = {"title": "Editor/a!", "company": {"display_name": "Example S.L."}}
        second = {"title": "EDITOR A", "company": {"display_name": "Example SL"}}
        self.assertEqual(job_fingerprint(first), job_fingerprint(second))

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
