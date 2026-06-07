import streamlit as st
import pandas as pd
import ollama


# 1. Funktion fuer das lokale LLM (Ollama) - Die saubere Profi-Variante
def ask_controlling_ai(prompt):
    response = ollama.generate(
        model='llama3',
        prompt=prompt
    )
    return response['response']




# 2. Layout der Web-Oberflaeche einrichten
st.set_page_config(page_title="AI Variance Analyzer", layout="wide")
st.title("📊 AI-Powered Corporate Controlling Dashboard")
st.subheader("Automatisierte Varianzanalyse & Management Summary")

# 3. Der magische Upload-Button für jede beliebige Excel-Datei
uploaded_file = st.file_uploader("Lade hier deine monatliche Excel-Datei (.xlsx) hoch:", type=["xlsx"])

if uploaded_file is not None:
    # Excel-Datei einlesen
    df = pd.read_excel(uploaded_file)
    st.success("Excel-Datei erfolgreich geladen!")

    # 1. Mathematische Berechnungen im Hintergrund
    df['Abweichung_Absolut'] = df['Ist_Wert'] - df['Budget']
    df['Abweichung_Prozent'] = (df['Abweichung_Absolut'] / df['Budget']) * 100
    df['Abweichung_Prozent'] = df['Abweichung_Prozent'].fillna(0)
    
    # WICHTIG: Erst die auffaelligen Daten berechnen, damit sie weiter unten bekannt sind!
    auffaellige_daten = df[(df['Abweichung_Prozent'] > 20) | ((df['Budget'] == 0) & (df['Ist_Wert'] > 0))]
    
    # 2. Visuelles Dashboard & KPIs (Die PowerBI-Karten)
    st.write("---")
    st.write("### 📈 Key Performance Indicators (KPIs)")
    
    col1, col2, col3 = st.columns(3)
    total_budget = df['Budget'].sum()
    total_ist = df['Ist_Wert'].sum()
    total_diff = total_ist - total_budget
    
    col1.metric("Gesamt Budget", f"{total_budget:,.2f} €".replace(",", "'"))
    col2.metric("Gesamt Ist-Kosten", f"{total_ist:,.2f} €".replace(",", "'"))
    col3.metric(
        "Gesamt Abweichung", 
        f"{total_diff:,.2f} €".replace(",", "'"), 
        delta=f"{total_diff:,.2f} €".replace(",", "'"), 
        delta_color="inverse"
    )

    st.write("---")

    # 3. Styling-Funktion fuer die rote Markierung
    def highlight_over_budget(row):
        return ['background-color: #f8d7da; color: #721c24;' if row['Abweichung_Absolut'] > 0 else '' for _ in row]

    # 4. Die Rohdaten-Tabelle formatiert ausgeben
    st.write("### 📊 Rohdaten aus dem ERP-System (Vorschau):")
    st.dataframe(df.style.apply(highlight_over_budget, axis=1))

    st.write("---")

    # 5. Die gefilterten Anomalien rot markiert anzeigen (Jetzt klappt es!)
    st.write("### 🚨 Automatisch erkannte Anomalien (>20% oder kein Budget):")
    st.dataframe(auffaellige_daten.style.apply(highlight_over_budget, axis=1))
    
    st.write("---")
    
    
    # Button zum Starten der KI-Analyse
    if st.button("🚀 Management Summary generieren"):
        with st.spinner("Lokale KI analysiert die Daten und Texte... Bitte warten."):
            
            # Daten fuer KI vorbereiten
            daten_fuer_ai = auffaellige_daten.to_string()
            
            # Strategischer Prompt
            prompt = f"""
            Du bist ein erfahrener Corporate Controller und FP&A-Experte. 
            Hier sind die auffälligen Budgetabweichungen für diesen Monat, die unser System automatisch aus der Excel-Tabelle gefiltert hat:

            {daten_fuer_ai}

            Deine Aufgabe:
            Schreibe eine professionelle, handlungsorientierte Management-Zusammenfassung (Management Summary) auf Deutsch für den CFO.
            Achte dabei besonders auf:
            1. Sehr vage Begründungen in den Kommentaren (z.B. bei Reisekosten).
            2. Unplausible Kombinationen von Abteilung und Kostenkategorie (z.B. IT und Catering).
            3. Die höchsten absoluten und prozentualen Risiken.

            Strukturiere deinen Bericht in klare "Top-Risiken/Auffälligkeiten" mit konkreten Handlungsempfehlungen (z.B. Nachprüfung, Fehlkontierung prüfen).
            Keep it concise and professional.
            """
            
            # KI aufrufen
            bericht = ask_controlling_ai(prompt)
            
            # Bericht in einer schoenen Box anzeigen
            st.write("### 📝 Generierter Bericht für den CFO:")
            st.info(bericht)
