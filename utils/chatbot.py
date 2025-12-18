from litellm import completion
import os

class EcoAssistant:
    def __init__(self):
        self.model = "gemini/gemini-2.5-flash-lite"
        self.api_key = os.getenv("GEMINI_API_KEY")

    def analyze_trip(self, start, end, df_results):
        """Analyse le trajet et donne des conseils (Fonctionnalité 1 & 2)."""
        data_context = df_results.to_string()
        
        prompt = f"""
        Tu es un expert en mobilité écologique. Analyse ce trajet : {start} -> {end}.
        Voici les données calculées :
        {data_context}

        Tes missions :
        1. Compare le TRAIN vs VOITURE vs AVION de manière percutante.
        2. Donne une équivalence concrète pour le CO2 économisé par le train (ex: nombre de repas végétariens, jours de chauffage...).
        3. Sois encourageant et pédagogique.
        """
        
        response = completion(model=self.model, messages=[{"role": "user", "content": prompt}], api_key=self.api_key)
        return response.choices[0].message.content

    def chat(self, user_question, context_str=""):
        """Chatbot généraliste sur l'écologie (Fonctionnalité 3)."""
        messages = [
            {"role": "system", "content": f"Tu es EcoBot, un assistant spécialisé dans l'impact carbone des transports. Contexte actuel : {context_str}"},
            {"role": "user", "content": user_question}
        ]
        response = completion(model=self.model, messages=messages, api_key=self.api_key)
        return response.choices[0].message.content