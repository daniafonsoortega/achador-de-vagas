# Achador de Vagas

MVP multiusuário que recebe um currículo e preferências, busca vagas diariamente na Adzuna, classifica a aderência e envia uma seleção pelo Telegram.

## Estrutura

```text
web/                                      site estático
scripts/daily_matcher.py                  busca e matching diário
supabase/schema.sql                       banco, RLS, Storage e exclusão de conta
supabase/functions/telegram-webhook/      conexão segura com Telegram
.github/workflows/daily_job_search.yml    agendamento diário
```

## 1. Supabase

1. Crie um projeto e execute `supabase/schema.sql` no SQL Editor.
2. Em Authentication, habilite login por e-mail e cadastre a URL do site em **Site URL** e **Redirect URLs**.
3. Guarde a Project URL, a chave `anon` e a chave secreta `service_role`.
4. Escolha a região do projeto e configure retenção/backups de acordo com seu aviso de privacidade.

Se o schema antigo já tiver sido executado, este arquivo não adicionará automaticamente todas as colunas com `create table if not exists`. Para um protótipo sem dados reais, recrie o projeto Supabase. Para produção, crie migrations versionadas.

## 2. Site e publicação automática

No GitHub, abra **Settings → Secrets and variables → Actions → Variables** e crie:

- `PUBLIC_SUPABASE_URL`: Project URL do Supabase.
- `PUBLIC_SUPABASE_ANON_KEY`: chave pública `anon` (nunca use `service_role`).
- `PUBLIC_TELEGRAM_BOT_USERNAME`: usuário do bot sem `@`.
- `PUBLIC_SUPPORT_EMAIL`: e-mail de ajuda (opcional).

Em **Settings → Pages**, escolha **GitHub Actions** como Source. O workflow `Publicar site` valida essas variáveis, gera `web/config.js` durante o build e publica a pasta `web`. A chave `anon` é pública por definição; a proteção dos dados depende das policies RLS do schema.

Para desenvolvimento local, copie `web/config.example.js` para `web/config.js`, preencha os valores públicos e sirva a pasta por HTTP. `web/config.js` está no `.gitignore`.

Antes de convidar usuários, substitua os campos entre colchetes em `web/privacy.html` e faça uma revisão de privacidade adequada ao uso real.

## 3. Telegram webhook

Crie um bot com `@BotFather`. Gere um segredo aleatório com 32–64 caracteres e configure os secrets:

```bash
supabase login
supabase link --project-ref SEU_PROJECT_REF
supabase secrets set TELEGRAM_BOT_TOKEN=... TELEGRAM_WEBHOOK_SECRET=...
supabase functions deploy telegram-webhook --no-verify-jwt
```

O `--no-verify-jwt` é necessário porque o Telegram não envia JWT do Supabase. A função valida o header secreto do próprio Telegram.

Registre o webhook (não coloque tokens em histórico público ou screenshots):

```text
POST https://api.telegram.org/bot<TOKEN>/setWebhook
url=https://<PROJECT_REF>.supabase.co/functions/v1/telegram-webhook
secret_token=<TELEGRAM_WEBHOOK_SECRET>
```

## 4. Busca diária

No repositório GitHub, crie estes **Actions secrets**:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `ANTHROPIC_API_KEY`
- `TELEGRAM_BOT_TOKEN`

Variáveis opcionais: `ANTHROPIC_MODEL`, `MATCH_THRESHOLD` e `MAX_NOTIFICATIONS_PER_USER`. O workflow roda às 08:00 UTC e também pode ser acionado manualmente.

## 5. Verificações automáticas

O workflow `Verificações` executa testes de configuração e matching e valida sintaxe Python/JavaScript em cada push e pull request. Não publique se ele estiver vermelho.

Use também o arquivo `LAUNCH_CHECKLIST.md` antes de enviar o link à primeira usuária.

## Teste recomendado

1. Entre com um e-mail de teste.
2. Envie PDF, DOCX e TXT separadamente e confirme texto e download.
3. Aceite o aviso, salve preferências e conecte o Telegram.
4. Rode o workflow manualmente e confira logs, ranking e limite de mensagens.
5. Altere o perfil e confirme que uma vaga antiga pode ser reavaliada.
6. Pause e desconecte; confirme que os envios param.
7. Exclua a conta de teste e confirme no Supabase que perfil, arquivo e histórico foram removidos.

## Limites atuais

- A única fonte implementada é Adzuna. Não faça scraping do LinkedIn sem autorização expressa.
- PDFs digitalizados como imagem precisam de OCR, ainda não implementado.
- A aplicação recomenda vagas, mas não se candidata automaticamente.
- O filtro determinístico cobre salário informado e indicação de remoto; contrato, idiomas e demais restrições participam do ranking por IA.
- Para escala, adicione migrations, observabilidade, testes de integração, fila/retries e métricas de feedback.
