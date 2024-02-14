import discord, asyncio
from random import randint, shuffle
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


@bot.command(description="Supprime les X derniers messages. !clear [nombre de messages à supprimer]")
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
        


# Créez un groupe de commandes nommé "jeux"
@bot.group()
async def jeux(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Veuillez spécifier une sous-commande pour le groupe "jeux".')


@jeux.command(description="Jouer au Puissance 4 contre un bot.")
async def p4(ctx):
    #test de la fonction
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






# Exécution du bot avec le jeton Discord
bot.run('TOKEN')
