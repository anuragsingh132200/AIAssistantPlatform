from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import pickle
from fastapi import Body

def clean_text(text: str) -> str:
    """Clean text by removing extra spaces, newlines, and special characters."""
    if not isinstance(text, str):
        return ""
    # Remove special characters but keep basic punctuation and letters
    text = re.sub(r'[^\w\s.,;:!?\-]', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

app = FastAPI(title="Medicine Recommendation API",
              description="API for filtering medicines based on symptoms and allergies using semantic search")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the sentence transformer model
MODEL_NAME = 'all-MiniLM-L6-v2'  # Lightweight model good for semantic similarity
EMBEDDINGS_CACHE = 'medicine_embeddings.pkl'

# Load or initialize the model and embeddings
def load_or_create_embeddings() -> Tuple[SentenceTransformer, Dict[str, Any]]:
    """Load or create embeddings for the medicines data."""
    model = SentenceTransformer(MODEL_NAME)
    
    # Load medicines data
    with open('drugs_data.json', 'r', encoding='utf-8') as f:
        try:
            medicines_data = json.load(f)
        except json.JSONDecodeError:
            content = f.read()
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'\([^)]*\)', '', content)
            medicines_data = json.loads(content)
    
    # Check if we have cached embeddings
    if os.path.exists(EMBEDDINGS_CACHE):
        try:
            with open(EMBEDDINGS_CACHE, 'rb') as f:
                embeddings_data = pickle.load(f)
            print("Loaded embeddings from cache")
            return model, embeddings_data
        except (pickle.UnpicklingError, EOFError, KeyError) as e:
            print(f"Error loading cached embeddings: {e}. Regenerating...")
    
    print("Generating new embeddings...")
    # Create a combined text field for each medicine for better semantic search
    texts = []
    for med in medicines_data:
        med_text = f"{med.get('drug_name', '')} {med.get('medical_condition', '')} {med.get('side_effects', '')}"
        texts.append(clean_text(med_text))
    
    # Generate embeddings
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    # Store the embeddings with the original data
    embeddings_data = {
        'medicines': medicines_data,
        'embeddings': embeddings,
        'texts': texts
    }
    
    # Cache the embeddings
    try:
        with open(EMBEDDINGS_CACHE, 'wb') as f:
            pickle.dump(embeddings_data, f)
        print("Generated and cached new embeddings")
    except Exception as e:
        print(f"Warning: Could not cache embeddings: {e}")
    
    return model, embeddings_data

# Load the model and data
model, embeddings_data = load_or_create_embeddings()
medicines_data = embeddings_data['medicines']
embeddings = embeddings_data['embeddings']

class MedicineResponse(BaseModel):
    drug_name: str
    medical_condition: str
    side_effects: str
    rating: Optional[str] = None
    drug_link: Optional[str] = None

class NLPSearchRequest(BaseModel):
    prompt: str

class NLPSearchResponse(BaseModel):
    drug_name: str
    medical_condition: str
    side_effects: str
    rating: Optional[str] = None
    drug_link: Optional[str] = None
    confidence_score: float

def semantic_search(query: str, top_k: int = 10, threshold: float = 0.3):
    """
    Perform semantic search on the medicines database.
    Returns indices of the top_k most similar medicines with similarity scores.
    """
    # Encode the query
    query_embedding = model.encode(query, convert_to_numpy=True).reshape(1, -1)
    
    # Calculate cosine similarity
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    
    # Get top_k results above threshold
    top_indices = np.argsort(similarities)[::-1][:top_k]
    top_indices = [i for i in top_indices if similarities[i] >= threshold]
    
    return [(i, float(similarities[i])) for i in top_indices]

# Mock region and pharmacy data
MOCK_REGIONS = [
    {"region_code": "NY", "region_name": "New York"},
    {"region_code": "CA", "region_name": "California"},
    {"region_code": "TX", "region_name": "Texas"},
    {"region_code": "FL", "region_name": "Florida"},
    {"region_code": "IL", "region_name": "Illinois"}
]

MOCK_PHARMACIES = {
    "NY": [
        {"pharmacy_name": "NY Health Pharmacy", "address": "123 Main St, New York, NY", "available_medicines": ["Aspirin", "Ibuprofen"]},
        {"pharmacy_name": "Manhattan Meds", "address": "456 Park Ave, New York, NY", "available_medicines": ["Paracetamol", "Cetirizine"]}
    ],
    "CA": [
        {"pharmacy_name": "CA Wellness", "address": "789 Sunset Blvd, Los Angeles, CA", "available_medicines": ["Aspirin", "Cetirizine"]},
        {"pharmacy_name": "Bay Area Pharmacy", "address": "101 Market St, San Francisco, CA", "available_medicines": ["Ibuprofen", "Paracetamol"]}
    ],
    "TX": [
        {"pharmacy_name": "Texas Meds", "address": "202 Lone Star Rd, Houston, TX", "available_medicines": ["Aspirin", "Paracetamol"]}
    ],
    "FL": [
        {"pharmacy_name": "Florida Health", "address": "303 Ocean Dr, Miami, FL", "available_medicines": ["Ibuprofen", "Cetirizine"]}
    ],
    "IL": [
        {"pharmacy_name": "Chicago Pharmacy", "address": "404 Lake Shore Dr, Chicago, IL", "available_medicines": ["Aspirin", "Ibuprofen"]}
    ]
}

@app.get("/regions")
async def get_regions():
    """Return a list of available regions (mocked)."""
    return MOCK_REGIONS

@app.get("/pharmacies")
async def get_pharmacies(region_code: str):
    """Return a list of pharmacies and their available medicines for a given region (mocked)."""
    return MOCK_PHARMACIES.get(region_code, [])

@app.get("/medicines", response_model=List[Dict[str, Any]])
async def get_medicines(
    symptom: str = Query(..., description="Symptom or medical condition to treat (natural language)"),
    allergy: str = Query(..., description="Allergy to avoid in the results (natural language)"),
    region: Optional[str] = Query(None, description="Region filter (region code, optional)"),
    top_k: int = Query(10, description="Number of results to return"),
    min_confidence: float = Query(0.3, description="Minimum confidence threshold (0-1)")
):
    try:
        query = f"Medicine for {symptom} but not for someone with {allergy} allergy"
        results = semantic_search(query, top_k=top_k * 2, threshold=min_confidence)
        filtered_medicines = []
        for idx, score in results:
            med = medicines_data[idx]
            if not all(key in med for key in ['drug_name', 'medical_condition', 'side_effects']):
                continue
            med_condition = clean_text(med.get('medical_condition', '')).lower()
            side_effects = clean_text(med.get('side_effects', '')).lower()
            drug_name = clean_text(med.get('drug_name', 'Unknown')).lower()
            allergy_embedding = model.encode(allergy, convert_to_numpy=True).reshape(1, -1)
            side_effects_embedding = model.encode(side_effects, convert_to_numpy=True).reshape(1, -1)
            allergy_similarity = float(cosine_similarity(allergy_embedding, side_effects_embedding)[0][0])
            if allergy_similarity > 0.4:
                continue
            # Region availability annotation
            available_in_region = None
            if region:
                pharmacies = MOCK_PHARMACIES.get(region, [])
                available_in_region = any(drug_name.capitalize() in p['available_medicines'] for p in pharmacies)
            response_med = {
                'drug_name': clean_text(med.get('drug_name', 'Unknown')),
                'medical_condition': med_condition,
                'side_effects': side_effects,
                'rating': clean_text(med.get('rating', 'N/A')),
                'drug_link': clean_text(med.get('drug_link', '')),
                'confidence_score': score,
                'allergy_risk': allergy_similarity,
                'available_in_region': available_in_region
            }
            filtered_medicines.append(response_med)
            if len(filtered_medicines) >= top_k:
                break
        return filtered_medicines
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/nlp-search", response_model=List[NLPSearchResponse])
async def nlp_search(request: NLPSearchRequest, top_k: int = 3):
    """
    Perform semantic search using a free-form NLP prompt and return the top matches from the drugs database.
    """
    try:
        results = semantic_search(request.prompt, top_k=top_k)
        matches = []
        for idx, score in results:
            med = medicines_data[idx]
            matches.append({
                'drug_name': clean_text(med.get('drug_name', 'Unknown')),
                'medical_condition': clean_text(med.get('medical_condition', '')),
                'side_effects': clean_text(med.get('side_effects', '')),
                'rating': clean_text(med.get('rating', 'N/A')),
                'drug_link': clean_text(med.get('drug_link', '')),
                'confidence_score': score
            })
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing NLP search: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
