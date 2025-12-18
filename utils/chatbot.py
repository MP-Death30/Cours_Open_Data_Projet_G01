from litellm import completion
import os
import time

class EcoAssistant:
    def __init__(self):
        self.model = "gemini/gemini-2.0-flash-exp"
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.max_retries = 3
        self.retry_delay = 2

    def _call_api_with_retry(self, messages, max_tokens=1000):
        for attempt in range(self.max_retries):
            try:
                response = completion(
                    model=self.model, 
                    messages=messages, 
                    api_key=self.api_key,
                    max_tokens=max_tokens,
                    timeout=30
                )
                return response.choices[0].message.content
            
            except Exception as e:
                error_str = str(e)
                
                if "503" in error_str or "overload" in error_str.lower():
                    if attempt < self.max_retries - 1:
                        print(f"⚠️ API surchargée, nouvelle tentative...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return self._get_fallback_analysis(messages)
                
                elif "401" in error_str or "authentication" in error_str.lower():
                    return self._get_no_api_key_message()
                
                else:
                    return self._get_fallback_analysis(messages)
        
        return self._get_fallback_analysis(messages)

    def _get_no_api_key_message(self):
        return """
### ⚠️ Configuration requise

L'assistant IA nécessite une clé API Gemini.

**Pour configurer :**
1. https://makersuite.google.com/app/apikey
2. Créez `.env` avec : `GEMINI_API_KEY="votre_clé"`
3. Relancez l'application

**Les calculs continuent de fonctionner normalement !**
"""

    def _get_fallback_analysis(self, messages):
        return """
### 🤖 Assistant IA temporairement indisponible

L'API est surchargée. Voici une analyse de base :

#### 🌱 Recommandation Écologique
Le **train** est le plus écologique avec des émissions 10-50x inférieures.

#### 💰 Recommandation Économique
Le **covoiturage** et le **bus** offrent les meilleurs prix.

Consultez l'onglet "Comparateur" pour tous les détails !
"""

    def analyze_trip(self, start, end, df_results):
        if not self.api_key:
            return self._get_no_api_key_message()
        
        data_context = df_results.to_string()
        
        prompt = f"""
Tu es un expert en mobilité écologique. Analyse ce trajet : {start} -> {end}.
Voici les données calculées :
{data_context}

Tes missions :
1. Compare le TRAIN vs VOITURE vs AVION.
2. Donne une équivalence concrète pour le CO2 économisé.
3. Compare aussi les PRIX.
4. Sois encourageant et pédagogique.

Réponds en français, format markdown avec des emojis.
"""
        
        messages = [{"role": "user", "content": prompt}]
        return self._call_api_with_retry(messages)

    def chat(self, user_question, context_str=""):
        if not self.api_key:
            return """
⚠️ **Clé API non configurée**

Pour l'obtenir : https://makersuite.google.com/app/apikey
"""
        
        messages = [
            {"role": "system", "content": f"Tu es EcoBot. Contexte : {context_str}"},
            {"role": "user", "content": user_question}
        ]
        
        return self._call_api_with_retry(messages, max_tokens=500)


def test_api_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return False, "❌ Clé API non configurée"
    
    try:
        response = completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Test"}],
            api_key=api_key,
            max_tokens=10,
            timeout=5
        )
        return True, "✅ API Gemini opérationnelle"
    
    except Exception as e:
        error_str = str(e)
        
        if "503" in error_str or "overload" in error_str.lower():
            return False, "⚠️ API temporairement surchargée"
        elif "401" in error_str:
            return False, "❌ Clé API invalide"
        else:
            return False, f"⚠️ Erreur : {str(e)[:100]}"