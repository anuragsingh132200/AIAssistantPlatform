# Medicine Recommendation API with Semantic Search

A FastAPI-based service that uses semantic search to recommend medicines based on natural language descriptions of symptoms while avoiding specified allergies. The API leverages sentence-transformers for semantic understanding of medical conditions and side effects.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the FastAPI server:
   ```
   uvicorn app:app --reload
   ```

## API Endpoints

### GET /medicines

Get a list of medicines filtered by symptom using semantic search, excluding those that might trigger the specified allergy.

**Parameters:**
- `symptom` (required): The symptom or medical condition to treat (natural language, e.g., "headache" or "sore throat")
- `allergy` (required): The allergy to avoid in the results (natural language, e.g., "penicillin" or "aspirin")
- `region` (optional): Region filter (currently a placeholder)
- `top_k` (optional, default=10): Number of results to return
- `min_confidence` (optional, default=0.3): Minimum confidence threshold (0-1) for semantic matches

**Example Request:**
```
GET /medicines?symptom=persistent headache&allergy=aspirin&top_k=5&min_confidence=0.4
```

**Response:**
```json
[
  {
    "drug_name": "ibuprofen",
    "medical_condition": "headache, pain, fever",
    "side_effects": "stomach pain, heartburn, dizziness",
    "rating": "7.5",
    "drug_link": "https://www.drugs.com/ibuprofen.html",
    "confidence_score": 0.85,
    "allergy_risk": 0.12
  },
  ...
]
```

## How It Works

1. **Embedding Generation**: When the server starts, it generates or loads pre-computed embeddings for all medicines using the `all-MiniLM-L6-v2` model from sentence-transformers.
2. **Semantic Search**: Queries are converted to embeddings and compared against the medicine database using cosine similarity.
3. **Allergy Filtering**: Additional semantic matching is used to filter out medicines that might trigger the specified allergy.
4. **Caching**: Embeddings are cached to disk for faster subsequent startups.

## Data Source

The API uses data from `drugs_data.json` which contains information about various medicines, their uses, and side effects.
