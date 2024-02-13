import uuid, os, math, requests, time, datetime
from bs4 import BeautifulSoup
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
    print(f'Connecté en tant que {nom}')
    
    user = await bot.fetch_user(admin)
    # Envoie un message privé à l'utilisateur
    await user.send(f"Bonjour Administrateur {user.mention}, je suis connecté en tant que {nom} !\nCode de sécurité : {code_secu}")


@bot.command()
async def scans(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Chemin du dossier à parcourir
    mangas_path = './mangas'
    message="```ansi\n"
    message+=f"[2;34m[2;36m[4;36m[1;36m{len(os.listdir(mangas_path))} scans disponibles :[0m[4;36m[0m[2;36m[0m[2;34m[0m\n"
    # Parcourt tous les dossiers dans le dossier spécifié
    for manga in os.listdir(mangas_path):
        message+=f"    [2;31m[2;32m[1;32m{manga} :[0m[2;32m[0m[2;31m[0m\n"
        # Chemin complet du dossier
        manga_path = os.path.join(mangas_path, manga)
        message+=f"        [2;34m{len(os.listdir(manga_path))} chapitres.\n"
        nb_img=0
        for chapter in os.listdir(manga_path):
            chapter_path=os.path.join(manga_path, chapter)
            nb_img+=len(os.listdir(chapter_path))
        moy_img=nb_img/len(os.listdir(manga_path)) 
        message+=f"        Moyenne de {math.floor(moy_img)} slides par chapitre.[0m\n"
    message+="```"
        
    await ctx.send(message)


@bot.command(description="Obtenir le status du site WEB local.")
async def status(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Création de l'embed pour afficher les informations
    embed = discord.Embed(title="Informations sur le site")
    try:
        # Effectuer une requête GET pour obtenir le contenu de la page
        response = requests.get('http://localhost/')  
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            # Utiliser BeautifulSoup pour analyser le contenu HTML de la page
            soup = BeautifulSoup(response.content, 'html.parser')      
            # Récupérer le titre de la page
            title = soup.title.string      
            # Afficher le titre de la page
            embed.add_field(name="Connectivité", value=f"{title} est en ligne.", inline=False)
            embed.color = discord.Color.green()
        else:
            embed.add_field(name="Connectivité", value=f"Impossible de récupérer le titre du site. Code de statut : {response.status_code}", inline=False)
            embed.color = discord.Color.orange()
    except requests.ConnectionError:
        embed.add_field(name="Connectivité", value="Impossible de se connecter au site !", inline=False)
        embed.color = discord.Color.red()
    embed.add_field(name="En savoir plus", value=f"{prefix}scans", inline=False)
    # Envoie l'embed dans le canal où la commande a été lancée
    await ctx.send(embed=embed)

# Stocke le moment du démarrage du bot
start_time = time.time()

@bot.command(description="Obtenir les informations du bot.")
async def infos(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Calcul de la durée écoulée depuis le démarrage du bot
    elapsed_time = time.time() - start_time
    formatted_elapsed_time = str(datetime.timedelta(seconds=int(elapsed_time)))
    # Création de l'embed pour afficher les informations
    embed = discord.Embed(title="Informations sur le bot", color=discord.Color.blue())
    embed.add_field(name="Date de démarrage", value=str(datetime.datetime.utcfromtimestamp(start_time)), inline=False)
    embed.add_field(name="Durée écoulée depuis le démarrage", value=formatted_elapsed_time, inline=False)
    embed.add_field(name="Nombre de serveurs", value=len(bot.guilds), inline=False)
    embed.add_field(name="Nombre d'utilisateurs", value=sum(len(guild.members) for guild in bot.guilds), inline=False)
    # Envoie l'embed dans le canal où la commande a été lancée
    await ctx.send(embed=embed)

@bot.command(description="Obtenir la liste des commandes utilisables.")
async def help(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Création de l'embed pour afficher les informations
    embed = discord.Embed(title="Commandes disponibles", color=discord.Color.purple())
    # Récupère la liste de toutes les commandes disponibles
    for command in bot.commands :
        embed.add_field(name=command.name, value=command.description, inline=False)
    # Envoie l'embed dans le canal où la commande a été lancée
    await ctx.send(embed=embed)


# Exécution du bot avec le jeton Discord
bot.run('token')
