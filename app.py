import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Forensic Alpha V12", layout="wide", page_icon="⚖️")

st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', sans-serif;}
    .audit-box {
        background-color: #1a1c24; 
        border: 1px solid #333; 
        padding: 20px; 
        border-radius: 5px; 
        text-align: center;
        margin: 20px 0;
    }
    .report-header {border-bottom: 2px solid #ffd700; padding-bottom: 10px; margin-bottom: 20px;}
    .section-title {color: #4FA8FF; font-size: 1.5em; font-weight: bold; margin-top: 20px;}
    .sub-title {color: #ffd700; font-size: 1.2em; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# --- 2. محرك التحليل الجنائي ---
def get_forensic_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # السعر
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price:
            hist = stock.history(period='1d')
            if not hist.empty:
                price = hist['Close'].iloc[-1]
            else:
                return None, "❌ السعر غير متوفر."

        mkt_cap = info.get('marketCap', 0)
        total_cash = info.get('totalCash', 0) or 0
        total_debt = info.get('totalDebt', 0) or 0
        
        # --- فلتر العملة الذكي (Currency Sanity Check) ---
        # إذا كانت نسبة الكاش > 100%، فهذا يعني غالباً أن الكاش بعملة مختلفة
        raw_cash_percent = (total_cash / mkt_cap * 100) if mkt_cap else 0
        currency_mismatch = False
        
        if raw_cash_percent > 100:
            currency_mismatch = True
            # محاولة تصحيح تقريبي (افتراض اليوان مقابل الدولار ~7.2)
            # ملاحظة: هذا تقدير للشركات الصينية، الأفضل التحذير فقط
            adjusted_cash_percent = raw_cash_percent / 7.2 
        else:
            adjusted_cash_percent = raw_cash_percent

        ev = mkt_cap - total_cash + total_debt
        
        pe_fwd = info.get('forwardPE', 0) or 0
        ps = info.get('priceToSalesTrailing12Months', 0) or 0
        growth = (info.get('revenueGrowth', 0) or 0) * 100
        ebitda = info.get('ebitda', 1) or 1
        leverage = (total_debt - total_cash) / ebitda if ebitda else 0

        return {
            "Symbol": ticker,
            "Price": price,
            "MktCap": mkt_cap,
            "Cash": total_cash,
            "Debt": total_debt,
            "Cash_Percent": adjusted_cash_percent, # النسبة المصححة أو الأصلية
            "Raw_Percent": raw_cash_percent,      # النسبة الخام للكشف
            "Mismatch": currency_mismatch,        # هل هناك خطأ عملة؟
            "EV": ev,
            "PE_Fwd": pe_fwd,
            "PS": ps,
            "Growth": growth,
            "Leverage": leverage,
            "News": stock.news if hasattr(stock, 'news') else [],
            "Financials": stock.financials
        }, None

    except Exception as e:
        return None, f"خطأ تقني: {str(e)}"

# --- 3. الواجهة ---
st.sidebar.header("⚖️ المحقق الجنائي")
ticker = st.sidebar.text_input("رمز السهم", value="BIDU").upper()
run_btn = st.sidebar.button("استخراج التقرير")

if ticker and run_btn:
    data, err = get_forensic_data(ticker)
    
    if err:
        st.error(err)
    elif data:
        # العنوان
        st.markdown(f"<h1 class='report-header'>📑 تقرير التدقيق الجنائي: {data['Symbol']}</h1>", unsafe_allow_html=True)
        st.write(f"**السعر الحالي:** ${data['Price']:,.2f} | **القيمة السوقية:** ${data['MktCap']/1e9:.2f}B")

        # الباب الأول
        st.markdown("<div class='section-title'>📜 الباب الأول: الطبقة الرقمية الصلبة</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='sub-title'>1. الكنز المدفون (Cash Analysis)</div>", unsafe_allow_html=True)
            
            # عرض الأرقام الخام
            st.write(f"- **حجم الكاش (الخام):** {data['Cash']/1e9:.2f}B")
            
            # --- منطق العرض الذكي ---
            if data['Mismatch']:
                st.warning(f"⚠️ تنبيه عملة: البيانات الخام تظهر نسبة كاش {data['Raw_Percent']:.0f}% وهذا مستحيل. يبدو أن الكاش باليوان والقيمة بالدولار.")
                st.info(f"✅ النسبة التقديرية بعد التصحيح: ~{data['Cash_Percent']:.1f}%")
            else:
                st.write(f"- **نسبة الكاش:** {data['Cash_Percent']:.1f}%")

            # رسالة التحليل
            if data['Cash_Percent'] > 30 and not data['Mismatch']:
                st.success(f"💎 الصدمة: الكاش يمثل {data['Cash_Percent']:.1f}% من القيمة! بنك ممتلئ بالمال.")
            elif data['Cash_Percent'] > 30 and data['Mismatch']:
                st.success(f"💎 تقدير: حتى بعد تصحيح العملة، النسبة ~{data['Cash_Percent']:.1f}% تظل ممتازة جداً (Asset Play).")
            elif data['Cash_Percent'] > 10:
                st.info("✅ ميزانية مستقرة.")
            else:
                st.warning("⚠️ مستوى كاش منخفض.")

        with col2:
            st.markdown("<div class='sub-title'>2. سعر الخردة (The Scrap Test)</div>", unsafe_allow_html=True)
            st.write(f"- **Fwd P/E:** {data['PE_Fwd']:.2f}x")
            st.write(f"- **النمو:** {data['Growth']:.1f}%")
            
            if data['PE_Fwd'] < 12:
                st.success("🔥 PASS: السهم مسعر كخردة.")
            else:
                st.warning("❌ السعر ليس رخيصاً جداً.")

        # الحكم النهائي
        st.markdown("<div class='section-title'>🏆 الحكم النهائي</div>", unsafe_allow_html=True)
        
        final_verdict = "🧩 HOLD / WATCH"
        v_color = "#b0b0b0"
        
        # القواعد
        if data['Growth'] < -5:
            final_verdict = "☠️ KILL SWITCH (انكماش)"
            v_color = "#ff2b2b"
        elif data['Cash_Percent'] > 30 and data['PE_Fwd'] < 15:
            final_verdict = "🧩 ASSET PLAY (لعبة أصول)"
            v_color = "#ffd700"
        elif data['Growth'] > 15 and data['PE_Fwd'] < 20:
            final_verdict = "💎 SCRAP ELITE"
            v_color = "#00ff00"

        st.markdown(f"""
        <div class="audit-box" style="border: 2px solid {v_color};">
            <h1 style="color: {v_color}; margin:0;">{final_verdict}</h1>
        </div>
        """, unsafe_allow_html=True)

        # الأخبار
        st.markdown("<div class='section-title'>📰 الأخبار</div>", unsafe_allow_html=True)
        if data['News']:
            for n in data['News']:
                title = n.get('title', 'No Title')
                link = n.get('link', '#')
                st.markdown(f"- [{title}]({link})")
