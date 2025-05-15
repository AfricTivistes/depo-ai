import requests
import re

from openai import OpenAI


class SecurityAuditAnalyzer:
    def __init__(self, api_key, model="deepseek/deepseek-chat", api_url="https://openrouter.ai/api/v1"):
        self.client = OpenAI(
            base_url=api_url,
            api_key=api_key
        )
        self.model = model
        self.extra_headers = {
            "HTTP-Referer": "http://localhost:8000",  # À remplacer par votre URL en prod
            "X-Title": "Security Audit API"
        }

    def analyze_responses(self, responses):
        """Analyse les réponses d'un audit en utilisant le client OpenAI"""
        try:
            completion = self.client.chat.completions.create(
                extra_headers=self.extra_headers,
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": self._build_prompt(responses)}
                ],
                temperature=0.5
            )

            analysis = completion.choices[0].message.content
            return self._parse_analysis(analysis)

        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "evaluation": {"score": 0, "level": "Inconnu"},
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "summary": "Erreur lors de la communication avec l'API"
            }

    # Gardez les autres méthodes (_get_system_prompt, _build_prompt, etc.) identiques
    def _get_system_prompt(self):
        return """Vous êtes un expert en cybersécurité spécialisé dans l'analyse des audits de sécurité.
Votre tâche est d'analyser les réponses fournies à un audit de sécurité et de produire une évaluation détaillée.

Adaptez votre analyse au type d'audit fourni (audit complet ou audit spécifique à un domaine).
Identifiez automatiquement le domaine spécifique de l'audit si les questions sont concentrées sur un sujet particulier 
(ex: sécurité des réseaux, politique de mots de passe, gestion des données, etc.).

Structurez toujours votre réponse avec les balises suivantes:
<AUDIT_TYPE>Type de l'audit identifié</AUDIT_TYPE>
<EVALUATION>Score sur 10 et niveau (Critique, Faible, Moyen, Bon, Excellent)</EVALUATION>
<POINTS_FORTS>Liste des points forts avec leur niveau d'importance (Fort, Moyen, Faible)</POINTS_FORTS>
<FAILLES>Liste des vulnérabilités identifiées avec leur niveau de risque (Critique, Élevé, Moyen, Faible)</FAILLES>
<RECOMMANDATIONS>Liste des recommandations détaillées pour chaque faille identifiée</RECOMMANDATIONS>
<RESUME>Résumé concis de la situation générale de sécurité et prochaines étapes prioritaires</RESUME>
"""

    def _build_prompt(self, responses):
        audit_type = self._detect_audit_type(responses)
        prompt = f"Type d'audit détecté: {audit_type}\n\n"
        prompt += "Voici les réponses à un audit de sécurité numérique:\n\n"
        for question, answer in responses.items():
            prompt += f"Question: {question}\nRéponse: {answer}\n\n"
        prompt += """
Analysez ces réponses et fournissez:
1. Le type d'audit que vous avez identifié
2. Une évaluation globale du niveau de sécurité (score sur 10 et niveau: Critique, Faible, Moyen, Bon, Excellent)
3. Les points forts de la sécurité actuelle (listez-les avec leur importance: Fort, Moyen, Faible)
4. Les vulnérabilités identifiées (listez-les avec leur niveau de risque: Critique, Élevé, Moyen, Faible)
5. Des recommandations détaillées pour résoudre chaque vulnérabilité
6. Un résumé général de la situation actuelle et prochaines étapes prioritaires

Formatez votre réponse avec les sections clairement délimitées par les balises spécifiées.
"""
        return prompt

    def _detect_audit_type(self, responses):
        domains = {
            "Politique de mots de passe": ["mot de passe", "password", "authentification", "connexion"],
            "Sécurité des réseaux": ["réseau", "network", "firewall", "pare-feu", "vpn", "wifi", "routeur"],
            "Gestion des accès": ["accès", "access", "droits", "permission", "privilege", "utilisateur", "user"],
            "Protection des données": ["donnée", "data", "chiffrement", "encryption", "backup", "sauvegarde"],
            "Sécurité physique": ["physique", "physical", "bâtiment", "building", "local", "vol", "theft"],
            "Formation et sensibilisation": ["formation", "training", "sensibilisation", "awareness", "employé"],
            "Gestion des incidents": ["incident", "crise", "réponse", "response", "attaque", "breach"],
            "Conformité réglementaire": ["rgpd", "gdpr", "conformité", "compliance", "régulation", "legal"]
        }
        domain_counts = {domain: 0 for domain in domains}
        for question in responses.keys():
            question_lower = question.lower()
            for domain, keywords in domains.items():
                for keyword in keywords:
                    if keyword.lower() in question_lower:
                        domain_counts[domain] += 1
        main_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        if len(main_domains) > 3 and main_domains[0][1] > 0 and main_domains[1][1] > 0 and main_domains[2][1] > 0:
            return "Audit de sécurité complet"
        elif main_domains[0][1] > 0:
            return f"Audit spécifique: {main_domains[0][0]}"
        else:
            return "Audit de sécurité général"

    def _parse_analysis(self, analysis):
        result = {
            "status": "success",
            "audit_type": self._extract_between(analysis, "<AUDIT_TYPE>", "</AUDIT_TYPE>"),
            "evaluation": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "summary": self._extract_between(analysis, "<RESUME>", "</RESUME>").strip()
        }
        eval_text = self._extract_between(analysis, "<EVALUATION>", "</EVALUATION>")
        score_match = re.search(r'(\d+)[\/\s]*10', eval_text)
        result["evaluation"]["score"] = int(score_match.group(1)) if score_match else 0

        level_keywords = ["Critique", "Faible", "Moyen", "Bon", "Excellent"]
        for keyword in level_keywords:
            if keyword.lower() in eval_text.lower():
                result["evaluation"]["level"] = keyword
                break
        else:
            result["evaluation"]["level"] = "Non spécifié"

        strengths_text = self._extract_between(analysis, "<POINTS_FORTS>", "</POINTS_FORTS>")
        result["strengths"] = self._extract_rated_items(strengths_text, ["Fort", "Moyen", "Faible"])

        weaknesses_text = self._extract_between(analysis, "<FAILLES>", "</FAILLES>")
        result["weaknesses"] = self._extract_rated_items(weaknesses_text, ["Critique", "Élevé", "Moyen", "Faible"])

        recommendations_text = self._extract_between(analysis, "<RECOMMANDATIONS>", "</RECOMMANDATIONS>")
        result["recommendations"] = self._extract_list_items(recommendations_text)

        if not result["audit_type"]:
            if "audit complet" in analysis.lower():
                result["audit_type"] = "Audit de sécurité complet"
            elif "audit spécifique" in analysis.lower():
                specific_match = re.search(r'audit spécifique[:\s]*([\w\s]+)', analysis.lower())
                if specific_match:
                    result["audit_type"] = f"Audit spécifique: {specific_match.group(1).strip().capitalize()}"
                else:
                    result["audit_type"] = "Audit spécifique"
            else:
                result["audit_type"] = "Audit de sécurité général"

        return result

    def _extract_between(self, text, start_marker, end_marker):
        try:
            start = text.index(start_marker) + len(start_marker)
            end = text.index(end_marker, start)
            return text[start:end].strip()
        except ValueError:
            return ""

    def _extract_list_items(self, text):
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith(('- ', '• ', '* ', '1. ', '2. ')) and len(line) > 2:
                items.append(line[2:].strip())
            elif line and not any(header in line.lower() for header in ["points", "failles", "recommandations"]):
                items.append(line)
        return [item for item in items if item]

    def _extract_rated_items(self, text, ratings):
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            item = {"text": line, "rating": None}
            for rating in ratings:
                if f"{rating}:" in line.lower() or f"{rating} :" in line.lower():
                    parts = re.split(f"{rating}:", line, 1, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        item["text"] = parts[1].strip()
                        item["rating"] = rating
                        break
                if f"({rating})" in line.lower() or f"[{rating}]" in line.lower():
                    item["text"] = re.sub(rf"[\(\[]?{rating}[\)\]]?", "", line, flags=re.IGNORECASE).strip()
                    item["rating"] = rating
                    break
            if item["rating"] is None and line.startswith(('- ', '• ', '* ')) and len(line) > 2:
                item["text"] = line[2:].strip()
            if item["text"] and not any(header in item["text"].lower() for header in ["points forts", "failles"]):
                items.append(item)
        return items