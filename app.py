import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="MVC Pro Terminal", layout="wide", page_icon="💎")

st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #fafafa;}
    .metric-box {
        background-color: #262730; 
        border: 1px solid #464b5d;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    .audit-pass {color: #00ff00; font-weight: bold;}
    .audit-fail {color: #ff2b2b; font-weight: bold;}
    .audit-neutral {color: #b0b0b0;}
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

        # جلب البيانات المالية
        financials = stock.financials

        data = {
            "Symbol": ticker,
            "Price": price,
            "MarketCap": info.get('marketCap', 0),
            "PEG": info.get('pegRatio', None),
            "PS": info.get('priceToSalesTrailing12Months', None),
            "Growth_Est": (info.get('revenueGrowth', 0) or 0) * 100,
            "ROIC": (info.get('returnOnEquity', 0) or 0) * 100,
            "News": stock.news if hasattr(stock, 'news') else [],
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

# --- 3. الواجهة والمنهجية ---
st.sidebar.header("🔍 الرادار")
symbol = st.sidebar.text_input("الرمز", value="NVDA").upper()
run_btn = st.sidebar.button("تحليل")

if symbol:
    data, err = get_data(symbol)
    
    if err:
        st.error(err)
    elif data:
        # --- تطبيق المنهجية (Audit Logic) ---
        audit_log = []
        
        # 1. فحص الإعدام (Kill Switch)
        is_killed = False
        if data['NetDebt_EBITDA'] > 3.5:
            audit_log.append(f"❌ <span class='audit-fail'>فشل الديون:</span> الرافعة {data['NetDebt_EBITDA']:.2f}x (أخطر من 3.5x)")
            is_killed = True
        else:
            audit_log.append(f"✅ <span class='audit-pass'>نجاح الديون:</span> الرافعة {data['NetDebt_EBITDA']:.2f}x (آمنة)")

        if data['Growth_Est'] < -5:
            audit_log.append(f"❌ <span class='audit-fail'>فشل النمو:</span> انكماش {data['Growth_Est']:.1f}%")
            is_killed = True
        else:
            audit_log.append(f"✅ <span class='audit-pass'>فحص النمو:</span> إيجابي {data['Growth_Est']:.1f}%")

        # تحديد الحكم النهائي
        verdict = "🧩 HOLD / WATCH"
        v_color = "#b0b0b0"
        
        if is_killed:
            verdict = "☠️ KILL SWITCH"
            v_color = "#ff2b2b"
        elif (data['PEG'] is not None and data['PEG'] < 1.2) and data['Growth_Est'] > 15:
            verdict = "💎 SCRAP ELITE"
            v_color = "#00ff00"
            audit_log.append("💎 <span class='audit-pass'>تطابق مواصفات النخبة (PEG منخفض + نمو مرتفع)</span>")
        elif data['ROIC'] > 15 and data['Growth_Est'] > 10:
            verdict = "👑 QUALITY COMPOUNDER"
            v_color = "#ffd700"
            audit_log.append("👑 <span class='audit-pass'>تطابق مواصفات الجودة (عائد ممتاز + نمو مستقر)</span>")
        else:
            audit_log.append("ℹ️ <span class='audit-neutral'>السهم جيد لكنه لا يطابق شروط النخبة الصارمة حالياً.</span>")

        # --- العرض ---
        st.markdown(f"""
        <div style="border: 2px solid {v_color}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h1 style="color: {v_color}; margin:0;">{verdict}</h1>
            <h3 style="margin-top:5px;">{data['Symbol']} • ${data['Price']:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)

        # عرض تقرير التدقيق (المنهجية المرئية)
        with st.expander("📋 عرض تقرير التدقيق وتفاصيل المنهجية", expanded=True):
            for log in audit_log:
                st.markdown(f"- {log}", unsafe_allow_html=True)

        # الأرقام الرئيسية
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("نمو المبيعات المتوقع", f"{data['Growth_Est']:.1f}%", delta="الهدف > 15%")
        c2.metric("مكرر PEG", f"{data['PEG']:.2f}" if data['PEG'] else "N/A", delta="الهدف < 1.2", delta_color="inverse")
        c3.metric("صافي الدين / EBITDA", f"{data['NetDebt_EBITDA']:.1f}x", delta="الحد الأقصى 3.5", delta_color="inverse")
        c4.metric("العائد ROIC/ROE", f"{data['ROIC']:.1f}%", delta="الهدف > 15%")

        st.markdown("---")

        # الرسم البياني والأخبار
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
                    fig.update_layout(height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("البيانات التاريخية غير متاحة.")
            except:
                st.info("تعذر رسم المبيعات.")

        with c_news:
            st.subheader("📰 آخر الأخبار")
            if data['News']:
                for n in data['News']:
                    # إصلاح مشكلة الروابط
                    link = n.get('link', '#')
                    title = n.get('title', 'No Title')
                    
                    st.markdown(f"""
                    <div style="background-color: #1E1E1E; padding: 10px; margin-bottom: 5px; border-radius: 5px;">
                        <a href="{link}" target="_blank" style="text-decoration: none; color: #4FA8FF; font-size: 0.9em;">{title}</a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("لا توجد أخبار.")
