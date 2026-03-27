"""
dashboard.py
============
Smart Water Quality Monitoring and Alert System
Streamlit Dashboard

Run with:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import shap
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

from remediation_engine import (
    get_recommendations,
    generate_report,
    batch_remediation,
    PRIORITY_COLOR,
    PRIORITY_ICON,
    REMEDIATION_KB,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='Smart Water Quality Monitor',
    page_icon='💧',
    layout='wide',
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .metric-box {
        background: white; border-radius: 12px;
        padding: 1.2rem 1rem; text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .metric-val   { font-size: 2rem; font-weight: 700; }
    .metric-lbl   { font-size: 0.82rem; color: #555; margin-top: 0.2rem; }
    .safe-color   { color: #2ecc71; }
    .marg-color   { color: #f39c12; }
    .unsafe-color { color: #e74c3c; }
    .section-header {
        font-size: 1.2rem; font-weight: 600;
        border-left: 4px solid #2980b9;
        padding-left: 0.7rem;
        margin: 1.2rem 0 0.8rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Load Model and Data ───────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open('water_quality_model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_data
def load_data():
    results = pd.read_excel('Water_Quality_Predictions_2023.xlsx')
    full    = pd.read_excel('Water_Quality_Full_Engineered.xlsx')
    return results, full

@st.cache_data
def compute_shap(_model_data, _full_df):
    feature_cols = _model_data['feature_cols']
    model        = _model_data['model']
    test_df      = _full_df[_full_df['Year'] == 2023].reset_index(drop=True)
    X_test       = test_df[feature_cols]
    explainer    = shap.TreeExplainer(model)
    shap_values  = explainer.shap_values(X_test)
    if isinstance(shap_values, list):
        shap_unsafe = shap_values[2]
    else:
        shap_unsafe = shap_values[:, :, 2]
    return shap_unsafe, X_test, test_df, explainer


# ── Load everything ───────────────────────────────────────────────────────────
try:
    model_data              = load_model()
    results_df, full_df     = load_data()
    shap_unsafe, X_test_df, test_df, explainer = compute_shap(model_data, full_df)
    FEATURE_COLS            = model_data['feature_cols']
    CLASS_NAMES             = model_data['class_names']
    results_df              = batch_remediation(results_df, shap_unsafe, FEATURE_COLS)
    DATA_LOADED             = True
except Exception as e:
    DATA_LOADED = False
    LOAD_ERROR  = str(e)


# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('### 💧 Water Quality Monitor')
    st.markdown('Smart Alert System for Water Supply')
    st.markdown('---')
    page = st.radio('Navigate', [
        '🏠 Overview',
        '📊 Analytics',
        '🚨 Alert System',
        '🔍 Station Inspector',
        '🏛️ Remediation Engine',
        '📥 Download Reports',
    ], label_visibility='collapsed')
    st.markdown('---')
    st.markdown('**Dataset:** NWMP 2019–2023')
    st.markdown('**Standard:** BIS IS 10500:2012')
    st.markdown('**Model:** XGBoost Classifier')

# ── Error Guard ───────────────────────────────────────────────────────────────
if not DATA_LOADED:
    st.error(
        f'Could not load required files. Make sure these are in the same folder:\n\n'
        f'- water_quality_model.pkl\n'
        f'- Water_Quality_Predictions_2023.xlsx\n'
        f'- Water_Quality_Full_Engineered.xlsx\n\n'
        f'Error: {LOAD_ERROR}'
    )
    st.stop()


# ═══════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════
if page == '🏠 Overview':
    st.markdown('## 💧 Smart Water Quality Monitoring and Alert System')
    st.markdown('**National Water Monitoring Programme | BIS IS 10500:2012 Compliant**')
    st.markdown('---')

    total      = len(results_df)
    n_safe     = (results_df['Predicted_Class'] == 'Safe').sum()
    n_marginal = (results_df['Predicted_Class'] == 'Marginal').sum()
    n_unsafe   = (results_df['Predicted_Class'] == 'Unsafe').sum()
    avg_wqi    = results_df['WQI'].mean()
    avg_conf   = results_df['Confidence_Pct'].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{total}</div>'
                    f'<div class="metric-lbl">Total Stations (2023)</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-val safe-color">{n_safe}</div>'
                    f'<div class="metric-lbl">✅ Safe</div></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="metric-val marg-color">{n_marginal}</div>'
                    f'<div class="metric-lbl">⚠️ Marginal</div></div>',
                    unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-box"><div class="metric-val unsafe-color">{n_unsafe}</div>'
                    f'<div class="metric-lbl">🚨 Unsafe</div></div>',
                    unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{avg_wqi:.0f}</div>'
                    f'<div class="metric-lbl">📈 Avg WQI Score</div></div>',
                    unsafe_allow_html=True)

    st.markdown('')
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Classification Distribution</div>',
                    unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=['Safe', 'Marginal', 'Unsafe'],
            values=[n_safe, n_marginal, n_unsafe],
            hole=0.45,
            marker_colors=['#2ecc71', '#f39c12', '#e74c3c'],
            textinfo='label+percent',
        ))
        fig.update_layout(height=300, margin=dict(t=10, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Top 10 Most Unsafe States</div>',
                    unsafe_allow_html=True)
        state_unsafe = (results_df[results_df['Predicted_Class'] == 'Unsafe']
                        .groupby('State').size()
                        .sort_values(ascending=True).tail(10))
        fig2 = go.Figure(go.Bar(
            x=state_unsafe.values, y=state_unsafe.index,
            orientation='h', marker_color='#e74c3c',
        ))
        fig2.update_layout(height=300, margin=dict(t=10, b=10),
                           xaxis_title='Unsafe Stations')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Top Pollutants Driving Unsafe Classification</div>',
                unsafe_allow_html=True)
    top_poll = (results_df[results_df['Predicted_Class'] == 'Unsafe']['Top_Pollutant']
                .value_counts())
    fig3 = px.bar(x=top_poll.index, y=top_poll.values,
                  color=top_poll.values, color_continuous_scale='Reds',
                  labels={'x': 'Pollutant', 'y': 'Number of Stations'})
    fig3.update_layout(height=280, margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — ANALYTICS
# ═══════════════════════════════════════════════════════════════
elif page == '📊 Analytics':
    st.markdown('## 📊 Water Quality Analytics')
    st.markdown('---')

    st.markdown('<div class="section-header">WQI Trend (2019–2023)</div>',
                unsafe_allow_html=True)
    yearly = full_df.groupby('Year')['WQI'].agg(['mean', 'median']).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yearly['Year'], y=yearly['mean'],
        mode='lines+markers+text', name='Mean WQI',
        line=dict(color='teal', width=2.5), marker=dict(size=8),
        text=yearly['mean'].round(1), textposition='top center',
    ))
    fig.add_trace(go.Scatter(
        x=yearly['Year'], y=yearly['median'],
        mode='lines+markers', name='Median WQI',
        line=dict(color='steelblue', width=2, dash='dash'),
    ))
    fig.update_layout(height=320, xaxis_title='Year', yaxis_title='WQI Score',
                      legend=dict(orientation='h', y=1.1))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">WQI by Water Body Type</div>',
                    unsafe_allow_html=True)
        fig2 = px.box(full_df, x='Water_Body_Type', y='WQI',
                      color='Water_Body_Type',
                      color_discrete_sequence=['#2ecc71', '#3498db', '#e74c3c', '#9b59b6'])
        fig2.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Class Distribution by Year</div>',
                    unsafe_allow_html=True)
        year_class = (full_df.groupby(['Year', 'BIS_Label'])
                      .size().reset_index(name='Count'))
        fig3 = px.bar(year_class, x='Year', y='Count', color='BIS_Label',
                      color_discrete_map={
                          'Safe': '#2ecc71', 'Marginal': '#f39c12', 'Unsafe': '#e74c3c'},
                      barmode='group')
        fig3.update_layout(height=320, legend_title='Class')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-header">Parameter Distribution by Safety Class</div>',
                unsafe_allow_html=True)
    param_choice = st.selectbox('Select parameter', [
        'DO', 'pH', 'BOD', 'Nitrate',
        'Conductivity', 'Fecal_Coliform', 'Total_Coliform',
    ])
    fig4 = px.histogram(full_df, x=param_choice, color='BIS_Label',
                        color_discrete_map={
                            'Safe': '#2ecc71', 'Marginal': '#f39c12', 'Unsafe': '#e74c3c'},
                        barmode='overlay', opacity=0.7, nbins=50)
    fig4.update_layout(height=300)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">State-Level Summary</div>',
                unsafe_allow_html=True)
    state_summary = (full_df.groupby('State').agg(
        Total=('Station_Code', 'count'),
        Avg_WQI=('WQI', 'mean'),
        Unsafe=('BIS_Class', lambda x: (x == 2).sum()),
    ).reset_index())
    state_summary['Unsafe_%'] = (state_summary['Unsafe'] /
                                  state_summary['Total'] * 100).round(1)
    state_summary['Avg_WQI'] = state_summary['Avg_WQI'].round(1)
    st.dataframe(state_summary.sort_values('Unsafe_%', ascending=False),
                 use_container_width=True, height=350)


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — ALERT SYSTEM
# ═══════════════════════════════════════════════════════════════
elif page == '🚨 Alert System':
    st.markdown('## 🚨 Water Quality Alert System')
    st.markdown('Stations requiring immediate government attention.')
    st.markdown('---')

    col1, col2, col3 = st.columns(3)
    with col1:
        state_f = st.selectbox('State', ['All'] + sorted(results_df['State'].unique()))
    with col2:
        type_f  = st.selectbox('Water Body Type',
                               ['All'] + sorted(results_df['Water_Body_Type'].unique()))
    with col3:
        class_f = st.selectbox('Classification', ['All', 'Unsafe', 'Marginal', 'Safe'])

    filtered = results_df.copy()
    if state_f != 'All':
        filtered = filtered[filtered['State'] == state_f]
    if type_f != 'All':
        filtered = filtered[filtered['Water_Body_Type'] == type_f]
    if class_f != 'All':
        filtered = filtered[filtered['Predicted_Class'] == class_f]

    st.markdown(f'**Showing {len(filtered)} stations**')

    def color_class(val):
        if val == 'Unsafe':
            return 'background-color:#fdecea; color:#c0392b; font-weight:bold'
        elif val == 'Marginal':
            return 'background-color:#fef9e7; color:#d68910; font-weight:bold'
        return 'background-color:#eafaf1; color:#1e8449'

    cols = ['Station_Name', 'State', 'Water_Body_Type',
            'WQI', 'Predicted_Class', 'Confidence_Pct',
            'Top_Pollutant', 'Immediate_Actions']

    styled = (filtered[cols].style
              .applymap(color_class, subset=['Predicted_Class'])
              .format({'WQI': '{:.1f}', 'Confidence_Pct': '{:.1f}%'}))
    st.dataframe(styled, use_container_width=True, height=450)

    if (filtered['Predicted_Class'] == 'Unsafe').sum() > 0:
        st.markdown('<div class="section-header">Unsafe Stations by State</div>',
                    unsafe_allow_html=True)
        unsafe_state = (filtered[filtered['Predicted_Class'] == 'Unsafe']
                        .groupby('State').size().sort_values(ascending=False))
        fig = px.bar(x=unsafe_state.index, y=unsafe_state.values,
                     color=unsafe_state.values, color_continuous_scale='Reds',
                     labels={'x': 'State', 'y': 'Unsafe Stations'})
        fig.update_layout(height=300, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — STATION INSPECTOR
# ═══════════════════════════════════════════════════════════════
elif page == '🔍 Station Inspector':
    st.markdown('## 🔍 Station Inspector')
    st.markdown('Inspect any station — parameters, prediction, and SHAP explanation.')
    st.markdown('---')

    col1, col2 = st.columns(2)
    with col1:
        state_sel = st.selectbox('State', sorted(results_df['State'].unique()))
    with col2:
        stations  = results_df[results_df['State'] == state_sel]['Station_Name'].tolist()
        stn_sel   = st.selectbox('Station', stations)

    row_idx = results_df[
        (results_df['State'] == state_sel) &
        (results_df['Station_Name'] == stn_sel)
    ].index[0]

    row   = results_df.loc[row_idx]
    x_row = X_test_df.iloc[row_idx]

    cls   = row['Predicted_Class']
    color = '#2ecc71' if cls == 'Safe' else ('#f39c12' if cls == 'Marginal' else '#e74c3c')
    icon  = '✅' if cls == 'Safe' else ('⚠️' if cls == 'Marginal' else '🚨')

    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:1.2rem 1.5rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:1rem;">
        <h3 style="margin:0 0 0.3rem 0;">{stn_sel}</h3>
        <p style="margin:0;color:#555;">{row['State']} | {row['Water_Body_Type']}</p>
        <p style="margin:0.5rem 0 0 0;">
            <span style="background:{color};color:white;padding:0.3rem 0.8rem;
                         border-radius:20px;font-weight:bold;">{icon} {cls}</span>
            &nbsp;&nbsp;WQI: <b>{row['WQI']:.1f}</b> ({row['WQI_Category']})
            &nbsp;&nbsp;Confidence: <b>{row['Confidence_Pct']:.1f}%</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Probability gauges
    c1, c2, c3 = st.columns(3)
    for col_widget, label, prob, clr in zip(
        [c1, c2, c3],
        ['Safe', 'Marginal', 'Unsafe'],
        [row['P_Safe'], row['P_Marginal'], row['P_Unsafe']],
        ['#2ecc71', '#f39c12', '#e74c3c'],
    ):
        with col_widget:
            fig_g = go.Figure(go.Indicator(
                mode='gauge+number',
                value=prob * 100,
                title={'text': label, 'font': {'size': 14}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': clr}},
                number={'suffix': '%', 'font': {'size': 20}},
            ))
            fig_g.update_layout(height=200, margin=dict(t=30, b=10, l=20, r=20))
            st.plotly_chart(fig_g, use_container_width=True)

    # Parameter readings
    st.markdown('<div class="section-header">Parameter Readings vs BIS Limits</div>',
                unsafe_allow_html=True)
    BIS_ACC  = {'Temperature': 25, 'DO': 6, 'pH': 8.5,
                'Conductivity': 750, 'BOD': 2, 'Nitrate': 45,
                'Fecal_Coliform': 2.2, 'Total_Coliform': 10}
    BIS_PERM = {'Temperature': 40, 'DO': 4, 'pH': 9.2,
                'Conductivity': 3000, 'BOD': 5, 'Nitrate': 100,
                'Fecal_Coliform': 500, 'Total_Coliform': 500}

    param_rows = []
    for p in BIS_ACC:
        val  = x_row[p]
        acc  = BIS_ACC[p]
        perm = BIS_PERM[p]
        if p == 'DO':
            status = '✅ Safe' if val >= acc else ('⚠️ Marginal' if val >= perm else '🚨 Unsafe')
        elif p == 'pH':
            status = '✅ Safe' if 6.5 <= val <= acc else ('⚠️ Marginal' if 6.5 <= val <= perm else '🚨 Unsafe')
        else:
            status = '✅ Safe' if val <= acc else ('⚠️ Marginal' if val <= perm else '🚨 Unsafe')
        param_rows.append({'Parameter': p, 'Value': round(val, 2),
                           'Acceptable': acc, 'Permissible': perm, 'Status': status})
    st.dataframe(pd.DataFrame(param_rows), use_container_width=True, hide_index=True)

    # SHAP waterfall
    st.markdown('<div class="section-header">SHAP Explanation</div>',
                unsafe_allow_html=True)
    try:
        shap_all = explainer.shap_values(X_test_df)
        if isinstance(shap_all, list):
            sv = shap_all[2][row_idx]
            ev = explainer.expected_value[2]
        else:
            sv = shap_all[row_idx, :, 2]
            ev = explainer.expected_value[2]

        shap_exp = shap.Explanation(
            values=sv, base_values=ev,
            data=x_row.values, feature_names=FEATURE_COLS,
        )
        shap.waterfall_plot(shap_exp, show=False, max_display=15)
        st.pyplot(plt.gcf())
        plt.close()
    except Exception as e:
        st.warning(f'SHAP plot unavailable: {e}')


# ═══════════════════════════════════════════════════════════════
# PAGE 5 — REMEDIATION ENGINE
# ═══════════════════════════════════════════════════════════════
elif page == '🏛️ Remediation Engine':
    st.markdown('## 🏛️ Remediation Recommendation Engine')
    st.markdown('Government-actionable steps to improve water quality at each station.')
    st.markdown('---')

    col1, col2 = st.columns(2)
    with col1:
        state_sel = st.selectbox('State', sorted(results_df['State'].unique()))
    with col2:
        stations  = results_df[results_df['State'] == state_sel]['Station_Name'].tolist()
        stn_sel   = st.selectbox('Station', stations)

    threshold = st.slider(
        'SHAP Contribution Threshold — pollutants above this value are flagged',
        min_value=0.01, max_value=0.30, value=0.05, step=0.01,
    )

    row_idx  = results_df[
        (results_df['State'] == state_sel) &
        (results_df['Station_Name'] == stn_sel)
    ].index[0]

    row      = results_df.loc[row_idx]
    shap_row = shap_unsafe[row_idx]
    recs     = get_recommendations(shap_row, FEATURE_COLS, threshold)

    cls   = row['Predicted_Class']
    color = '#2ecc71' if cls == 'Safe' else ('#f39c12' if cls == 'Marginal' else '#e74c3c')
    icon  = '✅' if cls == 'Safe' else ('⚠️' if cls == 'Marginal' else '🚨')

    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:1rem 1.4rem;
                box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:1rem;">
        <b>{stn_sel}</b> | {row['State']} | WQI: {row['WQI']:.1f}
        &nbsp;
        <span style="background:{color};color:white;padding:0.2rem 0.7rem;
                     border-radius:15px;font-size:0.85rem;">{icon} {cls}</span>
        &nbsp; Confidence: {row['Confidence_Pct']:.1f}%
    </div>
    """, unsafe_allow_html=True)

    if not recs['active_pollutants']:
        st.success('✅ No pollutants above the threshold. Water quality is within acceptable limits.')
    else:
        st.markdown('<div class="section-header">Active Pollutants Identified</div>',
                    unsafe_allow_html=True)
        poll_names = [p for p, _ in recs['active_pollutants']]
        poll_vals  = [v for _, v in recs['active_pollutants']]
        fig = go.Figure(go.Bar(
            x=[abs(v) for v in poll_vals], y=poll_names,
            orientation='h',
            marker_color=['#e74c3c' if v > 0 else '#3498db' for v in poll_vals],
            text=[f'{v:+.3f}' for v in poll_vals],
            textposition='outside',
        ))
        fig.update_layout(
            height=max(200, len(poll_names) * 50),
            xaxis_title='|SHAP Value|',
            margin=dict(t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

        imm   = len(recs['priority_summary']['Immediate'])
        short = len(recs['priority_summary']['Short Term'])
        long_ = len(recs['priority_summary']['Long Term'])
        c1, c2, c3 = st.columns(3)
        c1.metric('🚨 Immediate Actions', imm)
        c2.metric('⚠️ Short Term Actions', short)
        c3.metric('🔵 Long Term Actions', long_)

        for priority, icon_p in [('Immediate', '🚨'), ('Short Term', '⚠️'), ('Long Term', '🔵')]:
            actions = recs['priority_summary'][priority]
            if not actions:
                continue
            st.markdown(f'<div class="section-header">{icon_p} {priority} Actions</div>',
                        unsafe_allow_html=True)
            for a in actions:
                with st.expander(
                    f"**[{a['pollutant']}]** — {a['action']}",
                    expanded=(priority == 'Immediate'),
                ):
                    st.markdown(f"**🏢 Department:** {a['department']}")
                    st.markdown(f"**📋 Action:** {a['action']}")
                    st.markdown(f"**📝 Details:** {a['detail']}")
                    kb = REMEDIATION_KB[a['pollutant']]
                    st.markdown(f"**ℹ️ About {a['pollutant']}:** {kb['description']}")
                    st.markdown(f"**⚕️ Health Risk:** {kb['health_risk']}")
                    st.markdown('**🔍 Common Causes:**')
                    for cause in kb['cause']:
                        st.markdown(f'- {cause}')

        st.markdown('---')
        st.markdown('### 📄 Download Station Remediation Report')
        station_info = {
            'Station_Name'   : stn_sel,
            'State'          : row['State'],
            'WQI'            : round(row['WQI'], 1),
            'Predicted_Class': row['Predicted_Class'],
            'Confidence_Pct' : row['Confidence_Pct'],
        }
        report_text = generate_report(station_info, shap_row, FEATURE_COLS, threshold)
        st.download_button(
            label     = '📥 Download Remediation Report (.txt)',
            data      = report_text,
            file_name = f"Remediation_{stn_sel[:30].replace(' ', '_')}.txt",
            mime      = 'text/plain',
        )


# ═══════════════════════════════════════════════════════════════
# PAGE 6 — DOWNLOAD REPORTS
# ═══════════════════════════════════════════════════════════════
elif page == '📥 Download Reports':
    st.markdown('## 📥 Download Reports')
    st.markdown('---')

    st.markdown('### 📊 Full Predictions Report (2023)')
    st.dataframe(results_df, use_container_width=True, height=350)

    from io import BytesIO
    buffer = BytesIO()
    results_df.to_excel(buffer, index=False)
    st.download_button(
        label     = '📥 Download Full Predictions as Excel',
        data      = buffer.getvalue(),
        file_name = 'Water_Quality_Predictions_2023.xlsx',
        mime      = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

    st.markdown('---')
    st.markdown('### 🏛️ Batch Remediation Report — All Unsafe Stations')

    unsafe_df = results_df[results_df['Predicted_Class'] == 'Unsafe'].reset_index(drop=True)
    st.info(f'Will generate reports for {len(unsafe_df)} unsafe stations.')

    if st.button('Generate Batch Report'):
        all_reports = []
        bar = st.progress(0)
        for i, row in unsafe_df.iterrows():
            orig_idx = results_df[results_df['Station_Name'] == row['Station_Name']].index[0]
            info = {
                'Station_Name'   : row['Station_Name'],
                'State'          : row['State'],
                'WQI'            : round(row['WQI'], 1),
                'Predicted_Class': row['Predicted_Class'],
                'Confidence_Pct' : row['Confidence_Pct'],
            }
            all_reports.append(generate_report(info, shap_unsafe[orig_idx], FEATURE_COLS))
            bar.progress((i + 1) / len(unsafe_df))

        batch_report = '\n\n'.join(all_reports)
        st.download_button(
            label     = '📥 Download Batch Remediation Report',
            data      = batch_report,
            file_name = 'Batch_Remediation_Report_2023.txt',
            mime      = 'text/plain',
        )
        st.success('✅ Report ready!')
