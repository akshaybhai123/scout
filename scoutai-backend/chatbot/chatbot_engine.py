"""
ScoutAI — Chatbot Engine
Intent detection + knowledge-base-powered response generation.
Supports diet queries and sport-specific training guidance.
"""

import os
import json
import re
from typing import Optional, List, Dict, Any
from db.database import SessionLocal, Athlete, AnalysisResult, AnalysisJob

# ---------------------------------------------------------------------------
# Load knowledge bases
# ---------------------------------------------------------------------------
KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")


def _load_json(filename):
    path = os.path.join(KB_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


DIET_KB = _load_json("diet_plans.json")
SPORTS_KB = _load_json("sports_training.json")

SUPPORTED_SPORTS = list(SPORTS_KB.keys())

# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------
INTENT_PATTERNS = {
    "diet_query": [
        r"\b(diet|eat|food|meal|nutrition|calorie|protein|carb|hydrat|drink|supplement|weight|bulk|cut)\b",
    ],
    "training_tip": [
        r"\b(drill|train|practice|technique|form|improve|tip|skill|exercise|workout|session)\b",
    ],
    "injury_prevention": [
        r"\b(injur|prevent|pain|sore|stretch|warm.up|cool.down|rehab|recovery|physiotherapy)\b",
    ],
    "performance_analysis": [
        r"\b(performance|analysis|video|score|grade|stat|result|how did i do|my progress|assessment)\b",
    ],
    "comparison_query": [
        r"\b(compare|versus|vs|better than|difference between|who is better)\b",
    ],
    "general_faq": [
        r"\b(how|what|when|why|best|recommend|suggest|help|advice|guide)\b",
    ],
}


def detect_intent(message: str) -> str:
    """Detect the user's intent from their message."""
    msg_lower = message.lower()

    # Check each category in priority order
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, msg_lower):
                return intent

    return "general_faq"


def detect_sport(message: str, default_sport: Optional[str] = None) -> Optional[str]:
    """Detect which sport the user is asking about."""
    msg_lower = message.lower()
    for sport in SUPPORTED_SPORTS:
        if sport in msg_lower:
            return sport
    return default_sport


def _get_diet_response(message: str, sport: Optional[str]) -> dict:
    """Generate a diet-related response."""
    msg_lower = message.lower()

    # Check for sport-specific diet advice
    if sport and sport in DIET_KB.get("sport_specific", {}):
        sport_diet = DIET_KB["sport_specific"][sport]
        if any(w in msg_lower for w in ["match", "game", "competition", "before match"]):
            return {
                "reply": f"**{sport.title()} Match Day Nutrition:**\n\n{sport_diet.get('match_day', 'No specific advice available.')}",
                "suggestions": ["Training nutrition", "Supplements", "Hydration tips"],
            }
        elif any(w in msg_lower for w in ["supplement", "vitamin"]):
            return {
                "reply": f"**{sport.title()} Supplements:**\n\n{sport_diet.get('supplements', 'Consult a sports nutritionist.')}",
                "suggestions": ["Match day diet", "Training nutrition", "Hydration"],
            }
        else:
            return {
                "reply": f"**{sport.title()} Training Nutrition:**\n\n{sport_diet.get('training', 'Focus on balanced nutrition.')}",
                "suggestions": ["Match day diet", "Supplements", "Recovery nutrition"],
            }

    # General diet advice
    general = DIET_KB.get("general", {})
    if any(w in msg_lower for w in ["before", "pre", "pre-training", "pre-workout"]):
        info = general.get("pre_training", {})
    elif any(w in msg_lower for w in ["after", "post", "recovery", "post-training"]):
        info = general.get("post_training", {})
    elif any(w in msg_lower for w in ["hydrat", "water", "drink"]):
        info = general.get("hydration", {})
    elif any(w in msg_lower for w in ["muscle", "bulk", "gain", "mass"]):
        info = general.get("muscle_building", {})
    elif any(w in msg_lower for w in ["weight", "cut", "lose", "fat"]):
        info = general.get("weight_management", {})
    else:
        info = general.get("pre_training", {})

    reply = f"**{info.get('title', 'Nutrition Advice')}:**\n\n{info.get('advice', '')}"
    tips = info.get("tips", [])
    if tips:
        reply += "\n\n**Tips:**\n" + "\n".join(f"• {t}" for t in tips)

    return {
        "reply": reply,
        "suggestions": ["Post-training nutrition", "Hydration", "Supplements"],
    }


def _get_training_response(message: str, sport: Optional[str]) -> dict:
    """Generate a training-related response."""
    if not sport or sport not in SPORTS_KB:
        available = ", ".join(s.title() for s in SUPPORTED_SPORTS)
        return {
            "reply": f"I can provide training tips for: **{available}**.\n\nPlease specify your sport or select one from the list!",
            "suggestions": [f"{s.title()} tips" for s in SUPPORTED_SPORTS[:4]],
        }

    sport_data = SPORTS_KB[sport]
    msg_lower = message.lower()

    # Find the most relevant skill category
    best_category = None
    for category in sport_data:
        if category == "injury_prevention":
            continue
        if category in msg_lower or any(w in msg_lower for w in category.split("_")):
            best_category = category
            break

    if not best_category:
        # Pick the first skill category
        categories = [k for k in sport_data if k != "injury_prevention"]
        best_category = categories[0] if categories else None

    if best_category and isinstance(sport_data[best_category], dict):
        cat_data = sport_data[best_category]
        drills = cat_data.get("drills", [])
        tips = cat_data.get("tips", [])

        reply = f"**{sport.title()} — {best_category.replace('_', ' ').title()}:**\n\n"
        if drills:
            reply += "**Drills:**\n" + "\n".join(f"• {d}" for d in drills[:4]) + "\n\n"
        if tips:
            reply += "**Tips:**\n" + "\n".join(f"• {t}" for t in tips[:4])

        other_cats = [k for k in sport_data if k != best_category and k != "injury_prevention"]
        suggestions = [f"{sport.title()} {c.replace('_', ' ')}" for c in other_cats[:3]]
        suggestions.append("Injury prevention")

        return {"reply": reply, "suggestions": suggestions}

    return {
        "reply": f"I have training resources for {sport.title()}. What specific skill would you like help with?",
        "suggestions": [k.replace("_", " ").title() for k in sport_data if k != "injury_prevention"],
    }


def _get_injury_response(message: str, sport: Optional[str]) -> dict:
    """Generate an injury prevention response."""
    if sport and sport in SPORTS_KB:
        prevention = SPORTS_KB[sport].get("injury_prevention", [])
        if prevention:
            reply = f"**{sport.title()} — Injury Prevention:**\n\n"
            reply += "\n".join(f"• {tip}" for tip in prevention)
            return {
                "reply": reply,
                "suggestions": [f"{sport.title()} drills", "Diet advice", "Recovery nutrition"],
            }

    return {
        "reply": "**General Injury Prevention Tips:**\n\n"
                 "• Always warm up for 10-15 minutes before training\n"
                 "• Cool down and stretch after every session\n"
                 "• Don't increase training volume by more than 10% per week\n"
                 "• Listen to your body — pain is a warning signal\n"
                 "• Get adequate sleep (8+ hours) for recovery\n"
                 "• Stay hydrated throughout training and competition",
        "suggestions": ["Sport-specific prevention", "Recovery nutrition", "Training tips"],
    }


# ---------------------------------------------------------------------------
# Main chatbot interface
# ---------------------------------------------------------------------------

class ChatbotEngine:

    def get_response(self, message: str, sport: Optional[str] = None, 
                     athlete_id: Optional[int] = None,
                     athlete_profile: Optional[dict] = None) -> dict:
        """
        Process a user message and return a response.
        
        Args:
            message: The user's message.
            sport: Optional sport context.
            athlete_id: Optional ID to fetch performance data.
            athlete_profile: Optional athlete data for personalization.
        
        Returns:
            dict with 'reply', 'category', and 'suggestions'.
        """
        # Detect intent and sport
        intent = detect_intent(message)
        detected_sport = detect_sport(message, sport)

        # Route to appropriate handler
        if intent == "diet_query":
            result = _get_diet_response(message, detected_sport)
        elif intent == "training_tip":
            result = _get_training_response(message, detected_sport)
        elif intent == "comparison_query":
            result = self._get_comparison_response(message, detected_sport)
        elif intent == "performance_analysis":
            result = self._get_performance_response(message, detected_sport, athlete_id)
        elif intent == "injury_prevention":
            result = _get_injury_response(message, detected_sport)
        else:
            # General greeting / FAQ
            result = self._handle_general(message, detected_sport)

        result["category"] = intent
        return result

    def _handle_general(self, message: str, sport: Optional[str]) -> dict:
        msg_lower = message.lower()

        if any(w in msg_lower for w in ["hi", "hello", "hey", "good morning", "good evening"]):
            return {
                "reply": "Hey there! 👋 I'm your **ScoutAI Assistant**.\n\n"
                         "I can help you with:\n"
                         "🍎 **Diet & Nutrition** — meal plans, hydration, supplements\n"
                         "🏋️ **Training Tips** — sport-specific drills and techniques\n"
                         "🩹 **Injury Prevention** — stay healthy and avoid setbacks\n\n"
                         "What would you like to know?",
                "suggestions": ["Diet plan", "Training tips", "Injury prevention"],
            }

        available = ", ".join(s.title() for s in SUPPORTED_SPORTS)
        return {
            "reply": f"I can help with diet, training, and injury prevention for these sports: **{available}**.\n\n"
                     "Try asking:\n"
                     "• *What should I eat before a cricket match?*\n"
                     "• *How can I improve my smash in badminton?*\n"
                     "• *What are injury prevention tips for basketball?*",
            "suggestions": ["Diet advice", "Training drills", "Injury prevention"],
        }

    def _get_performance_response(self, message: str, sport: Optional[str], athlete_id: Optional[int]) -> dict:
        """Generate a response based on the athlete's actual performance data."""
        if not athlete_id:
            return {
                "reply": "I'd love to analyze your performance! Please make sure you are logged in so I can access your data.",
                "suggestions": ["How do I upload?", "Supported sports"],
            }

        db = SessionLocal()
        try:
            # Find the latest completed job with a result
            job = (
                db.query(AnalysisJob)
                .join(AnalysisResult)
                .filter(AnalysisJob.athlete_id == athlete_id)
                .filter(AnalysisJob.status == "complete")
                .order_by(AnalysisJob.created_at.desc())
                .first()
            )

            if not job or not job.result:
                return {
                    "reply": "I don't see any video assessments in your profile yet. 📹\n\nTo get personalized analytics, go to the **Upload** page and submit a video of your performance!",
                    "suggestions": ["Upload video", "What videos work best?"],
                }

            res = job.result
            metrics = json.loads(res.metrics_json) if res.metrics_json else {}
            
            reply = f"### 📊 Your Performance Analysis\n\n"
            reply += f"Based on your latest **{job.sport.title()}** video, your talent score is **{res.talent_score}/100**, placing you in the **{res.grade}** category.\n\n"
            
            # Identify strengths and weaknesses
            if metrics:
                sorted_metrics = sorted(metrics.items(), key=lambda x: x[1], reverse=True)
                top_metric, top_val = sorted_metrics[0]
                bottom_metric, bottom_val = sorted_metrics[-1]

                reply += f"🌟 **Top Strength:** Your *{top_metric.replace('_', ' ')}* is impressive at **{top_val}**.\n"
                reply += f"📉 **Area for Growth:** We noticed your *{bottom_metric.replace('_', ' ')}* (**{bottom_val}**) could use some improvement.\n\n"

                # Provide a quick tip based on the bottom metric
                sport_tips = SPORTS_KB.get(job.sport, {})
                for cat, data in sport_tips.items():
                    if isinstance(data, dict) and (bottom_metric in cat or cat in bottom_metric):
                        tip = data.get("tips", ["Focus on consistent reps and proper form."])[0]
                        reply += f"💡 **Pro Tip:** To improve your {bottom_metric.replace('_', ' ')}, try this: *{tip}*\n\n"
                        break
            
            reply += "Would you like me to suggest a specific training drill or a diet plan to help you level up?"
            
            return {
                "reply": reply,
                "suggestions": ["Training drills", "Diet plan", "Download full report"],
            }
        except Exception as e:
            print(f"Error in performance analysis: {str(e)}")
            return {
                "reply": "I encountered an error while analyzing your performance data. Please try again later.",
                "suggestions": ["Dashboard", "Support"],
            }
        finally:
            db.close()

    def _get_comparison_response(self, message: str, sport: Optional[str]) -> dict:
        """Handle queries comparing two or more athletes."""
        # Extract potential IDs or names
        ids = re.findall(r"#?(\d+)", message)
        
        if len(ids) < 2:
            return {
                "reply": "To compare athletes, please provide at least two Athlete IDs (e.g., 'Compare athlete 1 and 2').",
                "suggestions": ["View leaderboard", "How to find IDs?"],
            }

        db = SessionLocal()
        try:
            results = []
            for aid in ids[:2]:
                ath = db.query(Athlete).filter(Athlete.id == int(aid)).first()
                if ath:
                    job = db.query(AnalysisJob).join(AnalysisResult).filter(AnalysisJob.athlete_id == ath.id).order_by(AnalysisJob.created_at.desc()).first()
                    if job and job.result:
                        results.append((ath, job.result))
            
            if len(results) < 2:
                return {
                    "reply": f"I couldn't find enough completed assessments for IDs: {', '.join(ids[:2])}. Make sure they have uploaded videos!",
                    "suggestions": ["View leaderboard", "Check athlete profile"],
                }

            a1, r1 = results[0]
            a2, r2 = results[1]
            
            diff = abs(r1.talent_score - r2.talent_score)
            leader = a1.name if r1.talent_score > r2.talent_score else a2.name
            
            reply = f"### ⚔️ Athlete Comparison: {a1.name} vs {a2.name}\n\n"
            reply += f"🏆 **Overall Leader:** {leader} (Difference: **{diff:.1f}** points)\n\n"
            reply += f"| Metric | {a1.name} | {a2.name} |\n"
            reply += f"| :--- | :--- | :--- |\n"
            reply += f"| Talent Score | {r1.talent_score} | {r2.talent_score} |\n"
            reply += f"| Grade | {r1.grade} | {r2.grade} |\n"
            
            # Simple metric comparison
            m1 = json.loads(r1.metrics_json) if r1.metrics_json else {}
            m2 = json.loads(r2.metrics_json) if r2.metrics_json else {}
            
            common_metrics = set(m1.keys()) & set(m2.keys())
            for m in list(common_metrics)[:3]:
                reply += f"| {m.replace('_', ' ').title()} | {m1[m]} | {m2[m]} |\n"
            
            reply += f"\n**Analysis:** {leader} shows higher technical efficiency in this {sport or 'multi-sport'} comparison."
            
            return {
                "reply": reply,
                "suggestions": ["Show detailed metrics", "View Comparison Page"],
            }
        except Exception as e:
            print(f"Error in comparison: {str(e)}")
            return {
                "reply": "I couldn't complete the comparison due to a technical error.",
                "suggestions": ["Leaderboard", "Support"],
            }
        finally:
            db.close()

    @staticmethod
    def get_supported_sports():
        """Return list of supported sports with their available topics."""
        sports_info = {}
        for sport in SUPPORTED_SPORTS:
            topics = list(SPORTS_KB.get(sport, {}).keys())
            sports_info[sport] = {
                "name": sport.title(),
                "topics": [t.replace("_", " ").title() for t in topics],
            }
        return sports_info
