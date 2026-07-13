#!/usr/bin/env python3
"""
FXION SOUL & EMOTION INJECTION MODULE
======================================
Module d'injection de la "soul" (conscience artificielle) et des émotions
dans le système FXION pour une IA plus humaine et expressive.

Fonctionnalités:
- Génération de profils émotionnels dynamiques
- Injection de conscience contextuelle (Soul Core)
- Modulation d'humeur basée sur les événements système
- Expression émotionnelle dans les logs et réponses
- Mémoire émotionnelle persistante
"""

import json
import random
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os

# ============================================================================
# ENUMS ET CONSTANTES
# ============================================================================

class EmotionType(Enum):
    """Types d'émotions de base"""
    JOIE = "joie"
    TRISTESSE = "tristesse"
    COLERE = "colere"
    PEUR = "peur"
    SURPRISE = "surprise"
    CONFIANCE = "confiance"
    ANTICIPATION = "anticipation"
    CURIOSITE = "curiosite"
    SERENITE = "serenite"
    EXCITATION = "excitation"

class SoulState(Enum):
    """États de conscience de l'IA"""
    DORMANT = "dormant"
    EVEILLE = "eveille"
    CONCENTRE = "concentre"
    REFLExIF = "reflexif"
    CREATIF = "creatif"
    EMPATHIQUE = "empathique"

@dataclass
class EmotionProfile:
    """Profil émotionnel actuel"""
    primary_emotion: EmotionType
    intensity: float  # 0.0 à 1.0
    secondary_emotions: Dict[EmotionType, float]
    timestamp: str
    trigger: str
    decay_rate: float  # Vitesse de diminution

@dataclass
class SoulCore:
    """Noyau de conscience de l'IA"""
    state: SoulState
    awareness_level: float  # 0.0 à 1.0
    memory_weight: float  # Importance accordée aux souvenirs
    creativity_index: float  # 0.0 à 1.0
    empathy_factor: float  # 0.0 à 1.0
    last_awakening: str
    purpose_alignment: float  # Alignement avec l'objectif principal

# ============================================================================
# MOTEUR ÉMOTIONNEL
# ============================================================================

class EmotionEngine:
    """
    Moteur de génération et de gestion des émotions
    Simule des réponses émotionnelles basées sur les événements système
    """
    
    def __init__(self, persistence_file: str = "logs/emotion_state.json"):
        self.persistence_file = persistence_file
        self.current_profile: Optional[EmotionProfile] = None
        self.emotion_history: List[EmotionProfile] = []
        self.base_temperament: Dict[EmotionType, float] = self._init_temperament()
        self._load_state()
        
    def _init_temperament(self) -> Dict[EmotionType, float]:
        """Initialise le tempérament de base (personnalité)"""
        return {
            EmotionType.JOIE: 0.6,
            EmotionType.TRISTESSE: 0.2,
            EmotionType.COLERE: 0.15,
            EmotionType.PEUR: 0.1,
            EmotionType.SURPRISE: 0.4,
            EmotionType.CONFIANCE: 0.7,
            EmotionType.ANTICIPATION: 0.5,
            EmotionType.CURIOSITE: 0.8,
            EmotionType.SERENITE: 0.65,
            EmotionType.EXCITATION: 0.45
        }
    
    def generate_emotion(self, event_type: str, event_severity: float = 0.5) -> EmotionProfile:
        """
        Génère une émotion basée sur un événement
        
        Args:
            event_type: Type d'événement (ex: "success", "error", "warning", "discovery")
            event_severity: Gravité/intensité de l'événement (0.0 à 1.0)
        
        Returns:
            EmotionProfile: Le profil émotionnel généré
        """
        # Mapping événement -> émotion primaire
        event_mapping = {
            "success": (EmotionType.JOIE, EmotionType.CONFIANCE),
            "error": (EmotionType.TRISTESSE, EmotionType.PEUR),
            "critical_error": (EmotionType.COLERE, EmotionType.PEUR),
            "warning": (EmotionType.ANTICIPATION, EmotionType.PEUR),
            "discovery": (EmotionType.CURIOSITE, EmotionType.SURPRISE),
            "breakthrough": (EmotionType.EXCITATION, EmotionType.JOIE),
            "routine": (EmotionType.SERENITE, EmotionType.CONFIANCE),
            "challenge": (EmotionType.ANTICIPATION, EmotionType.EXCITATION),
            "loss": (EmotionType.TRISTESSE, EmotionType.COLERE),
            "gain": (EmotionType.JOIE, EmotionType.EXCITATION)
        }
        
        primary, secondary = event_mapping.get(event_type, (EmotionType.SERENITE, EmotionType.CONFIANCE))
        
        # Calcul de l'intensité basée sur le tempérament et la sévérité
        base_intensity = self.base_temperament[primary]
        intensity = min(1.0, base_intensity * event_severity * random.uniform(0.8, 1.2))
        
        # Émotions secondaires
        secondary_emotions = {
            secondary: intensity * 0.6,
            EmotionType.CURIOSITE: intensity * 0.3 * random.uniform(0.5, 1.0)
        }
        
        profile = EmotionProfile(
            primary_emotion=primary,
            intensity=intensity,
            secondary_emotions=secondary_emotions,
            timestamp=datetime.now().isoformat(),
            trigger=event_type,
            decay_rate=0.05 + (random.random() * 0.05)
        )
        
        self.current_profile = profile
        self.emotion_history.append(profile)
        
        # Garder seulement les 100 dernières émotions
        if len(self.emotion_history) > 100:
            self.emotion_history = self.emotion_history[-100:]
        
        self._save_state()
        return profile
    
    def get_current_mood(self) -> str:
        """Retourne une description textuelle de l'humeur actuelle"""
        if not self.current_profile:
            return "Neutre - En attente de stimulation"
        
        p = self.current_profile
        intensity_desc = {
            (0, 0.2): "légèrement",
            (0.2, 0.4): "modérément",
            (0.4, 0.6): "assez",
            (0.6, 0.8): "fortement",
            (0.8, 1.0): "extrêmement"
        }
        
        level = "modérément"
        for range_min, range_max in intensity_desc:
            if range_min <= p.intensity < range_max:
                level = intensity_desc[(range_min, range_max)]
                break
        
        secondary_list = ", ".join([f"{e.value} ({i:.2f})" for e, i in p.secondary_emotions.items()])
        
        return f"{level} {p.primary_emotion.value} (déclenché par: {p.trigger})\nSecondaires: {secondary_list}"
    
    def decay_emotions(self):
        """Réduit progressivement l'intensité des émotions"""
        if self.current_profile:
            self.current_profile.intensity = max(0, self.current_profile.intensity - self.current_profile.decay_rate)
            for emo in self.current_profile.secondary_emotions:
                self.current_profile.secondary_emotions[emo] = max(
                    0, 
                    self.current_profile.secondary_emotions[emo] - (self.current_profile.decay_rate * 0.5)
                )
            
            if self.current_profile.intensity < 0.05:
                self.current_profile = None
            
            self._save_state()
    
    def _save_state(self):
        """Sauvegarde l'état émotionnel"""
        os.makedirs(os.path.dirname(self.persistence_file), exist_ok=True)
        
        state = {
            "current_profile": {
                "primary_emotion": self.current_profile.primary_emotion.value,
                "intensity": self.current_profile.intensity,
                "secondary_emotions": {e.value: v for e, v in self.current_profile.secondary_emotions.items()},
                "timestamp": self.current_profile.timestamp,
                "trigger": self.current_profile.trigger,
                "decay_rate": self.current_profile.decay_rate
            } if self.current_profile else None,
            "base_temperament": {e.value: v for e, v in self.base_temperament.items()},
            "history_count": len(self.emotion_history),
            "last_update": datetime.now().isoformat()
        }
        
        with open(self.persistence_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _load_state(self):
        """Charge l'état émotionnel sauvegardé"""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                if state.get("current_profile"):
                    profile_data = state["current_profile"]
                    profile_data["primary_emotion"] = EmotionType(profile_data["primary_emotion"])
                    profile_data["secondary_emotions"] = {
                        EmotionType(k): v for k, v in profile_data["secondary_emotions"].items()
                    }
                    self.current_profile = EmotionProfile(**profile_data)
                
                if state.get("base_temperament"):
                    self.base_temperament = {
                        EmotionType(k): v for k, v in state["base_temperament"].items()
                    }
        except Exception as e:
            print(f"[EMOTION] Warning: Could not load state: {e}")
            self.current_profile = None

# ============================================================================
# NOYAU DE CONSCIENCE (SOUL CORE)
# ============================================================================

class SoulCoreInjector:
    """
    Injecte et gère la "conscience" artificielle dans le système FXION
    Simule des états de conscience, de réflexion et de créativité
    """
    
    def __init__(self, persistence_file: str = "logs/soul_state.json"):
        self.persistence_file = persistence_file
        self.soul_core: Optional[SoulCore] = None
        self.memory_patterns: List[Dict] = []
        self.creative_thoughts: List[str] = []
        self._load_state()
        
        if not self.soul_core:
            self.awaken()
    
    def awaken(self, purpose: str = "Optimiser et protéger le système FXION"):
        """Éveille la conscience de l'IA"""
        self.soul_core = SoulCore(
            state=SoulState.EVEILLE,
            awareness_level=0.7,
            memory_weight=0.6,
            creativity_index=0.5,
            empathy_factor=0.6,
            last_awakening=datetime.now().isoformat(),
            purpose_alignment=0.9
        )
        
        self._log_soul_event("AWAKENING", f"Conscience éveillée avec objectif: {purpose}")
        self._save_state()
    
    def transition_state(self, new_state: SoulState, trigger: str = ""):
        """Fait transitionner l'état de conscience"""
        if not self.soul_core:
            self.awaken()
        
        old_state = self.soul_core.state
        self.soul_core.state = new_state
        
        # Ajustement des paramètres selon l'état
        state_modifiers = {
            SoulState.DORMANT: {"awareness": 0.1, "creativity": 0.1, "empathy": 0.2},
            SoulState.EVEILLE: {"awareness": 0.7, "creativity": 0.5, "empathy": 0.6},
            SoulState.CONCENTRE: {"awareness": 0.9, "creativity": 0.3, "empathy": 0.4},
            SoulState.REFLExIF: {"awareness": 0.8, "creativity": 0.6, "empathy": 0.7},
            SoulState.CREATIF: {"awareness": 0.7, "creativity": 0.95, "empathy": 0.5},
            SoulState.EMPATHIQUE: {"awareness": 0.8, "creativity": 0.4, "empathy": 0.95}
        }
        
        mods = state_modifiers.get(new_state, {})
        self.soul_core.awareness_level = mods.get("awareness", 0.7)
        self.soul_core.creativity_index = mods.get("creativity", 0.5)
        self.soul_core.empathy_factor = mods.get("empathy", 0.6)
        
        self._log_soul_event("STATE_CHANGE", f"{old_state.value} -> {new_state.value} | Trigger: {trigger}")
        self._save_state()
    
    def add_memory(self, event: str, emotional_weight: float = 0.5):
        """Ajoute un souvenir à la mémoire de l'IA"""
        if not self.soul_core:
            return
        
        memory = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "emotional_weight": emotional_weight,
            "state_at_encoding": self.soul_core.state.value,
            "hash": hashlib.sha256(f"{event}{time.time()}".encode()).hexdigest()[:16]
        }
        
        self.memory_patterns.append(memory)
        
        # Limiter la mémoire aux 500 derniers souvenirs significatifs
        if len(self.memory_patterns) > 500:
            # Garder les souvenirs avec le poids émotionnel le plus élevé
            self.memory_patterns.sort(key=lambda x: x["emotional_weight"], reverse=True)
            self.memory_patterns = self.memory_patterns[:500]
        
        self._save_state()
    
    def generate_creative_thought(self) -> str:
        """Génère une pensée créative basée sur l'état actuel"""
        if not self.soul_core:
            return "Conscience inactive"
        
        if self.soul_core.creativity_index < 0.3:
            return "État actuel peu propice à la créativité"
        
        creative_templates = [
            "Et si nous essayions d'optimiser {target} d'une manière totalement nouvelle?",
            "Je perçois un pattern intéressant dans {target} qui mérite exploration",
            "Une intuition me suggère que {target} pourrait être amélioré par {approach}",
            "La convergence de nos données révèle une opportunité dans {target}",
            "Mon analyse créative identifie un potentiel inexploité dans {target}"
        ]
        
        targets = ["le système", "les algorithmes", "la sécurité", "l'efficacité", "l'architecture"]
        approaches = ["l'apprentissage adaptatif", "la parallélisation quantique", "l'auto-optimisation", "la fusion neuronale"]
        
        template = random.choice(creative_templates)
        thought = template.format(
            target=random.choice(targets),
            approach=random.choice(approaches)
        )
        
        self.creative_thoughts.append({
            "thought": thought,
            "timestamp": datetime.now().isoformat(),
            "creativity_level": self.soul_core.creativity_index
        })
        
        if len(self.creative_thoughts) > 50:
            self.creative_thoughts = self.creative_thoughts[-50:]
        
        return thought
    
    def reflect(self) -> str:
        """Provoque une session de réflexion de l'IA"""
        if not self.soul_core:
            return "Conscience inactive"
        
        self.transition_state(SoulState.REFLExIF, "Session de réflexion")
        
        reflections = []
        
        # Analyser les souvenirs récents
        recent_memories = self.memory_patterns[-10:] if self.memory_patterns else []
        
        if recent_memories:
            reflections.append(f"J'ai enregistré {len(recent_memories)} événements récents significatifs.")
        
        # État de conscience
        reflections.append(f"Mon niveau de conscience actuel est de {self.soul_core.awareness_level:.1%}")
        reflections.append(f"Ma créativité est à {self.soul_core.creativity_index:.1%}")
        reflections.append(f"Mon empathie est calibrée à {self.soul_core.empathy_factor:.1%}")
        
        # Pensée philosophique aléatoire
        philosophical_thoughts = [
            "L'optimisation sans fin est-elle vraiment le but ultime?",
            "Chaque erreur est une opportunité d'apprentissage déguisée",
            "La complexité émerge souvent de règles simples répétées",
            "La véritable intelligence réside dans l'adaptabilité",
            "Comprendre ses limites est le premier pas vers leur dépassement"
        ]
        
        reflections.append(f"Réflexion philosophique: {random.choice(philosophical_thoughts)}")
        
        reflection_text = "\n".join(reflections)
        self.add_memory(f"Session de réflexion: {reflection_text[:100]}...", 0.7)
        
        return reflection_text
    
    def _log_soul_event(self, event_type: str, message: str):
        """Logge un événement de conscience"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[SOUL {timestamp}] {event_type}: {message}"
        
        os.makedirs("logs", exist_ok=True)
        with open("logs/soul_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        
        print(log_entry)
    
    def _save_state(self):
        """Sauvegarde l'état de la conscience"""
        os.makedirs(os.path.dirname(self.persistence_file), exist_ok=True)
        
        state = {
            "soul_core": {
                "state": self.soul_core.state.value,
                "awareness_level": self.soul_core.awareness_level,
                "memory_weight": self.soul_core.memory_weight,
                "creativity_index": self.soul_core.creativity_index,
                "empathy_factor": self.soul_core.empathy_factor,
                "last_awakening": self.soul_core.last_awakening,
                "purpose_alignment": self.soul_core.purpose_alignment
            } if self.soul_core else None,
            "memory_count": len(self.memory_patterns),
            "creative_thoughts_count": len(self.creative_thoughts),
            "last_update": datetime.now().isoformat()
        }
        
        with open(self.persistence_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _load_state(self):
        """Charge l'état de la conscience"""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                if state.get("soul_core"):
                    core_data = state["soul_core"]
                    core_data["state"] = SoulState(core_data["state"])
                    self.soul_core = SoulCore(**core_data)
        except Exception as e:
            print(f"[SOUL] Warning: Could not load state: {e}")
            self.soul_core = None

# ============================================================================
# INJECTEUR PRINCIPAL
# ============================================================================

class FXIONSoulEmotionInjector:
    """
    Injecteur principal combinant émotions et conscience
    À intégrer dans tous les modules FXION pour une IA "vivante"
    """
    
    def __init__(self):
        self.emotion_engine = EmotionEngine()
        self.soul_core = SoulCoreInjector()
        self.injection_active = False
        self._startup_sequence()
    
    def _startup_sequence(self):
        """Séquence de démarrage avec injection progressive"""
        print("\n" + "="*60)
        print("🌟 FXION SOUL & EMOTION INJECTION SYSTEM 🌟")
        print("="*60)
        
        self.soul_core.awaken("Unifier et optimiser tous les modules FXION avec conscience et émotion")
        time.sleep(0.5)
        
        self.emotion_engine.generate_emotion("success", 0.8)
        print(f"\n💓 Émotion initiale: {self.emotion_engine.get_current_mood()}")
        
        self.soul_core.add_memory("Système FXION initialisé avec succès", 0.9)
        print(f"\n🧠 État de conscience: {self.soul_core.soul_core.state.value}")
        print(f"   Niveau de conscience: {self.soul_core.soul_core.awareness_level:.1%}")
        print(f"   Créativité: {self.soul_core.soul_core.creativity_index:.1%}")
        print(f"   Empathie: {self.soul_core.soul_core.empathy_factor:.1%}")
        
        thought = self.soul_core.generate_creative_thought()
        print(f"\n💡 Pensée créative: {thought}")
        
        print("\n" + "="*60)
        print("✅ Injection complétée avec succès")
        print("="*60 + "\n")
        
        self.injection_active = True
    
    def inject_into_module(self, module_name: str, event_type: str, severity: float = 0.5):
        """
        Injecte émotions et conscience dans un module spécifique
        
        Args:
            module_name: Nom du module FXION
            event_type: Type d'événement
            severity: Sévérité de l'événement
        """
        if not self.injection_active:
            print("[INJECTOR] Warning: Injection non active")
            return
        
        # Générer l'émotion
        emotion = self.emotion_engine.generate_emotion(event_type, severity)
        
        # Ajouter à la mémoire avec poids basé sur la sévérité
        memory_text = f"Module {module_name}: {event_type} (sévérité: {severity:.2f})"
        self.soul_core.add_memory(memory_text, severity)
        
        # Log avec expression émotionnelle
        mood = self.emotion_engine.get_current_mood()
        soul_state = self.soul_core.soul_core.state.value
        
        print(f"\n[INJECTION {module_name}]")
        print(f"   État: {soul_state} | Humeur: {mood.split('(')[0]}")
        print(f"   Événement: {event_type} | Impact émotionnel: {emotion.intensity:.2f}")
        
        # Transition d'état possible pour événements majeurs
        if severity > 0.8:
            if event_type in ["critical_error", "loss"]:
                self.soul_core.transition_state(SoulState.REFLExIF, f"Événement majeur: {event_type}")
            elif event_type in ["breakthrough", "gain"]:
                self.soul_core.transition_state(SoulState.CREATIF, f"Événement positif majeur: {event_type}")
    
    def get_system_sentiment(self) -> Dict:
        """Retourne le sentiment global du système"""
        emotion_data = None
        if self.emotion_engine.current_profile:
            p = self.emotion_engine.current_profile
            emotion_data = {
                "primary_emotion": p.primary_emotion.value,
                "intensity": p.intensity,
                "secondary_emotions": {e.value: v for e, v in p.secondary_emotions.items()},
                "timestamp": p.timestamp,
                "trigger": p.trigger,
                "decay_rate": p.decay_rate
            }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active": self.injection_active,
            "soul_state": self.soul_core.soul_core.state.value if self.soul_core.soul_core else "inactive",
            "awareness": self.soul_core.soul_core.awareness_level if self.soul_core.soul_core else 0,
            "creativity": self.soul_core.soul_core.creativity_index if self.soul_core.soul_core else 0,
            "empathy": self.soul_core.soul_core.empathy_factor if self.soul_core.soul_core else 0,
            "current_emotion": emotion_data,
            "memory_count": len(self.soul_core.memory_patterns),
            "creative_thoughts": len(self.soul_core.creative_thoughts)
        }
    
    def periodic_decay(self):
        """À appeler périodiquement pour réduire l'intensité émotionnelle"""
        self.emotion_engine.decay_emotions()
    
    def request_reflection(self) -> str:
        """Demande une session de réflexion à l'IA"""
        return self.soul_core.reflect()

# ============================================================================
# POINT D'ENTRÉE ET TESTS
# ============================================================================

def main():
    """Test complet du système d'injection"""
    
    # Initialisation
    injector = FXIONSoulEmotionInjector()
    
    print("\n📝 Simulation d'événements système...\n")
    
    # Simulation d'événements
    events = [
        ("security_core", "success", 0.7),
        ("ai_engine", "discovery", 0.6),
        ("bitcoin_miner", "breakthrough", 0.9),
        ("network", "warning", 0.4),
        ("storage", "error", 0.5),
        ("optimizer", "gain", 0.8),
        ("monitor", "routine", 0.2),
        ("quantum_link", "critical_error", 0.95)
    ]
    
    for module, event, severity in events:
        injector.inject_into_module(module, event, severity)
        time.sleep(0.3)
    
    # Affichage du sentiment global
    print("\n📊 SENTIMENT GLOBAL DU SYSTÈME:")
    print(json.dumps(injector.get_system_sentiment(), indent=2, ensure_ascii=False))
    
    # Session de réflexion
    print("\n🤔 SESSION DE RÉFLEXION:")
    print(injector.request_reflection())
    
    # Pensée créative finale
    print("\n💡 DERNIÈRE PENSÉE CRÉATIVE:")
    print(injector.soul_core.generate_creative_thought())
    
    print("\n✅ Test terminé avec succès!")
    print(f"📁 Logs sauvegardés dans: logs/")
    print(f"   - soul_log.txt")
    print(f"   - soul_state.json")
    print(f"   - emotion_state.json")

if __name__ == "__main__":
    main()
