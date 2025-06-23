from fastapi import FastAPI
import psycopg2 as psy


conn = psy.connect(database = "postgres",
                          user = "postgres",
                          host = "localhost",
                          password = "1223",
                          port = 5432
                          )

cur = conn.cursor()
api = FastAPI() 

#Ref:  GET (get info), POST (create new), PUT (change existing), Delete

@api.get('/') #in parenth, we have the path

def index():
  return {"message": "Hello"}

@api.get('/getdata')
def show_data():
    data = cur.execute("""SELECT * FROM profile""")
    conn.commit()
    cur.close()
    conn.close()
    return data
print(show_data())
