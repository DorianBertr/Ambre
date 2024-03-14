import discord, asyncio
from discord.ext import commands
from requetes_list import connection_list
from insert import insertion
from mult import mult_insertion
from datetime import datetime

prefix="<"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
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
        embed.add_field(name=prefix+command.name, value=command.description, inline=False)
    # Envoie l'embed dans le canal où la commande a été lancée
    await ctx.send(embed=embed)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bot.command()
async def profil(ctx):
    id=ctx.author.id
    query=f"select id_user from user where id_user={id};"
    user = connection_list(query)
    nom = await bot.fetch_user(id)
    embed = discord.Embed(title=f'Profil de {nom.name}', color=discord.Color.dark_orange())
    if len(user)==1:
        embed.color = discord.Color.blurple()
        # -----------------------------------------------------------------------------------------
        query_objs=f"select * from objectif where id_user={id} and actuel=1;"
        objectif = connection_list(query_objs)
        objf="Pas d'objectif en cours."
        if len(objectif)!=0:
            if objectif[0][3]==0:
                objf=objectif[0][2]
        embed.add_field(name=f'Objectif actuel', value=objf, inline=False)
        # -----------------------------------------------------------------------------------------
        query_perfs=f"select count(id_perf) from perf where id_user={id};"
        perfs = connection_list(query_perfs)[0][0]
        pluri=""
        if int(perfs)>1:
            pluri="s"

        query_last_perf=f"select * from perf where id_user={id} order by date_course desc limit 1;"
        last_perf = connection_list(query_last_perf)

        perf=""
        if len(last_perf)!=0:
            perf=f"Dernière : {last_perf[0][3]} km en {last_perf[0][4]} min"
        embed.add_field(name=f'{perfs} performance{pluri} réalisée{pluri}', value=perf, inline=False)
        # -----------------------------------------------------------------------------------------
        await ctx.send(embed=embed)
    else :
        embed.color = discord.Color.dark_orange()
        embed.add_field(name=f'Vous ne possedez pas de profil.', value=f"Voulez-vous en créer un ? (y/n)", inline=False)
        await ctx.send(embed=embed)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        try:
            reponse = await ctx.bot.wait_for('message', timeout=60.0, check=check)
            if reponse.content.lower()=="y":
                await ctx.send("```ansi\n[2;33mCréation en cours d'un profil...[0m```")
                result=insertion(f"insert into user (id_user) values ({id});")
                if result=="query_ok":
                    await ctx.send("```ansi\n[2;32mCréation du profil réussi.[0m```")
                else:
                    await ctx.send("```ansi\n[2;31mÉchec lors de la création du profil ![0m```")
        except asyncio.TimeoutError:
            await ctx.send(f"```ansi[2;34mLe temps imparti pour agir est terminé ![0m```")
            return

@bot.command()
async def addPerf(ctx, distance, duree, date_course=None, vitesse_moy=None, meteo=None, *, lieu=None):
    await ctx.send("```ansi\n[2;33mAjout de la performance...[0m```")
    options_set=""
    options_val=""
    options=[[date_course,"date_course"],[vitesse_moy,"vitesse_moy"],[meteo,"meteo"],[lieu,"lieu"]]
    for option in options:
        if option[0]!=None and option[0]!="None":
            options_set+=f",{option[1]}"
            val=option[0]
            if option[1]!="vitesse_moy":
                info=option[0]
                if option[1]=="date_course":
                    infos_date=option[0].split("/")
                    new_date = f"{infos_date[2]}-{infos_date[1]}-{infos_date[0]}"
                    info=new_date
                val=f'"{info}"'
            options_val+=f",{val}"
    query=f"insert into perf (id_user,distance,duree{options_set}) values ({ctx.author.id},{distance},{duree}{options_val});"
    result=insertion(query)
    if result=="query_ok":
        await ctx.send("```ansi\n[2;32mAjout de la performance réussi.[0m```")
    else:
        await ctx.send("```ansi\n[2;31mÉchec lors de l'ajout de la performance ![0m```")

@bot.command()
async def perfs(ctx):
    query = f"select * from perf where id_user={ctx.author.id} order by date_course desc;"
    perfs = connection_list(query)
    embed = discord.Embed(title=f'Liste des performances de {ctx.author.name}')
    if len(perfs)==0:
        embed.color = discord.Color.dark_orange()
        embed.add_field(name=f"Vous n'avez pas de performance enregistrée !", value="", inline=False)
    else :
        embed.color = discord.Color.dark_green()
        for perf in perfs:
            vitesse_moy=""
            if perf[5]!=None:
                vitesse_moy=f" avec une vitesse moyenne de {perf[5]}km/h"
            # ------------------------------
            lieu=""
            if perf[6]!=None:
                lieu=f" à {perf[6]}"
            # ------------------------------
            meteo=""
            if perf[7]!=None:
                meteo=f" sous un temps {perf[7]}"
            # ------------------------------
            embed.add_field(name=perf[2], value=f"{perf[3]} km en {perf[4]} min{vitesse_moy}{lieu}{meteo}.", inline=False)
    await ctx.send(embed=embed)
    
@bot.command()
async def objs(ctx):
    objectifs = connection_list(f"select * from objectif where id_user={ctx.author.id} order by creation desc;")
    embed = discord.Embed(title=f'Liste des objectifs de {ctx.author.name}')
    if len(objectifs)==0:
        embed.color = discord.Color.dark_orange()
        embed.add_field(name=f"Vous n'avez pas d'objectif enregistré !", value="", inline=False)
    else :
        embed.color = discord.Color.dark_green()
        for objectif in objectifs:
            if objectif[3]==0:
                valid="Non validé."
            else :
                date=""
                if objectif[4]!=None:
                    date=f" le {objectif[4]}"
                valid=f"validé{date}."
            embed.add_field(name=objectif[6], value=f"<{objectif[2]}> {valid}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def addObj(ctx, *, nom):
    id=ctx.author.id
    query_objs=f"select * from objectif where id_user={id} and actuel=1;"
    objectif = connection_list(query_objs)

    if len(objectif)!=0:
        await ctx.send(f"```ansi\n[2;33mAvez-vous terminé(e) votre précedent objectif ? (y/n)\nRappel : {objectif[0][2]}[0m```")
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        try:
            response = await ctx.bot.wait_for('message', timeout=60.0, check=check)
            reponse=response.content.lower()
            querys=[]
            if reponse=="y" or reponse=="n":
                query_1="update objectif set"
                if reponse=="y":
                    query_1+=" valid=1,"
                    await ctx.send(f"```ansi\n[2;33mQuelle date ? (date/n)[0m```")
                    try:
                        response = await ctx.bot.wait_for('message', timeout=60.0, check=check)
                        reponse=response.content.lower()
                        def is_valid_date(date_str):
                            try:
                                datetime.strptime(date_str, '%d/%m/%Y')
                                return True
                            except ValueError:
                                return False
                        if is_valid_date(reponse) or reponse=="n":
                            infos_date=reponse.split("/")
                            new_date = f"{infos_date[2]}-{infos_date[1]}-{infos_date[0]}"
                            query_1+=f" date_valid='{new_date}',"
                        else:
                            await ctx.send("```ansi\n[2;31mRéponse incorrecte ![0m```")
                    except asyncio.TimeoutError:
                        await ctx.send(f"```ansi[2;34mLe temps imparti pour agir est terminé ![0m```")
                        return
                query_1+=f" actuel=0 where actuel=1 and id_user={id};"
                querys.append(query_1)
                
                await ctx.send("```ansi\n[2;33mAjout d'un nouvel objectif...[0m```")
                querys.append(f'insert into objectif (id_user, nom) values ({id}, "{nom}");')
                result=mult_insertion(querys)
                if result=="query_ok":
                    await ctx.send("```ansi\n[2;32mAjout du nouvel objectif réussi.[0m```")
                else:
                    await ctx.send("```ansi\n[2;31mÉchec lors de l'ajout du nouvel objectif ![0m```")
                    
            else:
                await ctx.send("```ansi\n[2;31mRéponse incorrecte ![0m```")
        except asyncio.TimeoutError:
            await ctx.send(f"```ansi[2;34mLe temps imparti pour agir est terminé ![0m```")
            return


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Exécution du bot avec le jeton Discord
bot.run('')
