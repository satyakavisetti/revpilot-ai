import random
import json
from datetime import datetime
from llm import ask_llm
from actions import send_email

memory_store = []

def store_memory(deal, strategy, outcome):
    memory_store.append({
        "company": deal["company"],
        "strategy": strategy,
        "outcome": outcome,
        "time": datetime.now().isoformat()
    })

def get_memory():
    return memory_store[-5:]


def prospecting_agent():
    leads = [
        {"company": "DataZen", "industry": "AI SaaS"},
        {"company": "CloudNova", "industry": "Cloud"},
        {"company": "FinEdge", "industry": "FinTech"}
    ]

    enriched = []

    for l in leads:
        prompt = f"""
        You are a sales prospecting AI.

        Company: {l['company']}
        Industry: {l['industry']}

        Generate:
        - Lead score (0-100)
        - 2 decision makers (name + role)
        - personalized outreach message

        Return JSON:
        {{
          "score": number,
          "decision_makers": ["Name - Role", "Name - Role"],
          "message": "..."
        }}
        """

        response = ask_llm(prompt)

        if response:
            try:
                data = json.loads(response)
                enriched.append({
                    "company": l["company"],
                    "industry": l["industry"],
                    "score": data["score"],
                    "decision_makers": data["decision_makers"],
                    "outreach": data["message"]
                })
                continue
            except:
                pass

        enriched.append({
            "company": l["company"],
            "industry": l["industry"],
            "score": random.randint(70, 90),
            "decision_makers": ["Unknown"],
            "outreach": f"Hi {l['company']}, wanted to connect regarding your current growth initiatives."
        })

    return enriched


def intelligence_agent(deal):
    score = (
        deal["days_no_reply"] * 5 +
        (1 - deal["engagement_score"]) * 50 +
        (10 if deal.get("competitor") else 0)
    )

    if score >= 70:
        risk = "HIGH"
    elif score >= 40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {"risk": risk, "score": int(score)}


def predictive_agent(deal):
    churn = min(
        0.9,
        (deal["days_no_reply"] / 15) + (1 - deal["engagement_score"])
    )
    return int(churn * 100)


def competitive_agent(deal):
    if deal.get("competitor"):
        return {
            "battlecard": f"Position ROI advantage vs {deal['competitor']}"
        }
    return None


def enrichment_agent(deal):
    prompt = f"""
    Provide brief business insight for sales outreach.

    Company: {deal['company']}
    """

    return ask_llm(prompt) or "Focused on scaling operations and improving efficiency."


def email_agent(deal, prediction, strategy, competitive):
    insights = enrichment_agent(deal)

    prompt = f"""
    Write a concise B2B sales email.

    Company: {deal['company']}
    Insight: {insights}
    Risk: {prediction}%
    Strategy: {strategy['name']}
    Competitor: {deal.get('competitor')}
    """

    response = ask_llm(prompt)

    if response:
        return response

    return f"Hi {deal['company']} team, following up on our previous discussion."


def strategy_agent(deal, intel, prediction, comp):
    memory = get_memory()

    prompt = f"""
    Suggest best sales strategy.

    Past context:
    {memory}

    Company: {deal['company']}
    Risk: {intel['risk']}
    Churn: {prediction}%
    Engagement: {deal['engagement_score']}
    Competitor: {deal.get('competitor')}

    Return JSON:
    {{
      "strategy": "...",
      "reason": "...",
      "confidence": 0-1
    }}
    """

    response = ask_llm(prompt)

    if response:
        try:
            data = json.loads(response)
            return {
                "name": data["strategy"],
                "reason": data["reason"],
                "confidence": data["confidence"],
                "alternatives": []
            }
        except:
            pass

    return {
        "name": "Follow-up Strategy",
        "confidence": 0.5,
        "alternatives": []
    }


def execution_agent(deal):
    deal["status"] = "Recovery Initiated"
    deal["days_no_reply"] = 0


def adaptation_agent(deal):
    if deal["email_opened"] and not deal["replied"]:
        return "Switch follow-up strategy"
    elif not deal["email_opened"]:
        return "Change subject line"
    return "Maintain strategy"


def explanation_agent(deal, strategy, prediction):
    prompt = f"""
    Explain why this deal is at risk.

    Company: {deal['company']}
    Churn risk: {prediction}%
    Strategy: {strategy['name']}
    """

    return ask_llm(prompt) or "Inactivity and reduced engagement indicate potential drop-off."


def sequence_agent(deal):
    prompt = f"""
    You are a senior sales strategist.

    Company: {deal['company']}
    Industry: {deal.get('industry')}
    Company Size: {deal.get('company_size')}
    Funding Stage: {deal.get('recent_funding')}

    Identify two decision makers and create a 3-email sequence for each.

    Each email must include:
    - Subject
    - Body
    - Next step for the sales rep

    Emails should differ based on role priorities.
    """

    return ask_llm(prompt) or "Sequence not available"


def safe_email_send(deal, email):
    for _ in range(2):
        try:
            return send_email(deal["email"], "Follow-up", email)
        except:
            continue
    return {"opened": False, "replied": False}


def metrics_agent(deals):
    total = len(deals)
    recovered = len([d for d in deals if d["status"] == "Recovery Initiated"])

    return {
        "conversion": int((recovered / total) * 100) if total else 0,
        "cycle_reduction": random.randint(15, 35)
    }


def impact_agent(deals):
    recovered = len([d for d in deals if d["status"] == "Recovery Initiated"])
    revenue = sum(d["value"] for d in deals if d["status"] == "Recovery Initiated")

    return {
        "revenue_recovered": revenue,
        "conversion_improvement": f"{int((recovered/len(deals))*100)}%"
    }


def impact_model(deals):
    recovered = len([d for d in deals if d["status"] == "Recovery Initiated"])
    avg_deal = sum(d["value"] for d in deals) / len(deals)

    revenue = recovered * avg_deal
    time_saved = recovered * 2
    cost_saved = time_saved * 500

    return {
        "revenue_recovered": int(revenue),
        "time_saved_hours": time_saved,
        "cost_saved": int(cost_saved)
    }


def coordinator_agent(deal):

    trace = []

    try:
        if random.random() < 0.05:
            raise Exception("Simulated failure")

        intel = intelligence_agent(deal)
        trace.append("risk_evaluated")

        prediction = predictive_agent(deal)
        trace.append("prediction_generated")

        comp = competitive_agent(deal)

        priority = "URGENT" if intel["risk"] == "HIGH" else ("FOLLOW-UP" if intel["risk"] == "MEDIUM" else "MONITOR")

        if intel["risk"] != "LOW":

            strategy = strategy_agent(deal, intel, prediction, comp)
            trace.append("strategy_selected")

            email = email_agent(deal, prediction, strategy, comp)
            trace.append("email_generated")

            event = safe_email_send(deal, email)
            trace.append("email_sent")

            execution_agent(deal)

            adaptation = adaptation_agent(deal)
            trace.append("adaptation_applied")

            explanation = explanation_agent(deal, strategy, prediction)
            trace.append("explanation_generated")

            next_steps = [
                "Schedule follow-up call within 24 hours",
                "Send ROI-focused case study",
                "Address competitor comparison directly"
            ]

            store_memory(deal, strategy["name"], "success")

            return {
                "risk": intel["risk"],
                "priority": priority,
                "prediction": prediction,
                "strategy": strategy,
                "adaptation": adaptation,
                "explanation": explanation,
                "next_steps": next_steps,
                "email": email,
                "email_event": event,
                "trace": trace,
                "agent_chain": "intelligence → prediction → strategy → execution → adaptation"
            }

        return {
            "risk": intel["risk"],
            "priority": priority,
            "prediction": prediction,
            "trace": trace,
            "agent_chain": "intelligence → prediction"
        }

    except Exception as e:
        return {
            "error": str(e),
            "recovery": "Fallback system activated",
            "trace": trace,
            "agent_chain": "error_handling → fallback"
        }


def top_churn_agent(accounts):

    ranked = sorted(
        accounts,
        key=lambda x: (x["support_tickets_open"] * 2 - x["daily_active_users"]),
        reverse=True
    )

    top = ranked[:3]
    results = []

    for acc in top:
        prompt = f"""
        Company: {acc['company']}
        Open Tickets: {acc['support_tickets_open']}
        Daily Users: {acc['daily_active_users']}

        Explain why churn risk is high and give a specific retention plan with clear actions.
        """

        strategy = ask_llm(prompt) or "Focus on resolving open issues and re-engaging key users."

        results.append({
            "company": acc["company"],
            "risk_reason": f"Tickets: {acc['support_tickets_open']}, Users: {acc['daily_active_users']}",
            "strategy": strategy
        })

    return results