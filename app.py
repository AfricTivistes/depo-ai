from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from models import AuditResponses
from analyzer import SecurityAuditAnalyzer
from config import settings

app = FastAPI(
    title="Security Audit API",
    description="API pour analyser les réponses d'audits de sécurité",
    version="1.0.0"
)

# Initialisation de l'analyseur avec les paramètres de configuration
security_analyzer = SecurityAuditAnalyzer(
    api_key=settings.OPENROUTER_API_KEY,
    model=settings.MODEL,
    api_url=settings.API_URL
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """
    Gestionnaire d'erreur personnalisé pour les erreurs de validation Pydantic
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "Erreur de validation des données",
            "details": [
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "value": error.get("input")
                }
                for error in exc.errors()
            ],
            "help": "L'API accepte maintenant les valeurs string et array. Les arrays sont automatiquement convertis en texte."
        }
    )


@app.post("/api/analyze")
async def analyze_audit(responses: AuditResponses):
    """
    Analyse les réponses d'un audit de sécurité.

    Args:
        responses: Dictionnaire de questions/réponses
                  Les valeurs peuvent être des strings ou des listes
                  Les listes sont automatiquement converties en texte séparé par des virgules

    Returns:
        Résultats structurés de l'analyse
    """
    try:
        # Les réponses sont déjà normalisées par le validator Pydantic
        analysis_result = security_analyzer.analyze_responses(responses.responses)

        if analysis_result.get("status") == "error":
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Erreur lors de l'analyse",
                    "message": analysis_result.get("error", "Erreur inconnue")
                }
            )

        return analysis_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erreur interne du serveur",
                "message": str(e)
            }
        )


@app.get("/api/health")
async def health_check():
    """Vérifie l'état de l'API."""
    return {
        "status": "ok",
        "message": "API d'analyse d'audit de sécurité opérationnelle",
        "version": "1.0.0",
        "features": [
            "Support des réponses string et array",
            "Conversion automatique des listes en texte"
        ]
    }


@app.get("/api/info")
async def api_info():
    """
    Informations sur l'utilisation de l'API
    """
    return {
        "title": "Security Audit API",
        "description": "Cette API analyse les réponses d'audits de sécurité",
        "endpoints": {
            "/api/analyze": {
                "method": "POST",
                "description": "Analyse les réponses d'audit",
                "body_format": {
                    "responses": {
                        "question1": "réponse texte",
                        "question2": ["réponse1", "réponse2"],
                        "question3": "autre réponse"
                    }
                },
                "note": "Les listes sont automatiquement converties en texte séparé par des virgules"
            },
            "/api/health": {
                "method": "GET",
                "description": "Vérifie l'état de l'API"
            }
        }
    }