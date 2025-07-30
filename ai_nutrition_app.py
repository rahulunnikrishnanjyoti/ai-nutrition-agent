
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="🧠 AI Nutrition Analyzer", layout="wide")

st.markdown(
    "<h2 style='color: #3D5A80;'>📊 Student Nutrition Analysis Dashboard</h2>",
    unsafe_allow_html=True,
)

st.markdown("Upload your CSV file with the following columns: `Name`, `Gender`, `Age`, `Weight (kg)`, `Height (cm)`, `MUAC (cm)`")

uploaded_file = st.file_uploader("📁 Upload CSV", type=["csv"])

def classify_bmi(bmi):
    if bmi < 16:
        return "Severely Underweight"
    elif 16 <= bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def classify_muac(muac, age, gender):
    if age < 5:
        if muac < 11.5:
            return "Severe Acute Malnutrition"
        elif 11.5 <= muac < 12.5:
            return "Moderate Acute Malnutrition"
        else:
            return "Normal"
    else:
        if muac < 16:
            return "Low"
        elif 16 <= muac < 22:
            return "Normal"
        else:
            return "High"

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    df.columns = [c.strip().lower() for c in df.columns]

    df["height_m"] = df["height (cm)"] / 100
    df["BMI"] = df["weight (kg)"] / (df["height_m"] ** 2)
    df["BMI Category"] = df["BMI"].apply(classify_bmi)

    df["MUAC Category"] = df.apply(
        lambda row: classify_muac(row["muac (cm)"], row["age"], row["gender"]), axis=1
    )

    st.success("✅ Analysis Complete")

    st.dataframe(df[["name", "gender", "age", "weight (kg)", "height (cm)", "BMI", "BMI Category", "muac (cm)", "MUAC Category"]])

    st.subheader("📈 Visual Summary")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(df, names="BMI Category", title="BMI Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(df, names="MUAC Category", title="MUAC Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📌 Summary Stats")
    st.write(f"**Average BMI:** {round(df['BMI'].mean(), 2)}")
    st.write("**BMI Counts:**")
    st.write(df["BMI Category"].value_counts())
    st.write("**MUAC Counts:**")
    st.write(df["MUAC Category"].value_counts())
