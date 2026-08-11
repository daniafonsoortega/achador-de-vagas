import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);
const botToken = Deno.env.get("TELEGRAM_BOT_TOKEN")!;
const webhookSecret = Deno.env.get("TELEGRAM_WEBHOOK_SECRET")!;

async function sendTelegram(chatId: number, text: string) {
  const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text }),
  });
  if (!response.ok) throw new Error(`Telegram returned ${response.status}`);
}

Deno.serve(async (request) => {
  if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
  if (!webhookSecret || request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== webhookSecret) {
    return new Response("Unauthorized", { status: 401 });
  }

  let update: Record<string, any>;
  try {
    update = await request.json();
  } catch {
    return new Response("ok");
  }

  const message = update.message;
  if (!message?.text || !message?.chat?.id) return new Response("ok");

  const chatId = Number(message.chat.id);
  const [command, code] = String(message.text).trim().split(/\s+/, 2);
  if (!command.startsWith("/start")) return new Response("ok");

  if (!code || !/^[a-f0-9]{32}$/.test(code)) {
    await sendTelegram(chatId, "Abra o site e use o botão “Conectar Telegram” para gerar um link válido.");
    return new Response("ok");
  }

  // A unique chat belongs to only one profile; the code rotates after use.
  const { data, error } = await supabase
    .from("profiles")
    .update({
      telegram_chat_id: String(chatId),
      connect_code: crypto.randomUUID().replaceAll("-", ""),
    })
    .eq("connect_code", code)
    .is("telegram_chat_id", null)
    .select("user_id")
    .maybeSingle();

  if (error || !data) {
    await sendTelegram(chatId, "Esse link é inválido, já foi utilizado ou este Telegram já está conectado.");
  } else {
    await sendTelegram(chatId, "✅ Conectado! Você receberá aqui somente as vagas selecionadas para o seu perfil.");
  }
  return new Response("ok");
});

