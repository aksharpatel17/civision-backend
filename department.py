import sqlite3
import requests

def create_db():
    conn = sqlite3.connect('departments.db') 
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            code TEXT PRIMARY KEY,
            libelle TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def fetch_departments():
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/departements"
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

def insert_departments(departments):
    conn = sqlite3.connect('departments.db')
    cursor = conn.cursor()
    
    for department in departments:
        code = department.get('code')
        libelle = department.get('libelle')
        
        if code and libelle:
            cursor.execute('''
                INSERT OR REPLACE INTO departments (code, libelle) 
                VALUES (?, ?)
            ''', (code, libelle))
    
    conn.commit()
    conn.close()

def fetch_department_by_code(department_code):
    conn = sqlite3.connect('departments.db')
    cursor = conn.cursor()

    cursor.execute("SELECT code, libelle FROM departments WHERE code = ?", (department_code,))
    
    row = cursor.fetchone()

    if row:
        return row[1]
    else:
        return "Unknown"
    

def main():
    create_db()
    # departments = fetch_departments()  
    # insert_departments(departments) 
    # print("Departments have been successfully stored in the database.")

    fetch_department_by_code("78")

if __name__ == "__main__":
    main()
