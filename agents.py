import os
from crewai import Agent, LLM
from tools import InternetSearchTool, PredictScrapPriceTool, SendEmailTool

class ScrapAgents:
    def __init__(self):
        self.gemini_llm = LLM(
            model="gemini/gemini-3-flash-preview", # الاسم المضمون عندك
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1
        )

    def data_scout_agent(self):
        return Agent(
            role='Market Data Scout',
            goal='Fetch exact numeric market values for Feb 2026.',
            backstory='Expert financial auditor. You only accept verified Feb 2026 data.',
            tools=[InternetSearchTool()],
            llm=self.gemini_llm,
            max_rpm=1,
            verbose=True
        )

    def ml_analyst_agent(self):
        return Agent(
            role='Quantitative Analyst',
            goal='Use the XGBoost model to get technical forecasts.',
            backstory='Data scientist specialized in XGBoost. You turn JSON into predictions.',
            tools=[PredictScrapPriceTool()],
            llm=self.gemini_llm,
            max_rpm=1,
            verbose=True
        )

    def market_strategist_agent(self):
        return Agent(
            role='Chief Market Strategist',
            goal='Synthesize data into a report and SEND it via email.',
            backstory='Steel industry veteran. You MUST use the send_email_tool to deliver the final report.',
            tools=[SendEmailTool()],
            llm=self.gemini_llm,
            max_rpm=1,
            verbose=True
        )