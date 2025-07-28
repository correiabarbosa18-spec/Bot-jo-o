import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.environ.get("TOKEN")  # Token seguro via ambiente
CANAL_ID = 123456789012345678  # Coloque o ID do canal do Discord

itens_desejados = [
    "burning bud", "giant pinecone", "sugar apple", "ember lily",
    "bean stalk", "cacao", "peppers", "grape", "mushroom"
]

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    checar_loja.start()

def verificar_estoque():
    url = "https://rellseas.gg/grow-a-garden/stocks/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    encontrados = []
    for item in itens_desejados:
        if item.lower() in soup.text.lower():
            encontrados.append(item)
    return encontrados

@tasks.loop(minutes=5)
async def checar_loja():
    canal = bot.get_channel(CANAL_ID)
    encontrados = verificar_estoque()

    if encontrados:
        itens_formatados = ', '.join(encontrados)
        await canal.send(f"🌟 Itens raros encontrados na loja: **{itens_formatados}**")
    else:
        print("Nenhum item raro encontrado.")

# Roda o bot
bot.run(TOKEN)
