# Checklist de lançamento

Use esta lista somente depois de seguir o README.

## Identidade e privacidade

- [ ] Escolher nome definitivo do serviço e e-mail de suporte.
- [ ] Substituir os campos entre colchetes em `web/privacy.html`.
- [ ] Confirmar região, retenção e termos dos fornecedores de dados.
- [ ] Fazer um teste real de exclusão de conta.

## Supabase e Telegram

- [ ] Executar `supabase/schema.sql` em um projeto novo.
- [ ] Configurar Site URL e Redirect URLs depois de obter a URL pública.
- [ ] Criar o bot e definir foto, descrição e comandos no BotFather.
- [ ] Publicar a Edge Function e registrar webhook com `secret_token`.
- [ ] Confirmar que um link de conexão não funciona duas vezes.

## GitHub

- [ ] Criar as quatro variables `PUBLIC_*` descritas no README.
- [ ] Criar os seis Actions secrets da busca diária.
- [ ] Em Settings → Pages, escolher **GitHub Actions** como fonte.
- [ ] Rodar os workflows “Verificações”, “Publicar site” e “Busca diária”.
- [ ] Conferir que nenhum token secreto foi commitado.

## Teste com a primeira usuária

- [ ] Login por e-mail funciona no celular.
- [ ] PDF ou DOCX extrai texto legível.
- [ ] Perfil salva e permanece depois de novo login.
- [ ] Telegram conecta e recebe uma vaga com link válido.
- [ ] Pausar, desconectar e excluir funcionam.
- [ ] Mensagens não são excessivas nem repetidas.

## Lançamento inicial

- [ ] Começar com apenas uma usuária por pelo menos três dias.
- [ ] Revisar manualmente falsos positivos e vagas perdidas.
- [ ] Ajustar `MATCH_THRESHOLD` antes de convidar mais pessoas.
- [ ] Manter candidatura automática fora do primeiro lançamento.

