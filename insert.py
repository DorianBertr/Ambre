import mysql.connector
from mysql.connector import errorcode
from infos import valeurs

def insertion(query):
    try:
        bdd = mysql.connector.connect(user=valeurs()[0], password=valeurs()[1], host=valeurs()[2], database=valeurs()[3])

    except mysql.connector.Error as err:
        
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            # print("User ou MDP incorrect !")
            return "User ou MDP incorrect !"
            
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            # print("La BDD n'existe pas !")
            return "La BDD n'existe pas !"
            
        else:
            # print(err)
            return err
            
    else:

        if bdd and bdd.is_connected():
            curseur=bdd.cursor()
            try:
                curseur.execute(query)
                bdd.commit()
                bdd.close()
                fin = "query_ok"
            except Exception  as err:
                bdd.close()
                fin = f"Erreur lors de l'exécution de la requête : {err}"
            return fin
        else:

            # print("N'as pas pu se connecter !")
            return "N'as pas pu se connecter !"