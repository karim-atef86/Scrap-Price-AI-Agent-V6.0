import os
import json
import pandas as pd
import xgboost as xgb
import smtplib
from datetime import datetime
from crewai.tools import BaseTool
from tavily import TavilyClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


# --- 1. أداة البحث ---
class InternetSearchTool(BaseTool):
    name: str = "internet_search_tool"
    description: str = "Search the internet for real-time (Feb 2026) steel scrap prices, iron ore prices, and market news."

    def _run(self, query: str) -> str:
        from datetime import datetime
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        current_context = datetime.now().strftime('%B %Y')
        enhanced_query = f"{query} {current_context} latest price"

        return str(tavily.search(query=enhanced_query, search_depth="advanced"))


# --- 2. أداة التنبؤ المطورة ---
class PredictScrapPriceTool(BaseTool):
    name: str = "predict_scrap_price"
    description: str = "Input: JSON string containing market values. Output: Predicted scrap price for next week."

    def _run(self, market_data_json: str) -> str:
        try:
            # تنظيف وتحميل الـ JSON
            clean_json = market_data_json.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)

            def get_v(primary, aliases):
                flat_data = {}
                for k, v in data.items():
                    if isinstance(v, dict):
                        for inner_k, inner_v in v.items():
                            flat_data[inner_k] = inner_v
                    else:
                        flat_data[k] = v

                for key in [primary] + aliases:
                    for k in flat_data.keys():
                        if key.lower() in k.lower():
                            return float(flat_data[k])
                return 0.0

            scrap = get_v('Scrap_Price', ['Today', 'now', 'CFR'])
            iron = get_v('Iron_Ore_Price', ['Iron', '62%'])

            if scrap < 300 or scrap > 450:
                return f"ERROR: The scrap price found (${scrap}) seems incorrect for Feb 2026. Please find the REAL CFR Turkey price (usually $370-$385) and retry."

            input_dict = {
                'Scrap_Price': scrap,
                'Iron_Ore_Price': iron,
                'Brent_Oil': get_v('Brent_Oil', ['Brent', 'Oil']),
                'Natural_Gas': get_v('Natural_Gas', ['Gas', 'HH']),
                'USD_TRY': get_v('USD_TRY', ['TRY', 'Lira']),
                'Scrap_MA_7': get_v('Scrap_MA_7', ['Avg', 'Average']),
                'Scrap_Iron_Ratio': scrap / iron if iron != 0 else 3.5,
                'Scrap_Lag_7': get_v('Scrap_Lag_7', ['7D', 'ago']),
                'Iron_Lag_7': get_v('Iron_Lag_7', ['Iron_7D']),
                'Month': datetime.now().month,
                'DayOfWeek': datetime.now().weekday()
            }

            if input_dict['Scrap_MA_7'] == 0:
                input_dict['Scrap_MA_7'] = scrap

            bst = xgb.Booster()
            bst.load_model('scrap_price_model.json')

            feature_names = ['Scrap_Price', 'Iron_Ore_Price', 'Brent_Oil', 'Natural_Gas', 'USD_TRY',
                             'Scrap_MA_7', 'Scrap_Iron_Ratio', 'Scrap_Lag_7', 'Iron_Lag_7', 'Month', 'DayOfWeek']

            df = pd.DataFrame([input_dict], columns=feature_names)
            prediction = bst.predict(xgb.DMatrix(df))[0]

            return f"SUCCESS: Next week forecast is ${float(prediction):.2f}"

        except Exception as e:
            return f"Error processing data: {str(e)}. Please provide data in a flat JSON format."


# --- 3. أداة إرسال الإيميل  ---
class SendEmailTool(BaseTool):
    name: str = "send_email_tool"
    description: str = "Sends the final Arabic report to management via email."

    def _run(self, report_content: str) -> str:
        import os, smtplib, re
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.header import Header
        from datetime import datetime

        sender = os.getenv("EMAIL_SENDER")
        receiver = os.getenv("EMAIL_RECEIVER")
        password = os.getenv("EMAIL_PASSWORD")

        def extract_val(pattern, text):
            match = re.search(pattern, text)
            return match.group(1).strip() if match else "N/A"

        scrap_now = extract_val(r"السعر الحالي:\s*(.*?)(?:\n|$)", report_content)
        prediction = extract_val(r"التوقع الرقمي:\s*(.*?)(?:\n|$)", report_content)
        status = extract_val(r"الاتجاه:\s*(.*?)(?:\n|$)", report_content)
        iron = extract_val(r"الخام:\s*(.*?)(?:\n|$)", report_content)
        oil = extract_val(r"البترول:\s*(.*?)(?:\n|$)", report_content)
        gas = extract_val(r"الغاز:\s*(.*?)(?:\n|$)", report_content)
        try_rate = extract_val(r"الليرة:\s*(.*?)(?:\n|$)", report_content)
        recommendation = extract_val(r"التوصية:\s*(.*?)(?:\n|$)", report_content)

        theme_color = "#e74c3c" if "أقل" in status or "هبوط" in status else "#27ae60"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = Header(f"📊 تقرير أسعار الخردة الاستراتيجي - {datetime.now().strftime('%d/%m/%Y')}",
                                'utf-8').encode()

        html_template = f"""
        <html>
          <body dir="rtl" style="font-family: 'Tahoma', 'Arial', sans-serif; background-color: #f9f9f9; padding: 20px; margin: 0;">
            <div style="max-width: 800px; margin: auto; background: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">

              <div style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 20px;">
                <h1 style="color: #1a2a6c; margin: 0; font-size: 26px;">تقرير اسعار الخردة - حديد المصريين</h1>
                <p style="color: #666; font-size: 14px; margin: 5px 0;">تاريخ التقرير: {datetime.now().strftime('%Y/%m/%d')}</p>
              </div>

              <!-- Dashboard Table -->
              <table width="100%" style="margin-bottom: 20px; text-align: center; border-collapse: collapse;">
                <tr>
                  <td width="50%" style="padding: 15px; border-left: 1px solid #eee;">
                    <span style="color: #888; font-size: 14px;">توقع الأسبوع القادم</span><br>
                    <span style="font-size: 32px; font-weight: bold; color: {theme_color};">{prediction}</span>
                  </td>
                  <td width="50%" style="padding: 15px;">
                    <span style="color: #888; font-size: 14px;">السعر الحالي</span><br>
                    <span style="font-size: 32px; font-weight: bold; color: #1a2a6c;">{scrap_now}</span>
                  </td>
                </tr>
              </table>

              <div style="text-align: center; font-size: 18px; font-weight: bold; color: {theme_color}; margin-bottom: 25px;">
                الاتجاه المتوقع: {status}
              </div>

              <!-- Indicators Table -->
              <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h3 style="margin-top: 0; font-size: 16px; color: #1a2a6c; border-bottom: 2px solid #1a2a6c; display: inline-block; padding-bottom: 3px;">المؤشرات العالمية المكتشفة</h3>
                <table width="100%" style="font-size: 15px; line-height: 2;">
                  <tr><td>• سعر خام الحديد (62%):</td><td style="text-align: left; font-weight: bold;">{iron}</td></tr>
                  <tr><td>• سعر خام برنت (نفط):</td><td style="text-align: left; font-weight: bold;">{oil}</td></tr>
                  <tr><td>• سعر الغاز الطبيعي:</td><td style="text-align: left; font-weight: bold;">{gas}</td></tr>
                  <tr><td>• سعر الليرة التركية:</td><td style="text-align: left; font-weight: bold;">{try_rate}</td></tr>
                </table>
              </div>

              <!-- Strategic Analysis -->
              <div style="margin-top: 25px; padding: 15px; border-right: 5px solid #1a2a6c; background: #fafafa;">
                <h3 style="margin-top: 0; color: #1a2a6c;">التحليل الاستراتيجي:</h3>
                <div style="font-size: 15px; line-height: 1.6; color: #444;">
                    {report_content}
                </div>
              </div>

              <!-- Recommendation Bar -->
              <div style="margin-top: 25px; background: {theme_color}; color: white; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; border-radius: 5px;">
                التوصية: {recommendation}
              </div>

              <div style="margin-top: 20px; text-align: center; font-size: 12px; color: #999;">
                تم إصدار هذا التقرير آلياً بواسطة نظام التنبؤ الرقمي (V6.0).
              </div>
            </div>
          </body>
        </html>
        """

        msg.attach(MIMEText(html_template, 'html', 'utf-8'))
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
            return "✅ تم إرسال التقرير بنجاح بصيغة الـ Dashboard الأصلية."
        except Exception as e:
            return f"❌ فشل الإرسال: {str(e)}"