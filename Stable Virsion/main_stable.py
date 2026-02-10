import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

# منع التوجه لـ OpenAI افتراضياً
os.environ["OPENAI_API_KEY"] = "NA"

from crewai import Crew, Process
from agents import ScrapAgents
from tasks import ScrapTasks

# 1. البدء
agents = ScrapAgents()
tasks = ScrapTasks()

scout = agents.data_scout_agent()
analyst = agents.ml_analyst_agent()
strategist = agents.market_strategist_agent()

today_date = datetime.now().strftime('%d %B %Y')
task1 = tasks.harvest_data_task(scout, today_date)
task2 = tasks.technical_prediction_task(analyst)
task3 = tasks.final_report_task(strategist)

# 2. تكوين الفريق مع لجام RPM لحل مشكلة 429
scrap_crew = Crew(
    agents=[scout, analyst, strategist],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    max_rpm=2,
    verbose=True
)

print("🚀 جاري تشغيل المحلل الذكي...")
result = scrap_crew.kickoff()
print(result)