from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import StringIO
from collections import Counter

app = FastAPI()

# Allow frontend (http://localhost:5500) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
datasets = {}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    content = await file.read()
    try:
        # Use utf-8-sig to handle BOM, skip bad lines
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
        stats["min"] = series.min()
        stats["max"] = series.max()
        stats["mean"] = series.mean()
        stats["median"] = series.median()
        stats["mode"] = series.mode().iloc[0] if not series.mode().empty else None
    else:
        stats["mode"] = Counter(series).most_common(1)[0][0]

    stats["missing_count"] = df[col].isna().sum()
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
    return {"bins": bin_edges.tolist(), "counts": counts}
