import sqlite3

def create_tables():
    conn = sqlite3.connect("total_data.db")
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS Cities')
    cur.execute('''CREATE TABLE Cities (city_id INTEGER PRIMARY KEY,
                                        city_name TEXT)''')

    cur.execute('DROP TABLE IF EXISTS Shops')
    cur.execute('''CREATE TABLE Shops (shop_id INTEGER PRIMARY KEY,
                                        shop_name TEXT,
                                        latitude INTEGER,
                                        longitude INTEGER)''')

    cur.execute('DROP TABLE IF EXISTS Colleges')
    cur.execute('''CREATE TABLE Colleges (college_id INTEGER PRIMARY KEY, 
                                        normalize_name TEXT,
                                        city_id INTEGER,
                                        enrollment INTEGER,
                                        place_id TEXT,
                                        url TEXT,
                                        tuition INTEGER,
                                        year_founded INTEGER,
                                        latitude INTEGER,
                                        longitude INTEGER,
                                        FOREIGN KEY (city_id) REFERENCES Cities(city_id))''')

    cur.execute('DROP TABLE IF EXISTS Boba_near_Colleges')
    cur.execute('''CREATE TABLE Boba_near_Colleges (college_id INTEGER,
                                                shop_id INTEGER,
                                                review_count INTEGER,
                                                rating INTEGER,
                                                latitude INTEGER,
                                                longitude INTEGER,
                                                price TEXT,
                                                distance_from_college INTEGER,
                                                FOREIGN KEY(college_id) REFERENCES Colleges(college_id)
                                                FOREIGN KEY (shop_id) REFERENCES Shops (shop_id))''')

    conn.commit()


if __name__ == "__main__":
    print('You called me from the command line!')
    create_tables()
    print('SQL tables have been created in "total_data.db"!')
else:
    print(__name__ , 'was imported as a module!')
