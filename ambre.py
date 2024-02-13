import uuid
import os
import math
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



# Exécution du bot avec le jeton Discord
bot.run('token')
