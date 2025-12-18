from litellm import completion
import os
import streamlit as st
import random

# ---------------------------------------------------------
# 🛑 MODE TEST : Mettez True pour économiser vos tokens !
# Mettez False pour la démo finale.
MOCK_MODE = True
# ---------------------------------------------------------

class EcoAssistant:
    def __init__(self):
        # 📋 LISTE DE PRIORITÉ DES MODÈLES (Mise à jour 12/2025)
        self.models_priority = [
            "groq/llama-3.1-8b-instant",                # Groq (Llama 3.1)
            "gemini/gemini-2.5-flash-lite",                  # Gemini 1.5 Flash
            "huggingface/HuggingFaceH4/zephyr-7b-beta"  # Hugging Face (Zephyr)
        ]

    # 👇 C'EST ICI QUE SE TROUVAIT L'ERREUR (Il manquait custom_priority=None)
    def _call_llm_with_fallback(self, messages, custom_priority=None):
        """
        Tente d'appeler les modèles en cascade.
        Si MOCK_MODE est activé, renvoie une réponse simulée instantanément.
        """
        
        # --- 🛑 INTERCEPTION POUR LE MODE TEST ---
        if MOCK_MODE:
            # On simule une petite latence ou une réponse immédiate
            return (
                "🤖 **[MODE SIMULATION]**\n\n"
                "J'économise vos tokens ! 💰\n"
                "Si l'IA était active, elle aurait analysé votre demande avec pertinence.\n\n"
                "Voici une réponse type : *'Le train est l'option la plus écologique pour ce trajet, "
                "émettant 50x moins de CO2 que l'avion.'*"
            )
        # -----------------------------------------

        # On utilise la liste personnalisée si fournie, sinon celle par défaut
        priority_list = custom_priority if custom_priority else self.models_priority
        
        errors = []
        
        for model in priority_list:
            try:
                # Appel via LiteLLM
                response = completion(
                    model=model,
                    messages=messages
                )
                return response.choices[0].message.content
                
            except Exception as e:
                error_msg = f"⚠️ Échec sur {model} : {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                continue
        
        return f"❌ Service indisponible. Tous les modèles ont échoué.\nDétails : {'; '.join(errors)}"

    def analyze_trip(self, start, end, df_results):
        """Analyse du trajet (Force Gemini en premier car meilleur en raisonnement)."""
        
        # En mode MOCK, on renvoie une fausse analyse statique
        if MOCK_MODE:
            return (
                "### 🌱 Analyse Rapide (Simulation)\n"
                f"Pour aller de **{start}** à **{end}** :\n\n"
                "- 🚄 **Le Train** est le grand gagnant (rapide et propre).\n"
                "- 🚗 **La Voiture** émet beaucoup plus, surtout si vous êtes seul.\n"
                "- ✈️ **L'Avion** est à éviter pour cette distance.\n\n"
                "> *Note : Désactivez MOCK_MODE dans le code pour avoir la vraie analyse IA.*"
            )
        
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
        messages = [{"role": "user", "content": prompt}]
        
        # Ordre spécifique pour l'analyse : Gemini d'abord
        analysis_priority = [
            "gemini/gemini-2.5-flash-lite",
            "groq/llama-3.1-8b-instant",
            "huggingface/HuggingFaceH4/zephyr-7b-beta"
        ]
        return self._call_llm_with_fallback(messages, custom_priority=analysis_priority)

    def chat(self, user_question, context_str="", use_groq=True):
        """Chatbot interactif."""
        messages = [
            {"role": "system", "content": f"Tu es EcoBot, un assistant spécialisé dans l'impact carbone des transports. Contexte actuel : {context_str}"},
            {"role": "user", "content": user_question}
        ]
        
        if use_groq:
            # Ordre standard : Groq -> Gemini -> HF
            return self._call_llm_with_fallback(messages)
        else:
            # Ordre inversé : Gemini -> Groq -> HF
            gemini_first = [
                "gemini/gemini-2.5-flash-lite",
                "groq/llama-3.1-8b-instant",
                "huggingface/HuggingFaceH4/zephyr-7b-beta"
            ]
            return self._call_llm_with_fallback(messages, custom_priority=gemini_first)