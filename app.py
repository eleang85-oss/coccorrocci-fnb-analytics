from sys import api_version
# Configurazione della pagina (ottimizzata per Mobile)
st.set_page_config(
    page_title="Coccorrocci F&B Dashboard",
    page_icon="🍷",
    layout="wide"
)

st.title("🍷 Coccorrocci - Management & AI Assistant")
st.caption ("Dashboard gestionale per il Ristorante e la Pizzeria del Campeggio")

# 2. Modello AI integrato (cached per velocità)
@st.cache_resource
def load_ai_model():
  model = RandomForestRegressor(n_estimators=50, random_state=42)
  X_train= np.array([
      [150, 28.0, 0], [200, 30.0, 1], [300, 32.0, 1], 
      [350, 34.0, 1], [100, 25.0, 0], [400, 35.0, 1], 
      [250, 29.0, 0], [120, 26.0, 0], [180, 27.0, 1]
  ])
  y_train = np.array([45, 65, 85, 95, 90, 110, 50, 5, 30])
  model.fit(X_train, y_train)
  return model

ai_model = load_ai_model()

# 3. Sidebar per la selezione funzionalità
st.sidebar.header("⚙️ Menu Gestione")
sezione = st.sidebar.radio("Scegli operazione:", ["📊 Inserimento & Margini Giornalieri", "🤖 Previsione AI Scorte"])

# ------------------------------------------------------------------------------
# SEZIONE 1 : CALCOLO MARGINI GIORNALIERI
# ------------------------------------------------------------------------------
if sezione == "📊 Inserimento & Margini Giornalieri":
  st.subheader("📊 Inserisci i dati di fine giornata")

  col1, col2 = st.columns(2)

  with col1:
    st.markdown("### 🍕 Ristorante & Asporto")
    coperti = st.number_input("Coperti serviti al ristorante", min_value=0, value=85, step=0.5)
    scontrino_rist = st.number_input("Scontrino medio ristorante (€)", min_value=0, value=25.0, step=0.5)
    ordini_asporto = st.number_input("Ordini Asporto / Pizzeria", min_value=0, value=40, step=5)
    scontrino_asporto = st.number_input("Scontrino medio Asporto (€)", min_value=0, value=13.0, step=0.5)

  with col2:
    st.markdown("### 🛒 Costi Materie Prime")
    food_cost = st.number_input("Spesa complessiva/bevande di oggi (€)", min_value=0, value=750.0, step=10)
    canone_annuo = 20000.0
    canone_giornaliero = canone_annuo/ 120

# Calcoli
  ricavo_rist = coperti * scontrino_rist
  ricavo_asp = ordini_asporto * scontrino_asporto
  ricavo_totale = ricavo_rist + ricavo_asp

  costo_personale = ricavo_totale * 0.28
  utenze_gestionale = ricavo_totale * 0.065
  ebitda_giornaliero = ricavo_totale - (food_cost + costo_personale + utenze_gestionale + canone_giornaliero)
  food_cost_pct = (food_cost / ricavo_totale * 100) if ricavo_totale > 0 else 0

  st.markdown("---")
  st.subheader("📈 Indicatori del Giorno")

# Schede Metriche (Stile App Mobile)
  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Fatturato totale", f"€ {ricavo_totale:.2f}")
  m2.metric("Incidenza Food Cost", f"{food_cost_pct:.1f}%", delta="- Target 30%" if food_cost_pct <= 30 else "+ Troppo Alto!", delta_color="inverse")
  m3.metric("Costo Personale Stima", f"€ {costo_personale:,.2f}")
  m4.metric("EBITDA Netto Giorno", f"€ {ebitda_giornaliero:,.2f}", delta="Utile Positivo" if ebitda_giornaliero > 0 else "In Perdita")

#Grafico a barre
  st.markdown("### 📉 Breakdown Incidenza Spese")
  df_chart = pd.DataFrame({
    "Voce": ["Ricavo Totale", "Food Cost", " Personale (28%)", "Utenze/Gesione", "EBITDA Netto"],
    "Importo (€)": [ricavo_totale, food_cost, costo_personale, utenze_gestione + canone_giornaliero, ebitda_giornaliero]
})
  st.bar_chart(df_chart.set_index("Voce"))

#-------------------------------------------------------------------------------
# SEZIONE 2: PREVISIONE AI SCORTE
#-------------------------------------------------------------------------------

else:
  st.subheader("🤖 Assistente AI: Previsione Coperti e Ordini Spesa")
  st.info("Inserisci le condizioni di domani per ricevere i consigli di approvvigionamento.")
    
  presenze = st.slider("Presenze totali stimate nel campeggio", min_value=50, max_value=600, value=350, step=10)
  temp = st.slider("Temperatura massima prevista (°C)", min_value=20.0, max_value=45.0, step=0.5)
  is_weekend = st.checkbox("E' un giorno del Weekend(Venerdì / Sabato / Domenica)?", value=True)

  if st.button("🔮 Calcola Previsione Scorte"):
    X_test = np.array([[presenze, temp, 1 if is_weekend else 0]])
    coperti_previsti = int(ai_model.predict(X_test)[0])
    kg_carne_pesce = round(coperti_previsti * 0.25, 1)
    panetti_pizza = int(coperti_previsti * 0.4)

    st.success("✅ Previsione elaborata dal modello Machine Learning!")
    c1, c2, c3 = st.columns(3)
    c1.metrics("Coperti Previsti Ristorante", f"{coperti_previsti}")
    c2.metrics("Carne/Pesce Consigliati", f"{kg_carne_pesce} kg")
    c3.metrics("Panetti Pizza da Preparare", f"{panetti_pizza} pezzi")

