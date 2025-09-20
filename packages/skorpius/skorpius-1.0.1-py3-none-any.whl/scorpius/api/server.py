#!/usr/bin/env python3
"""
Scorpius API Server
REST API for the world's strongest smart contract scanner
"""

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import List, Dict, Any, Optional
    import uvicorn
    
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ..core.scanner import ScorpiusScanner

# API Models
if FASTAPI_AVAILABLE:
    class ScanRequest(BaseModel):
        contract_code: str
        contract_path: Optional[str] = None
        confidence_threshold: Optional[float] = 0.5
        severity_filter: Optional[str] = None

    class ScanResponse(BaseModel):
        contract_hash: str
        scan_time: float
        vulnerabilities: List[Dict[str, Any]]
        total_found: int
        summary: Dict[str, Any]

    class PredictionRequest(BaseModel):
        code_snippet: str

    class PredictionResponse(BaseModel):
        predicted_type: str
        predicted_severity: str
        confidence: float
        recommendation: str

# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Scorpius Scanner API",
        description="World's Strongest Smart Contract Security Scanner API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global scanner instance
    scanner = None

    @app.on_event("startup")
    async def startup_event():
        """Initialize scanner on startup"""
        global scanner
        scanner = ScorpiusScanner()
        await scanner.initialize()

    @app.get("/")
    async def root():
        """Root endpoint with scanner information"""
        return {
            "name": "Scorpius Scanner API",
            "version": "1.0.0",
            "description": "World's Strongest Smart Contract Security Scanner",
            "status": "ready",
            "docs": "/docs"
        }

    @app.post("/scan", response_model=ScanResponse)
    async def scan_contract(request: ScanRequest):
        """Scan a smart contract for vulnerabilities"""
        try:
            # Configure scanner
            scanner.config.update({
                'confidence_threshold': request.confidence_threshold,
                'severity_filter': request.severity_filter
            })
            
            # Scan contract
            result = await scanner.scan_contract(
                request.contract_code, 
                request.contract_path
            )
            
            return ScanResponse(**result)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/predict", response_model=PredictionResponse)
    async def predict_vulnerability(request: PredictionRequest):
        """Predict vulnerability type for code snippet"""
        try:
            prediction = await scanner.predict_vulnerability(request.code_snippet)
            
            return PredictionResponse(
                predicted_type=prediction['predicted_type'],
                predicted_severity=prediction['predicted_severity'],
                confidence=prediction['confidence'],
                recommendation=prediction['recommendation']
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/stats")
    async def get_statistics():
        """Get scanner statistics"""
        try:
            stats = await scanner.learning_system.get_statistics()
            return stats
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z",
            "version": "1.0.0"
        }

else:
    # Fallback when FastAPI is not available
    app = None

def start_server():
    """Start the API server"""
    if not FASTAPI_AVAILABLE:
        print("❌ API server requires FastAPI. Install with: pip install scorpius-scanner[api]")
        return
    
    print("🌐 Starting Scorpius API server...")
    uvicorn.run(
        "scorpius.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )