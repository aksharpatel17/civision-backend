# Job Trends Tracker

This application is a Flask-based web app designed to track job posting trends over time. It fetches job postings from the France Travail API, stores them in a SQLite database, and provides graphical representations of the trends based on contract types, departments, and municipalities using Plotly.

## Features

- **Fetch Job Data**: Collects job postings from the past specified months using the France Travail API.
- **Store Job Data**: Stores job postings in a SQLite database with fields like title, location, municipality, department, contract type, experience level, and sector.
- **Visualize Trends**: Creates interactive bar charts for contract type distribution, department-wise postings, and top municipalities using Plotly.
- **Filter Data**: Allows users to select the time period (3, 6, 9, or 12 months) for trend analysis.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Flask**
- **Flask_SQLAlchemy**
- **requests**
- **plotly**
- **pandas**

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/job-trends-tracker.git
   cd job-trends-tracker
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```python
   python
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```

### API Authorization

This application requires an authorization token to access the France Travail API. Set your token in the `fetch_daily_jobs` function:

```python
headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer <YOUR_TOKEN>'
}
```

### Running the Application

Start the Flask server by running:

```bash
python app.py
```

The app will be accessible at `http://127.0.0.1:5000/`.

## Usage

1. Open your browser and go to `http://127.0.0.1:5000/`.
2. Choose the number of months for trend analysis (3, 6, 9, or 12 months).
3. The app will display interactive charts showing:
   - **Contract Type Distribution**
   - **Job Postings by Department**
   - **Top 20 Municipalities by Job Postings**

## Project Structure

- `app.py`: The main application file containing the Flask app, database models, and job fetching and visualization logic.
- `templates/index.html`: HTML template for rendering the web interface.
- `department.py` and `municipality.py`: Utility functions to fetch department and municipality names by code.

## License

This project is open-source and available under the MIT License.
