from core.runtime import agent_app

from agents.investment.agent import InvestmentAgent

app = agent_app(InvestmentAgent())
