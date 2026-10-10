import sqlite3
connect = sqlite3.connect("test.db")
cursor = connect.cursor()

cursor.execute("DROP TABLE IF EXISTS cars")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY,
    brand TEXT,
    model TEXT,
    transmission TEXT,
    horsepower INTEGER
)
""")

cursor.execute("""
               INSERT INTO cars (brand, model, transmission, horsepower) 
                  VALUES ('audi', 'a3', 'manual', 180),
                         ('audi', 'a4', 'manual', 200),
                         ('bmw', 'm3', 'auto', 230)
""")

cursor.execute("UPDATE cars SET horsepower = horsepower + 50 WHERE brand = 'bmw' ")

connect.commit()

cursor.execute("SELECT * FROM cars WHERE transmission = 'manual'")

result = cursor.fetchall()

print("Found vehicles:")
for item in result:
    print(f"– {item[1]}, Power: {item[-1]}")
connect.close()