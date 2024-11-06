import sqlite3
import requests

def create_db():
    conn = sqlite3.connect('municipalities.db')  
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS municipalities (
            code TEXT PRIMARY KEY,
            libelle TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def fetch_municipalities():
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/communes"
    headers = {
        "Authorization": "Bearer <TOKEN>",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def insert_municipalities(municipalities):
    conn = sqlite3.connect('municipalities.db')
    cursor = conn.cursor()
    
    for municipality in municipalities:
        code = municipality.get('code')
        libelle = municipality.get('libelle')
        
        if code and libelle:
            cursor.execute('''
                INSERT OR REPLACE INTO municipalities (code, libelle) 
                VALUES (?, ?)
            ''', (code, libelle))
    
    conn.commit()
    conn.close()

def fetch_municipality_by_code(municipality_code):
    conn = sqlite3.connect('municipalities.db')
    cursor = conn.cursor()

    cursor.execute("SELECT code, libelle FROM municipalities WHERE code = ?", (municipality_code,))
    
    row = cursor.fetchone()

    if row:
        return row[1] 
    else:
        return "Unknown"

  

def main():
    # create_db()  
    # municipalities = fetch_municipalities()  
    # insert_municipalities(municipalities)  
    # print("Municipalities have been successfully stored in the database.")

    fetch_municipality_by_code("03101") 
   


if __name__ == "__main__":
    main()
