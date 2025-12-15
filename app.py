import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة (Design) ---
st.set_page_config(page_title="Forensic Alpha V7.7", layout="wide", page_icon="⚖️")

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
    .pass {color: #00ff00; font-weight: bold;}
    .fail {color: #ff2b2b; font-weight: bold;}
    .neutral {color: #ffd700; font-weight: bold;}
    .metric-container {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #464b5d;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. محرك التحليل الجنائي (Forensic Engine) ---
def analyze_stock(ticker):
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
                return None, "❌ لم نتمكن من العثور على سعر."

        # جلب البيانات المالية
        financials = stock.financials

        # 1. الكنز المدفون (Cash Analysis)
        mkt_cap = info.get('marketCap', 0)
        total_cash = info.get('totalCash', 0) or 0
        total_debt = info.get('totalDebt', 0) or 0
        
        # تجنب القسمة على صفر
        cash_percent = (total_cash / mkt_cap * 100) if mkt_cap else 0
        ev = mkt_cap - total_cash + total_debt

        # 2. مؤشرات النمو والتقييم
        growth = (info.get('revenueGrowth', 0) or 0) * 100
        pe_fwd = info.get('forwardPE', 0) or 0
        ps_ratio = info.get('priceToSalesTrailing12Months', 0) or 0
        
        # 3. الأخبار (مع الحماية من الأخطاء)
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
        return None, f"خطأ تقني: {str(e)}"

# --- 3. الواجهة والتنفيذ ---
st.sidebar.title("🕵️‍♂️ المحقق الجنائي")
ticker = st.sidebar.text_input("رمز السهم", value="BIDU").upper()
run = st.sidebar.button("تشغيل التدقيق")

if ticker:
    data, err = analyze_stock(ticker)
    
    if err:
        st.error(err)
    elif data:
        # === العنوان ===
        st.markdown(f"# 📑 تقرير التدقيق الجنائي: {data['Symbol']}")
        st.markdown(f"### السعر الحالي: ${data['Price']:,.2f} | القيمة السوقية: ${data['MktCap']/1e9:.2f}B")
        
        # === التحليل والمنهجية (Logic) ===
        # تحديد الحكم النهائي بناءً على المصفوفة
        verdict = "🧩 HOLD / WATCH"
        v_color = "#b0b0b0"
        why_msg = "الشركة في المنطقة الرمادية."

        # شروط المصفوفة
        if data['Debt'] > (data['Cash'] * 3.5) and data['Cash'] > 0:
            verdict = "☠️ KILL SWITCH"
            v_color = "#ff2b2b"
            why_msg = "الديون مرتفعة جداً (خطر الإفلاس)."
        elif data['Growth'] > 15 and (data['PS'] < 1.5 or data['PE_Fwd'] < 15):
            verdict = "💎 SCRAP ELITE"
            v_color = "#00ff00"
            why_msg = "نمو قوي بسعر خردة (فرصة نادرة)."
        elif data['Cash_Percent'] > 30:
            verdict = "🧩 ASSET PLAY"
            v_color = "#ffd700" # ذهبي
            why_msg = f"الشركة عبارة عن بنك! الكاش يمثل {data['Cash_Percent']:.1f}% من قيمتها."

        # عرض الحكم في صندوق كبير
        st.markdown(f"""
        <div class="audit-box" style="border-color: {v_color}; box-shadow: 0 0 10px {v_color}40;">
            <h1 style="color: {v_color}; margin:0;">{verdict}</h1>
            <p style="color: #ccc; margin-top: 10px;">{why_msg}</p>
        </div>
        """, unsafe_allow_html=True)

        # === التفاصيل الجنائية (The Proof) ===
        st.markdown("## 📜 الباب الأول: الطبقة الرقمية الصلبة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 1. الكنز المدفون (Cash)")
            st.metric("حجم الكاش", f"${data['Cash']/1e9:.2f}B")
            st.metric("نسبة الكاش من السوق", f"{data['Cash_Percent']:.1f}%", delta="الهدف > 20%")
            st.caption(f"القيمة الحقيقية للمنشأة (EV): ${data['EV']/1e9:.2f}B")

        with col2:
            st.markdown("### 2. سعر الخردة (Valuation)")
            st.metric("مكرر الربحية المتوقع (Fwd P/E)", f"{data['PE_Fwd']:.2f}x", delta="رخيص < 15", delta_color="inverse")
            st.metric("نمو المبيعات", f"{data['Growth']:.1f}%", delta="قوي > 15%")
            st.metric("مكرر المبيعات (P/S)", f"{data['PS']:.2f}x", delta="خردة < 1.5", delta_color="inverse")

        st.markdown("---")

        # === فحص المحرك (الرسم البياني) ===
        st.markdown("## 📊 فحص المحرك (مسار الإيرادات)")
        try:
            fin = data['Financials']
            if not fin.empty and 'Total Revenue' in fin.index:
                rev_hist = fin.loc['Total Revenue'].iloc[:4][::-1]
                years = [d.strftime('%Y') for d in rev_hist.index]
                values = list(rev_hist.values)
                
                fig = go.Figure(data=[go.Bar(
                    x=years, 
                    y=values, 
                    marker_color='#1f77b4',
                    text=[f"${v/1e9:.1f}B" for v in values],
                    textposition='auto'
                )])
                fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("البيانات التاريخية غير متوفرة للرسم.")
        except Exception as e:
            st.info("تعذر رسم المخطط البياني.")

        # === الأخبار (مع إصلاح الخطأ السابق) ===
        st.markdown("---")
        st.markdown("## 📰 آخر الأخبار (الطبقة النوعية)")
        
        if data['News']:
            for n in data['News']:
                # --- هنا الإصلاح: استخدام .get لمنع الانهيار ---
                link = n.get('link', '#')
                title = n.get('title', 'عنوان غير متاح')
                publisher = n.get('publisher', 'مصدر غير معروف')
                
                st.markdown(f"""
                <div style="background-color: #1E1E1E; padding: 10px; margin-bottom: 8px; border-radius: 5px; border-left: 3px solid {v_color};">
                    <a href="{link}" target="_blank" style="text-decoration: none; color: white; font-weight: bold;">{title}</a>
                    <br><span style="color: gray; font-size: 0.8em;"> المصدر: {publisher}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("لا توجد أخبار حديثة.")
