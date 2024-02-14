import discord
from discord.ext import commands

prefix="<"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)

# Initialisation de l'id de l'admin
admin=0



# Événement de connexion
@bot.event
async def on_ready():
    nom=bot.user.name
    user = await bot.fetch_user(admin)
    # Envoie un message privé à l'utilisateur
    print(f"Bonjour Administrateur {user.name}, je suis connecté en tant que {nom} !")

    
@bot.command(description="Obtenir la liste des commandes utilisables.")
async def help(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Création de l'embed pour afficher les informations
    embed = discord.Embed(title="Commandes disponibles", color=discord.Color.gold())
    # Récupère la liste de toutes les commandes disponibles
    for command in bot.commands :
        embed.add_field(name=command.name, value=command.description, inline=False)
    # Envoie l'embed dans le canal où la commande a été lancée
    await ctx.send(embed=embed)









# Exécution du bot avec le jeton Discord
bot.run('TOKEN')
