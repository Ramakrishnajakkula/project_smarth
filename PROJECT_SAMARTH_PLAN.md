# Project Samarth: Intelligent Q&A System over Data.gov.in

**Author:** ramakrishna-18  
**Date:** 2025-10-29  
**Technology Stack:** Python 3.8, Streamlit, REST APIs

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Phase 1: Data Discovery & Integration](#phase-1-data-discovery--integration)
6. [Phase 2: Intelligent Q&A System](#phase-2-intelligent-qa-system)
7. [Phase 3: API Development](#phase-3-api-development)
8. [Phase 4: Streamlit UI](#phase-4-streamlit-ui)
9. [Phase 5: Deployment](#phase-5-deployment)
10. [Timeline & Milestones](#timeline--milestones)
11. [Testing Strategy](#testing-strategy)
12. [Sample Queries](#sample-queries)

> Task tracking: See PROJECT_SAMARTH_TRACKER.md for a live, checkbox-style work breakdown and progress tracker.

---

## 🎯 Project Overview

### The Vision

Build a functional, end-to-end prototype of an intelligent Q&A system that sources information directly from data.gov.in to answer complex natural language questions about India's agricultural economy and climate patterns.

### Core Requirements

- ✅ Answer complex cross-domain questions
- ✅ Cite all data sources with traceability
- ✅ Handle inconsistent data formats
- ✅ Provide accurate, data-backed responses
- ✅ Deploy in secure, private environment

### Key Deliverables

1. Functional Q&A system with Streamlit UI
2. Python 3.8 codebase
3. REST APIs for model inference
4. 2-minute Loom video walkthrough
5. Documentation and deployment guide

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                           │
│                   (Streamlit Frontend)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   API GATEWAY LAYER                          │
│              (FastAPI/Flask REST APIs)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Query Processor │    │  Answer Generator│
│  & Intent Detect │    │   (LLM/Hybrid)   │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│              DATA INTEGRATION LAYER                          │
│    - Source Router                                           │
│    - Query Translator                                        │
│    - Result Synthesizer                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│ Agriculture Data │    │   Climate Data   │
│  (Min. of Agri)  │    │      (IMD)       │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│              LOCAL DATA CACHE/DATABASE                       │
│     (MongoDB Atlas M0 free / Parquet & JSON cache)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Core Technologies

- **Language:** Python 3.8
- **UI Framework:** Streamlit
- **API Framework:** FastAPI or Flask
- **Database:** MongoDB (Atlas M0 free tier for dev/prod); optional local JSON/Parquet cache for quick reads
- **Data Processing:** Pandas, NumPy

### NLP & AI

- **LLM Options:**
  - Hugging Face Inference API (free-tier) or local Transformers/llama.cpp (free, on-device)
  - OpenAI GPT (optional, not default; requires paid API key)
  - LangChain/LlamaIndex for orchestration
- **Intent Classification:** spaCy, NLTK
- **Embeddings:** Sentence-Transformers

### Data Access

- **HTTP Requests:** requests, aiohttp
- **Web Scraping:** BeautifulSoup4, Selenium (if needed)
- **API Clients:** Custom Python clients

### Deployment

- **Containerization:** Docker
- **Cloud Options (free-tier first):**
  - Deta Space (FastAPI backend, free)
  - Streamlit Community Cloud (UI, free)
  - Alternative: Vercel Serverless Functions for Python (free hobby tier)
- **Local:** Virtual environment with requirements.txt

---

## 📁 Project Structure

```
project-samarth/
│
├── README.md
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
│
├── data/
│   ├── raw/                    # Raw downloaded datasets
│   ├── processed/              # Cleaned and normalized data
│   └── cache/                  # Cached query results
│
├── src/
│   ├── __init__.py
│   │
│   ├── data_ingestion/
│   │   ├── __init__.py
│   │   ├── data_fetcher.py     # Fetch data from data.gov.in
│   │   ├── agriculture_loader.py
│   │   ├── climate_loader.py
│   │   └── data_normalizer.py  # Normalize & clean data
│   │
│   ├── data_processing/
│   │   ├── __init__.py
│   │   ├── query_parser.py     # Parse user queries
│   │   ├── intent_classifier.py
│   │   └── data_router.py      # Route to correct data source
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── llm_handler.py      # LLM integration
│   │   ├── prompt_templates.py
│   │   └── citation_tracker.py # Track data sources
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI/Flask app
│   │   ├── routes.py           # API endpoints
│   │   └── schemas.py          # Pydantic models
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # Configuration
│       ├── logger.py           # Logging setup
│       └── helpers.py          # Utility functions
│
├── streamlit_app/
│   ├── app.py                  # Main Streamlit app
│   ├── components/
│   │   ├── query_input.py
│   │   ├── result_display.py
│   │   └── citation_view.py
│   └── styles/
│       └── custom.css
│
├── tests/
│   ├── test_data_ingestion.py
│   ├── test_query_processing.py
│   └── test_api.py
│
└── notebooks/
    ├── data_exploration.ipynb
    └── model_evaluation.ipynb
```

---

## 📊 Phase 1: Data Discovery & Integration

### Objectives

1. Identify relevant datasets on data.gov.in
2. Understand data formats and access methods
3. Build ingestion pipeline
4. Normalize and store data

### Key Datasets to Target

#### Agriculture Data (Ministry of Agriculture & Farmers Welfare)

- Crop production statistics (state/district level)
- Area under cultivation
- Yield data
- Soil health data
- Market prices

#### Climate Data (IMD)

- Rainfall data (monthly/annual)
- Temperature records
- Humidity levels
- Weather patterns

### Implementation: Data Fetcher

```python
# src/data_ingestion/data_fetcher.py

import requests
import pandas as pd
from typing import Dict, List, Optional
import os
from pathlib import Path

class DataGovInFetcher:
    """Fetch datasets from data.gov.in portal"""

    BASE_URL = "https://data.gov.in/api/datastore/resource.json"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize fetcher with optional API key

        Args:
            api_key: data.gov.in API key (if required)
        """
        self.api_key = api_key or os.getenv('DATA_GOV_IN_API_KEY')
        self.session = requests.Session()

    def fetch_resource(self, resource_id: str, filters: Optional[Dict] = None,
                       limit: int = 1000) -> pd.DataFrame:
        """
        Fetch data from a specific resource ID

        Args:
            resource_id: Dataset resource ID from data.gov.in
            filters: Optional filters to apply
            limit: Maximum records to fetch

        Returns:
            DataFrame with fetched data
        """
        params = {
            'resource_id': resource_id,
            'limit': limit
        }

        if self.api_key:
            params['api-key'] = self.api_key

        if filters:
            params['filters'] = filters

        try:
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if 'records' in data:
                df = pd.DataFrame(data['records'])
                df.attrs['source_url'] = response.url
                df.attrs['resource_id'] = resource_id
                return df
            else:
                raise ValueError(f"No records found for resource {resource_id}")

        except Exception as e:
            print(f"Error fetching resource {resource_id}: {e}")
            return pd.DataFrame()

    def download_csv_resource(self, url: str, save_path: Optional[str] = None) -> pd.DataFrame:
        """
        Download CSV file from direct URL

        Args:
            url: Direct download URL
            save_path: Optional path to save the file

        Returns:
            DataFrame with loaded data
        """
        try:
            df = pd.read_csv(url)
            df.attrs['source_url'] = url

            if save_path:
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(save_path, index=False)

            return df

        except Exception as e:
            print(f"Error downloading CSV from {url}: {e}")
            return pd.DataFrame()


# Example usage
if __name__ == "__main__":
    fetcher = DataGovInFetcher()

    # Example: Fetch crop production data
    # (Replace with actual resource IDs from data.gov.in)
    crop_data = fetcher.fetch_resource(
        resource_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        filters={"State": "Maharashtra"},
        limit=5000
    )

    print(f"Fetched {len(crop_data)} records")
```

### Implementation: Data Normalizer

```python
# src/data_ingestion/data_normalizer.py

import pandas as pd
import re
from typing import Dict, List
import numpy as np

class DataNormalizer:
    """Normalize and clean data from different sources"""

    # Standardized state names mapping
    STATE_MAPPING = {
        'MAHARASHTRA': 'Maharashtra',
        'Maharashtra': 'Maharashtra',
        'maharashtra': 'Maharashtra',
        'UTTAR PRADESH': 'Uttar Pradesh',
        'UP': 'Uttar Pradesh',
        # Add more mappings...
    }

    # Standardized crop names
    CROP_MAPPING = {
        'RICE': 'Rice',
        'rice': 'Rice',
        'Paddy': 'Rice',
        'WHEAT': 'Wheat',
        'wheat': 'Wheat',
        # Add more mappings...
    }

    def __init__(self):
        self.state_map = self.STATE_MAPPING
        self.crop_map = self.CROP_MAPPING

    def normalize_state_names(self, df: pd.DataFrame, state_column: str) -> pd.DataFrame:
        """Normalize state names to standard format"""
        df = df.copy()

        if state_column in df.columns:
            df[state_column] = df[state_column].map(
                lambda x: self.state_map.get(x, x) if pd.notna(x) else x
            )

        return df

    def normalize_crop_names(self, df: pd.DataFrame, crop_column: str) -> pd.DataFrame:
        """Normalize crop names to standard format"""
        df = df.copy()

        if crop_column in df.columns:
            df[crop_column] = df[crop_column].map(
                lambda x: self.crop_map.get(x, x) if pd.notna(x) else x
            )

        return df

    def standardize_units(self, df: pd.DataFrame,
                          value_column: str,
                          unit_column: Optional[str] = None,
                          target_unit: str = 'tonnes') -> pd.DataFrame:
        """Convert values to standard units"""
        df = df.copy()

        # Conversion factors
        conversions = {
            'kg': 0.001,
            'quintal': 0.1,
            'tonnes': 1.0,
            'ton': 1.0,
            'mt': 1.0
        }

        if unit_column and unit_column in df.columns:
            for unit, factor in conversions.items():
                mask = df[unit_column].str.lower() == unit
                df.loc[mask, value_column] = df.loc[mask, value_column] * factor

        return df

    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
        """Handle missing values in dataset"""
        df = df.copy()

        if strategy == 'drop':
            df = df.dropna()
        elif strategy == 'fill_zero':
            df = df.fillna(0)
        elif strategy == 'forward_fill':
            df = df.fillna(method='ffill')

        return df

    def add_metadata(self, df: pd.DataFrame, source: str, dataset_name: str) -> pd.DataFrame:
        """Add metadata columns for traceability"""
        df = df.copy()
        df['_source'] = source
        df['_dataset'] = dataset_name
        df['_fetched_at'] = pd.Timestamp.now()

        return df


# Example usage
if __name__ == "__main__":
    normalizer = DataNormalizer()

    # Example DataFrame
    sample_data = pd.DataFrame({
        'State': ['MAHARASHTRA', 'UP', 'maharashtra'],
        'Crop': ['RICE', 'wheat', 'Paddy'],
        'Production': [1000, 2000, 1500]
    })

    # Normalize
    normalized = normalizer.normalize_state_names(sample_data, 'State')
    normalized = normalizer.normalize_crop_names(normalized, 'Crop')
    normalized = normalizer.add_metadata(normalized, 'data.gov.in', 'crop_production')

    print(normalized)
```

---

## 🤖 Phase 2: Intelligent Q&A System

### Architecture Components

1. **Query Parser**: Extract entities and intent from user questions
2. **Intent Classifier**: Determine question type (comparison, trend, correlation, etc.)
3. **Data Router**: Route to appropriate data sources
4. **LLM Handler**: Generate natural language responses
5. **Citation Tracker**: Maintain source references

### Implementation: Query Parser

```python
# src/data_processing/query_parser.py

import spacy
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ParsedQuery:
    """Structured representation of parsed query"""
    raw_query: str
    intent: str
    entities: Dict[str, List[str]]
    temporal: Optional[Dict[str, any]]
    comparison: bool
    aggregation: Optional[str]

class QueryParser:
    """Parse natural language queries into structured format"""

    def __init__(self):
        # Load spaCy model (install: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Installing spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        # Define patterns
        self.state_pattern = re.compile(r'\b(Maharashtra|Gujarat|Punjab|Haryana|Karnataka|' +
                                        r'Tamil Nadu|Andhra Pradesh|Kerala|Rajasthan|' +
                                        r'Madhya Pradesh|Uttar Pradesh|Bihar|West Bengal)\b',
                                        re.IGNORECASE)

        self.crop_pattern = re.compile(r'\b(rice|wheat|cotton|sugarcane|maize|pulses|' +
                                       r'jowar|bajra|soybean|groundnut|sunflower)\b',
                                       re.IGNORECASE)

        self.time_pattern = re.compile(r'(\d{4})|' +  # Year
                                       r'(last \d+ years?)|' +  # Last N years
                                       r'(decade)|' +  # Decade
                                       r'(\d{4}-\d{4})')  # Year range

    def parse(self, query: str) -> ParsedQuery:
        """
        Parse user query into structured format

        Args:
            query: Natural language question

        Returns:
            ParsedQuery object with extracted information
        """
        doc = self.nlp(query)

        # Extract entities
        entities = {
            'states': self._extract_states(query),
            'crops': self._extract_crops(query),
            'districts': self._extract_districts(doc),
            'metrics': self._extract_metrics(query)
        }

        # Determine intent
        intent = self._classify_intent(query)

        # Extract temporal information
        temporal = self._extract_temporal(query)

        # Check for comparison
        is_comparison = self._detect_comparison(query)

        # Extract aggregation type
        aggregation = self._extract_aggregation(query)

        return ParsedQuery(
            raw_query=query,
            intent=intent,
            entities=entities,
            temporal=temporal,
            comparison=is_comparison,
            aggregation=aggregation
        )

    def _extract_states(self, query: str) -> List[str]:
        """Extract state names from query"""
        matches = self.state_pattern.findall(query)
        return [m.title() for m in matches]

    def _extract_crops(self, query: str) -> List[str]:
        """Extract crop names from query"""
        matches = self.crop_pattern.findall(query)
        return [m.title() for m in matches]

    def _extract_districts(self, doc) -> List[str]:
        """Extract district names using NER"""
        districts = []
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical entity
                # Simple heuristic: if not a known state, might be district
                if ent.text not in self.state_pattern.pattern:
                    districts.append(ent.text)
        return districts

    def _extract_metrics(self, query: str) -> List[str]:
        """Extract metrics mentioned (production, rainfall, yield, etc.)"""
        metrics_keywords = {
            'production': ['production', 'produce', 'output', 'yield'],
            'rainfall': ['rainfall', 'precipitation', 'rain'],
            'temperature': ['temperature', 'temp'],
            'area': ['area', 'acreage', 'cultivation'],
            'yield': ['yield', 'productivity']
        }

        query_lower = query.lower()
        metrics = []

        for metric, keywords in metrics_keywords.items():
            if any(kw in query_lower for kw in keywords):
                metrics.append(metric)

        return metrics

    def _classify_intent(self, query: str) -> str:
        """Classify query intent"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['compare', 'comparison', 'versus', 'vs']):
            return 'comparison'
        elif any(word in query_lower for word in ['trend', 'over time', 'change', 'growth']):
            return 'trend_analysis'
        elif any(word in query_lower for word in ['correlate', 'correlation', 'relationship', 'impact']):
            return 'correlation'
        elif any(word in query_lower for word in ['highest', 'lowest', 'maximum', 'minimum', 'top', 'bottom']):
            return 'ranking'
        elif any(word in query_lower for word in ['list', 'show', 'display']):
            return 'list'
        else:
            return 'general_query'

    def _extract_temporal(self, query: str) -> Optional[Dict]:
        """Extract temporal information"""
        match = self.time_pattern.search(query)

        if not match:
            return None

        temporal = {}

        # Extract year
        if match.group(1):
            temporal['year'] = int(match.group(1))

        # Extract "last N years"
        if match.group(2):
            n_years = re.search(r'\d+', match.group(2))
            if n_years:
                temporal['last_n_years'] = int(n_years.group())

        # Decade
        if match.group(3):
            temporal['period'] = 'decade'
            temporal['last_n_years'] = 10

        return temporal

    def _detect_comparison(self, query: str) -> bool:
        """Detect if query involves comparison"""
        comparison_keywords = ['compare', 'versus', 'vs', 'between', 'and']
        return any(kw in query.lower() for kw in comparison_keywords)

    def _extract_aggregation(self, query: str) -> Optional[str]:
        """Extract aggregation type (average, sum, max, min)"""
        query_lower = query.lower()

        if 'average' in query_lower or 'mean' in query_lower:
            return 'average'
        elif 'total' in query_lower or 'sum' in query_lower:
            return 'sum'
        elif 'highest' in query_lower or 'maximum' in query_lower or 'max' in query_lower:
            return 'max'
        elif 'lowest' in query_lower or 'minimum' in query_lower or 'min' in query_lower:
            return 'min'

        return None


# Example usage
if __name__ == "__main__":
    parser = QueryParser()

    query = "Compare the average annual rainfall in Maharashtra and Gujarat for the last 5 years"
    parsed = parser.parse(query)

    print(f"Intent: {parsed.intent}")
    print(f"States: {parsed.entities['states']}")
    print(f"Metrics: {parsed.entities['metrics']}")
    print(f"Temporal: {parsed.temporal}")
    print(f"Is Comparison: {parsed.comparison}")
    print(f"Aggregation: {parsed.aggregation}")
```

### Implementation: LLM Handler with LangChain

```python
# src/models/llm_handler.py

from typing import Dict, List, Optional
import os
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
import pandas as pd

class LLMHandler:
    """Handle LLM interactions for answer generation"""

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.3):
        """
        Initialize LLM handler

        Args:
            model_name: OpenAI model to use
            temperature: Creativity parameter (0-1)
        """
        self.api_key = os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=self.api_key
        )

        self.answer_template = self._create_answer_template()

    def _create_answer_template(self) -> PromptTemplate:
        """Create prompt template for answer generation"""
        template = """You are an expert data analyst specializing in agricultural and climate data for India.

User Question: {question}

Available Data:
{data_summary}

Data Sources:
{sources}

Instructions:
1. Answer the question accurately based ONLY on the provided data
2. Cite specific data sources for every claim using [Source: dataset_name]
3. If data is insufficient, clearly state what's missing
4. Present numbers with appropriate units
5. Be concise but comprehensive

Answer:"""

        return PromptTemplate(
            input_variables=["question", "data_summary", "sources"],
            template=template
        )

    def generate_answer(self,
                       question: str,
                       data: Dict[str, pd.DataFrame],
                       sources: Dict[str, str]) -> Dict[str, any]:
        """
        Generate answer using LLM

        Args:
            question: User's question
            data: Dictionary of DataFrames with relevant data
            sources: Dictionary mapping dataset names to source URLs

        Returns:
            Dictionary with answer, citations, and metadata
        """
        # Prepare data summary
        data_summary = self._prepare_data_summary(data)

        # Format sources
        sources_text = self._format_sources(sources)

        # Create chain
        chain = LLMChain(llm=self.llm, prompt=self.answer_template)

        # Generate answer with token tracking
        with get_openai_callback() as cb:
            answer = chain.run(
                question=question,
                data_summary=data_summary,
                sources=sources_text
            )

            tokens_used = cb.total_tokens
            cost = cb.total_cost

        # Extract citations from answer
        citations = self._extract_citations(answer, sources)

        return {
            'answer': answer,
            'citations': citations,
            'tokens_used': tokens_used,
            'cost': cost,
            'model': self.llm.model_name
        }

    def _prepare_data_summary(self, data: Dict[str, pd.DataFrame]) -> str:
        """Convert DataFrames to text summary for LLM"""
        summaries = []

        for dataset_name, df in data.items():
            summary = f"\n--- {dataset_name} ---\n"
            summary += f"Columns: {', '.join(df.columns.tolist())}\n"
            summary += f"Rows: {len(df)}\n"

            # Add sample data (first few rows)
            summary += "\nSample Data:\n"
            summary += df.head(10).to_string(index=False)

            # Add statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary += "\n\nStatistics:\n"
                summary += df[numeric_cols].describe().to_string()

            summaries.append(summary)

        return "\n\n".join(summaries)

    def _format_sources(self, sources: Dict[str, str]) -> str:
        """Format sources dictionary to text"""
        lines = []
        for name, url in sources.items():
            lines.append(f"- {name}: {url}")
        return "\n".join(lines)

    def _extract_citations(self, answer: str, sources: Dict[str, str]) -> List[Dict]:
        """Extract citations from answer text"""
        import re

        citations = []
        pattern = r'\[Source: ([^\]]+)\]'
        matches = re.findall(pattern, answer)

        for match in matches:
            if match in sources:
                citations.append({
                    'dataset': match,
                    'url': sources[match]
                })

        return citations


# Alternative: Local LLM Handler (for data sovereignty)
class LocalLLMHandler:
    """Handle local LLM for secure deployment"""

    def __init__(self, model_path: str):
        """
        Initialize local LLM

        Args:
            model_path: Path to local model (e.g., GGUF format)
        """
        from langchain.llms import LlamaCpp

        self.llm = LlamaCpp(
            model_path=model_path,
            temperature=0.3,
            max_tokens=2000,
            n_ctx=4096
        )

    # Similar methods as LLMHandler...
```

---

## 🔌 Phase 3: API Development

### Implementation: FastAPI Backend

```python
# src/api/main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime

# Import custom modules
import sys
sys.path.append('..')
from data_processing.query_parser import QueryParser
from models.llm_handler import LLMHandler
from data_integration.data_router import DataRouter

app = FastAPI(
    title="Project Samarth API",
    description="Intelligent Q&A API over agricultural and climate data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
query_parser = QueryParser()
llm_handler = LLMHandler()
data_router = DataRouter()

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    context: Optional[Dict] = None

class Citation(BaseModel):
    dataset: str
    url: str
    description: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    query_metadata: Dict
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process natural language query

    Args:
        request: QueryRequest with question and optional context

    Returns:
        QueryResponse with answer and citations
    """
    try:
        # Parse query
        parsed = query_parser.parse(request.question)

        # Route to appropriate data sources and fetch data
        data, sources = data_router.fetch_relevant_data(parsed)

        if not data:
            raise HTTPException(
                status_code=404,
                detail="No relevant data found for this query"
            )

        # Generate answer using LLM
        result = llm_handler.generate_answer(
            question=request.question,
            data=data,
            sources=sources
        )

        # Format citations
        citations = [
            Citation(
                dataset=c['dataset'],
                url=c['url'],
                description=f"Data from {c['dataset']}"
            )
            for c in result['citations']
        ]

        # Log query (background task)
        background_tasks.add_task(
            log_query,
            question=request.question,
            intent=parsed.intent,
            sources_used=list(sources.keys())
        )

        return QueryResponse(
            answer=result['answer'],
            citations=citations,
            query_metadata={
                'intent': parsed.intent,
                'entities': parsed.entities,
                'temporal': parsed.temporal,
                'tokens_used': result['tokens_used'],
                'model': result['model']
            },
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/datasets")
async def list_datasets():
    """List available datasets"""
    return {
        "agriculture": data_router.get_agriculture_datasets(),
        "climate": data_router.get_climate_datasets()
    }


@app.get("/stats")
async def get_stats():
    """Get API usage statistics"""
    # Implement statistics tracking
    return {
        "total_queries": 0,
        "popular_intents": {},
        "avg_response_time": 0
    }


def log_query(question: str, intent: str, sources_used: List[str]):
    """Log query for analytics (background task)"""
    # Implement logging to database or file
    import json
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'intent': intent,
        'sources': sources_used
    }

    with open('logs/queries.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Implementation: Data Router

```python
# src/data_integration/data_router.py

import pandas as pd
from typing import Dict, List, Tuple
import os
from pathlib import Path

class DataRouter:
    """Route queries to appropriate data sources"""

    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.agriculture_data = {}
        self.climate_data = {}
        self._load_datasets()

    def _load_datasets(self):
        """Load all processed datasets into memory"""
        # Load agriculture datasets
        agri_dir = self.data_dir / "agriculture"
        if agri_dir.exists():
            for file in agri_dir.glob("*.parquet"):
                df = pd.read_parquet(file)
                self.agriculture_data[file.stem] = df

        # Load climate datasets
        climate_dir = self.data_dir / "climate"
        if climate_dir.exists():
            for file in climate_dir.glob("*.parquet"):
                df = pd.read_parquet(file)
                self.climate_data[file.stem] = df

    def fetch_relevant_data(self, parsed_query) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
        """
        Fetch relevant data based on parsed query

        Args:
            parsed_query: ParsedQuery object

        Returns:
            Tuple of (data dict, sources dict)
        """
        relevant_data = {}
        sources = {}

        # Determine which datasets to query based on intent and entities
        metrics = parsed_query.entities.get('metrics', [])

        # Agriculture data
        if any(m in ['production', 'yield', 'area'] for m in metrics):
            agri_data = self._filter_agriculture_data(parsed_query)
            if not agri_data.empty:
                relevant_data['agriculture_data'] = agri_data
                sources['agriculture_data'] = "https://data.gov.in/agriculture/crop-production"

        # Climate data
        if any(m in ['rainfall', 'temperature'] for m in metrics):
            climate_data = self._filter_climate_data(parsed_query)
            if not climate_data.empty:
                relevant_data['climate_data'] = climate_data
                sources['climate_data'] = "https://data.gov.in/imd/rainfall-data"

        return relevant_data, sources

    def _filter_agriculture_data(self, parsed_query) -> pd.DataFrame:
        """Filter agriculture datasets based on query"""
        if 'crop_production' not in self.agriculture_data:
            return pd.DataFrame()

        df = self.agriculture_data['crop_production'].copy()

        # Filter by states
        states = parsed_query.entities.get('states', [])
        if states:
            df = df[df['State'].isin(states)]

        # Filter by crops
        crops = parsed_query.entities.get('crops', [])
        if crops:
            df = df[df['Crop'].isin(crops)]

        # Filter by time period
        if parsed_query.temporal:
            if 'year' in parsed_query.temporal:
                df = df[df['Year'] == parsed_query.temporal['year']]
            elif 'last_n_years' in parsed_query.temporal:
                n = parsed_query.temporal['last_n_years']
                max_year = df['Year'].max()
                df = df[df['Year'] >= (max_year - n + 1)]

        return df

    def _filter_climate_data(self, parsed_query) -> pd.DataFrame:
        """Filter climate datasets based on query"""
        if 'rainfall' not in self.climate_data:
            return pd.DataFrame()

        df = self.climate_data['rainfall'].copy()

        # Filter by states
        states = parsed_query.entities.get('states', [])
        if states:
            df = df[df['State'].isin(states)]

        # Filter by time period
        if parsed_query.temporal:
            if 'year' in parsed_query.temporal:
                df = df[df['Year'] == parsed_query.temporal['year']]
            elif 'last_n_years' in parsed_query.temporal:
                n = parsed_query.temporal['last_n_years']
                max_year = df['Year'].max()
                df = df[df['Year'] >= (max_year - n + 1)]

        return df

    def get_agriculture_datasets(self) -> List[str]:
        """Get list of available agriculture datasets"""
        return list(self.agriculture_data.keys())

    def get_climate_datasets(self) -> List[str]:
        """Get list of available climate datasets"""
        return list(self.climate_data.keys())
```

---

## 🎨 Phase 4: Streamlit UI

### Implementation: Main Streamlit App

```python
# streamlit_app/app.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="Project Samarth - Intelligent Q&A",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #558B2F;
        margin-top: 2rem;
    }
    .citation-box {
        background-color: #F1F8E9;
        border-left: 4px solid #7CB342;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .answer-box {
        background-color: #FFFFFF;
        border: 1px solid #C5E1A5;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

def main():
    # Header
    st.markdown('<h1 class="main-header">🌾 Project Samarth</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">Intelligent Q&A System over Agricultural and Climate Data</p>',
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/2E7D32/FFFFFF?text=Project+Samarth",
                 use_column_width=True)

        st.markdown("### About")
        st.info("""
        This system answers complex questions about India's agricultural economy
        and climate patterns using live data from data.gov.in.

        **Features:**
        - 📊 Cross-domain data analysis
        - 🔍 Source citation & traceability
        - 🤖 AI-powered insights
        - 🔒 Secure & private deployment
        """)

        st.markdown("### Sample Questions")
        sample_questions = [
            "Compare average annual rainfall in Maharashtra and Gujarat for last 5 years",
            "Top 3 rice producing districts in Punjab",
            "Correlation between rainfall and wheat production in Haryana",
            "Production trend of cotton in Maharashtra over last decade"
        ]

        selected_sample = st.selectbox(
            "Try a sample question:",
            [""] + sample_questions,
            index=0
        )

        if st.button("Use This Question"):
            st.session_state.selected_question = selected_sample

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<h2 class="sub-header">Ask Your Question</h2>', unsafe_allow_html=True)

        # Question input
        default_question = st.session_state.get('selected_question', '')
        question = st.text_area(
            "Enter your question about agricultural and climate data:",
            value=default_question,
            height=100,
            placeholder="e.g., Compare the average annual rainfall in Maharashtra and Gujarat for the last 5 years..."
        )

        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            submit_button = st.button("🔍 Ask", type="primary", use_container_width=True)
        with col_btn2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)

        if clear_button:
            st.session_state.selected_question = ''
            st.rerun()

        # Process query
        if submit_button and question:
            with st.spinner("🤔 Analyzing your question and fetching data..."):
                try:
                    # Call API
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={"question": question},
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # Display answer
                        st.markdown('<h2 class="sub-header">Answer</h2>', unsafe_allow_html=True)
                        st.markdown(f'<div class="answer-box">{result["answer"]}</div>',
                                  unsafe_allow_html=True)

                        # Display citations
                        if result['citations']:
                            st.markdown('<h2 class="sub-header">📚 Data Sources</h2>',
                                      unsafe_allow_html=True)

                            for i, citation in enumerate(result['citations'], 1):
                                st.markdown(f"""
                                <div class="citation-box">
                                    <strong>{i}. {citation['dataset']}</strong><br>
                                    <a href="{citation['url']}" target="_blank">🔗 View Source</a>
                                </div>
                                """, unsafe_allow_html=True)

                        # Display metadata
                        with st.expander("🔍 Query Analysis Details"):
                            col_m1, col_m2, col_m3 = st.columns(3)

                            with col_m1:
                                st.metric("Intent", result['query_metadata']['intent'])

                            with col_m2:
                                st.metric("Tokens Used", result['query_metadata']['tokens_used'])

                            with col_m3:
                                st.metric("Model", result['query_metadata']['model'])

                            st.json(result['query_metadata']['entities'])

                        # Add to history
                        st.session_state.query_history.append({
                            'timestamp': datetime.now(),
                            'question': question,
                            'answer': result['answer'][:200] + '...'
                        })

                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to API. Make sure the backend is running at http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    with col2:
        st.markdown('<h2 class="sub-header">Query History</h2>', unsafe_allow_html=True)

        if st.session_state.query_history:
            for i, query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
                with st.expander(f"Query {len(st.session_state.query_history) - i + 1}"):
                    st.write(f"**Time:** {query['timestamp'].strftime('%H:%M:%S')}")
                    st.write(f"**Q:** {query['question']}")
                    st.write(f"**A:** {query['answer']}")
        else:
            st.info("No queries yet. Ask a question to get started!")

    # Footer
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        if st.button("📊 View Datasets"):
            show_datasets()

    with col_f2:
        if st.button("📈 API Stats"):
            show_stats()

    with col_f3:
        if st.button("ℹ️ About Project"):
            show_about()


def show_datasets():
    """Display available datasets"""
    try:
        response = requests.get(f"{API_BASE_URL}/datasets")
        if response.status_code == 200:
            datasets = response.json()

            st.subheader("Available Datasets")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Agriculture Datasets**")
                for ds in datasets.get('agriculture', []):
                    st.write(f"- {ds}")

            with col2:
                st.markdown("**Climate Datasets**")
                for ds in datasets.get('climate', []):
                    st.write(f"- {ds}")
    except:
        st.error("Could not fetch datasets")


def show_stats():
    """Display API statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()

            st.subheader("API Usage Statistics")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Queries", stats.get('total_queries', 0))

            with col2:
                st.metric("Avg Response Time", f"{stats.get('avg_response_time', 0):.2f}s")

            # Popular intents chart
            if stats.get('popular_intents'):
                fig = px.bar(
                    x=list(stats['popular_intents'].keys()),
                    y=list(stats['popular_intents'].values()),
                    title="Popular Query Intents"
                )
                st.plotly_chart(fig, use_container_width=True)
    except:
        st.error("Could not fetch statistics")


def show_about():
    """Show about information"""
    st.subheader("About Project Samarth")
    st.markdown("""
    ### Project Overview
    Project Samarth is an intelligent Q&A system designed to help policymakers,
    researchers, and analysts derive insights from India's agricultural and climate data.

    ### Key Features
    - **Multi-source Integration**: Combines data from Ministry of Agriculture and IMD
    - **Natural Language Queries**: Ask questions in plain English
    - **Source Citation**: Every claim is backed by traceable data sources
    - **Cross-domain Analysis**: Correlate agricultural and climate patterns

    ### Technology Stack
    - Python 3.8
    - Streamlit (Frontend)
    - FastAPI (Backend)
    - LangChain & OpenAI (AI/LLM)
    - Pandas & NumPy (Data Processing)

    ### Data Sources
    All data is sourced from [data.gov.in](https://data.gov.in), the official
    open data platform of the Government of India.

    ---
    **Developer:** ramakrishna-18
    **Date:** 2025-10-29
    """)


if __name__ == "__main__":
    main()
```

---

## 🚀 Phase 5: Deployment

### Docker Configuration

```dockerfile
# Dockerfile

FROM python:3.8-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run both API and Streamlit
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0"]
```

### Docker Compose (MongoDB for local dev)

```yaml
# docker-compose.yml

version: "3.8"

services:
  api:
    build: .
    container_name: samarth-api
    ports:
      - "8000:8000"
    environment:
      - HF_API_TOKEN=${HF_API_TOKEN}
      - DATA_GOV_IN_API_KEY=${DATA_GOV_IN_API_KEY}
      - MONGODB_URI=${MONGODB_URI}
      - MONGODB_DB=${MONGODB_DB}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

  streamlit:
    build: .
    container_name: samarth-ui
    ports:
      - "8501:8501"
    depends_on:
      - api
    environment:
      - API_BASE_URL=http://api:8000
    command: streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0

  mongo:
    image: mongo:6
    container_name: samarth-mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### Requirements File

```txt
# requirements.txt

# Web Frameworks
fastapi==0.104.1
uvicorn[standard]==0.24.0
streamlit==1.28.1

# Data Processing
pandas==1.5.3
numpy==1.24.3
openpyxl==3.1.2

# NLP & AI
langchain==0.0.335
openai==1.3.5
spacy==3.5.4
sentence-transformers==2.2.2

# HTTP & Scraping
requests==2.31.0
aiohttp==3.9.0
beautifulsoup4==4.12.2

# Database
sqlalchemy==2.0.23
pymongo==4.9.1
motor==3.6.0

# Visualization
plotly==5.18.0
matplotlib==3.7.3

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
python-multipart==0.0.6

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Environment Configuration

```bash
# .env.example

# API Keys
HF_API_TOKEN=your-huggingface-api-token  # free-tier possible; or leave empty for local models
DATA_GOV_IN_API_KEY=your-data-gov-in-api-key

# Database (MongoDB Atlas M0 or local)
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority
MONGODB_DB=samarth

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Data Paths
RAW_DATA_PATH=data/raw
PROCESSED_DATA_PATH=data/processed
CACHE_PATH=data/cache
```

---

## ⏱️ Timeline & Milestones

### Week 1: Data Discovery & Setup

- **Day 1-2**: Explore data.gov.in, identify datasets
- **Day 3-4**: Build data fetching scripts
- **Day 5-7**: Implement data normalization & storage

### Week 2: Core System Development

- **Day 8-9**: Build query parser & intent classifier
- **Day 10-11**: Implement LLM integration
- **Day 12-14**: Develop data router & API endpoints

### Week 3: UI & Integration

- **Day 15-16**: Build Streamlit interface
- **Day 17-18**: Integrate frontend with backend
- **Day 19-21**: End-to-end testing & refinement

### Week 4: Deployment & Documentation

- **Day 22-23**: Docker configuration & deployment
- **Day 24-25**: Testing sample queries
- **Day 26-27**: Record Loom video & finalize documentation
- **Day 28**: Final submission

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/test_query_processing.py

import pytest
from src.data_processing.query_parser import QueryParser

def test_query_parser_states():
    parser = QueryParser()
    query = "Compare rainfall in Maharashtra and Gujarat"
    parsed = parser.parse(query)

    assert 'Maharashtra' in parsed.entities['states']
    assert 'Gujarat' in parsed.entities['states']
    assert parsed.intent == 'comparison'

def test_query_parser_temporal():
    parser = QueryParser()
    query = "Production trends over last 5 years"
    parsed = parser.parse(query)

    assert parsed.temporal is not None
    assert parsed.temporal['last_n_years'] == 5

def test_intent_classification():
    parser = QueryParser()

    # Comparison
    q1 = parser.parse("Compare A and B")
    assert q1.intent == 'comparison'

    # Trend
    q2 = parser.parse("Show trend over time")
    assert q2.intent == 'trend_analysis'

    # Ranking
    q3 = parser.parse("Top 5 producers")
    assert q3.intent == 'ranking'
```

### Integration Tests

```python
# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query_endpoint():
    response = client.post(
        "/query",
        json={"question": "Average rainfall in Maharashtra"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data

def test_datasets_endpoint():
    response = client.get("/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "agriculture" in data
    assert "climate" in data
```

---

## 📝 Sample Queries

### Query 1: Comparison

```
Question: Compare the average annual rainfall in Maharashtra and Gujarat
for the last 5 years. List the top 3 most produced crops in each state.

Expected Output:
- Average rainfall data for both states (5-year period)
- Top 3 crops with production volumes
- Citations to rainfall and crop production datasets
```

### Query 2: Ranking

```
Question: Identify the district in Punjab with the highest rice production
in 2022 and compare with the lowest producing district in Haryana.

Expected Output:
- Highest producing district in Punjab with production figure
- Lowest producing district in Haryana with production figure
- Citations to district-level crop production data
```

### Query 3: Trend Analysis

```
Question: Analyze the production trend of wheat in northern India over
the last decade and correlate with rainfall patterns.

Expected Output:
- Wheat production trend (10 years)
- Rainfall trend for same period
- Correlation analysis
- Citations to both datasets
```

### Query 4: Policy Support

```
Question: Based on last 10 years data, provide 3 data-backed arguments
to promote drought-resistant crops over water-intensive crops in Maharashtra.

Expected Output:
- Rainfall variability data
- Crop performance under different conditions
- Water usage comparisons
- 3 specific recommendations with data support
- Multiple citations
```

---

## 📚 Additional Resources

### Learning Resources

- [Data.gov.in API Documentation](https://data.gov.in/help/api)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Data Sources

- [Ministry of Agriculture](https://agricoop.nic.in/)
- [India Meteorological Department](https://mausam.imd.gov.in/)
- [AGMARKNET](https://agmarknet.gov.in/)

### Tools

- [Loom for Screen Recording](https://www.loom.com/)
- [Postman for API Testing](https://www.postman.com/)
- [MongoDB Compass (DB GUI)](https://www.mongodb.com/products/compass)
- [DBeaver for Database Management](https://dbeaver.io/) (supports MongoDB too)

---

## 🎬 Video Walkthrough Script (2 minutes)

### Introduction (15 seconds)

"Hi, I'm [Name], and this is Project Samarth - an intelligent Q&A system
that answers complex questions about India's agricultural and climate data
using live data from data.gov.in."

### Dataset Overview (20 seconds)

"I've integrated datasets from the Ministry of Agriculture covering crop
production, yield, and cultivation area, along with IMD climate data
including rainfall and temperature patterns across states and districts."

### System Architecture (25 seconds)

"The system uses a Python 3.8 backend with FastAPI, implementing a query
parser that understands natural language, an LLM-powered answer generator
using LangChain and OpenAI, and a data router that fetches relevant
information from normalized datasets stored in SQLite."

### Demo (45 seconds)

"Let me show you a live demo. [Show Streamlit interface] I'll ask:
'Compare average rainfall in Maharashtra and Gujarat for the last 5 years.'
[Submit query] As you can see, the system parses the query, identifies
the states and time period, fetches rainfall data, and generates an answer
with specific numbers, all while citing the exact data source from data.gov.in."

### Key Features (15 seconds)

"Key features include complete source traceability, handling of inconsistent
data formats, and the ability to correlate cross-domain data for insights
that support policy decisions."

### Closing (10 seconds)

"The entire codebase is containerized with Docker for secure deployment.
Thank you for watching!"

---

## 📋 Checklist Before Submission

- [ ] All datasets identified and documented
- [ ] Data ingestion pipeline working
- [ ] Query parser handles all sample questions
- [ ] LLM integration complete with citation tracking
- [ ] FastAPI backend fully functional
- [ ] Streamlit UI polished and user-friendly
- [ ] Docker configuration tested
- [ ] All sample queries tested and working
- [ ] Code documented with comments
- [ ] README.md complete
- [ ] requirements.txt up to date
- [ ] .env.example provided
- [ ] 2-minute Loom video
