import discord, uuid, os, math, requests, time, datetime, asyncio
from random import randint, shuffle
from mtranslate import translate
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
    await user.send(f"Bonjour Administrateur {user.mention}, je suis connecté en tant que {nom}.\nCode de sécurité : {code_secu}")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Définition de la fonction helping
async def helping(ctx, grp, mode):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Création de l'embed pour afficher les informations
    embed = discord.Embed(title="Commandes disponibles", color=discord.Color.purple())
    # Récupère la liste de toutes les commandes disponibles
    for command in grp.commands :
        embed.add_field(name=prefix+command.name, value=command.description, inline=False)
    if mode==0:
        if ctx.invoked_subcommand is None:
            embed.add_field(name='Veuillez spécifier une sous-commande.', value=f"{prefix}{str(grp)} [nom de la sous-commande]", inline=False)
    # Envoie l'embed dans le canal où la commande a été lancée
    await ctx.send(embed=embed)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Créez un groupe de commandes nommé "Gestion"
@bot.group(description="Liste toutes les commandes de Gestion.")
async def gest(ctx):
    await helping(ctx, gest, 0)

@gest.command(description=f"Supprime les X derniers messages. {prefix}gest clear [nombre de messages à supprimer]")
async def clear(ctx, amount: int):
    # Supprime le message de la commande
    await ctx.message.delete()
    
    # Vérifie si l'utilisateur a la permission de gérer les messages
    if ctx.author.guild_permissions.manage_messages:
        # Supprime les X derniers messages dans le canal
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} messages ont été supprimés.")
    else:
        await ctx.send("Désolé, vous n'avez pas la permission nécessaire pour supprimer des messages.")

@gest.command(description=f"Renomme l'user mentionné. {prefix}gest nick @user [surnom]")
async def nick(ctx, member: discord.Member, *, nickname):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Change le surnom du membre
    await member.edit(nick=nickname)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Créez un groupe de commandes nommé "moderation"
@bot.group(description="Liste toutes les commandes de Modération.")
async def mod(ctx):
    await helping(ctx, mod, 0)

@mod.command(description=f"Liste les permissions de l'user mentionné. {prefix}mod perms @user")
async def perms(ctx, member: discord.Member):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Crée une embed pour stocker les informations des permissions
    embed = discord.Embed(title=f"Permissions de {member.name}", color = discord.Color.teal())
    list_perms=[]
    # Pour chaque rôle de l'utilisateur
    for role in member.roles:
        # Pour chaque permission du rôle
        for perm, value in role.permissions:
            if value is True:
                if perm not in list_perms:
                    list_perms.append(perm)
                    new_perm = perm.replace("_", " ")
                    perm_trad = translate(new_perm, 'fr')
                    embed.add_field(name=perm_trad[0].upper()+perm_trad[1:], value="", inline=False)
    # Envoie les informations des permissions dans le canal où la commande a été utilisée
    await ctx.send(embed=embed)

# Définition de la fonction action
async def action(action, ctx, member, reason):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    message=""
    fin=False
    if (await verif(member.id)==True) :
        # Vérifie si l'utilisateur a la permission de bannir des membres
        autorisation_bot=0
        if action=="kick":
            autorisation_bot=ctx.author.guild_permissions.kick_members
        else:
            autorisation_bot=ctx.author.guild_permissions.ban_members
        if autorisation_bot:
            bot_top_role_position = member.guild.me.top_role.position
            hierarchie=True
            # Parcourt les rôles du membre
            for role in member.roles:
                # Vérifie si le rôle du membre a une position plus élevée que celui du bot
                if role.position > bot_top_role_position:
                    hierarchie=False
            if hierarchie:
                # Envoie un message privé à l'utilisateur
                message=f"```ansi\n[2;31mVous avez été {action} du serveur {ctx.guild.name}"
                if reason!=None:
                    message+=f" pour la raison suivante : {reason}"
                message+="[0m```"
                await member.send(message)

                message=f"> {member.name} a été {action} du serveur."
                fin=True
            else:
                message=f"```ansi\n[2;31m[2;33mDésolé, je ne peux pas {action} un membre qui m'est hiérarchiquement supérieur.[0m[2;31m[0m```"
                fin=False
        else:
            message=f"```ansi\n[2;31m[2;33mDésolé, vous n'avez pas la permission de {action} des membres.[0m[2;31m[0m```"
    else :
        message=f"```ansi\n[2;31m[2;33m{ctx.author.mention} tu ne peux pas {action} mon père.[0m[2;31m[0m```"
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, action, False, reason)
    await ctx.send(message)
    return fin

@mod.command(description=f"Ban l'user mentionné. {prefix}mod ban @user [raison](optionnel)")
async def ban(ctx, member: discord.Member, *, reason=None):
    if await action("ban", ctx, member, reason):
        await member.ban(reason=reason)

@mod.command(description=f"Kick l'user mentionné. {prefix}mod kick @user [raison](optionnel)")
async def kick(ctx, member: discord.Member, *, reason=None):
    if await action("kick", ctx, member, reason):
        await member.kick(reason=reason)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Créez un groupe de commandes nommé "autre"
@bot.group(description="Liste toutes les autres commandes.")
async def autre(ctx):
    await helping(ctx, autre, 0)

@autre.command(description=f"Fait parler le bot. {prefix}autre msg [message]")      
async def msg(ctx, *, message):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    await ctx.send(message)

@autre.command(description=f"Le bot mp l'user mentionné avec vottre message. {prefix}autre mp @user [message]")
async def mp(ctx, member: discord.Member, *, message):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Envoie un message privé à l'utilisateur
    await member.send(message)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Créez un groupe de commandes nommé "site"
@bot.group(description="Liste toutes les commandes pour le Site.")
async def site(ctx):
    await helping(ctx, site, 0)

@site.command(description=f"Donne le status du site WEB. {prefix}site status [https://...](optionnel)")
async def status(ctx, site=None):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    # Création de l'embed pour afficher les informations
    embed = discord.Embed(title="Informations sur le site")
    message=""
    try:
        # Effectuer une requête GET pour obtenir le contenu de la page
        lien='http://192.168.1.152/'
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
            message=f"{title} est en ligne."
            embed.color = discord.Color.green()
        else:
            message=f"Impossible de récupérer le titre du site. Code de statut : {response.status_code}"
            embed.color = discord.Color.orange()
    except requests.ConnectionError:
        message="Impossible de se connecter au site."
        embed.color = discord.Color.red()
    embed.add_field(name=message, value="", inline=False)
    if site==None:
        embed.add_field(name="En savoir plus", value=f"{prefix}scans", inline=False)
    # Envoie l'embed dans le canal où la commande a été lancée
    await ctx.send(embed=embed)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
    await helping(ctx, bot, 1)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Il est long pour afficher la grille !

# Créez un groupe de commandes nommé "Jeux"
@bot.group(description="Liste tout les jeux disponibles.")
async def jeux(ctx):
    await helping(ctx, jeux, 0)

async def creer_grille(vide):
    possibilites=[" ","X","O"]
    #6 lignes, 7 colonnes imposés
    grille=[]
    for i in range(6):
        ligne=[]
        for j in range(7):
            if vide==True :
                case=" "
            else :
                case=possibilites[randint(0,2)]
            ligne.append(case)
        grille.append(ligne)
    return grille

async def affiche_grille(ctx, grille):
    liste_chiffres_col =[str(i) for i in range(1,8)]
    await ctx.send(" "+" " . join (liste_chiffres_col)+" ")
    for ligne in grille :
        await ctx.send("|"+"|".join(ligne)+"|")
        await ctx.send("-"*(15))
        
async def placer_pion(num_col, type_pion, grille ):  #num_col entre 1 et 7
    if grille[0][num_col-1] != " ":
        #Cas où la colonne est pleine...
        return (grille, False)
    for num_ligne in range(5,-1,-1):
        if grille[num_ligne][num_col-1]==" ":
            #on peut placer le pion
            grille[num_ligne][num_col-1]=type_pion
            return (grille,True)

async def verif_vainqueur_ligne(grille):
    for ligne in grille :
        chaine_ligne="".join(ligne)
        fin, symbole_vainqueur=await verif_4_alignes(chaine_ligne)
        if fin==True :
            return (True, symbole_vainqueur)
    return (False,"")

async def verif_vainqueur_colonne(grille):
    #pour chaque colonne, construire chaine_col
    for num_col in range(7):
        chaine_col=""
        for ligne in grille :
            chaine_col=chaine_col+ligne[num_col]
        fin, symbole_vainqueur=await verif_4_alignes(chaine_col)
        if fin==True :
            return (True, symbole_vainqueur)
    return (False,"")

async def verif_vainqueur_diag(grille):
    for sens in (-1,1):
        for b in range(3):
            if b==0 :
                borne_a=4
            else :
                borne_a=1
            for a in range(borne_a):
                i=0
                j=0
                chaine_diag=""
                while i+b <=5 and j+a <= 6 :
                    if sens==1 :
                        chaine_diag=chaine_diag+grille[b+i][a+j]
                    else :
                        chaine_diag=chaine_diag+grille[b+i][6-(a+j)]
                    i=i+1
                    j=j+1
                fin, symbole_vainqueur=await verif_4_alignes(chaine_diag)
                if fin==True :
                    return (True, symbole_vainqueur)
    return (False,"")
    
async def verif_vainqueur_global(grille):
    fin, vainqueur=await verif_vainqueur_ligne(grille)
    if fin==True: 
        return True,vainqueur
    fin, vainqueur=await verif_vainqueur_colonne(grille)
    if fin==True: 
        return True, vainqueur
    fin, vainqueur=await verif_vainqueur_diag(grille)
    if fin==True: 
        return True, vainqueur
    return False,""

async def verif_4_alignes(chaine):
    if "XXXX" in chaine :
        return (True, "X")
    if "OOOO" in chaine :
        return (True, "O")
    return (False,"")

async def joueur_joue(ctx, grille):
    num_col_possibles=[i for i in range(1,8)]
    while True :
        try:
            reponse=""
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel
            try:
                await ctx.send("Saisissez un chiffre entre 1 et 7 ... (Q pour quitter)")
                response = await bot.wait_for('message', timeout=60.0, check=check)
                reponse=response.content.upper()
                if reponse=="Q":
                    await ctx.send(f"Vous demandez à quittez la partie !")
                    return True, "END"
                else:
                    await ctx.send(f"Vous avez choisi : {reponse} !")
            except asyncio.TimeoutError:
                await ctx.send("Désolé, vous n'avez pas répondu à temps.")
                
            num_col=int(reponse)
            if num_col >=1 and num_col <= 7 :
                #numéro de colonne OK
                grille, ok=await placer_pion(num_col,"X",grille)  # type: ignore
                if ok==True :
                    await affiche_grille(ctx, grille)
                    return True, grille
                else :
                    num_col_possibles.remove(num_col)
                    if num_col_possibles==[] :
                        #Le joueur ne peut plus jouer : égalité
                        return False, grille
                    await ctx.send("La colonne choisie est pleine, réessayez")
            else :
                await ctx.send("Vous devez saisir un chiffre entre 1 et 7 ...")    
        except:
            await ctx.send("Vous devez saisir un chiffre entre 1 et 7 ...")

async def copie_liste(liste_de_listes) :
    copie_liste_de_listes=[]
    for liste in liste_de_listes :
        liste_copiee=[]
        for element in liste:
            liste_copiee.append(element)
        copie_liste_de_listes.append(liste_copiee)    
    return copie_liste_de_listes
       
async def ordi_joue(nb_tours, ctx, grille):
    #Opération spéciale du 1er tour
    if nb_tours==2 :
        if grille[5][3]==" ":
            num_col=4
        elif grille[5][2]==" ":
            num_col=3
        grille, ok=await placer_pion(num_col,"O",grille)  # type: ignore
        await affiche_grille(ctx, grille)
        return True, grille     
    
    num_col_possibles=[i for i in range(1,8)]
    for num_col in num_col_possibles :
        grille_simu=await copie_liste(grille) #création d'une grille de simu copie de la grille de jeu
        grille_simu, ok=await placer_pion(num_col,"O",grille_simu)  # type: ignore
        if not ok :
            num_col_possibles.remove(num_col)
            if num_col_possibles==[]:
                return False,grille
        fin, vainqueur=await verif_vainqueur_global(grille_simu)
        if fin== True :
            #en jouant dans num_col, l'ordi va gagner : il va jouer là
            grille, ok=await placer_pion(num_col,"O",grille)  # type: ignore
            if ok==True :
                await affiche_grille(ctx, grille)
                return True, grille
    #quelque soit la colonne où il jouera, l'ordi ne peut pas gagner au prochain tour
    num_col_possibles=[i for i in range(1,8)]
    shuffle(num_col_possibles)
    for num_col in num_col_possibles :
        joueur_peut_gagner=False
        grille_simu=await copie_liste(grille)
        grille_simu, ok=await placer_pion(num_col,"O",grille_simu)  # type: ignore
        if not ok :
            #num_col_possibles.remove(num_col)
            continue
        num_col_possibles_joueur=[i for i in range(1,8)]
        for num_col_joueur in num_col_possibles_joueur:
            grille_simu_joueur =await copie_liste(grille_simu)
            grille_simu_joueur, ok=await placer_pion(num_col_joueur,"X",grille_simu_joueur)  # type: ignore
            if not ok :
                continue
            fin, vainqueur=await verif_vainqueur_global(grille_simu_joueur)
            if fin :
                joueur_peut_gagner=True
                break
        if joueur_peut_gagner :
            continue
        #si l'ordi joue dans num_col, le joueur ne pourra pas gagner au prochain tour
        grille, ok=await placer_pion(num_col,"O",grille)  # type: ignore
        if ok==True :
                await affiche_grille(ctx, grille)
                return True, grille
    #Il existe toujours une possibilité que le joueur gagne au prochain tour : on joue au hasard
    grille, ok=await placer_pion(num_col_possibles[randint(0,len(num_col_possibles)-1)],"O",grille)  # type: ignore
    if ok : 
        await affiche_grille(ctx, grille)
        return True, grille

@jeux.command(description="Jouer au Puissance 4 contre un bot.")
async def p4(ctx):
    grille_jeu = await creer_grille(True)
    peut_jouer=True
    fin=False
    joueur_en_cours="X"
    nb_tours=0
    while peut_jouer==True and fin==False :
        nb_tours+=1
        if joueur_en_cours=="X" :
            peut_jouer, grille_jeu=await joueur_joue(ctx, grille_jeu)
            if grille_jeu=="END":
                peut_jouer=False
                fin=grille_jeu
            else:
                joueur_en_cours="O"
        else : 
            peut_jouer, grille_jeu=await ordi_joue(nb_tours, ctx, grille_jeu)  # type: ignore
            joueur_en_cours="X"
        if fin!="END":
            fin, vainqueur=await verif_vainqueur_global(grille_jeu)
    if fin==True :
        await ctx.send(f"Le vainqueur est {vainqueur} en {nb_tours} coups !")
    elif fin=="END" :
        await ctx.send(f"Vous avez bien quittez la partie.")
    else :
        await ctx.send(f"Match nul, {nb_tours} coups réalisés !")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Exécution du bot avec le jeton Discord
bot.run('TOKEN')
