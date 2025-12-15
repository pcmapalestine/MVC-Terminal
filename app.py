import streamlit as st
import yfinance as yf
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Forensic Alpha V7.7", layout="wide", page_icon="⚖️")

# تصميم مطابق لتقريرك (داكن واحترافي)
st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #e0e0e0;}
    .header-box {border-bottom: 2px solid #464b5d; padding-bottom: 10px; margin-bottom: 20px;}
    .audit-box {
        background-color: #1a1c24; 
        border: 1px solid #333; 
        padding: 20px; 
        border-radius: 5px; 
        margin-bottom: 15px;
    }
    .highlight {color: #ffd700; font-weight: bold;}
    .pass {color: #00ff00; font-weight: bold;}
    .fail {color: #ff2b2b; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # --- استخراج البيانات الجنائية ---
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        mkt_cap = info.get('marketCap', 0)
        
        # 1. الكنز المدفون (Cash Analysis)
        total_cash = info.get('totalCash', 0)
        total_debt = info.get('totalDebt', 0)
        cash_per_share = info.get('totalCashPerShare', 0)
        cash_percent = (total_cash / mkt_cap) * 100 if mkt_cap else 0
        enterprise_value = mkt_cap - total_cash + total_debt
        
        # 2. التقييم (Valuation)
        pe_fwd = info.get('forwardPE', 0)
        peg = info.get('pegRatio', 0)
        
        # 3. النمو (Growth)
        rev_growth = (info.get('revenueGrowth', 0) or 0) * 100
        
        return {
            "Symbol": ticker,
            "Price": price,
            "MktCap": mkt_cap,
            "Cash": total_cash,
            "Debt": total_debt,
            "Cash_Percent": cash_percent,
            "EV": enterprise_value,
            "PE_Fwd": pe_fwd,
            "PEG": peg,
            "Growth": rev_growth,
            "News": stock.news[:3] if hasattr(stock, 'news') else []
        }
    except Exception as e:
        return None

# --- الواجهة الجانبية ---
st.sidebar.title("🕵️‍♂️ المحقق الجنائي")
ticker = st.sidebar.text_input("رمز السهم", value="BIDU").upper()
run = st.sidebar.button("ابدأ التدقيق")

if run and ticker:
    data = analyze_stock(ticker)
    
    if not data:
        st.error("لم يتم العثور على البيانات. تأكد من الرمز.")
    else:
        # === العنوان ===
        st.markdown(f"# 📑 تقرير التدقيق الجنائي: {data['Symbol']}")
        st.markdown(f"### السعر الحالي: ${data['Price']} | القيمة السوقية: ${data['MktCap']/1e9:.2f}B")
        
        # === الباب الأول: الطبقة الرقمية الصلبة ===
        st.markdown("## 📜 الباب الأول: الطبقة الرقمية الصلبة (The Hard Layer)")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 1. الكنز المدفون (Cash Audit)")
            st.write(f"حجم الكاش في الخزنة: **${data['Cash']/1e9:.2f}B**")
            st.write(f"نسبة الكاش من قيمة الشركة: **{data['Cash_Percent']:.1f}%**")
            
            if data['Cash_Percent'] > 30:
                st.markdown(f"✅ <span class='pass'>صدمة إيجابية: الشركة عبارة عن بنك ممتلئ بالمال!</span>", unsafe_allow_html=True)
            else:
                st.markdown("⚠️ مستوى الكاش طبيعي.")

            # معادلة Enterprise Value
            st.markdown("#### المعادلة الجنائية (Enterprise Value):")
            st.code(f"EV = {data['MktCap']/1e9:.1f}B (Cap) - {data['Cash']/1e9:.1f}B (Cash) = {data['EV']/1e9:.1f}B")
            st.caption("هذا هو السعر الحقيقي الذي تدفعه مقابل النشاط التشغيلي.")

        with c2:
            st.markdown("### 2. سعر الخردة (The Scrap Test)")
            st.write(f"مكرر الربحية المتوقع (Fwd P/E): **{data['PE_Fwd']:.2f}x**")
            st.write(f"معدل النمو: **{data['Growth']:.2f}%**")
            
            verdict = ""
            if data['PE_Fwd'] < 15 and data['Growth'] > 0:
                verdict = "🔥 PASS (سعر خردة). السهم رخيص جداً."
            elif data['PE_Fwd'] < 15 and data['Growth'] <= 0:
                 verdict = "⚠️ رخيص ولكنه لا ينمو (فخ قيمة محتمل)."
            else:
                verdict = "❌ غالي مقارنة بالنمو."
            
            st.markdown(f"**الحكم:** {verdict}")

        st.markdown("---")

        # === الباب الثاني: فحص المحرك (Engine Audit) ===
        st.markdown("## 📊 فحص المحرك (Engine Audit)")
        
        # بناء الجدول يدوياً ليكون مطابقاً للتقرير
        engine_data = {
            "المعيار": ["نمو الإيرادات", "التقييم (P/E)", "قوة الميزانية (Cash)"],
            "الأرقام": [f"{data['Growth']:.1f}%", f"{data['PE_Fwd']:.1f}x", f"${data['Cash']/1e9:.1f}B"],
            "التشخيص": [
                "⚠️ محرك بارد" if data['Growth'] < 5 else "🚀 محرك قوي",
                "🔥 رخيص جداً" if data['PE_Fwd'] < 12 else "💰 سعر عادل/غالي",
                "💎 حصن مالي" if data['Cash_Percent'] > 20 else "ميزانية عادية"
            ]
        }
        df_engine = pd.DataFrame(engine_data)
        st.table(df_engine)

        # === الحكم النهائي (Final Matrix) ===
        st.markdown("## 🏆 الحكم النهائي (The Final Matrix)")
        
        final_verdict = "🧩 HOLD / WATCH"
        matrix_msg = "الشركة في المنطقة الرمادية."
        
        # منطق المصفوفة V7.7
        if data['Cash_Percent'] > 40 and data['PE_Fwd'] < 12:
            final_verdict = "🧩 لعبة أصول (Asset Play)"
            matrix_msg = "أنت تشتري الدولار بـ 50 سنتاً. المخاطرة محدودة جداً بسبب الكاش الهائل."
        elif data['Growth'] > 15 and data['PEG'] < 1.2:
            final_verdict = "💎 Scrap Elite (نخبة الخردة)"
            matrix_msg = "نمو متفجر بسعر رخيص."
        elif data['Debt'] > (data['Cash'] * 3):
            final_verdict = "☠️ Kill Switch (Debt)"
            matrix_msg = "الشركة غارقة في الديون."
            
        st.markdown(f"""
        <div class="audit-box" style="text-align: center; border: 2px solid #ffd700;">
            <h1 style="color: #ffd700;">{final_verdict}</h1>
            <p>{matrix_msg}</p>
