import mysql.connector, datetime
from mysql.connector import errorcode
from infos import valeurs

def connection_list(query):
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
            result = curseur.execute(query)

            rows = curseur.fetchall()
            
            resultat=[]
            for row in rows:
                column=[]
                for col in row:
                    val=col
                    if isinstance(col, datetime.date):
                        val=col.strftime('%d/%m/%Y')
                    column.append(val)
                resultat.append(column)
                
            bdd.close()
            return resultat

        else:

            # print("N'as pas pu se connecter !")
            return "N'as pas pu se connecter !"