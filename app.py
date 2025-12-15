import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة والتصميم الداكن (Professional UI) ---
st.set_page_config(page_title="MVC Pro Terminal", layout="wide", page_icon="📈")

# فرض التصميم الداكن وتحسين الصناديق
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

# --- 2. محرك البيانات (Data Engine) ---
def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # محاولة جلب السعر الحالي بأكثر من طريقة
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price:
            hist = stock.history(period='1d')
            if not hist.empty:
                price = hist['Close'].iloc[-1]
            else:
                return None, "❌ لم نتمكن من العثور على سعر لهذا السهم. تأكد من الرمز."

        # جلب القوائم المالية
        financials = stock.financials

        # تجهيز المتغيرات الأساسية (مع معالجة القيم المفقودة)
        data = {
            "Symbol": ticker,
            "Price": price,
            "MarketCap": info.get('marketCap', 0),
            "PEG": info.get('pegRatio', None),
            "PS": info.get('priceToSalesTrailing12Months', None),
            "Growth_Est": (info.get('revenueGrowth', 0) or 0) * 100,
            "ROIC": (info.get('returnOnEquity', 0) or 0) * 100, # نستخدم ROE كمؤشر بديل متاح
            "News": stock.news[:5] if hasattr(stock, 'news') else [],
            "Financials": financials
        }

        # حساب الديون (Solvency Check)
        try:
            total_debt = info.get('totalDebt', 0) or 0
            cash = info.get('totalCash', 0) or 0
            ebitda = info.get('ebitda', 1) or 1 # تجنب القسمة على صفر
            net_debt = total_debt - cash
            data['NetDebt_EBITDA'] = net_debt / ebitda
        except:
            data['NetDebt_EBITDA'] = 0.0

        return data, None

    except Exception as e:
        return None, f"خطأ تقني: {str(e)}"

# --- 3. الواجهة والتنفيذ (UI & Logic) ---
st.sidebar.header("🔍 إعدادات الرادار")
symbol = st.sidebar.text_input("رمز السهم (Ticker)", value="NVDA").upper()
run_btn = st.sidebar.button("تشغيل التحليل")

if symbol:
    data, err = get_data(symbol)
    
    if err:
        st.error(err)
    elif data:
        # --- منطق الحكم (The Verdict Logic) ---
        verdict = "🧩 HOLD / WATCH"
        v_color = "#b0b0b0" # رمادي
        v_msg = "الشركة في المنطقة المحايدة."

        # 1. KILL SWITCH (الإعدام)
        if data['NetDebt_EBITDA'] > 3.5:
            verdict = "☠️ KILL SWITCH (DEBT)"
            v_color = "#ff2b2b"
            v_msg = "الديون مرتفعة جداً (أكثر من 3.5 أضعاف الأرباح)."
        elif data['Growth_Est'] < -5:
            verdict = "☠️ KILL SWITCH (GROWTH)"
            v_color = "#ff2b2b"
            v_msg = "الشركة تعاني من انكماش في المبيعات."
            
        # 2. SCRAP ELITE (النخبة الرخيصة)
        # PEG < 1.0 (أو قريب منه) + نمو قوي
        elif (data['PEG'] is not None and data['PEG'] < 1.2) and data['Growth_Est'] > 15:
            verdict = "💎 SCRAP ELITE"
            v_color = "#00ff00" # أخضر فاقع
            v_msg = "فرصة ذهبية: نمو مرتفع بسعر رخيص جداً."

        # 3. QUALITY COMPOUNDER (الجودة)
        elif data['ROIC'] > 15 and data['Growth_Est'] > 10:
            verdict = "👑 QUALITY COMPOUNDER"
            v_color = "#ffd700" # ذهبي
            v_msg = "شركة ذات جودة عالية وتنمو بثبات."

        # --- عرض النتيجة ---
        st.markdown(f"""
        <div class="verdict-box" style="border-color: {v_color}; box-shadow: 0 0 15px {v_color}40;">
            <h1 style="color: {v_color}; margin:0; font-size: 3em;">{verdict}</h1>
            <h3 style="margin-top:10px;">{data['Symbol']} • ${data['Price']:,.2f}</h3>
            <p style="color: #cccccc;">{v_msg}</p>
        </div>
        """, unsafe_allow_html=True)

        # --- مؤشرات الأداء (Metrics) ---
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("نمو المبيعات (المتوقع)", f"{data['Growth_Est']:.1f}%", delta="هدف > 15%")
        with col2:
            peg_display = f"{data['PEG']:.2f}" if data['PEG'] else "N/A"
            st.metric("مكرر PEG", peg_display, delta="هدف < 1.0", delta_color="inverse")
        with col3:
            st.metric("صافي الدين / EBITDA", f"{data['NetDebt_EBITDA']:.1f}x", delta="خطر > 3.5", delta_color="inverse")
        with col4:
            st.metric("الجودة (ROIC/ROE)", f"{data['ROIC']:.1f}%", delta="هدف > 15%")

        st.markdown("---")

        # --- الرسوم البيانية والأخبار ---
        c_chart, c_news = st.columns([2, 1])

        with c_chart:
            st.subheader("📊 مسار الإيرادات (الماضي + المستقبل)")
            try:
                # محاولة رسم المبيعات التاريخية
                fin = data['Financials']
                if not fin.empty and 'Total Revenue' in fin.index:
                    # نأخذ آخر 4 سنوات ونعكس الترتيب
                    rev_hist = fin.loc['Total Revenue'].iloc[:4][::-1]
                    
                    # نحسب السنة القادمة بناءً على نسبة النمو المتوقع
                    last_val = rev_hist.iloc[-1]
                    next_val = last_val * (1 + data['Growth_Est']/100)
                    
                    years = [d.strftime('%Y') for d in rev_hist.index] + ["Next Year (Est)"]
                    values = list(rev_hist.values) + [next_val]
                    colors = ['#1f77b4'] * len(rev_hist) + ['#ff7f0e'] # برتقالي للمستقبل

                    fig = go.Figure(data=[go.Bar(x=years, y=values, marker_color=colors, text=[f"${v/1e9:.1f}B" for v in values])])
                    fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("البيانات التاريخية غير متوفرة للرسم البياني.")
            except Exception as e:
                st.info("لم نتمكن من رسم المبيعات لهذا السهم.")

        with c_news:
            st.subheader("📰 آخر الأخبار")
            if data['News']:
                for n in data['News']:
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid {v_color};">
                        <a href="{n['link']}" target="_blank" style="text-decoration: none; color: white; font-weight: bold; font-size: 0.9em;">{n['title']}</a>
                        <br><span style="color: gray; font-size: 0.7em;">{n.get('publisher', 'News')}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("لا توجد أخبار حديثة.")
