import discord
from discord.ext import tasks, commands
import requests
from bs4 import BeautifulSoup
import os

# Token e canal
TOKEN = os.environ["TOKEN"]
CHANNEL_ID = 1398565271148560416

# Intents e bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Itens monitorados
itens_desejados = [
    "Burning Bud", "Giant Pinecone", "Sugar Apple", "Ember Lily",
    "Bean Stalk", "Cacao", "Peppers", "Grape", "Mushroom",
    "Dragon Fruit", "Cactus", "Rare Summer Egg", "Mythical Egg",
    "Paradise Egg", "Bug Egg"
]

# Itens raros
itens_raros = [
    "Burning Bud", "Mythical Egg", "Paradise Egg", "Rare Summer Egg"
]

def verificar_estoque():
    url = "https://rellseas.gg/grow-a-garden/stocks/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    resultados = []
    for item in itens_desejados:
        if item.lower() in soup.text.lower():
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

    itens_alertar = [item for item in itens_achados if item in itens_raros]

    if itens_alertar:
        mensagem = "🌱 **Itens RAROS encontrados na loja!**\n"
        mensagem += "\n".join(f"🔔 {item}" for item in itens_alertar)
    else:
        mensagem = "🔕 Nenhum item interessante na loja no momento."

    await canal.send(mensagem)

# Comandos do bot
@bot.command()
async def teste(ctx):
    await ctx.reply("✅ Bot está funcionando normalmente!")

@bot.command()
async def resetar(ctx):
    checar_loja.cancel()
    itens_achados = verificar_estoque()
    itens_alertar = [item for item in itens_achados if item in itens_raros]

    if itens_alertar:
        mensagem = "🌱 **Itens RAROS encontrados na loja!**\n"
        mensagem += "\n".join(f"🔔 {item}" for item in itens_alertar)
    else:
        mensagem = "🚫 Nenhum item interessante na loja no momento."

    await ctx.reply(f"♻️ Contador reiniciado!\n{mensagem}")
    checar_loja.start()

@bot.command()
async def itens(ctx):
    if not itens_desejados:
        await ctx.reply("📦 Nenhum item está sendo monitorado.")
    else:
        lista = "\n".join(f"• {item}" for item in itens_desejados)
        await ctx.reply(f"📋 Itens monitorados atualmente:\n{lista}")

@bot.command()
async def adicionar(ctx, *, item):
    item_formatado = item.strip().title()
    if item_formatado in itens_desejados:
        await ctx.reply(f"⚠️ O item **{item_formatado}** já está na lista.")
    else:
        itens_desejados.append(item_formatado)
        await ctx.reply(f"✅ Item **{item_formatado}** adicionado à lista!")

@bot.command()
async def remover(ctx, *, item):
    item_formatado = item.strip().title()
    if item_formatado in itens_desejados:
        itens_desejados.remove(item_formatado)
        await ctx.reply(f"🗑️ Item **{item_formatado}** removido.")
    else:
        await ctx.reply(f"❌ O item **{item_formatado}** não está na lista.")

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="📘 Menu de Comandos",
        description="Aqui estão os comandos disponíveis:",
        color=0x00ff00
    )
    embed.add_field(name="!teste", value="Verifica se o bot está online", inline=False)
    embed.add_field(name="!resetar", value="Reinicia a verificação da loja", inline=False)
    embed.add_field(name="!itens", value="Lista os itens monitorados", inline=False)
    embed.add_field(name="!adicionar [item]", value="Adiciona um item à lista", inline=False)
    embed.add_field(name="!remover [item]", value="Remove um item da lista", inline=False)
    embed.add_field(name="!menu", value="Mostra este menu de comandos", inline=False)
    await ctx.reply(embed=embed)

# Rodar bot
bot.run(TOKEN)
