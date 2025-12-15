import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Forensic Alpha V10", layout="wide", page_icon="⚖️")

st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #e0e0e0;}
    .audit-box {
        background-color: #1a1c24; 
        border: 1px solid #333; 
        padding: 20px; 
        border-radius: 5px; 
        margin-bottom: 15px;
        text-align: center;
    }
    .metric-container {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #464b5d;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك التحليل الجنائي ---
def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price:
            # محاولة بديلة
            hist = stock.history(period='1d')
            if not hist.empty:
                price = hist['Close'].iloc[-1]
            else:
                return None, "❌ السعر غير متوفر."

        financials = stock.financials

        # البيانات الأساسية
        mkt_cap = info.get('marketCap', 0)
        total_cash = info.get('totalCash', 0) or 0
        total_debt = info.get('totalDebt', 0) or 0
        
        cash_percent = (total_cash / mkt_cap * 100) if mkt_cap else 0
        ev = mkt_cap - total_cash + total_debt

        # المؤشرات
        growth = (info.get('revenueGrowth', 0) or 0) * 100
        pe_fwd = info.get('forwardPE', 0) or 0
        ps_ratio = info.get('priceToSalesTrailing12Months', 0) or 0
        
        # الأخبار
        news_data = stock.news if hasattr(stock, 'news') else []

        data = {
            "Symbol": ticker,
            "Price": price,
            "MktCap": mkt_cap,
            "Cash": total_cash,
            "Debt": total_debt,
            "Cash_Percent": cash_percent,
            "EV": ev,
            "PE_Fwd": pe_fwd,
            "PS": ps_ratio,
            "Growth": growth,
            "News": news_data,
            "Financials": financials
        }
        return data, None

    except Exception as e:
        return None, f"خطأ: {str(e)}"

# --- 3. الواجهة ---
st.sidebar.title("🕵️‍♂️ المحقق الجنائي")
ticker = st.sidebar.text_input("رمز السهم", value="HITI").upper()
run = st.sidebar.button("تشغيل التدقيق")

if ticker:
    data, err = analyze_stock(ticker)
    
    if err:
        st.error(err)
    elif data:
        # === منطق الحكم (Matrix Logic) ===
        verdict = "🧩 HOLD / WATCH"
        v_color = "#b0b0b0"
        why_msg = "الشركة في المنطقة المحايدة."

        # القواعد الصارمة
        if data['Debt'] > (data['Cash'] * 3.5) and data['Cash'] > 0:
            verdict = "☠️ KILL SWITCH"
            v_color = "#ff2b2b"
            why_msg = "الديون خطرة (أكثر من 3.5x الكاش)."
        elif data['Growth'] > 15 and (data['PS'] < 1.5 or data['PE_Fwd'] < 15):
            verdict = "💎 SCRAP ELITE"
            v_color = "#00ff00"
            why_msg = "نمو ممتاز (>15%) بسعر رخيص."
        elif data['Cash_Percent'] > 30:
            verdict = "🧩 ASSET PLAY"
            v_color = "#ffd700"
            why_msg = f"بنك من المال ({data['Cash_Percent']:.1f}% كاش)."

        # عرض الصندوق الكبير
        st.markdown(f"""
        <div class="audit-box" style="border-color: {v_color}; box-shadow: 0 0 10px {v_color}40;">
            <h1 style="color: {v_color}; margin:0;">{verdict}</h1>
            <h3 style="margin-top:5px;">{data['Symbol']} • ${data['Price']:,.2f}</h3>
            <p style="color: #ccc;">{why_msg}</p>
        </div>
        """, unsafe_allow_html=True)

        # === الباب الأول: الأرقام الحقيقية (الديناميكية) ===
        st.markdown("## 📊 التحليل الرقمي المقارن")
        
        c1, c2, c3 = st.columns(3)
        
        # 1. تحليل الكاش (الهدف > 20%)
        with c1:
            cash_diff = data['Cash_Percent'] - 20
            st.metric(
                "نسبة الكاش (الهدف > 20%)", 
                f"{data['Cash_Percent']:.1f}%", 
                delta=f"{cash_diff:.1f}% فرق عن الهدف"
            )

        # 2. تحليل النمو (الهدف > 15%)
        with c2:
            growth_diff = data['Growth'] - 15
            st.metric(
                "النمو (الهدف > 15%)", 
                f"{data['Growth']:.1f}%", 
                delta=f"{growth_diff:.1f}% فرق عن الهدف"
            )

        # 3. تحليل السعر (الهدف P/E < 15) - معكوس (الأقل أفضل)
        with c3:
            # هنا نعكس المنطق: إذا كان المكرر 10 والهدف 15، الفرق 5 (إيجابي)
            pe_gap = 15 - data['PE_Fwd'] 
            st.metric(
                "مكرر الربحية (الهدف < 15x)", 
                f"{data['PE_Fwd']:.1f}x", 
                delta=f"{pe_gap:.1f} (هامش أمان)",
                delta_color="normal" # الأخضر يعني أرخص من الهدف
            )

        st.markdown("---")

        # === الرسم البياني ===
        c_chart, c_news = st.columns([2, 1])
        
        with c_chart:
            st.subheader("📈 مسار الإيرادات")
            try:
                fin = data['Financials']
                if not fin.empty and 'Total Revenue' in fin.index:
                    rev_hist = fin.loc['Total Revenue'].iloc[:4][::-1]
                    years = [d.strftime('%Y') for d in rev_hist.index]
                    values = list(rev_hist.values)
                    
                    fig = go.Figure(data=[go.Bar(x=years, y=values, marker_color='#1f77b4')])
                    fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("الرسم البياني غير متاح.")
            except:
                st.info("تعذر الرسم.")

        # === الأخبار ===
        with c_news:
            st.subheader("📰 الأخبار")
            if data['News']:
                for n in data['News']:
                    title = n.get('title', 'No Title')
                    link = n.get('link', '#')
                    st.markdown(f"[{title}]({link})")
            else:
                st.write("لا توجد أخبار.")
