import uuid
import os
import math
import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

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


@bot.command()
async def status(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    
    message="```ansi\n"
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
            message+=f"[2;32mLe site {title} est en ligne localement ![0m\n```"
            await ctx.send(message)
        else:
            message+=f"[2;32m[2;31mImpossible de récupérer le titre du site. Code de statut : {response.status_code}[0m[2;32m[0m\n```"
            await ctx.send(message)
    except requests.ConnectionError:
        message+="[2;32m[2;31mImpossible de se connecter au site ![0m[2;32m[0m\n```"
        await ctx.send(message)



# Exécution du bot avec le jeton Discord
bot.run('token')
