# CSV Analyzer – Full Stack Assignment

## Overview
This project is a simple full‑stack CSV Analyzer built with:

- **Backend:** FastAPI (Python)  
- **Frontend:** HTML + JavaScript  
- **Data Processing:** Pandas  

It allows users to:
- Upload a CSV file
- View the dataset in a table
- Compute column statistics (min, max, mean, median, mode, missing count)
- Plot histograms for numeric columns

---

## Project Structure
frontend/
├── index.html       # Web interface
└── script.js        # Frontend logic
.gitignore             # Git ignore file
Sample_input.csv       # Example dataset
main.py                # FastAPI backend
output.png             # Output frontend

Code

---

## Features
- **Upload CSV:** Accepts CSV files and parses them with Pandas  
- **Table View:** Displays the uploaded dataset in a clean HTML table  
- **Column Stats:** Shows min, max, mean, median, mode, and missing count  
- **Histogram Plot:** Visualizes numeric column distributions with bar charts  
- **CORS Enabled:** Allows frontend and backend communication seamlessly  
- **Static Serving:** FastAPI serves the frontend files directly, so only one server is needed  

---

## Backend (FastAPI)
- **POST** `/api/upload` → Upload CSV, return dataset ID + schema  
- **GET** `/api/dataset/{id}/table` → Return table rows  
- **GET** `/api/dataset/{id}/column/{col}/stats` → Return column statistics  
- **GET** `/api/dataset/{id}/column/{col}/hist` → Return histogram bins + counts  

*Fix applied:* NumPy scalars are converted to native Python types (int, float) to avoid serialization errors.  

---

## Frontend (HTML + JS)
- **index.html:** UI with file upload, table display, column selector, stats panel, and histogram canvas  
- **script.js:** Handles API calls, renders table, formats stats, and draws histograms  
- Stats are displayed as a neat list in the right panel  

---

## How to Run
**Install dependencies:**
```bash
pip install fastapi uvicorn pandas
Start the backend:

bash
uvicorn main:app --reload
Open in browser:

Code
http://127.0.0.1:8000
Upload a CSV (e.g., Sample_input.csv) and interact with the app.

Example Workflow
Upload Sample_input.csv (student scores)

Table displays roll numbers, names, and subject scores

Select Physics column → click Get Stats

Output: Min, Max, Mean, Median, Mode, Missing Count

Click Plot Histogram → see distribution of Physics scores as bars
