import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import os
from keep_alive import manter_online

manter_online()  # Mantém o bot vivo no Render

TOKEN = os.environ["TOKEN"]
CHANNEL_ID = 1398565271148560416

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Traduções português ↔ inglês
traducoes = {
    "Broto Ardente": "Burning Bud",
    "Pinha Gigante": "Giant Pinecone",
    "Maçã Doce": "Sugar Apple",
    "Lírio Incandescente": "Ember Lily",
    "Caule de Feijão": "Bean Stalk",
    "Cacau": "Cacao",
    "Pimentas": "Peppers",
    "Uva": "Grape",
    "Cogumelo": "Mushroom",
    "Fruta do Dragão": "Dragon Fruit",
    "Cacto": "Cactus",
    "Ovo Raro de Verão": "Rare Summer Egg",
    "Ovo Mítico": "Mythical Egg",
    "Ovo do Paraíso": "Paradise Egg",
    "Ovo de Inseto": "Bug Egg",
    # também aceita os nomes em inglês como chave
}

# Lista de itens desejados e raros (em inglês)
itens_desejados = list(set(traducoes.values()))
itens_raros = ["Burning Bud", "Mythical Egg", "Paradise Egg", "Rare Summer Egg"]

# Função de verificação
def verificar_estoque():
    url = "https://rellseas.gg/grow-a-garden/stocks/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    texto_site = soup.text.lower()

    resultados = []

    for pt_br, en_us in traducoes.items():
        if pt_br.lower() in texto_site or en_us.lower() in texto_site:
            resultados.append(en_us)

    return resultados

# Evento quando o bot entra
@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    checar_loja.start()

# Loop que checa a cada 5 min
@tasks.loop(minutes=5)
async def checar_loja():
    canal = bot.get_channel(CHANNEL_ID)
    itens_achados = verificar_estoque()
    itens_alertar = [item for item in itens_achados if item in itens_raros]

    if itens_alertar:
        mensagem = "🌱 **Itens RAROS encontrados na loja!**\n"
        mensagem += "\n".join(f"🔔 {item}" for item in itens_alertar)
    else:
        mensagem = "🔕 Nenhum item raro encontrado na loja no momento."

    await canal.send(mensagem)

# Comando !resetar
@bot.command()
async def resetar(ctx):
    checar_loja.cancel()
    itens_achados = verificar_estoque()
    itens_alertar = [item for item in itens_achados if item in itens_raros]

    if itens_alertar:
        mensagem = "🌱 **Itens RAROS encontrados na loja!**\n"
        mensagem += "\n".join(f"🔔 {item}" for item in itens_alertar)
    else:
        mensagem = "🚫 Nenhum item raro encontrado agora."

    await ctx.reply(f"♻️ Contador reiniciado!\n{mensagem}")
    checar_loja.start()

# Comando !itens
@bot.command()
async def itens(ctx):
    lista = "\n".join(f"• {item}" for item in itens_desejados)
    await ctx.reply(f"📋 Itens monitorados atualmente:\n{lista}")

# Comando !teste
@bot.command()
async def teste(ctx):
    await ctx.reply("✅ Bot está funcionando normalmente!")

# Comando !menu
@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="📖 Menu de Comandos",
        description="Veja abaixo o que você pode fazer com o bot:",
        color=0x00ff00
    )
    embed.add_field(name="🔍 `!itens`", value="Lista os itens sendo monitorados.", inline=False)
    embed.add_field(name="♻️ `!resetar`", value="Verifica a loja agora e reinicia o contador.", inline=False)
    embed.add_field(name="✅ `!teste`", value="Confirma que o bot está online.", inline=False)
    await ctx.reply(embed=embed)

# Iniciar bot
bot.run(TOKEN)
