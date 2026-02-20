# backend/utils/gen_insights.py
from sqlalchemy.orm import Session
from backend.database import Expense
from backend.utils.predict_category import is_recurring_transaction
from sqlalchemy import func
import plotly.graph_objects as go
import json
import plotly.utils

def generate_insights(db: Session, user_id: int, start_date, end_date):
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        func.date(Expense.timestamp) >= start_date,
        func.date(Expense.timestamp) <= end_date
    ).order_by(Expense.timestamp.asc()).all()

    total_spent = 0.0
    category_wise = {}
    daily_spending = {} # New: Daily totals tracker
    high_urgency_count = 0
    recurring_merchants = set() 

    for exp in expenses:
        total_spent += exp.amount
        
        # Category breakdown
        cat = exp.category or "uncategorized"
        category_wise[cat] = category_wise.get(cat, 0) + exp.amount

        # New: Daily spending calculation
        date_str = exp.timestamp.date().isoformat()
        daily_spending[date_str] = daily_spending.get(date_str, 0) + exp.amount

        if exp.urgency and exp.urgency.lower() == "critical":
            high_urgency_count += 1
        if is_recurring_transaction(db, user_id, exp.merchant_name):
            recurring_merchants.add(exp.merchant_name)

    # --- 1. DAILY SPENDING LINE CHART ---
    sorted_days = sorted(daily_spending.keys())
    sorted_vals = [daily_spending[d] for d in sorted_days]

    fig_line = go.Figure(data=[go.Scatter(
        x=sorted_days, y=sorted_vals,
        mode='lines+markers',
        line=dict(color='#4338CA', width=3),
        marker=dict(size=6, color='#6366F1'),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)'
    )])
    fig_line.update_layout(
        height=250, margin=dict(l=20, r=20, t=10, b=20),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', tickfont=dict(size=10))
    )

    # --- 2. CATEGORY BAR CHART ---
    color_map = {"red": "#EF4444", "orange": "#F97316", "yellow": "#EAB308"}
    cats = list(category_wise.keys())
    bar_colors = [color_map.get(c, "#4338CA") for c in cats]

    fig_bar = go.Figure(data=[go.Bar(x=cats, y=list(category_wise.values()), marker_color=bar_colors)])
    fig_bar.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # --- 3. DONUT CHART ---
    fig_pie = go.Figure(data=[go.Pie(labels=cats, values=list(category_wise.values()), hole=.6, marker=dict(colors=bar_colors))])
    fig_pie.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')

    return {
        "total_spent": round(total_spent, 2),
        "category_wise_spending": category_wise,
        "high_urgency_expenses": high_urgency_count,
        "distinct_recurring_merchants": len(recurring_merchants),
        "savings_warning": "High urgency detected!" if high_urgency_count > 3 else "Spending okay.",
        "daily_trend_plotly": json.dumps(fig_line, cls=plotly.utils.PlotlyJSONEncoder),
        "bar_chart_plotly": json.dumps(fig_bar, cls=plotly.utils.PlotlyJSONEncoder),
        "pie_chart_plotly": json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)
    }