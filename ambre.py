import discord, uuid, os, math, requests, time, datetime
from bs4 import BeautifulSoup
from discord.ext import commands

prefix="!"
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)

# Initialisation de l'id de l'admin
admin=0
# Stocke le moment du démarrage du bot
start_time = time.time()


# Événement de connexion
@bot.event
async def on_ready():
    nom=bot.user.name
    print(f'Connecté en tant que {nom}')
    
    user = await bot.fetch_user(admin)
    # Envoie un message privé à l'utilisateur
    await user.send(f"Bonjour Administrateur {user.mention}, je suis connecté en tant que {nom} !")


# Définition de la fonction verif
async def verif(id):
    if (id==admin):
        return False
    return True

# Définition de la fonction send_dm
async def annonce(member, serveur, action, valid, raison=None):
    # Récupère l'utilisateur correspondant à l'ID spécifié
    user = await bot.fetch_user(admin)
    message=""
    opt=" "
    opti=" "
    optio=""
    if action!="destroy":
        opt=" te "
        opti=" sur "
        optio=f" pour la raison suivante : {raison}"
    if valid==True:
        message+=f"{member[0]} ({member[1]}) {action} le serveur {serveur}"
    else:
        message+=f"Tentative de{opt}{action}{opti}le serveur {serveur} par {member[0]} ({member[1]}){optio}"
    # Envoie un message privé à l'admin    
    await user.send(message)


@bot.command()
async def membres(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Récupère la liste des membres du serveur
    members = ctx.guild.members
    # Crée une chaîne pour stocker les noms des membres
    members_list = ""
    # Parcours la liste des membres et ajoute leur nom à la chaîne
    for member in members:
        members_list += f"{member.name}\n"
    # Envoie la liste des membres dans le canal où la commande a été lancée
    await ctx.send(members_list)

@bot.command(description="Liste les permissions de l'user mentionné. !perms @user")
async def perms(ctx, member: discord.Member):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Crée une chaîne pour stocker les informations des permissions
    permissions_info=f"Permissions de {member.mention} :\n\n"
    list_perms=[]
    # Pour chaque rôle de l'utilisateur
    for role in member.roles:
        # Pour chaque permission du rôle
        for perm, value in role.permissions:
            if value is True:
                if perm not in list_perms:
                    permissions_info+=f"    {perm}\n"
    # Envoie les informations des permissions dans le canal où la commande a été utilisée
    await ctx.send(permissions_info)

@bot.command(description="Ban l'user mentionné. !ban @user [raison](optionnel)")
async def ban(ctx, member: discord.Member, *, reason=None):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if (await verif(member.id)==True) :
        # Vérifie si l'utilisateur a la permission de bannir des membres
        if ctx.author.guild_permissions.ban_members:
            # Envoie un message privé à l'utilisateur
            message=f"Vous avez été ban du serveur {ctx.guild.name}"
            if reason!=None:
                message+=f" pour la raison suivante : {reason}"
            await member.send(message)
            # Fait son taff
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} a été banni du serveur.")
        else:
            await ctx.send("Désolé, vous n'avez pas la permission de bannir des membres.")
    else :
        await ctx.send(f"{ctx.author.mention} tu ne peux pas ban mon père.")
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "ban", False, reason)

@bot.command(description="Kick l'user mentionné. !kick @user [raison](optionnel)")
async def kick(ctx, member: discord.Member, *, reason=None):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if (await verif(member.id)==True) :
        # Vérifie si l'utilisateur a la permission d'expulser des membres
        if ctx.author.guild_permissions.kick_members:
            # Envoie un message privé à l'utilisateur
            message=f"Vous avez été kick du serveur {ctx.guild.name}"
            if reason!=None:
                message+=f" pour la raison suivante : {reason}"
            await member.send(message)
            # Fait son taff
            await member.kick(reason=reason)
            await ctx.send(f"{member.mention} a été expulsé du serveur.")
        else:
            await ctx.send("Désolé, vous n'avez pas la permission d'expulser des membres.")
    else :
        await ctx.send(f"{ctx.author.mention} tu ne peux pas kick mon père.")
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "kick", False, reason)
        
@bot.command(description="Fait parler le bot. !msg [message]")      
async def msg(ctx, *, message):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(description="Le bot mp l'user mentionné avec vottre message. !mp @user [message]")
async def mp(ctx, member: discord.Member, *, message):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Envoie un message privé à l'utilisateur
    await member.send(message)
    
@bot.command(description="Renomme l'user mentionné. !nick @user [surnom]")
async def nick(ctx, member: discord.Member, *, nickname):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Change le surnom du membre
    await member.edit(nick=nickname)

@bot.command(description="Donne le status du site WEB local.")
async def status(ctx, site=None):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Création de l'embed pour afficher les informations
    embed = discord.Embed(title="Informations sur le site")
    try:
        # Effectuer une requête GET pour obtenir le contenu de la page
        lien='site par default, mettre le http/s'
        if site!=None:
            lien=site
        response = requests.get(lien)  
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

@bot.command(description="Liste les commandes utilisables.")
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
bot.run('TOKEN')
