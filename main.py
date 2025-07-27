import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import os
import re

TOKEN = os.environ["TOKEN"]
CHANNEL_ID = 1398565271148560416  # ID do canal no Discord

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

itens_base_en = [
    "Cacao", "Burning Bud", "Giant Pinecone", "Sugar Apple", "Ember Lily",
    "Bean Stalk", "Peppers", "Grape", "Mushroom", "Dragon Fruit",
    "Cactus", "Elder Strawberry"
]

itens_base_pt = [
    "Cacau", "Botão Flamejante", "Pinheiro Gigante", "Fruta-doce",
    "Lírio Braseado", "Pé de Feijão", "Pimentas", "Uva", "Cogumelo",
    "Fruta do Dragão", "Cacto", "Morango Ancião"
]

eggs_base_en = [
    "Rare Summer Egg", "Mythical Egg", "Paradise Egg", "Bug Egg"
]

eggs_base_pt = [
    "Ovo de Verão Raro", "Ovo Mítico", "Ovo do Paraíso", "Ovo de Inseto"
]

pt_to_en = {
    "Cacau": "Cacao", "Botão Flamejante": "Burning Bud", "Pinheiro Gigante": "Giant Pinecone",
    "Fruta-doce": "Sugar Apple", "Lírio Braseado": "Ember Lily", "Pé de Feijão": "Bean Stalk",
    "Pimentas": "Peppers", "Uva": "Grape", "Cogumelo": "Mushroom", "Fruta do Dragão": "Dragon Fruit",
    "Cacto": "Cactus", "Morango Ancião": "Elder Strawberry", "Ovo de Verão Raro": "Rare Summer Egg",
    "Ovo Mítico": "Mythical Egg", "Ovo do Paraíso": "Paradise Egg", "Ovo de Inseto": "Bug Egg"
}

itens_desejados = []
for item in itens_base_en:
    itens_desejados.append(item)
    itens_desejados.append(f"{item} Seed")
itens_desejados.extend(itens_base_pt)
for egg in eggs_base_en:
    itens_desejados.append(egg)
    itens_desejados.append(f"{egg} Egg")
itens_desejados.extend(eggs_base_pt)
itens_desejados = list(set(itens_desejados))

def verificar_estoque():
    url = "https://rellseas.gg/grow-a-garden/stocks/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    pagina = soup.text.lower()
    resultados = []
    for item in itens_desejados:
        base = re.escape(item.lower().replace(" seed", "").replace(" egg", ""))
        pattern = rf"\b{base}( seed(s)?| seedling| egg(s)?)?\b"
        if re.search(pattern, pagina):
            resultados.append(item)
    return resultados

@bot.event
async def on_ready():
    print(f"🤖 Bot conectado como {bot.user}")
    checar_loja.start()

@tasks.loop(minutes=5)
async def checar_loja():
    canal = bot.get_channel(CHANNEL_ID)
    itens_achados = verificar_estoque()
    if itens_achados:
        mensagem = "🌱 Items found in the store!\n"
        for item in itens_achados:
            nome_en = pt_to_en.get(item, item)
            mensagem += f"🔔 {nome_en}\n"
    else:
        mensagem = "🔕 No interesting items in the store right now."
    await canal.send(mensagem)

@bot.command()
async def teste(ctx):
    await ctx.send("✅ Bot está funcionando normalmente!")

@bot.command()
async def itens(ctx):
    lista = "\n".join(f"• {item}" for item in sorted(itens_desejados))
    await ctx.send(f"📋 **Currently monitored items:**\n{lista}")

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="🤖 Command Menu - Grow a Garden Bot",
        description="Available commands:",
        color=0x3498db
    )
    embed.add_field(name="!itens", value="📋 Show monitored items list.", inline=False)
    embed.add_field(name="!teste", value="✅ Test if the bot is working.", inline=False)
    embed.add_field(name="!menu", value="📖 Show this menu.", inline=False)
    embed.add_field(name="!reiniciar", value="🔄 Restart the stock checking loop.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def reiniciar(ctx):
    await ctx.send("🔄 Reiniciando o monitoramento da loja...")
    checar_loja.cancel()  # Para o loop
    checar_loja.start()   # Reinicia o loop imediatamente
    await ctx.send("✅ Loop reiniciado com sucesso! Vou checar agora.")

bot.run(TOKEN)
