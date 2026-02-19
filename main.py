from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
from io import StringIO
from collections import Counter
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")



@app.get("/")
def read_root():
    return FileResponse(os.path.join("frontend", "index.html"))
datasets = {}



@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df = pd.read_csv(
            StringIO(content.decode("utf-8-sig")),
            sep=",",
            on_bad_lines="skip",
            engine="python"
        )
    except Exception as e:
        return {"error": f"CSV parsing failed: {str(e)}"}

    dataset_id = str(len(datasets) + 1)
    datasets[dataset_id] = df

    schema_summary = [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
    return {"dataset_id": dataset_id, "schema": schema_summary}



@app.get("/api/dataset/{dataset_id}/table")
def get_table(dataset_id: str):
    df = datasets.get(dataset_id)
    if df is None:
        return {"error": "Dataset not found"}
    return df.to_dict(orient="records")



@app.get("/api/dataset/{dataset_id}/column/{col}/stats")
def get_stats(dataset_id: str, col: str):
    df = datasets.get(dataset_id)
    if df is None or col not in df.columns:
        return {"error": "Invalid dataset or column"}

    series = df[col].dropna()
    stats = {}

    if pd.api.types.is_numeric_dtype(series):
        stats["min"] = series.min().item()
        stats["max"] = series.max().item()
        stats["mean"] = float(series.mean())
        stats["median"] = float(series.median())
        stats["mode"] = series.mode().iloc[0].item() if not series.mode().empty else None
    else:
        stats["mode"] = Counter(series).most_common(1)[0][0]

    stats["missing_count"] = int(df[col].isna().sum())
    return stats




@app.get("/api/dataset/{dataset_id}/column/{col}/hist")
def get_histogram(dataset_id: str, col: str, bins: int = 30):
    df = datasets.get(dataset_id)
    if df is None or col not in df.columns:
        return {"error": "Invalid dataset or column"}

    series = df[col].dropna()
    if not pd.api.types.is_numeric_dtype(series):
        return {"error": "Histogram only for numeric columns"}

    hist, bin_edges = pd.cut(series, bins=bins, retbins=True)
    counts = hist.value_counts().tolist()
    return {
        "bins": [float(b) for b in bin_edges.tolist()],
        "counts": [int(c) for c in counts]
    }
