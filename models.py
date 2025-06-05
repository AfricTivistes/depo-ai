from pydantic import BaseModel, field_validator
from typing import Union, Dict, Any


class AuditResponses(BaseModel):
    responses: Dict[str, Union[str, list]]

    @field_validator('responses')
    @classmethod
    def normalize_responses(cls, v: Dict[str, Any]) -> Dict[str, str]:
        """
        Normalise les réponses en convertissant les listes en chaînes de caractères.
        Les valeurs string restent inchangées, les listes sont jointes avec des virgules.
        """
        normalized = {}
        for question, answer in v.items():
            if isinstance(answer, list):
                # Convertit la liste en chaîne séparée par des virgules
                normalized[question] = ", ".join(str(item) for item in answer)
            else:
                # Garde la valeur string telle quelle
                normalized[question] = str(answer)
        return normalized