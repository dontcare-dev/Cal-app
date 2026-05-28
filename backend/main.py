import sqlite3
import json
import base64
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# =============================================================================
# SYSTEM CONFIGURATION & INITIALIZATION
# =============================================================================
app = FastAPI(title="weare.kitty.devs API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "nutrition_scanner.db"

# =============================================================================
# DATABASE MANAGEMENT (PREVENTING COLUMN ERRORS)
# =============================================================================
def init_db():
    """Initializes the SQLite database with strict schema enforcement."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Core User Scans Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            brand TEXT NOT NULL,
            score INTEGER NOT NULL,
            rating TEXT NOT NULL,
            calories INTEGER DEFAULT 0,
            raw_image_data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Detailed Traits Table (Linked via Foreign Key)
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_traits (
            trait_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            trait_type TEXT NOT NULL,  -- 'positive' or 'negative'
            trait_name TEXT NOT NULL,
            description TEXT,
            value TEXT,
            indicator_color TEXT,
            FOREIGN KEY(scan_id) REFERENCES scan_history(scan_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# =============================================================================
# DATA MODELS (TYPE VALIDATION)
# =============================================================================
class ImagePayload(BaseModel):
    user_id: str
    image_base64: str

class Trait(BaseModel):
    name: str
    desc: str
    value: str
    color: str

class ScanResponse(BaseModel):
    productName: str
    brand: str
    score: int
    rating: str
    negatives: List[Trait]
    positives: List[Trait]

# =============================================================================
# AI / MOCK PROCESSING PIPELINE 
# =============================================================================
def process_image_stream(b64_string: str) -> dict:
    """
    In a full production environment (>1000 lines), this module hooks into 
    Google Cloud Vision or OpenAI GPT-4o. For local development, this parses 
    the request and returns a structured payload matching the local database.
    """
    # Simulate processing latency
    time.sleep(1.5)
    
    # Mocking a detected product based on your UI layout requirements
    return {
        "productName": "Tangy Cheese Tortilla Chips",
        "brand": "Doritos",
        "score": 21,
        "rating": "Bad",
        "calories": 501,
        "negatives": [
            {"name": "Additives", "desc": "Contains additives to avoid", "value": "9", "color": "red"},
            {"name": "Energy", "desc": "A bit too caloric", "value": "501 kcal", "color": "orange"},
            {"name": "Salt", "desc": "A bit too salty", "value": "1.19g", "color": "orange"}
        ],
        "positives": [
            {"name": "Fibre", "desc": "Excellent amount of fibre", "value": "5.6g", "color": "green"},
            {"name": "Protein", "desc": "Some protein", "value": "6.5g", "color": "green"},
            {"name": "Sugar", "desc": "Low sugar", "value": "2.7g", "color": "green"}
        ]
    }

# =============================================================================
# API ENDPOINTS
# =============================================================================
@app.post("/api/v1/scan", response_model=ScanResponse)
async def analyze_food_product(payload: ImagePayload):
    try:
        # 1. Process the image
        analysis_result = process_image_stream(payload.image_base64)
        
        # 2. Store the primary record in SQLite
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("""
            INSERT INTO scan_history (user_id, product_name, brand, score, rating, calories) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload.user_id, 
            analysis_result['productName'], 
            analysis_result['brand'], 
            analysis_result['score'], 
            analysis_result['rating'], 
            analysis_result['calories']
        ))
        
        scan_id = c.lastrowid
        
        # 3. Store traits linked to the scan_id
        for neg in analysis_result['negatives']:
            c.execute("""
                INSERT INTO product_traits (scan_id, trait_type, trait_name, description, value, indicator_color)
                VALUES (?, 'negative', ?, ?, ?, ?)
            """, (scan_id, neg['name'], neg['desc'], neg['value'], neg['color']))
            
        for pos in analysis_result['positives']:
            c.execute("""
                INSERT INTO product_traits (scan_id, trait_type, trait_name, description, value, indicator_color)
                VALUES (?, 'positive', ?, ?, ?, ?)
            """, (scan_id, pos['name'], pos['desc'], pos['value'], pos['color']))
            
        conn.commit()
        conn.close()
        
        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run via: python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
