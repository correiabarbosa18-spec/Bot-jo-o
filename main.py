import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import os
import threading
import socket

# Simula uma porta falsa para manter o Render "acordado"
def manter_socket_aberto():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 10000))
    s.listen()
    while True:
        conn, _ = s.accept()
        conn.close()

threading.Thread(target=manter_socket_aberto, daemon=True).start()

# Token e canal
TOKEN = os.environ["TOKEN"]
CHANNEL_ID = 1398565271148560416

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Traduções: português → inglês
traducoes = {
    "Brotinho Flamejante": "Burning Bud",
    "Botão Flamejante": "Burning Bud",
    "Burning Bud": "Burning Bud",

    "Pinha Gigante": "Giant Pinecone",
    "Giant Pinecone": "Giant Pinecone",

    "Maçã de Açúcar": "Sugar Apple",
    "Sugar Apple": "Sugar Apple",

    "Lírio de Brasa": "Ember Lily",
    "Ember Lily": "Ember Lily",

    "Caule de Feijão": "Bean Stalk",
    "Bean Stalk": "Bean Stalk",

    "Cacau": "Cacao",
    "Cacao": "Cacao",

    "Pimentas": "Peppers",
    "Peppers": "Peppers",

    "Uva": "Grape",
    "Grape": "Grape",

    "Cogumelo": "Mushroom",
    "Mushroom": "Mushroom",

    "Fruta do Dragão": "Dragon Fruit",
    "Dragon Fruit": "Dragon Fruit",

    "Cacto": "Cactus",
    "Cactus": "Cactus",

    "Ovo Mítico": "Mythical Egg",
    "Mythical Egg": "Mythical Egg",

    "Ovo Paraíso": "Paradise Egg",
    "Paradise Egg": "Paradise Egg",

    "Ovo Raro de Verão": "Rare Summer Egg",
    "Rare Summer Egg": "Rare Summer Egg",

    "Ovo de Inseto": "Bug Egg",
    "Bug Egg": "Bug Egg",
}

# Lista de itens desejados (em inglês)
itens_desejados = list(set(traducoes.values()))

# Lista de itens considerados raros
itens_raros = [
    "Burning Bud", "Mythical Egg", "Paradise Egg", "Rare Summer Egg"
]

# Função que verifica o site
def verificar_estoque():
    url = "https://rellseas.gg/grow-a-garden/stocks/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    achados = []

    for nome in traducoes:
        if nome.lower() in soup.text.lower():
            nome_en = traducoes[nome]
            if nome_en not in achados:
                achados.append(nome_en)

    return achados

# Quando o bot conecta
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    checar_loja.start()

# Verifica a loja a cada 5 min
@tasks.loop(minutes=5)
async def checar_loja():
    canal = bot.get_channel(CHANNEL_ID)
    encontrados = verificar_estoque()
    raros = [item for item in encontrados if item in itens_raros]

    if raros:
        msg = "🌟 **Itens RAROS encontrados na loja!**\n"
        msg += "\n".join(f"🔔 {item}" for item in raros)
    else:
        msg = "🔕 Nenhum item raro na loja no momento."

    await canal.send(msg)

# Comando de teste
@bot.command()
async def teste(ctx):
    await ctx.reply("✅ Bot está funcionando normalmente!")

# Comando para reiniciar a checagem
@bot.command()
async def resetar(ctx):
    checar_loja.cancel()
    encontrados = verificar_estoque()
    raros = [item for item in encontrados if item in itens_raros]

    if raros:
        msg = "🌟 **Itens RAROS encontrados na loja!**\n"
        msg += "\n".join(f"🔔 {item}" for item in raros)
    else:
        msg = "🔕 Nenhum item raro encontrado na loja."

    await ctx.reply(f"♻️ Verificação reiniciada!\n{msg}")
    checar_loja.start()

# Mostrar os itens monitorados
@bot.command()
async def itens(ctx):
    lista = "\n".join(f"• {item}" for item in itens_desejados)
    await ctx.reply(f"📋 Itens monitorados atualmente:\n{lista}")

# Comando de menu
@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="📖 Menu de Comandos",
        description="Esses são os comandos disponíveis:",
        color=0x00ff00
    )
    embed.add_field(name="🔍 `!itens`", value="Mostra os itens sendo monitorados.", inline=False)
    embed.add_field(name="♻️ `!resetar`", value="Verifica a loja agora e reinicia o contador.", inline=False)
    embed.add_field(name="✅ `!teste`", value="Testa se o bot está online.", inline=False)
    await ctx.reply(embed=embed)

# Inicia o bot
bot.run(TOKEN)
