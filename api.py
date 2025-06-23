import psycopg2 as psy

try:
  conn = psy.connect(database = "postgres",
                          user = "postgres",
                          host = "localhost",
                          password = "1223",
                          port = 5432
                          )

  cur = conn.cursor()

  cur.execute("""CREATE TABLE test_zone(
              id SERIAL PRIMARY KEY,
              firstname VARCHAR(255) NOT NULL,
              lastname varchar(255) NOT NULL,
              project_id INT);""")
  conn.commit()
  cur.close()
  conn.close()
except: 
  print("Error in connection")

