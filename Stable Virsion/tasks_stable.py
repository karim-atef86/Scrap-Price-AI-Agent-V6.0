from crewai import Task

class ScrapTasks:
    def harvest_data_task(self, agent, current_date):  # استقبال التاريخ
        return Task(
            description=f"""
            1. ابحث عن أسعار اليوم لـ: (Scrap CFR Turkey, Iron Ore 62% Fe CFR China, Brent Oil, Natural Gas, USD/TRY).
            2. ابحث عن أسعار نفس العناصر منذ 7 أيام ومنذ 14 يوماً.

            🛡️ بروتوكول ضمان الحداثة التلقائي (Auto-Freshness Protocol):
            - تاريخ اليوم المرجعي هو: ({current_date}).
            - أي سعر تجده يجب أن يكون مرتبطاً بهذا التاريخ أو بحد أقصى 48 ساعة قبله.
            - ارفض تماماً أي نتائج بحث تظهر سنوات سابقة (2025, 2024, إلخ) إلا في حالة الـ Lags المطلوبة.
            - تأكد من أن سعر 'خام الحديد' (Iron Ore) مُحدث بتاريخ اليوم ({current_date}).

            3. أخرج البيانات في شكل JSON بـ 11 قيمة المطلوبة للموديل.
            """,
            expected_output="Verified JSON data based on the dynamic current date provided.",
            agent=agent
        )

    def technical_prediction_task(self, agent):
        return Task(
            description="Run the predict_scrap_price tool with the JSON data to get the forecast.",
            expected_output="The numeric forecast for next week.",
            agent=agent
        )

    def final_report_task(self, agent):
        return Task(
            description="""
            1. Analyze the prediction and news.
            2. Prepare the report for 'Egyptian Steel' strictly starting with these key values:
               السعر الحالي: [الرقم]
               التوقع الرقمي: [الرقم]
               الاتجاه: [أقل / أعلى]
               الخام: [الرقم]
               البترول: [الرقم]
               الغاز: [الرقم]
               الليرة: [الرقم]
               التوصية: [اكتب التوصية مع إيموجي مناسب]

            3. Then write a detailed strategic analysis explaining 'Why' based on global factors.
            4. Finally, call 'send_email_tool'.""",
            expected_output="A dashboard-style email sent with the strategic analysis.",
            agent=agent
        )