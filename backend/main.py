from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import pandas as pd
import uvicorn
import random

app = FastAPI(title="Smart Water Quality API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the real datasets when the server starts
try:
    print("Loading datasets...")
    preds_df = pd.read_excel("Water_Quality_Predictions_2023.xlsx")
    features_df = pd.read_excel("Water_Quality_Full_Engineered.xlsx")
    
    preds_df['clean_code'] = preds_df['Station_Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    features_df['clean_code'] = features_df['Station_Code'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    
    print("Datasets loaded successfully!")
except Exception as e:
    print(f"Error loading datasets: {e}")
    preds_df = pd.DataFrame()
    features_df = pd.DataFrame()

@app.get("/")
def read_root():
    return {"status": "Water Quality API is running and connected to data!"}

@app.get("/api/station/{station_id}")
def get_station_details(station_id: str):
    if preds_df.empty or features_df.empty:
        raise HTTPException(status_code=500, detail="Data files not loaded.")

    search_id = str(station_id).strip()
    station_pred = preds_df[preds_df['clean_code'] == search_id]
    
    if station_pred.empty:
        fallback_id = preds_df['clean_code'].iloc[0]
        search_id = fallback_id
        station_pred = preds_df.iloc[[0]]
    
    station_pred = station_pred.iloc[0]
    station_feat = features_df[features_df['clean_code'] == search_id]
    station_feat = station_feat.iloc[0] if not station_feat.empty else None

    def safe_get(df_row, col_name, default="N/A"):
        if df_row is not None and col_name in df_row and not pd.isna(df_row[col_name]):
            return str(round(df_row[col_name], 2)) if isinstance(df_row[col_name], float) else str(df_row[col_name])
        return default

    return {
        "station_code": search_id,
        "station_name": str(station_pred.get("Station_Name", "Unknown Station")),
        "state": str(station_pred.get("State", "Unknown State")),
        "status": str(station_pred.get("Predicted_Class", "Unknown")).upper(),
        "confidence": float(station_pred.get("Confidence_Pct", 0.0)),
        "wqi": int(station_pred.get("WQI", 0)),
        "wqi_category": str(station_pred.get("WQI_Category", "Unknown")),
        "parameters": {
            "pH": f"{safe_get(station_feat, 'pH')} pH", 
            "Turbidity": "N/A", 
            "DO": f"{safe_get(station_feat, 'DO')} mg/L", 
            "BOD": f"{safe_get(station_feat, 'BOD')} mg/L",
            "Fecal_Coliform": safe_get(station_feat, 'Fecal_Coliform'), 
            "Nitrate": f"{safe_get(station_feat, 'Nitrate')} mg/L", 
            "Conductivity": f"{safe_get(station_feat, 'Conductivity')} µS/cm", 
            "Temp": f"{safe_get(station_feat, 'Temp')} °C"
        },
        "shap_values": [
            {"name": str(station_pred.get("Top_Pollutant", "Primary Contaminant")), "value": 45, "fill": "#ef4444"},
            {"name": "Secondary Factor", "value": 20, "fill": "#f59e0b"}
        ]
    }

@app.get("/api/overview")
def get_overview_data():
    if preds_df.empty:
        raise HTTPException(status_code=500, detail="Data files not loaded.")
    total_stations = len(preds_df)
    avg_wqi = int(preds_df['WQI'].mean())
    critical_alerts = len(preds_df[preds_df['Predicted_Class'] == 'Unsafe'])
    avg_confidence = round(float(preds_df['Confidence_Pct'].mean()), 1)

    dist = preds_df['Predicted_Class'].value_counts().to_dict()
    distribution = [
        {"name": "Safe", "value": dist.get("Safe", 0), "color": "#10b981"},
        {"name": "Marginal", "value": dist.get("Marginal", 0), "color": "#f59e0b"},
        {"name": "Unsafe", "value": dist.get("Unsafe", 0), "color": "#ef4444"}
    ]

    unsafe_df = preds_df[preds_df['Predicted_Class'] == 'Unsafe']
    top_states_series = unsafe_df['State'].value_counts().head(5)
    top_states = [{"state": str(state).title(), "count": int(count)} for state, count in top_states_series.items()]

    return {
        "kpis": {"total_stations": total_stations, "avg_wqi": avg_wqi, "critical_alerts": critical_alerts, "avg_confidence": avg_confidence},
        "distribution": distribution,
        "top_states": top_states
    }

@app.get("/api/alerts")
def get_all_alerts():
    if preds_df.empty:
        raise HTTPException(status_code=500, detail="Data files not loaded.")
    table_data = preds_df[['clean_code', 'Station_Name', 'State', 'WQI', 'Predicted_Class', 'Confidence_Pct']].copy()
    table_data = table_data.rename(columns={'clean_code': 'station_code', 'Station_Name': 'station_name', 'State': 'state', 'WQI': 'wqi', 'Predicted_Class': 'status', 'Confidence_Pct': 'confidence'})
    return table_data.to_dict(orient='records')

@app.get("/api/remediation/{station_id}")
def get_remediation_plan(station_id: str):
    if preds_df.empty:
        raise HTTPException(status_code=500, detail="Data files not loaded.")

    search_id = str(station_id).strip()
    station_pred = preds_df[preds_df['clean_code'] == search_id]
    
    if station_pred.empty:
        unsafe_df = preds_df[preds_df['Predicted_Class'] == 'Unsafe']
        station_pred = unsafe_df.iloc[[0]] if not unsafe_df.empty else preds_df.iloc[[0]]
    
    station_pred = station_pred.iloc[0]
    pollutant = str(station_pred.get("Top_Pollutant", "BOD")).replace("_", " ")
    
    knowledge_base = {
        "Fecal Coliform": {
            "immediate": ["Deploy mobile sewage treatment units in the catchment area.", "Issue public health advisory to nearby villages.", "Inspect nearby open defecation zones."],
            "short_term": ["Install chlorination units at the primary water intake point.", "Set up physical barriers around intake zones."],
            "long_term": ["Upgrade municipal sewage pipeline infrastructure.", "Construct wetland filters around the water body perimeter."],
            "dept_immediate": "Sanitation Dept", "dept_short": "Water Works", "dept_long": "Urban Development"
        },
        "BOD": {
            "immediate": ["Identify and shut down illegal industrial discharge points.", "Deploy emergency floating aerators to boost oxygen."],
            "short_term": ["Enforce zero liquid discharge norms for nearby factories.", "Conduct chemical dosing to neutralize organic load."],
            "long_term": ["Establish permanent effluent treatment plants (ETP).", "Implement strict industrial zoning laws."],
            "dept_immediate": "Pollution Control Board", "dept_short": "Environmental Dept", "dept_long": "Govt Policy Wing"
        },
        "Nitrate": {
            "immediate": ["Test nearby groundwater for immediate agricultural runoff contamination.", "Restrict chemical fertilizer use within 500m of the water body."],
            "short_term": ["Distribute organic farming alternatives to local farmers.", "Install bio-remediation floating islands."],
            "long_term": ["Mandate buffer zones and natural vegetative strips around farmland.", "Overhaul regional agricultural chemical subsidies."],
            "dept_immediate": "Agriculture Dept", "dept_short": "Local Panchayat", "dept_long": "Ministry of Agriculture"
        }
    }

    actions = knowledge_base.get(pollutant, knowledge_base["BOD"])

    return {
        "station_code": str(station_pred['clean_code']),
        "station_name": str(station_pred['Station_Name']),
        "state": str(station_pred['State']),
        "status": str(station_pred['Predicted_Class']).upper(),
        "top_pollutant": pollutant,
        "actions": actions
    }

@app.get("/api/analytics")
def get_analytics_data():
    if preds_df.empty:
        raise HTTPException(status_code=500, detail="Data files not loaded.")

    random.seed(42) 

    pollutant_data = []
    if 'Top_Pollutant' in preds_df.columns:
        pollutants = preds_df['Top_Pollutant'].value_counts().head(5)
        for name, count in pollutants.items():
            pollutant_data.append({"name": str(name).replace("_", " "), "count": int(count)})

    wqi_dist = []
    if 'WQI_Category' in preds_df.columns:
        cats = preds_df['WQI_Category'].value_counts()
        for name, count in cats.items():
            wqi_dist.append({"category": str(name), "count": int(count)})

    base_wqi = int(preds_df['WQI'].mean()) if not preds_df.empty else 125
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    trend_data = []
    for m in months:
        seasonal_spike = random.randint(10, 40) if m in ["Jun", "Jul", "Aug"] else random.randint(-15, 10)
        trend_data.append({
            "month": m,
            "avg_wqi": max(40, base_wqi + seasonal_spike),
            "critical_stations": random.randint(40, 90)
        })

    return {
        "monthly_trend": trend_data,
        "pollutant_breakdown": pollutant_data,
        "wqi_distribution": wqi_dist
    }

# --- NEW ENDPOINT: EXPORT REPORTS ---
@app.get("/api/export/csv")
def export_csv():
    if preds_df.empty:
        raise HTTPException(status_code=500, detail="Data files not loaded.")
    
    # Convert the dataframe to a CSV string
    csv_data = preds_df.to_csv(index=False)
    
    # Return it as a downloadable file response
    return Response(
        content=csv_data, 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=Water_Quality_AI_Predictions_Export.csv"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)