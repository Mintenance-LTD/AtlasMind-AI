from core.runtime import agent_app

from agents.country_risk.agent import CountryRiskAgent

app = agent_app(CountryRiskAgent())
