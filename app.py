from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.io as pio
import pandas as pd
import time
from department import fetch_department_by_code
from municipality import fetch_municipality_by_code


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class JobPosting(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    municipality = db.Column(db.String, nullable=False)
    department = db.Column(db.String, nullable=False)
    contract_type = db.Column(db.String, nullable=False)
    experience_level = db.Column(db.String, nullable=False)
    sector = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()


def fetch_daily_jobs(months=3, monthly_job_limit=600):
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer <TOKEN>'
    }
    
    today = datetime.utcnow()
    start_date = today - timedelta(days=30 * months)
    
    url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
    
    
    total_fetched = 0

    for month in range(months):
        current_start_date = start_date + timedelta(days=30 * month)
        current_end_date = current_start_date + timedelta(days=30)
        
        params = {
            "minCreationDate": current_start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "maxCreationDate": current_end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        offset = 0
        jobs_stored = 0

        while jobs_stored < monthly_job_limit:
            params["range"] = f"{offset}-{offset + 149}"

            
            response = requests.get(url, headers=headers, params=params)
            

            jobs = response.json().get('resultats', [])
            if not jobs:
                print(f"No jobs found from {current_start_date} to {current_end_date}")
                break

            print(f"Fetched {len(jobs)} jobs from {current_start_date} to {current_end_date}")

            for job in jobs:
                if jobs_stored >= monthly_job_limit:
                    break

                if not JobPosting.query.get(job['id']):
                    job_entry = JobPosting(
                        id=job.get('id'),
                        title=job.get('intitule', 'Unknown Title'),
                        location=job.get('lieuTravail', {}).get('libelle', 'Unknown Location'),
                        municipality=fetch_municipality_by_code(str(job.get('lieuTravail', {}).get('commune', 'Unknown Municipality'))),
                        department=fetch_department_by_code(str(job.get('secteurActivite', 'Unknown Department'))),
                        contract_type=job.get('typeContrat', 'Unknown Contract'),
                        experience_level=job.get('experienceLibelle', 'Unknown Experience Level'),
                        sector=job.get('secteurActiviteLibelle', 'Unknown Sector'),
                        date_created=datetime.strptime(job['dateCreation'], "%Y-%m-%dT%H:%M:%S.%fZ") if 'dateCreation' in job else None,
                    )
                    db.session.add(job_entry)
                    jobs_stored += 1

            db.session.commit()
            total_fetched += len(jobs)
            offset += 150 

            time.sleep(0.1) 

    print(f"Total jobs fetched and stored: {total_fetched}")

def calculate_trends(months=6):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30 * months)
    
    jobs = JobPosting.query.filter(
        JobPosting.date_created >= start_date,
        JobPosting.date_created <= end_date
    ).all()
    
    data = [{
        'title': job.title,
        'location': job.location,
        'municipality': job.municipality,
        'department': job.department,
        'contract_type': job.contract_type,
        'experience_level': job.experience_level,
        'sector': job.sector,
        'date_created': job.date_created,
    } for job in jobs]
    
    df = pd.DataFrame(data)
    
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    contract_type_counts = df['contract_type'].value_counts().reset_index()
    contract_type_counts.columns = ['Contract Type', 'Count']
    filtered_df = df[(df['department'] != "Unknown") & (df['municipality'] != "Unknown")]

    department_counts = filtered_df.groupby('department').size().reset_index(name='Count')
    department_counts = department_counts.nlargest(20, 'Count')

    municipality_counts = filtered_df.groupby('municipality').size().reset_index(name='Count')
    municipality_counts = municipality_counts.nlargest(20, 'Count')


    return contract_type_counts, department_counts, municipality_counts
@app.route('/', methods=['GET', 'POST'])
def index():
    month_options = [3, 6, 9, 12]
    selected_months = request.args.get('months', default=3, type=int)
    
    if selected_months not in month_options:
        selected_months = 3
    
    fetch_daily_jobs(selected_months)
    contract_trend, department_trend, municipality_trend= calculate_trends(selected_months)
    
    if not contract_trend.empty:
        fig_contract = px.bar(contract_trend, x='Contract Type', y='Count', 
                            title=f"Contract Type Distribution (Last {selected_months} months)")
        fig_department = px.bar(department_trend.head(20), x='department', y='Count', 
                              title=f"Job Postings by Department (Last {selected_months} months)")
        fig_municipality = px.bar(municipality_trend.head(20), x='municipality', y='Count', 
                                title=f"Top 20 Municipalities by Job Postings (Last {selected_months} months)")
     
        
        contract_html = pio.to_html(fig_contract, full_html=False)
        department_html = pio.to_html(fig_department, full_html=False)
        municipality_html = pio.to_html(fig_municipality, full_html=False)
    else:
        contract_html = "<p>No data available for the selected time period</p>"
        department_html = "<p>No data available for the selected time period</p>"
        municipality_html = "<p>No data available for the selected time period</p>"

    return render_template('index.html', 
                         contract_chart=contract_html, 
                         department_chart=department_html, 
                         municipality_chart=municipality_html,
                         month_options=month_options,
                         selected_months=selected_months)

if __name__ == '__main__':
    app.run(debug=True)