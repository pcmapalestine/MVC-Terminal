import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="MVC Pro Terminal", layout="wide", page_icon="📈")

st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #fafafa;}
    .metric-box {
        background-color: #262730;
        border: 1px solid #464b5d;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .verdict-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
        border: 2px solid;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك البيانات ---
def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # جلب السعر
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price:
            hist = stock.history(period='1d')
            if not hist.empty:
                price = hist['Close'].iloc[-1]
            else:
                return None, "❌ لم نتمكن من العثور على سعر. تأكد من الرمز."

        # جلب القوائم المالية
        financials = stock.financials

        data = {
            "Symbol": ticker,
            "Price": price,
            "MarketCap": info.get('marketCap', 0),
            "PEG": info.get('pegRatio', None),
            "PS": info.get('priceToSalesTrailing12Months', None),
            "Growth_Est": (info.get('revenueGrowth', 0) or 0) * 100,
            "ROIC": (info.get('returnOnEquity', 0) or 0) * 100,
            "News": stock.news if hasattr(stock, 'news') else [], # جلب الأخبار وتخطي الأخطاء
            "Financials": financials
        }

        # حساب الديون
        try:
            total_debt = info.get('totalDebt', 0) or 0
            cash = info.get('totalCash', 0) or 0
            ebitda = info.get('ebitda', 1) or 1
            net_debt = total_debt - cash
            data['NetDebt_EBITDA'] = net_debt / ebitda
        except:
            data['NetDebt_EBITDA'] = 0.0

        return data, None

    except Exception as e:
        return None, f"خطأ تقني: {str(e)}"

# --- 3. الواجهة ---
st.sidebar.header("🔍 إعدادات الرادار")
symbol = st.sidebar.text_input("رمز السهم", value="NVDA").upper()
run_btn = st.sidebar.button("تشغيل التحليل")

if symbol:
    data, err = get_data(symbol)
    
    if err:
        st.error(err)
    elif data:
        # الحكم
        verdict = "🧩 HOLD / WATCH"
        v_color = "#b0b0b0"
        v_msg = "الشركة في المنطقة المحايدة."

        if data['NetDebt_EBITDA'] > 3.5:
            verdict = "☠️ KILL SWITCH"
            v_color = "#ff2b2b"
            v_msg = "الديون مرتفعة جداً."
        elif (data['PEG'] is not None and data['PEG'] < 1.2) and data['Growth_Est'] > 15:
            verdict = "💎 SCRAP ELITE"
            v_color = "#00ff00"
            v_msg = "فرصة ذهبية: نمو مرتفع بسعر رخيص."
        elif data['ROIC'] > 15 and data['Growth_Est'] > 10:
            verdict = "👑 QUALITY COMPOUNDER"
            v_color = "#ffd700"
            v_msg = "جودة عالية ونمو مستمر."

        st.markdown(f"""
        <div class="verdict-box" style="border-color: {v_color}; box-shadow: 0 0 15px {v_color}40;">
            <h1 style="color: {v_color}; margin:0;">{verdict}</h1>
            <h3 style="margin-top:10px;">{data['Symbol']} • ${data['Price']:,.2f}</h3>
            <p style="color: #cccccc;">{v_msg}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("نمو المبيعات", f"{data['Growth_Est']:.1f}%")
        col2.metric("PEG Ratio", f"{data['PEG']:.2f}" if data['PEG'] else "N/A")
        col3.metric("Net Debt/EBITDA", f"{data['NetDebt_EBITDA']:.1f}x")
        col4.metric("ROIC", f"{data['ROIC']:.1f}%")

        st.markdown("---")

        c_chart, c_news = st.columns([2, 1])

        with c_chart:
            st.subheader("📊 مسار الإيرادات")
            try:
                fin = data['Financials']
                if not fin.empty and 'Total Revenue' in fin.index:
                    rev_hist = fin.loc['Total Revenue'].iloc[:4][::-1]
                    last_val = rev_hist.iloc[-1]
                    next_val = last_val * (1 + data['Growth_Est']/100)
                    
                    years = [d.strftime('%Y') for d in rev_hist.index] + ["Next Year (Est)"]
                    values = list(rev_hist.values) + [next_val]
                    colors = ['#1f77b4'] * len(rev_hist) + ['#ff7f0e']

                    fig = go.Figure(data=[go.Bar(x=years, y=values, marker_color=colors)])
                    fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("الرسم البياني غير متاح.")
            except:
                st.info("الرسم البياني غير متاح.")

        with c_news:
            st.subheader("📰 آخر الأخبار")
            if data['News']:
                for n in data['News']:
                    # التعديل هنا: استخدام .get لتجنب الخطأ إذا لم يوجد رابط
                    link = n.get('link', '#')
                    title = n.get('title', 'No Title')
                    publisher = n.get('publisher', 'News')
                    
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid {v_color};">
                        <a href="{link}" target="_blank" style="text-decoration: none; color: white; font-weight: bold;">{title}</a>
                        <br><span style="color: gray; font-size: 0.7em;">{publisher}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("لا توجد أخبار حديثة.")
