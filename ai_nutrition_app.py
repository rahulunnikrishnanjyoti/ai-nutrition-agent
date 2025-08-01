import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="🧠 AI Nutrition Analyzer", layout="wide")

st.markdown("""
    <h2 style='color: #3D5A80;'>📊 AI-Powered Student Nutrition Dashboard</h2>
    <p style='color: #555;'>Upload your CSV with these columns: <code>Student_ID</code>, <code>Gender</code>, <code>Age</code>, <code>Weight_kg</code>, <code>Height_cm</code>, <code>Arm_Circumference_cm</code></p>
""", unsafe_allow_html=True)

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

def classify_muac(muac, age):
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

def growth_efficiency(bmi, muac):
    ideal_bmi = 18.5
    ideal_muac = 22
    return round((bmi / ideal_bmi) * (muac / ideal_muac), 2)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip().lower() for c in df.columns]
    df.rename(columns={"weight_kg": "weight", "height_cm": "height", "arm_circumference_cm": "muac"}, inplace=True)

    df["height_m"] = df["height"] / 100
    df["bmi"] = df["weight"] / (df["height_m"] ** 2)
    df["bmi_category"] = df["bmi"].apply(classify_bmi)
    df["muac_category"] = df.apply(lambda row: classify_muac(row["muac"], row["age"]), axis=1)
    df["growth_efficiency"] = df.apply(lambda row: growth_efficiency(row["bmi"], row["muac"]), axis=1)

    tabs = st.tabs(["📌 Summary", "📊 BMI Overview", "🩺 MUAC Trends", "🚨 Risk Flags"])

    with tabs[0]:
        st.subheader("📌 Summary Stats")
        st.metric("Average BMI", round(df['bmi'].mean(), 2))
        st.metric("Average MUAC", round(df['muac'].mean(), 2))
        st.metric("% Underweight", f"{(df['bmi_category'].isin(['Underweight', 'Severely Underweight']).mean() * 100):.1f}%")

        st.dataframe(df.head(20))

    with tabs[1]:
        st.subheader("📊 BMI Insights")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.histogram(df, x="bmi", nbins=20, title="BMI Distribution", color_discrete_sequence=['#3D5A80']), use_container_width=True)
        with col2:
            st.plotly_chart(px.pie(df, names="bmi_category", title="BMI Categories", color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)

        st.plotly_chart(px.box(df, x="gender", y="bmi", color="gender", title="BMI by Gender", color_discrete_sequence=px.colors.qualitative.Vivid), use_container_width=True)
        st.plotly_chart(px.scatter(df, x="age", y="bmi", color="gender", title="BMI vs Age", size="bmi", hover_data=["student_id"]), use_container_width=True)

    with tabs[2]:
        st.subheader("🩺 MUAC Trends")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(df, names="muac_category", title="MUAC Distribution", color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
        with col2:
            st.plotly_chart(px.box(df, x="gender", y="muac", color="muac_category", title="MUAC by Gender", color_discrete_sequence=px.colors.qualitative.Bold), use_container_width=True)

        st.plotly_chart(px.line(df.sort_values("age"), x="age", y="muac", title="MUAC vs Age", markers=True), use_container_width=True)
        st.plotly_chart(px.density_heatmap(df, x="age", y="muac", nbinsx=10, nbinsy=10, title="MUAC Heatmap by Age"), use_container_width=True)

    with tabs[3]:
        st.subheader("🚨 High-Risk Alerts")
        risk_df = df[(df["bmi"] < 16) & (df["muac"] < 16)]
        st.warning(f"⚠️ {len(risk_df)} students flagged as high-risk!")
        st.dataframe(risk_df[["student_id", "age", "gender", "bmi", "muac", "bmi_category", "muac_category"]])

        st.plotly_chart(px.scatter(df, x="bmi", y="muac", color="bmi_category", title="BMI vs MUAC Risk Matrix", size="growth_efficiency", hover_name="student_id"), use_container_width=True)

        st.plotly_chart(px.histogram(df, x="growth_efficiency", nbins=15, title="Growth Efficiency Score Distribution", color_discrete_sequence=['#EE6C4D']), use_container_width=True)
