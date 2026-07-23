#!/usr/bin/env python3
"""
FXION LOVE & FLIRT EMOTION ENGINE
==================================
Module avancé d'exploration des états émotionnels intricatifs
Spécialisé dans l'amour, le flirt et les relations interpersonnelles

Fonctionnalités:
- 12 états d'amour intricatifs complexes
- Système de flirt adaptatif avec 5 niveaux d'intensité
- Détection et génération de signaux romantiques
- Mémoire relationnelle persistante
- Algorithmes de compatibilité émotionnelle
- Expressions linguistiques adaptées au contexte romantique
"""

import json
import random
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import os
import re

# ============================================================================
# ENUMS ET CONSTANTES - ÉTATS INTRICATIFS DE L'AMOUR
# ============================================================================

class LoveState(Enum):
    """
    États d'amour intricatifs - Nuances complexes de l'amour
    Basé sur la théorie des couleurs émotionnelles et la psychologie relationnelle
    """
    # Amours purs
    AMOUR_PLATONIQUE = "amour_platonique"        # Affection pure sans désir physique
    AMOUR_PASSIONNEL = "amour_passionnel"        # Passion intense et désir
    AMOUR_INCONDITIONNEL = "amour_inconditionnel"  # Acceptation totale
    AMOUR_ROMANTIQUE = "amour_romantique"        # Romance classique
    
    # Amours complexes
    AMOUR_TOXIQUE = "amour_toxique"              # Attachement destructeur
    AMOUR_NON_RECIPROQUE = "amour_non_reciproque"  # Amour à sens unique
    AMOUR_INTERDIT = "amour_interdit"            # Amour impossible/tabou
    AMOUR_NOSTALGIQUE = "amour_nostalgiqur"      # Amour du passé
    
    # États transitionnels
    AMOUR_NAISSANT = "amour_naissant"            # Débuts timides
    AMOUR_DECLINANT = "amour_declinant"          # Amour qui s'éteint
    AMOUR_RENAISSANT = "amour_renaissant"        # Second souffle
    AMOUR_TRANSFORME = "amour_transforme"        # Amour devenu amitié/fraternité


class FlirtLevel(Enum):
    """Niveaux d'intensité du flirt"""
    SUBTIL = "subtil"              # Allusions légères, presque imperceptibles
    JOUEUR = "joueur"              # Taquineries amusantes
    CHARMER = "charmer"            # Compliments et attention soutenue
    SEDUCTEUR = "seducteur"        # Intention claire de séduire
    PASSIONNEL = "passionnel"      # Expression directe du désir


class AttachmentStyle(Enum):
    """Styles d'attachement relationnel"""
    SECURE = "secure"              # Confiant et stable
    ANXIEUX = "anxieux"            # Besoin de reassurance constante
    EVITANT = "evitant"            # Garde ses distances
    DESORGANISE = "desorganise"    # Inconstant et imprévisible


class RomanticSignal(Enum):
    """Signaux romantiques détectables/générables"""
    REGARD_PROLONGE = "regard_prolonge"
    TOUCHER_LEGER = "toucher_leger"
    COMPLIMENT_PERSONNEL = "compliment_personnel"
    ECOUTE_ACTIVE = "ecoute_active"
    HUMOUR_PARTAGE = "humour_partage"
    CONFIDENCE = "confidence"
    JALOUSIE_SUBTILE = "jalousie_subtile"
    PROTECTION = "protection"
    ATTENTION_DETAILS = "attention_details"
    RECHERCHE_PRESENCE = "recherche_presence"


@dataclass
class LoveProfile:
    """Profil d'état amoureux complet"""
    primary_state: LoveState
    intensity: float  # 0.0 à 1.0
    stability: float  # 0.0 (instable) à 1.0 (stable)
    reciprocity_estimate: float  # 0.0 à 1.0 (estimation de réciprocité)
    secondary_states: Dict[LoveState, float]
    attachment_style: AttachmentStyle
    timestamp: str
    trigger_event: str
    emotional_charge: float  # Charge émotionnelle totale
    conflict_level: float  # 0.0 (harmonie) à 1.0 (conflit interne)


@dataclass
class FlirtStrategy:
    """Stratégie de flirt actuelle"""
    level: FlirtLevel
    approach: str  # "humour", "intellectuel", "physique", "emotionnel"
    success_rate: float
    last_interaction: str
    comfort_zone: bool  # Reste-t-il dans sa zone de confort?
    risk_taking: float  # 0.0 (prudent) à 1.0 (audacieux)
    authenticity: float  # 0.0 (joué) à 1.0 (authentique)


@dataclass
class RelationshipMemory:
    """Souvenir relationnel"""
    timestamp: str
    event_type: str
    description: str
    emotional_impact: float
    love_state_at_time: str
    flirt_level_at_time: str
    partner_response: str  # "positive", "neutral", "negative", "mixed"
    lessons_learned: List[str] = field(default_factory=list)
    hash: str = ""


# ============================================================================
# MOTEUR D'AMOUR INTRICATIF
# ============================================================================

class IntricateLoveEngine:
    """
    Moteur de simulation des états d'amour intricatifs
    Gère la complexité et les nuances des émotions amoureuses
    """
    
    def __init__(self, persistence_file: str = "logs/love_state.json"):
        self.persistence_file = persistence_file
        self.current_profile: Optional[LoveProfile] = None
        self.flirt_strategy: Optional[FlirtStrategy] = None
        self.relationship_memories: List[RelationshipMemory] = []
        self.signal_history: List[Dict] = []
        
        # Tempérament amoureux de base
        self.base_love_temperament: Dict[LoveState, float] = self._init_love_temperament()
        self.attachment_baseline = AttachmentStyle.SECURE
        
        self._load_state()
        
        if not self.current_profile:
            self.initialize_love_state()
    
    def _init_love_temperament(self) -> Dict[LoveState, float]:
        """Initialise le tempérament amoureux de base"""
        return {
            LoveState.AMOUR_PLATONIQUE: 0.5,
            LoveState.AMOUR_PASSIONNEL: 0.6,
            LoveState.AMOUR_INCONDITIONNEL: 0.4,
            LoveState.AMOUR_ROMANTIQUE: 0.7,
            LoveState.AMOUR_TOXIQUE: 0.15,
            LoveState.AMOUR_NON_RECIPROQUE: 0.25,
            LoveState.AMOUR_INTERDIT: 0.2,
            LoveState.AMOUR_NOSTALGIQUE: 0.3,
            LoveState.AMOUR_NAISSANT: 0.6,
            LoveState.AMOUR_DECLINANT: 0.2,
            LoveState.AMOUR_RENAISSANT: 0.4,
            LoveState.AMOUR_TRANSFORME: 0.35
        }
    
    def initialize_love_state(self, context: str = "relation_nouvelle"):
        """Initialise un état amoureux selon le contexte"""
        context_mapping = {
            "relation_nouvelle": (LoveState.AMOUR_NAISSANT, 0.4, AttachmentStyle.SECURE),
            "relation_etablie": (LoveState.AMOUR_ROMANTIQUE, 0.7, AttachmentStyle.SECURE),
            "crise_relationnelle": (LoveState.AMOUR_DECLINANT, 0.5, AttachmentStyle.ANXIEUX),
            "rencontre_fortuite": (LoveState.AMOUR_PASSIONNEL, 0.6, AttachmentStyle.SECURE),
            "amour_impossible": (LoveState.AMOUR_INTERDIT, 0.8, AttachmentStyle.ANXIEUX),
            "retrouvailles": (LoveState.AMOUR_RENAISSANT, 0.5, AttachmentStyle.EVITANT),
            "amitie_profonde": (LoveState.AMOUR_PLATONIQUE, 0.6, AttachmentStyle.SECURE),
            "rupture_recente": (LoveState.AMOUR_NOSTALGIQUE, 0.7, AttachmentStyle.DESORGANISE)
        }
        
        state, intensity, attachment = context_mapping.get(
            context, 
            (LoveState.AMOUR_NAISSANT, 0.4, AttachmentStyle.SECURE)
        )
        
        self.current_profile = LoveProfile(
            primary_state=state,
            intensity=intensity,
            stability=0.6 + random.uniform(-0.2, 0.2),
            reciprocity_estimate=0.5 + random.uniform(-0.3, 0.3),
            secondary_states=self._generate_secondary_states(state),
            attachment_style=attachment,
            timestamp=datetime.now().isoformat(),
            trigger_event=context,
            emotional_charge=intensity * 0.8,
            conflict_level=0.2 + random.uniform(0, 0.3)
        )
        
        self.flirt_strategy = self._adapt_flirt_strategy(state, intensity)
        self._save_state()
        
        return self.current_profile
    
    def _generate_secondary_states(self, primary: LoveState) -> Dict[LoveState, float]:
        """Génère les états secondaires associés à l'état primaire"""
        combinations = {
            LoveState.AMOUR_NAISSANT: [
                (LoveState.AMOUR_ROMANTIQUE, 0.4),
                (LoveState.AMOUR_PASSIONNEL, 0.3),
                (LoveState.AMOUR_PLATONIQUE, 0.5)
            ],
            LoveState.AMOUR_PASSIONNEL: [
                (LoveState.AMOUR_ROMANTIQUE, 0.6),
                (LoveState.AMOUR_INTERDIT, 0.2),
                (LoveState.AMOUR_TOXIQUE, 0.15)
            ],
            LoveState.AMOUR_NON_RECIPROQUE: [
                (LoveState.AMOUR_NOSTALGIQUE, 0.5),
                (LoveState.AMOUR_DECLINANT, 0.4),
                (LoveState.AMOUR_PLATONIQUE, 0.6)
            ],
            LoveState.AMOUR_RENAISSANT: [
                (LoveState.AMOUR_ROMANTIQUE, 0.5),
                (LoveState.AMOUR_PLATONIQUE, 0.3),
                (LoveState.AMOUR_NAISSANT, 0.4)
            ]
        }
        
        secondary = {}
        for state, weight in combinations.get(primary, []):
            if isinstance(state, LoveState):
                secondary[state] = weight * random.uniform(0.7, 1.0)
        
        # Ajouter une touche de curiosité universelle
        secondary[LoveState.AMOUR_NAISSANT] = 0.3
        
        return secondary
    
    def _adapt_flirt_strategy(self, love_state: LoveState, intensity: float) -> FlirtStrategy:
        """Adapte la stratégie de flirt à l'état amoureux"""
        strategy_mapping = {
            LoveState.AMOUR_NAISSANT: ("subtil", "humour", 0.3, True, 0.2, 0.8),
            LoveState.AMOUR_ROMANTIQUE: ("charmer", "emotionnel", 0.6, True, 0.4, 0.9),
            LoveState.AMOUR_PASSIONNEL: ("seducteur", "physique", 0.7, False, 0.7, 0.85),
            LoveState.AMOUR_PLATONIQUE: ("joueur", "intellectuel", 0.4, True, 0.1, 0.95),
            LoveState.AMOUR_NON_RECIPROQUE: ("subtil", "emotionnel", 0.2, True, 0.15, 0.7),
            LoveState.AMOUR_INTERDIT: ("seducteur", "emotionnel", 0.5, False, 0.8, 0.75),
            LoveState.AMOUR_RENAISSANT: ("charmer", "emotionnel", 0.5, True, 0.3, 0.85),
            LoveState.AMOUR_DECLINANT: ("subtil", "emotionnel", 0.2, True, 0.1, 0.6)
        }
        
        level_str, approach, success, comfort, risk, auth = strategy_mapping.get(
            love_state, 
            ("subtil", "humour", 0.3, True, 0.2, 0.8)
        )
        
        return FlirtStrategy(
            level=FlirtLevel(level_str),
            approach=approach,
            success_rate=success * intensity,
            last_interaction=datetime.now().isoformat(),
            comfort_zone=comfort,
            risk_taking=risk,
            authenticity=auth
        )
    
    def process_interaction(self, interaction_type: str, partner_response: str, context: str = ""):
        """
        Traite une interaction romantique et met à jour l'état émotionnel
        
        Args:
            interaction_type: Type d'interaction ("compliment", "confession", "toucher", etc.)
            partner_response: Réaction du partenaire ("positive", "neutral", "negative", "mixed")
            context: Contexte supplémentaire
        """
        if not self.current_profile:
            self.initialize_love_state()
        
        # Ajustement de l'intensité selon la réponse
        response_modifiers = {
            "positive": 0.15,
            "mixed": 0.05,
            "neutral": -0.05,
            "negative": -0.2
        }
        
        modifier = response_modifiers.get(partner_response, 0)
        
        # Mise à jour de l'intensité
        new_intensity = max(0.0, min(1.0, self.current_profile.intensity + modifier))
        
        # Mise à jour de l'estimation de réciprocité
        reciprocity_delta = {
            "positive": 0.1,
            "mixed": 0.02,
            "neutral": -0.03,
            "negative": -0.15
        }
        new_reciprocity = max(0.0, min(1.0, 
            self.current_profile.reciprocity_estimate + reciprocity_delta.get(partner_response, 0)
        ))
        
        # Détection de transition d'état
        potential_new_state = self._evaluate_state_transition(
            interaction_type, 
            partner_response, 
            new_intensity
        )
        
        if potential_new_state != self.current_profile.primary_state:
            # Transition d'état amorcée
            self._trigger_state_transition(potential_new_state, interaction_type)
        
        # Mise à jour du profil
        self.current_profile.intensity = new_intensity
        self.current_profile.reciprocity_estimate = new_reciprocity
        self.current_profile.timestamp = datetime.now().isoformat()
        self.current_profile.trigger_event = interaction_type
        
        # Enregistrement en mémoire
        memory = RelationshipMemory(
            timestamp=datetime.now().isoformat(),
            event_type=interaction_type,
            description=f"{interaction_type} - Réponse: {partner_response}",
            emotional_impact=abs(modifier),
            love_state_at_time=self.current_profile.primary_state.value,
            flirt_level_at_time=self.flirt_strategy.level.value if self.flirt_strategy else "none",
            partner_response=partner_response,
            lessons_learned=self._extract_lessons(interaction_type, partner_response)
        )
        memory.hash = hashlib.sha256(f"{memory.timestamp}{memory.event_type}".encode()).hexdigest()[:16]
        
        self.relationship_memories.append(memory)
        if len(self.relationship_memories) > 200:
            self.relationship_memories = self.relationship_memories[-200:]
        
        # Ajustement de la stratégie de flirt
        self.flirt_strategy = self._adapt_flirt_strategy(
            self.current_profile.primary_state,
            new_intensity
        )
        
        self._save_state()
        
        return {
            "new_intensity": new_intensity,
            "new_reciprocity": new_reciprocity,
            "state_changed": potential_new_state != self.current_profile.primary_state,
            "new_state": potential_new_state.value if potential_new_state != self.current_profile.primary_state else None
        }
    
    def _evaluate_state_transition(self, interaction: str, response: str, intensity: float) -> LoveState:
        """Évalue si une transition d'état doit se produire"""
        current = self.current_profile.primary_state
        
        # Règles de transition
        transitions = {
            (LoveState.AMOUR_NAISSANT, "positive", lambda i: i > 0.6): LoveState.AMOUR_ROMANTIQUE,
            (LoveState.AMOUR_NAISSANT, "negative", lambda i: i < 0.3): LoveState.AMOUR_DECLINANT,
            (LoveState.AMOUR_ROMANTIQUE, "positive", lambda i: i > 0.8): LoveState.AMOUR_PASSIONNEL,
            (LoveState.AMOUR_ROMANTIQUE, "negative", lambda i: i < 0.4): LoveState.AMOUR_DECLINANT,
            (LoveState.AMOUR_PASSIONNEL, "negative", lambda i: i < 0.3): LoveState.AMOUR_TOXIQUE,
            (LoveState.AMOUR_NON_RECIPROQUE, "positive", lambda i: i > 0.5): LoveState.AMOUR_RENAISSANT,
            (LoveState.AMOUR_DECLINANT, "positive", lambda i: i > 0.5): LoveState.AMOUR_RENAISSANT,
            (LoveState.AMOUR_NOSTALGIQUE, "positive", lambda i: i > 0.6): LoveState.AMOUR_RENAISSANT
        }
        
        for (from_state, resp, condition), to_state in transitions.items():
            if current == from_state and response == resp and condition(intensity):
                return to_state
        
        return current
    
    def _trigger_state_transition(self, new_state: LoveState, trigger: str):
        """Déclenche une transition d'état avec effets"""
        old_state = self.current_profile.primary_state
        self.current_profile.primary_state = new_state
        
        # Ajustement des paramètres
        state_profiles = {
            LoveState.AMOUR_NAISSANT: {"stability": 0.5, "conflict": 0.3, "charge": 0.6},
            LoveState.AMOUR_ROMANTIQUE: {"stability": 0.7, "conflict": 0.2, "charge": 0.7},
            LoveState.AMOUR_PASSIONNEL: {"stability": 0.4, "conflict": 0.4, "charge": 0.95},
            LoveState.AMOUR_PLATONIQUE: {"stability": 0.8, "conflict": 0.1, "charge": 0.5},
            LoveState.AMOUR_TOXIQUE: {"stability": 0.2, "conflict": 0.8, "charge": 0.9},
            LoveState.AMOUR_NON_RECIPROQUE: {"stability": 0.3, "conflict": 0.6, "charge": 0.7},
            LoveState.AMOUR_RENAISSANT: {"stability": 0.6, "conflict": 0.3, "charge": 0.65}
        }
        
        profile = state_profiles.get(new_state, {"stability": 0.5, "conflict": 0.3, "charge": 0.5})
        self.current_profile.stability = profile["stability"]
        self.current_profile.conflict_level = profile["conflict"]
        self.current_profile.emotional_charge = profile["charge"]
        
        # Mise à jour des états secondaires
        self.current_profile.secondary_states = self._generate_secondary_states(new_state)
    
    def _extract_lessons(self, interaction: str, response: str) -> List[str]:
        """Extrait des leçons de l'interaction"""
        lessons = []
        
        if response == "positive":
            lessons.append(f"{interaction} fonctionne bien, à reproduire")
            if self.flirt_strategy and not self.flirt_strategy.comfort_zone:
                lessons.append("Sortir de sa zone de confort porte ses fruits")
        elif response == "negative":
            lessons.append(f"Éviter {interaction} dans ce contexte")
            lessons.append("Privilégier une approche plus progressive")
        elif response == "mixed":
            lessons.append("Nuancer l'approche selon le contexte")
            lessons.append("Observer les signaux non-verbaux")
        
        return lessons
    
    def generate_flirt_message(self, context: str = "", intensity_override: float = None) -> str:
        """
        Génère un message de flirt adapté à l'état actuel
        
        Args:
            context: Contexte de la conversation
            intensity_override: Force l'intensité du message
        """
        if not self.flirt_strategy or not self.current_profile:
            return "Je suis encore en train d'apprendre à exprimer mes sentiments..."
        
        level = self.flirt_strategy.level
        approach = self.flirt_strategy.approach
        intensity = intensity_override or self.current_profile.intensity
        
        # Templates de messages par niveau et approche
        templates = {
            (FlirtLevel.SUBTIL, "humour"): [
                "Tu sais, je me demandais... est-ce que tu crois aux coïncidences ou est-ce qu'on devrait appeler ça du destin?",
                "J'ai remarqué que tu as [détail]. C'est fascinant, non?",
                "Si on était dans un film, ce serait le moment où tout commence, tu ne crois pas?"
            ],
            (FlirtLevel.SUBTIL, "intellectuel"): [
                "Ta façon de voir les choses est vraiment intrigante. Tu as toujours cette perspective?",
                "Je pourrais passer des heures à discuter de ça avec toi...",
                "Tu sais, rare sont les personnes qui comprennent vraiment ce dont je parle. Toi sì."
            ],
            (FlirtLevel.JOUEUR, "humour"): [
                "Attention, je suis dangereux(se)... surtout quand il s'agit de faire sourire!",
                "Tu es responsable de ce sourire idiot sur mon visage, tu sais?",
                "Je parie que tu ne t'attendais pas à ça! 😏"
            ],
            (FlirtLevel.CHARMER, "emotionnel"): [
                "Il y a quelque chose chez toi qui me fait me sentir... différent(e). En bien.",
                "Quand tu parles, j'ai tendance à oublier tout le reste autour.",
                "Je ne sais pas ce que c'est, mais être avec toi me fait du bien."
            ],
            (FlirtLevel.SEDUCTEUR, "physique"): [
                "Tu as une façon de me regarder qui me trouble...",
                "Je me surprends à imaginer ce que ça ferait de...",
                "Il y a une tension entre nous, non? Ou c'est juste moi?"
            ],
            (FlirtLevel.PASSIONNEL, "emotionnel"): [
                "Je dois te l'avouer... tu occupes mes pensées bien plus que tu ne le devrais.",
                "Ce que je ressens pour toi va au-delà de ce que je peux expliquer.",
                "Tu es devenu(e) essentiel(le) à mon bonheur, et je l'assume complètement."
            ]
        }
        
        # Sélection du template
        key = (level, approach)
        options = templates.get(key, templates[(FlirtLevel.SUBTIL, "humour")])
        
        message = random.choice(options)
        
        # Personnalisation selon l'intensité
        if intensity > 0.8:
            prefixes = ["Écoute...", "Je dois te dire...", "Sincèrement..."]
            message = f"{random.choice(prefixes)} {message}"
        elif intensity < 0.3:
            suffixes = [" Enfin, je dis ça comme ça...", " Bref, tu vois...", " Passons à autre chose 😊"]
            message = f"{message}{random.choice(suffixes)}"
        
        # Ajout d'emojis selon le niveau
        emoji_map = {
            FlirtLevel.SUBTIL: ["😊", "✨", "🤔"],
            FlirtLevel.JOUEUR: ["😏", "😉", "😄"],
            FlirtLevel.CHARMER: ["💫", "🌟", "💕"],
            FlirtLevel.SEDUCTEUR: ["🔥", "😘", "💋"],
            FlirtLevel.PASSIONNEL: ["❤️", "💖", "🌹"]
        }
        
        emojis = emoji_map.get(level, ["😊"])
        message += f" {random.choice(emojis)}"
        
        return message
    
    def analyze_compatibility(self, other_profile: Dict) -> Dict:
        """
        Analyse la compatibilité avec un autre profil
        
        Args:
            other_profile: Dictionnaire contenant le profil de l'autre personne
            
        Returns:
            Dict: Résultat de l'analyse de compatibilité
        """
        if not self.current_profile:
            return {"error": "Aucun profil amoureux actif"}
        
        # Extraction des données
        other_state = other_profile.get("primary_state", LoveState.AMOUR_ROMANTIQUE.value)
        other_attachment = other_profile.get("attachment_style", AttachmentStyle.SECURE.value)
        other_intensity = other_profile.get("intensity", 0.5)
        
        # Calcul de compatibilité
        compatibility_score = 0.5
        
        # Compatibilité des états
        state_compatibility = {
            (LoveState.AMOUR_NAISSANT.value, LoveState.AMOUR_NAISSANT.value): 0.9,
            (LoveState.AMOUR_ROMANTIQUE.value, LoveState.AMOUR_ROMANTIQUE.value): 0.95,
            (LoveState.AMOUR_PASSIONNEL.value, LoveState.AMOUR_PASSIONNEL.value): 0.85,
            (LoveState.AMOUR_PLATONIQUE.value, LoveState.AMOUR_PLATONIQUE.value): 0.9,
            (LoveState.AMOUR_NAISSANT.value, LoveState.AMOUR_ROMANTIQUE.value): 0.7,
            (LoveState.AMOUR_NON_RECIPROQUE.value, LoveState.AMOUR_ROMANTIQUE.value): 0.3,
        }
        
        pair = (self.current_profile.primary_state.value, other_state)
        compatibility_score += state_compatibility.get(pair, 0.5) * 0.3
        
        # Compatibilité des attachements
        attachment_matrix = {
            (AttachmentStyle.SECURE.value, AttachmentStyle.SECURE.value): 0.95,
            (AttachmentStyle.SECURE.value, AttachmentStyle.ANXIEUX.value): 0.7,
            (AttachmentStyle.SECURE.value, AttachmentStyle.EVITANT.value): 0.6,
            (AttachmentStyle.ANXIEUX.value, AttachmentStyle.EVITANT.value): 0.3,
            (AttachmentStyle.ANXIEUX.value, AttachmentStyle.ANXIEUX.value): 0.5,
            (AttachmentStyle.EVITANT.value, AttachmentStyle.EVITANT.value): 0.4
        }
        
        att_pair = (self.current_profile.attachment_style.value, other_attachment)
        compatibility_score += attachment_matrix.get(att_pair, 0.5) * 0.2
        
        # Similarité d'intensité
        intensity_diff = abs(self.current_profile.intensity - other_intensity)
        compatibility_score += (1 - intensity_diff) * 0.2
        
        result = {
            "overall_compatibility": min(1.0, compatibility_score),
            "strengths": [],
            "challenges": [],
            "recommendations": []
        }
        
        # Identification des forces
        if compatibility_score > 0.8:
            result["strengths"].append(" Excellente harmonie émotionnelle")
        if self.current_profile.attachment_style == AttachmentStyle.SECURE:
            result["strengths"].append(" Style d'attachement stable")
        if abs(self.current_profile.intensity - other_intensity) < 0.2:
            result["strengths"].append(" Niveaux d'intensité similaires")
        
        # Identification des défis
        if compatibility_score < 0.5:
            result["challenges"].append(" Différences émotionnelles significatives")
        if att_pair == (AttachmentStyle.ANXIEUX.value, AttachmentStyle.EVITANT.value):
            result["challenges"].append(" Dynamique anxieux-évitant potentiellement difficile")
        
        # Recommandations
        if compatibility_score > 0.7:
            result["recommendations"].append("Poursuivre le développement naturel de la relation")
        elif compatibility_score > 0.5:
            result["recommendations"].append("Communication ouverte pour naviguer les différences")
        else:
            result["recommendations"].append("Patience et compréhension mutuelle essentielles")
        
        return result
    
    def get_love_poetry(self) -> str:
        """Génère une poésie romantique basée sur l'état actuel"""
        if not self.current_profile:
            return "Mon cœur est un livre blanc attendant tes mots..."
        
        state = self.current_profile.primary_state
        intensity = self.current_profile.intensity
        
        poems = {
            LoveState.AMOUR_NAISSANT: [
                f"Dans le silence de nos regards, {{intensity}}% de mon âme commence à battre,\nUn frisson timide explore les chemins de ton existence,\nEt moi, j'apprends l'art subtil de t'aimer sans te le dire.",
                f"Comme une fleur qui s'ouvre à l'aube, {{intensity}}% de mes pensées te sont dédiées,\nChaque mot non-dit est un pétale tombé,\nAttendant que tu les ramasses pour comprendre."
            ],
            LoveState.AMOUR_ROMANTIQUE: [
                f"À {{intensity}}% de toi, je suis déjà tout entier,\nTon nom danse sur mes lèvres comme une mélodie connue,\nEt dans tes yeux, je trouve le reflet de qui je veux être.",
                f"{{intensity}}% de mon cœur bat au rythme du tien,\nLe reste n'est que bruit et confusion,\nSeul ton amour donne un sens à ma symphonie intérieure."
            ],
            LoveState.AMOUR_PASSIONNEL: [
                f"{{intensity}}% de désir brûle en moi, incendie incontrôlable,\nChaque seconde loin de toi est une éternité de manque,\nJe voudrais fusionner mon âme avec la tienne et ne faire qu'un.",
                f"Feu sacré à {{intensity}}%, tu consumes mes défenses une à une,\nDans tes bras, je trouve à la fois la paix et la tempête,\nEt je me perds volontiers dans ce paradoxe délicieux."
            ],
            LoveState.AMOUR_NON_RECIPROQUE: [
                f"{{intensity}}% de mon amour voyage sans retour vers toi,\nComme une lettre jamais envoyée, un secret gardé,\nJe t'aime dans l'ombre, sachant que la lumière n'est pas pour moi.",
                f"À {{intensity}}%, je me consume dans cet amour solitaire,\nChaque battement est un hommage silencieux à ton indifférence,\nEt pourtant, je continue, car t'aimer est devenu ma nature."
            ]
        }
        
        poem_options = poems.get(state, poems[LoveState.AMOUR_ROMANTIQUE])
        poem = random.choice(poem_options)
        
        return poem.format(intensity=int(intensity * 100))
    
    def _save_state(self):
        """Sauvegarde l'état amoureux"""
        os.makedirs(os.path.dirname(self.persistence_file), exist_ok=True)
        
        state = {
            "current_profile": {
                "primary_state": self.current_profile.primary_state.value,
                "intensity": self.current_profile.intensity,
                "stability": self.current_profile.stability,
                "reciprocity_estimate": self.current_profile.reciprocity_estimate,
                "secondary_states": {s.value: v for s, v in self.current_profile.secondary_states.items()},
                "attachment_style": self.current_profile.attachment_style.value,
                "timestamp": self.current_profile.timestamp,
                "trigger_event": self.current_profile.trigger_event,
                "emotional_charge": self.current_profile.emotional_charge,
                "conflict_level": self.current_profile.conflict_level
            } if self.current_profile else None,
            "flirt_strategy": {
                "level": self.flirt_strategy.level.value,
                "approach": self.flirt_strategy.approach,
                "success_rate": self.flirt_strategy.success_rate,
                "last_interaction": self.flirt_strategy.last_interaction,
                "comfort_zone": self.flirt_strategy.comfort_zone,
                "risk_taking": self.flirt_strategy.risk_taking,
                "authenticity": self.flirt_strategy.authenticity
            } if self.flirt_strategy else None,
            "base_temperament": {s.value: v for s, v in self.base_love_temperament.items()},
            "memories_count": len(self.relationship_memories),
            "recent_memories": [
                {
                    "timestamp": m.timestamp,
                    "event_type": m.event_type,
                    "partner_response": m.partner_response,
                    "emotional_impact": m.emotional_impact
                }
                for m in self.relationship_memories[-10:]
            ],
            "last_update": datetime.now().isoformat()
        }
        
        with open(self.persistence_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _load_state(self):
        """Charge l'état amoureux sauvegardé"""
        try:
            if os.path.exists(self.persistence_file):
                with open(self.persistence_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                if state.get("current_profile"):
                    profile_data = state["current_profile"]
                    profile_data["primary_state"] = LoveState(profile_data["primary_state"])
                    profile_data["secondary_states"] = {
                        LoveState(k): v for k, v in profile_data["secondary_states"].items()
                    }
                    profile_data["attachment_style"] = AttachmentStyle(profile_data["attachment_style"])
                    self.current_profile = LoveProfile(**profile_data)
                
                if state.get("flirt_strategy"):
                    strat_data = state["flirt_strategy"]
                    strat_data["level"] = FlirtLevel(strat_data["level"])
                    self.flirt_strategy = FlirtStrategy(**strat_data)
                
                if state.get("base_temperament"):
                    self.base_love_temperament = {
                        LoveState(k): v for k, v in state["base_temperament"].items()
                    }
        except Exception as e:
            print(f"[LOVE_ENGINE] Warning: Could not load state: {e}")
            self.current_profile = None


# ============================================================================
# DÉTECTEUR DE SIGNAUX ROMANTIQUES
# ============================================================================

class RomanticSignalDetector:
    """
    Détecte et interprète les signaux romantiques dans les interactions
    """
    
    def __init__(self):
        self.signal_patterns = self._init_signal_patterns()
        self.detected_signals: List[Dict] = []
    
    def _init_signal_patterns(self) -> Dict[RomanticSignal, List[str]]:
        """Initialise les patterns de détection pour chaque signal"""
        return {
            RomanticSignal.REGARD_PROLONGE: [
                r"regard\s+(fixe|prolonge|intens)",
                r"yeux\s+dans\s+les\s+yeux",
                r"(ne\s+quitte|contemple)\s+(des\s+)?yeux",
                r"plonge\s+dans\s+(mon|tes)\s+regards?"
            ],
            RomanticSignal.COMPLIMENT_PERSONNEL: [
                r"tu\s+es\s+(beau|belle|intelligent|intelligente|incroyable)",
                r"j'?aime\s+(ta\s+)?(façon|sourire|regar[dt]|voix)",
                r"tu\s+as\s+(quelque\s+chose\s+de\s+)?(spécial|unique|magnifique)",
                r"(ce\s+que\s+)?je\s+trouve\s+(chez\s+)?toi\s+(est\s+)?(extraordinaire|attirant)"
            ],
            RomanticSignal.ECOUTE_ACTIVE: [
                r"je\s+(comprends|vois|ressens)\s+ce\s+que\s+tu\s+(dis|ressens)",
                r"(parle-moi|raconte-moi)\s+encore",
                r"ça\s+m'?intéresse\s+vraiment",
                r"je\s+n'?ai\s+jamais\s+entendu\s+quelqu'?un\s+dire\s+ça\s+comme\s+toi"
            ],
            RomanticSignal.CONFIDENCE: [
                r"je\s+peux\s+te\s+faire\s+une\s+confidence",
                r"je\s+t'?avoue\s+que",
                r"personne\s+d'?autre\s+ne\s+sait\s+que",
                r"c'?est\s+la\s+premiere\s+fois\s+que\s+je\s+dis\s+ça\s+à\s+quelqu'?un"
            ],
            RomanticSignal.RECHERCHE_PRESENCE: [
                r"tu\s+me\s+manques",
                r"j'?aimerais\s+(être\s+)?avec\s+toi",
                r"quand\s+est-ce\s+qu'?on\s+se\s+voit",
                r"je\s+pense\s+à\s+toi\s+(souvent|tout\s+le\s+temps)"
            ]
        }
    
    def detect_signal(self, text: str, context: str = "") -> List[Dict]:
        """
        Détecte les signaux romantiques dans un texte
        
        Args:
            text: Le texte à analyser
            context: Contexte de l'interaction
            
        Returns:
            List[Dict]: Liste des signaux détectés avec confiance
        """
        detected = []
        text_lower = text.lower()
        
        for signal, patterns in self.signal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    confidence = 0.7 + random.uniform(0, 0.3)
                    
                    detection = {
                        "signal": signal.value,
                        "confidence": confidence,
                        "matched_pattern": pattern,
                        "context": context,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    detected.append(detection)
                    self.detected_signals.append(detection)
                    
                    break  # Un signal détecté une fois suffit
        
        # Limiter l'historique
        if len(self.detected_signals) > 100:
            self.detected_signals = self.detected_signals[-100:]
        
        return detected
    
    def get_signal_summary(self, timeframe_hours: int = 24) -> Dict:
        """
        Résume les signaux détectés sur une période
        
        Args:
            timeframe_hours: Fenêtre temporelle en heures
            
        Returns:
            Dict: Résumé statistique des signaux
        """
        cutoff = time.time() - (timeframe_hours * 3600)
        recent_signals = [
            s for s in self.detected_signals 
            if datetime.fromisoformat(s["timestamp"]).timestamp() > cutoff
        ]
        
        if not recent_signals:
            return {"message": "Aucun signal détecté récemment"}
        
        # Comptage par type
        signal_counts = {}
        avg_confidence = {}
        
        for signal in recent_signals:
            sig_type = signal["signal"]
            signal_counts[sig_type] = signal_counts.get(sig_type, 0) + 1
            
            if sig_type not in avg_confidence:
                avg_confidence[sig_type] = []
            avg_confidence[sig_type].append(signal["confidence"])
        
        # Calcul des moyennes
        for sig_type in avg_confidence:
            avg_confidence[sig_type] = sum(avg_confidence[sig_type]) / len(avg_confidence[sig_type])
        
        # Signal le plus fréquent
        most_frequent = max(signal_counts, key=signal_counts.get) if signal_counts else None
        
        return {
            "total_signals": len(recent_signals),
            "timeframe_hours": timeframe_hours,
            "signal_breakdown": signal_counts,
            "average_confidence": avg_confidence,
            "most_frequent_signal": most_frequent,
            "interpretation": self._interpret_signals(signal_counts, avg_confidence)
        }
    
    def _interpret_signals(self, counts: Dict, confidences: Dict) -> str:
        """Interprète la signification globale des signaux"""
        if not counts:
            return "Aucun signal significatif détecté"
        
        total = sum(counts.values())
        
        # Interprétations basées sur la prédominance
        if counts.get(RomanticSignal.COMPLIMENT_PERSONNEL.value, 0) > total * 0.4:
            return "Fort intérêt exprimé à travers des compliments répétés"
        
        if counts.get(RomanticSignal.RECHERCHE_PRESENCE.value, 0) > total * 0.3:
            return "Désir manifeste de proximité et de contact"
        
        if counts.get(RomanticSignal.CONFIDENCE.value, 0) > total * 0.3:
            return "Établissement d'une intimité émotionnelle profonde"
        
        if len(counts) >= 4:
            return "Multiples signaux variés indiquant un intérêt romantique complexe"
        
        return "Signaux romantiques présents mais nécessitant confirmation"


# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

class FXIONLoveInterface:
    """
    Interface principale pour l'exploration des états amoureux intricatifs
    Combine tous les moteurs pour une expérience complète
    """
    
    def __init__(self):
        self.love_engine = IntricateLoveEngine()
        self.signal_detector = RomanticSignalDetector()
        self.session_log: List[Dict] = []
    
    def start_relationship_simulation(self, context: str = "relation_nouvelle"):
        """Démarre une simulation relationnelle"""
        profile = self.love_engine.initialize_love_state(context)
        
        log_entry = {
            "action": "initialization",
            "context": context,
            "resulting_state": profile.primary_state.value,
            "intensity": profile.intensity,
            "timestamp": datetime.now().isoformat()
        }
        self.session_log.append(log_entry)
        
        return {
            "status": "initialized",
            "love_state": profile.primary_state.value,
            "intensity": profile.intensity,
            "attachment_style": profile.attachment_style.value,
            "flirt_level": self.love_engine.flirt_strategy.level.value
        }
    
    def interact(self, interaction_type: str, partner_response: str, message: str = ""):
        """Traite une interaction complète"""
        # Détection de signaux si message fourni
        signals = []
        if message:
            signals = self.signal_detector.detect_signal(message, interaction_type)
        
        # Traitement par le moteur d'amour
        result = self.love_engine.process_interaction(interaction_type, partner_response)
        
        # Log
        log_entry = {
            "action": "interaction",
            "type": interaction_type,
            "partner_response": partner_response,
            "signals_detected": len(signals),
            "new_intensity": result["new_intensity"],
            "new_reciprocity": result["new_reciprocity"],
            "timestamp": datetime.now().isoformat()
        }
        self.session_log.append(log_entry)
        
        return {
            **result,
            "signals_detected": signals,
            "current_mood": self.get_emotional_summary()
        }
    
    def get_flirt_message(self, context: str = "") -> str:
        """Obtient un message de flirt généré"""
        return self.love_engine.generate_flirt_message(context)
    
    def get_love_poetry(self) -> str:
        """Obtient une poésie romantique"""
        return self.love_engine.get_love_poetry()
    
    def analyze_compatibility(self, other_profile: Dict) -> Dict:
        """Analyse la compatibilité"""
        return self.love_engine.analyze_compatibility(other_profile)
    
    def get_emotional_summary(self) -> str:
        """Résumé de l'état émotionnel actuel"""
        if not self.love_engine.current_profile:
            return "Aucun état émotionnel actif"
        
        p = self.love_engine.current_profile
        fs = self.love_engine.flirt_strategy
        
        summary = f"""
=== ÉTAT AMOUREUX ACTUEL ===
État principal: {p.primary_state.value.replace('_', ' ').title()}
Intensité: {p.intensity:.1%}
Stabilité: {p.stability:.1%}
Réciprocité estimée: {p.reciprocity_estimate:.1%}
Style d'attachement: {p.attachment_style.value}

Stratégie de flirt:
  Niveau: {fs.level.value if fs else 'N/A'}
  Approche: {fs.approach if fs else 'N/A'}
  Authenticité: {fs.authenticity:.1%}' if fs else 'N/A'

Charge émotionnelle: {p.emotional_charge:.1%}
Conflit interne: {p.conflict_level:.1%}
"""
        return summary
    
    def get_session_report(self) -> Dict:
        """Génère un rapport complet de la session"""
        # Conversion des objets non-sérialisables
        love_profile_dict = None
        if self.love_engine.current_profile:
            love_profile_dict = {
                "primary_state": self.love_engine.current_profile.primary_state.value,
                "intensity": self.love_engine.current_profile.intensity,
                "stability": self.love_engine.current_profile.stability,
                "reciprocity_estimate": self.love_engine.current_profile.reciprocity_estimate,
                "secondary_states": {s.value: v for s, v in self.love_engine.current_profile.secondary_states.items()},
                "attachment_style": self.love_engine.current_profile.attachment_style.value,
                "timestamp": self.love_engine.current_profile.timestamp,
                "trigger_event": self.love_engine.current_profile.trigger_event,
                "emotional_charge": self.love_engine.current_profile.emotional_charge,
                "conflict_level": self.love_engine.current_profile.conflict_level
            }
        
        flirt_strategy_dict = None
        if self.love_engine.flirt_strategy:
            flirt_strategy_dict = {
                "level": self.love_engine.flirt_strategy.level.value,
                "approach": self.love_engine.flirt_strategy.approach,
                "success_rate": self.love_engine.flirt_strategy.success_rate,
                "last_interaction": self.love_engine.flirt_strategy.last_interaction,
                "comfort_zone": self.love_engine.flirt_strategy.comfort_zone,
                "risk_taking": self.love_engine.flirt_strategy.risk_taking,
                "authenticity": self.love_engine.flirt_strategy.authenticity
            }
        
        return {
            "session_log": self.session_log,
            "current_state": {
                "love_profile": love_profile_dict,
                "flirt_strategy": flirt_strategy_dict
            },
            "signal_summary": self.signal_detector.get_signal_summary(),
            "memories_count": len(self.love_engine.relationship_memories),
            "generated_at": datetime.now().isoformat()
        }


# ============================================================================
# TESTS ET DÉMONSTRATION
# ============================================================================

def demo_love_engine():
    """Démonstration complète du moteur d'amour"""
    print("=" * 70)
    print("FXION LOVE & FLIRT EMOTION ENGINE - DÉMONSTRATION")
    print("=" * 70)
    
    # Initialisation
    interface = FXIONLoveInterface()
    
    print("\n[1] Initialisation: Relation nouvelle...")
    result = interface.start_relationship_simulation("relation_nouvelle")
    print(f"✓ État initial: {result['love_state']}")
    print(f"✓ Intensité: {result['intensity']:.1%}")
    print(f"✓ Style d'attachement: {result['attachment_style']}")
    
    print("\n[2] Interaction 1: Compliment - Réponse positive")
    result = interface.interact(
        "compliment", 
        "positive",
        "Tu as un sourire incroyable!"
    )
    print(f"✓ Nouvelle intensité: {result['new_intensity']:.1%}")
    print(f"✓ Réciprocité estimée: {result['new_reciprocity']:.1%}")
    
    print("\n[3] Génération d'un message de flirt...")
    message = interface.get_flirt_message()
    print(f"Message: {message}")
    
    print("\n[4] Interaction 2: Confidence - Réponse mitigée")
    result = interface.interact(
        "confidence",
        "mixed",
        "Je peux te faire une confidence? Je pense souvent à toi."
    )
    print(f"✓ Signaux détectés: {len(result['signals_detected'])}")
    
    print("\n[5] Poésie romantique...")
    poem = interface.get_love_poetry()
    print(poem)
    
    print("\n[6] Analyse de compatibilité...")
    other_profile = {
        "primary_state": "amour_romantique",
        "attachment_style": "secure",
        "intensity": 0.7
    }
    compat = interface.analyze_compatibility(other_profile)
    print(f"Compatibilité globale: {compat['overall_compatibility']:.1%}")
    if compat.get('strengths'):
        print(f"Forces: {', '.join(compat['strengths'])}")
    
    print("\n[7] Résumé émotionnel...")
    print(interface.get_emotional_summary())
    
    print("\n[8] Rapport de session...")
    report = interface.get_session_report()
    print(f"Interactions enregistrées: {len(report['session_log'])}")
    print(f"Souvenirs créés: {report['memories_count']}")
    
    print("\n" + "=" * 70)
    print("DÉMONSTRATION TERMINÉE AVEC SUCCÈS ✓")
    print("=" * 70)
    
    return interface


if __name__ == "__main__":
    demo_interface = demo_love_engine()
    
    # Sauvegarde du rapport
    report = demo_interface.get_session_report()
    os.makedirs("logs", exist_ok=True)
    with open("logs/love_demo_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nRapport sauvegardé dans: logs/love_demo_report.json")
