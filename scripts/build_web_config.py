"""Build the public runtime config used by the static site."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def validated_config(env: dict[str, str]) -> dict[str, str]:
    config = {
        "supabaseUrl": env.get("SUPABASE_URL", "").strip().rstrip("/"),
        "supabaseAnonKey": env.get("SUPABASE_ANON_KEY", "").strip(),
        "telegramBotUsername": env.get("TELEGRAM_BOT_USERNAME", "").strip().lstrip("@"),
        "supportEmail": env.get("SUPPORT_EMAIL", "").strip(),
    }
    errors = []
    if not re.fullmatch(r"https://[a-z0-9-]+\.supabase\.co", config["supabaseUrl"]):
        errors.append("SUPABASE_URL inválida")
    if len(config["supabaseAnonKey"]) < 20:
        errors.append("SUPABASE_ANON_KEY ausente ou inválida")
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", config["telegramBotUsername"]):
        errors.append("TELEGRAM_BOT_USERNAME inválido")
    if config["supportEmail"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", config["supportEmail"]):
        errors.append("SUPPORT_EMAIL inválido")
    if errors:
        raise ValueError("; ".join(errors))
    return config


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("uso: build_web_config.py CAMINHO_DE_SAIDA")
    config = validated_config(dict(os.environ))
    target = Path(sys.argv[1])
    target.write_text(
        "window.APP_CONFIG = " + json.dumps(config, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Configuração pública criada em {target}")


if __name__ == "__main__":
    main()

