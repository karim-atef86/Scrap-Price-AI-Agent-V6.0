# 🏗️ Steel Scrap Price Intelligence Agent (V6.0)

An Industrial AI Multi-Agent System designed to forecast Global Steel Scrap prices (CFR Turkey) with high precision (MAE: $4.54).

## 🌟 Overview
In the high-volatility steel industry, timing the purchase of raw materials is worth millions. This project replaces manual market analysis with an **Autonomous AI Crew** that fetches real-time global data, runs a custom-trained **XGBoost** predictive model, and generates strategic buying recommendations.

## 🧠 System Architecture (Multi-Agent Crew)
The system uses **CrewAI** to orchestrate three specialized agents:
1.  **Market Data Scout:** Automates data harvesting from SteelOrbis, Investing.com, and Yahoo Finance.
2.  **Quantitative Analyst:** Processes raw data and executes the **XGBoost V6.0** model to generate a numeric forecast.
3.  **Chief Market Strategist:** Correlates the prediction with global news (Energy, China demand, Logistics) to provide a final "Buy or Wait" decision.

## 🛠️ Technical Stack
- **AI Framework:** CrewAI, LangChain.
- **LLM:** Google Gemini 2.5 (Optimized for Tool Calling).
- **Machine Learning:** XGBoost (Regression Model).
- **Data Source:** Tavily AI (Real-time Web Search), Yahoo Finance.
- **Backend:** Python.

## 📊 Performance
- **Target:** CFR Turkey Steel Scrap Price (7-day forecast).
- **Accuracy:** Mean Absolute Error (MAE) of **$4.54**.
- **Features:** Scrap/Iron Ratio, Seasonality (Month/Day), Energy Indices, and Historical Lags.

## 📩 Output
The system generates a professional **RTL HTML Dashboard** sent via email to stakeholders, ensuring they receive actionable insights before market shifts.