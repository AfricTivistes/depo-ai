from fastapi import FastAPI, HTTPException
from models import AuditResponses
from analyzer import SecurityAuditAnalyzer
from config import settings

app = FastAPI(title="Security Audit API", description="API pour analyser les réponses d'audits de sécurité")

# Initialisation de l'analyseur avec les paramètres de configuration
security_analyzer = SecurityAuditAnalyzer(
    api_key=settings.OPENROUTER_API_KEY,
    model=settings.MODEL,
    api_url=settings.API_URL
)

@app.post("/api/analyze")
async def analyze_audit(responses: AuditResponses):
    """
    Analyse les réponses d'un audit de sécurité.
    
    Args:
        responses: Dictionnaire de questions/réponses
    
    Returns:
        Résultats structurés de l'analyse
    """
    analysis_result = security_analyzer.analyze_responses(responses.responses)
    if analysis_result.get("status") == "error":
        raise HTTPException(status_code=500, detail=analysis_result["error"])
    return analysis_result

@app.get("/api/health")
async def health_check():
    """Vérifie l'état de l'API."""
    return {"status": "ok", "message": "API d'analyse d'audit de sécurité opérationnelle"}