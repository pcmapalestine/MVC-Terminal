import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. إعدادات الصفحة (Design) ---
st.set_page_config(page_title="Forensic Alpha V11", layout="wide", page_icon="⚖️")

st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    .report-header {border-bottom: 2px solid #ffd700; padding-bottom: 10px; margin-bottom: 20px;}
    .section-title {color: #4FA8FF; font-size: 1.5em; font-weight: bold; margin-top: 20px;}
    .sub-title {color: #ffd700; font-size: 1.2em; font-weight: bold;}
    .audit-box {
        background-color: #1a1c24; 
        border: 1px solid #333; 
        padding: 20px; 
        border-radius: 5px; 
        text-align: center;
        margin: 20px 0;
    }
    .pass {color: #00ff00; font-weight: bold;}
    .fail {color: #ff2b2b; font-weight: bold;}
    .neutral {color: #b0b0b0;}
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

        # البيانات المالية الأساسية
        mkt_cap = info.get('marketCap', 0)
        total_cash = info.get('totalCash', 0) or 0
        total_debt = info.get('totalDebt', 0) or 0
        shares = info.get('sharesOutstanding', 0)
        
        # الحسابات الجنائية
        cash_percent = (total_cash / mkt_cap * 100) if mkt_cap else 0
        ev = mkt_cap - total_cash + total_debt # Enterprise Value
        
        # المؤشرات
        pe_fwd = info.get('forwardPE', 0) or 0
        ps = info.get('priceToSalesTrailing12Months', 0) or 0
        growth = (info.get('revenueGrowth', 0) or 0) * 100
        ebitda = info.get('ebitda', 1) or 1
        debt_leverage = (total_debt - total_cash) / ebitda if ebitda else 0

        # الأخبار
        news = stock.news if hasattr(stock, 'news') else []

        return {
            "Symbol": ticker,
            "Price": price,
            "MktCap": mkt_cap,
            "Cash": total_cash,
            "Debt": total_debt,
            "Cash_Percent": cash_percent,
            "EV": ev,
            "PE_Fwd": pe_fwd,
            "PS": ps,
            "Growth": growth,
            "Leverage": debt_leverage,
            "News": news,
            "Financials": stock.financials
        }, None

    except Exception as e:
        return None, f"خطأ تقني: {str(e)}"

# --- 3. الواجهة (بناء التقرير النصي) ---
st.sidebar.header("⚖️ المحقق الجنائي")
ticker = st.sidebar.text_input("رمز السهم", value="BIDU").upper()
run_btn = st.sidebar.button("استخراج التقرير")

if ticker and run_btn:
    data, err = get_forensic_data(ticker)
    
    if err:
        st.error(err)
    elif data:
        # === 1. العنوان الرئيسي ===
        st.markdown(f"<h1 class='report-header'>📑 تقرير التدقيق الجنائي: {data['Symbol']}</h1>", unsafe_allow_html=True)
        st.write(f"**السعر الحالي:** ${data['Price']:,.2f} | **القيمة السوقية:** ${data['MktCap']/1e9:.2f}B")

        # === 2. الباب الأول: الطبقة الرقمية الصلبة ===
        st.markdown("<div class='section-title'>📜 الباب الأول: الطبقة الرقمية الصلبة (The Hard Layer)</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='sub-title'>1. الكنز المدفون (Cash Analysis)</div>", unsafe_allow_html=True)
            st.write(f"- **حجم الكاش:** ${data['Cash']/1e9:.2f}B")
            st.write(f"- **نسبة الكاش من القيمة السوقية:** {data['Cash_Percent']:.1f}%")
            
            # منطق السرد النصي (Narrative Logic)
            if data['Cash_Percent'] > 30:
                st.success(f"💎 الصدمة: الكاش يمثل {data['Cash_Percent']:.1f}% من قيمة الشركة! أنت تشتري النشاط التشغيلي بسعر بخس.")
            elif data['Cash_Percent'] > 10:
                st.info("✅ ميزانية قوية ومستقرة.")
            else:
                st.warning("⚠️ مستوى الكاش منخفض نسبياً.")

            # المعادلة الجنائية
            st.code(f"Enterprise Value = {data['MktCap']/1e9:.1f}B (Cap) - {data['Cash']/1e9:.1f}B (Cash) = ${data['EV']/1e9:.1f}B", language="python")

        with col2:
            st.markdown("<div class='sub-title'>2. سعر الخردة (The Scrap Test)</div>", unsafe_allow_html=True)
            st.write(f"- **مكرر الربحية المتوقع (Fwd P/E):** {data['PE_Fwd']:.2f}x")
            st.write(f"- **معدل النمو:** {data['Growth']:.1f}%")
            
            if data['PE_Fwd'] < 12 and data['Growth'] > 0:
                st.success("🔥 PASS (سعر خردة). السهم مسعر للموت رغم وجود نمو.")
            elif data['Growth'] < 0:
                st.error("⚠️ انكماش: الشركة رخيصة لأنها تنكمش.")
            else:
                st.warning("❌ السعر ليس رخيصاً بما يكفي ليكون 'خردة'.")

        # === 3. زر التدمير ===
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>3. زر التدمير (Kill Switch)</div>", unsafe_allow_html=True)
        
        kill_reasons = []
        if data['Leverage'] > 3.5:
            kill_reasons.append(f"❌ خطر الديون: الرافعة {data['Leverage']:.2f}x مرتفعة جداً.")
        if data['Growth'] < -5:
            kill_reasons.append(f"❌ خطر النمو: المبيعات تنكمش بنسبة {data['Growth']:.1f}%.")
            
        if kill_reasons:
            for reason in kill_reasons:
                st.error(reason)
        else:
            st.success("✅ الفحص الأمني: لا توجد مؤشرات تدمير فورية (الديون والنمو في الحدود الآمنة).")

        # === 4. فحص المحرك (Engine Audit) - الجدول ===
        st.markdown("<div class='section-title'>📊 فحص المحرك (Engine Audit)</div>", unsafe_allow_html=True)
        
        # تشخيص المحرك
        engine_status = "🚀 محرك قوي" if data['Growth'] > 10 else ("⚠️ محرك بارد" if data['Growth'] > 0 else "🛑 محرك معطل")
        val_status = "🔥 رخيص جداً" if data['PE_Fwd'] < 15 else "💰 سعر عادل/مرتفع"
        fin_status = "💎 حصن مالي" if data['Cash_Percent'] > 20 else "✅ مستقر"

        engine_data = {
            "المعيار": ["نمو الإيرادات", "التقييم (P/E)", "قوة الميزانية"],
            "الأرقام": [f"{data['Growth']:.1f}%", f"{data['PE_Fwd']:.1f}x", f"${data['Cash']/1e9:.1f}B"],
            "التشخيص": [engine_status, val_status, fin_status]
        }
        st.table(pd.DataFrame(engine_data))

        # === 5. الحكم النهائي (Final Matrix) ===
        st.markdown("<div class='section-title'>🏆 الحكم النهائي (The Final Matrix)</div>", unsafe_allow_html=True)
        
        final_verdict = "🧩 HOLD / WATCH"
        matrix_msg = "الشركة جيدة لكنها لا تطابق شروط النخبة."
        v_color = "#b0b0b0"

        # منطق المصفوفة
        if kill_reasons:
            final_verdict = "☠️ KILL SWITCH"
            matrix_msg = "ابتعد فوراً. المخاطر مرتفعة جداً."
            v_color = "#ff2b2b"
        elif data['Cash_Percent'] > 40 and data['PE_Fwd'] < 15:
            final_verdict = "🧩 ASSET PLAY (لعبة أصول)"
            matrix_msg = "أنت تشتري الدولار بـ 50 سنتاً. القيمة في الأصول وليست في النمو."
            v_color = "#ffd700"
        elif data['Growth'] > 15 and (data['PS'] < 2.0 or data['PE_Fwd'] < 20):
            final_verdict = "💎 SCRAP ELITE"
            matrix_msg = "نمو متفجر بسعر خردة. فرصة نادرة."
            v_color = "#00ff00"

        st.markdown(f"""
        <div class="audit-box" style="border: 2px solid {v_color};">
            <h1 style="color: {v_color}; margin:0;">{final_verdict}</h1>
            <p style="font-size: 1.1em; margin-top: 10px;">{matrix_msg}</p>
        </div>
        """, unsafe_allow_html=True)

        # === 6. قائمة التدقيق الذهبية ===
        st.markdown("### ✅ قائمة التدقيق الذهبية")
        checklist = {
            "البند": ["1. الهوية (القطاع)", "2. الأصول (Cash)", "3. التقييم", "4. الأمان (الديون)", "5. الحكم"],
            "النتيجة": [
                f"{data['Symbol']}",
                "👑 ممتاز" if data['Cash_Percent'] > 25 else "✅ جيد",
                "🔥 رخيص" if data['PE_Fwd'] < 15 else "❌ مرتفع",
                "✅ آمن" if data['Leverage'] < 3.0 else "⚠️ خطر",
                final_verdict
            ]
        }
        st.table(pd.DataFrame(checklist))

        # === 7. الطبقة النوعية (الأخبار) ===
        st.markdown("<div class='section-title'>🧠 الطبقة النوعية (الأخبار)</div>", unsafe_allow_html=True)
        if data['News']:
            for n in data['News']:
                title = n.get('title', 'No Title')
                link = n.get('link', '#')
                pub = n.get('publisher', 'Source')
                st.markdown(f"- **[{title}]({link})** <span style='color:gray; font-size:0.8em;'>({pub})</span>", unsafe_allow_html=True)
        else:
            st.write("لا توجد أخبار حديثة.")
