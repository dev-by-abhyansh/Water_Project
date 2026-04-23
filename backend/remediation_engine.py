"""
remediation_engine.py
=====================
Remediation Recommendation Engine for the
Smart Water Quality Monitoring and Alert System.

Given a station's SHAP values and parameter readings,
this module identifies all pollutants above a contribution
threshold and returns prioritised, government-actionable
recommendations for each one.

Usage:
    from remediation_engine import get_recommendations, generate_report
"""

# ── Threshold: minimum absolute SHAP value to flag a pollutant ───────────────
SHAP_THRESHOLD = 0.05   # pollutants contributing less than this are ignored


# ── Remediation Knowledge Base ────────────────────────────────────────────────
# Structure per parameter:
#   'description' : plain-language explanation of what this parameter means
#   'cause'       : common real-world causes of elevated levels
#   'health_risk' : health impact on humans
#   'actions'     : list of dicts, each with:
#       'priority'    : 'Immediate' | 'Short Term' | 'Long Term'
#       'department'  : responsible government department
#       'action'      : the specific action to take
#       'detail'      : more detail on how/why

REMEDIATION_KB = {

    'Fecal_Coliform': {
        'description': 'Fecal Coliform bacteria indicate contamination from human or animal waste.',
        'cause': [
            'Open defecation near the water body',
            'Untreated sewage discharge into the water body',
            'Animal waste runoff from nearby farms or grazing land',
            'Leaking septic tanks or drainage systems',
        ],
        'health_risk': 'Causes severe waterborne diseases including cholera, typhoid, dysentery, and gastroenteritis.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'Public Health Engineering Department (PHED)',
                'action'    : 'Issue a public health advisory for the affected area',
                'detail'    : 'Prohibit use of this water body for drinking, bathing, or irrigation immediately. Notify district health officer.',
            },
            {
                'priority'  : 'Immediate',
                'department': 'Urban Local Body / Gram Panchayat',
                'action'    : 'Deploy mobile chlorination or disinfection units at the water intake point',
                'detail'    : 'Chlorine dose of 0.5 mg/L residual to be maintained. Test daily until levels drop below BIS limits.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Swachh Bharat Mission (SBM) / District Administration',
                'action'    : 'Survey and eliminate open defecation zones within 1 km of the water body',
                'detail'    : 'Identify households without toilets, fast-track construction under SBM-Grameen, enforce no-open-defecation zones.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'State Pollution Control Board (SPCB)',
                'action'    : 'Inspect and repair all sewage outfalls and drainage lines discharging near the water body',
                'detail'    : 'Use CCTV pipe inspection where needed. Issue compliance notices to defaulting local bodies.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'Jal Shakti Ministry / State Urban Development',
                'action'    : 'Construct Sewage Treatment Plant (STP) for the catchment area',
                'detail'    : 'Design STP capacity based on population load. Target tertiary treatment to achieve <10 MPN/100ml at outlet.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'Animal Husbandry Department',
                'action'    : 'Establish regulated grazing buffer zones and animal waste management systems',
                'detail'    : 'Minimum 200m no-grazing buffer. Provide biogas units for cattle waste management in nearby villages.',
            },
        ],
    },

    'Total_Coliform': {
        'description': 'Total Coliform indicates general microbial contamination from soil, vegetation, or animal waste.',
        'cause': [
            'Surface runoff carrying soil bacteria into the water body',
            'Decomposing organic matter in and around the water body',
            'Animal waste and agricultural runoff',
            'Inadequate water treatment at supply points',
        ],
        'health_risk': 'Indicator of general contamination risk. High levels suggest the water is unsafe to drink without treatment.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'Public Health Engineering Department (PHED)',
                'action'    : 'Strengthen chlorination at water treatment plants drawing from this source',
                'detail'    : 'Ensure residual chlorine of 0.2 mg/L at consumer end. Increase sampling frequency to daily.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Forest and Environment Department',
                'action'    : 'Develop vegetative buffer strips around the water body',
                'detail'    : 'Plant native grass and shrub species in a 50m buffer zone to filter runoff before it enters the water body.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'District Collector / Irrigation Department',
                'action'    : 'Reduce organic waste dumping near the water body',
                'detail'    : 'Install fencing and signage. Establish waste collection points away from the shore. Conduct awareness drives.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'Jal Shakti / State Water Quality Lab',
                'action'    : 'Install real-time online water quality monitoring sensors at the station',
                'detail'    : 'IoT-based sensors for coliform, pH, turbidity. Data to be fed into state water quality dashboard for continuous surveillance.',
            },
        ],
    },

    'BOD': {
        'description': 'BOD (Biological Oxygen Demand) measures the amount of oxygen consumed by organic matter decomposition.',
        'cause': [
            'Industrial effluent discharge (food processing, textiles, paper mills)',
            'Untreated or partially treated sewage inflow',
            'Agricultural runoff with high organic content',
            'Decomposition of algae due to eutrophication',
        ],
        'health_risk': 'High BOD depletes dissolved oxygen, killing aquatic life and making water anaerobic and foul-smelling.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'State Pollution Control Board (SPCB)',
                'action'    : 'Identify and seal illegal industrial discharge points around the water body',
                'detail'    : 'Conduct surprise inspections of industries within 2 km. Issue closure notices to violators under Water (Prevention and Control of Pollution) Act, 1974.',
            },
            {
                'priority'  : 'Immediate',
                'department': 'Irrigation / Water Resources Department',
                'action'    : 'Deploy surface aerators to increase dissolved oxygen levels',
                'detail'    : 'Install paddle wheel or fountain aerators. Target minimum DO of 4 mg/L throughout the water body.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'SPCB / Industries Department',
                'action'    : 'Enforce Zero Liquid Discharge (ZLD) norms for all industries in the catchment',
                'detail'    : 'Industries must treat effluent to meet IS 2490 standards before discharge. Conduct monthly third-party audits.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Urban Local Body',
                'action'    : 'Upgrade or repair existing Sewage Treatment Plants in the catchment area',
                'detail'    : 'Ensure biological treatment stage is operational. Target BOD < 30 mg/L at STP outlet as per CPCB norms.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'National Mission for Clean Ganga (NMCG) / State Equivalent',
                'action'    : 'Implement constructed wetland or phytoremediation systems at inflow points',
                'detail'    : 'Constructed wetlands using Phragmites, Typha species can reduce BOD by 70–90%. Low cost, sustainable solution for rural areas.',
            },
        ],
    },

    'DO': {
        'description': 'Dissolved Oxygen (DO) is the amount of oxygen dissolved in water. Low DO indicates pollution.',
        'cause': [
            'High organic load causing microbial oxygen consumption',
            'Excessive algal blooms (eutrophication)',
            'High temperature reducing oxygen solubility',
            'Industrial thermal discharges',
        ],
        'health_risk': 'Low DO kills fish and aquatic organisms, creates anaerobic conditions, produces toxic gases like H2S.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'Fisheries / Water Resources Department',
                'action'    : 'Install emergency aeration equipment',
                'detail'    : 'Deploy mechanical aerators immediately if DO falls below 4 mg/L. Critical for preventing fish kills.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Agriculture Department',
                'action'    : 'Control nutrient runoff to prevent algal blooms',
                'detail'    : 'Promote balanced fertilizer use. Establish nutrient management plans for farms within 1 km of the water body.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'SPCB',
                'action'    : 'Identify and stop thermal discharges from industries',
                'detail'    : 'Thermal power plants and factories must cool effluent to within 5°C of ambient water temperature before discharge.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'Forest Department / District Administration',
                'action'    : 'Restore riparian vegetation along the water body shoreline',
                'detail'    : 'Native tree and shrub planting provides shade (reduces temperature), filters runoff, and stabilises banks.',
            },
        ],
    },

    'Nitrate': {
        'description': 'Nitrate contamination is primarily caused by agricultural fertilizers and sewage leaching into water.',
        'cause': [
            'Excessive use of nitrogenous fertilizers in nearby farmland',
            'Leaching from septic tanks and latrines',
            'Industrial effluents from fertilizer or food processing plants',
            'Animal waste decomposition',
        ],
        'health_risk': 'Causes blue baby syndrome (methemoglobinemia) in infants. Linked to cancer risk in adults with long-term exposure.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'District Health Department',
                'action'    : 'Issue advisory against using this water for infant feeding or formula preparation',
                'detail'    : 'Nitrate above 45 mg/L is dangerous for infants under 6 months. Distribute safe water supply in affected villages.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Agriculture Department / Krishi Vigyan Kendra',
                'action'    : 'Promote precision farming and balanced fertilizer application in the catchment area',
                'detail'    : 'Soil testing before fertilizer application. Promote use of organic manure and slow-release fertilizers. Train farmers within 2 km radius.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Groundwater Department',
                'action'    : 'Establish nitrate monitoring network for groundwater in the area',
                'detail'    : 'Test all drinking water wells within 1 km quarterly. Map high-risk zones for agricultural intensification.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'Agriculture / Environment Department',
                'action'    : 'Create mandatory buffer zones between agricultural fields and the water body',
                'detail'    : 'Minimum 50m no-fertilizer buffer. Plant nitrogen-absorbing crops (legumes) or grass strips in the buffer zone.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'Jal Shakti / PHED',
                'action'    : 'Install ion-exchange or reverse osmosis treatment at community water supply points',
                'detail'    : 'Centralised treatment plants with nitrate removal capacity for villages drawing water from affected sources.',
            },
        ],
    },

    'Conductivity': {
        'description': 'Conductivity measures dissolved salts and ions in water. High conductivity indicates industrial or agricultural pollution.',
        'cause': [
            'Industrial effluents with high dissolved solids (mining, chemicals, textiles)',
            'Irrigation return flows carrying salts',
            'Saline intrusion in coastal areas',
            'Road runoff with de-icing salts',
        ],
        'health_risk': 'High conductivity makes water unpalatable and can damage kidneys with prolonged consumption.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'SPCB',
                'action'    : 'Identify and sample industries discharging high TDS effluent in the catchment',
                'detail'    : 'Check compliance with Total Dissolved Solids limit of 2100 mg/L for industrial discharge under IS 2490.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Mining Department / SPCB',
                'action'    : 'Audit mining and quarrying operations near the water body for leachate control',
                'detail'    : 'Mining operations must have lined leachate collection systems. Conduct water quality testing upstream and downstream of mining zones.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Irrigation Department',
                'action'    : 'Improve irrigation efficiency to reduce saline return flows',
                'detail'    : 'Promote drip and sprinkler irrigation. Reduce waterlogging which concentrates salts and leads to saline drainage.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'PHED / Jal Shakti',
                'action'    : 'Install Reverse Osmosis (RO) treatment systems for community water supply',
                'detail'    : 'Community RO plants effective for TDS above 1000 mg/L. Solar-powered units suitable for remote villages.',
            },
        ],
    },

    'pH': {
        'description': 'pH measures acidity or alkalinity of water. Values outside 6.5–8.5 indicate chemical contamination.',
        'cause': [
            'Acid rain from industrial air pollution',
            'Mining drainage (acid mine drainage)',
            'Industrial effluents (acidic or alkaline)',
            'Excessive algal growth causing pH spikes',
        ],
        'health_risk': 'Extreme pH causes corrosion of pipes leading to heavy metal leaching. Affects taste and can damage mucous membranes.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'PHED / Water Treatment Authority',
                'action'    : 'Adjust pH at the water treatment plant using lime dosing (for acidic water) or CO2 (for alkaline)',
                'detail'    : 'Target pH of 7.0–7.5 at treatment plant outlet. Continuous pH monitoring required at inlet and outlet.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'SPCB',
                'action'    : 'Inspect industries for acidic or alkaline effluent discharge',
                'detail'    : 'All industrial effluent must have pH between 5.5–9.0 before discharge. Neutralisation tanks to be mandatory.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'Environment Department / CPCB',
                'action'    : 'Monitor and control acid rain sources through industrial emission controls',
                'detail'    : 'Enforce SO2 and NOx emission limits for industries. Install flue gas desulfurisation systems in thermal plants.',
            },
        ],
    },

    'Temperature': {
        'description': 'Elevated water temperature reduces oxygen solubility and promotes harmful bacterial and algal growth.',
        'cause': [
            'Thermal discharge from power plants or industries',
            'Deforestation removing shade cover from water bodies',
            'Climate change increasing ambient temperatures',
            'Dark-coloured industrial effluents absorbing more heat',
        ],
        'health_risk': 'High temperature accelerates microbial growth, promotes algal blooms, and reduces DO — indirectly worsening all other parameters.',
        'actions': [
            {
                'priority'  : 'Immediate',
                'department': 'SPCB',
                'action'    : 'Enforce thermal discharge limits for power plants and industries',
                'detail'    : 'Effluent temperature must not raise receiving water temperature by more than 5°C above ambient. Issue show-cause notices to violators.',
            },
            {
                'priority'  : 'Short Term',
                'department': 'Forest Department',
                'action'    : 'Plant shade trees along the shoreline to reduce solar heating',
                'detail'    : 'Dense native tree planting on the south and west shores provides maximum afternoon shade. Target 70% canopy cover within 3 years.',
            },
            {
                'priority'  : 'Long Term',
                'department': 'District Administration / Climate Cell',
                'action'    : 'Include water body temperature management in district climate action plan',
                'detail'    : 'Model temperature rise projections for 2030–2050. Plan infrastructure (shading, aeration) accordingly.',
            },
        ],
    },
}


# ── Priority color mapping (for dashboard display) ────────────────────────────
PRIORITY_COLOR = {
    'Immediate'  : '#e74c3c',   # red
    'Short Term' : '#f39c12',   # orange
    'Long Term'  : '#3498db',   # blue
}

PRIORITY_ICON = {
    'Immediate'  : '🚨',
    'Short Term' : '⚠️',
    'Long Term'  : '🔵',
}


# ── Core Functions ────────────────────────────────────────────────────────────

def get_active_pollutants(shap_row, feature_names, threshold=SHAP_THRESHOLD):
    """
    Given a 1D array of SHAP values for a single sample (Unsafe class),
    return a sorted list of (feature_name, shap_value) tuples
    where abs(shap_value) >= threshold.

    Parameters
    ----------
    shap_row     : np.ndarray, shape (n_features,)
    feature_names: list of str
    threshold    : float

    Returns
    -------
    list of (feature_name, shap_value) sorted by abs(shap_value) descending
    """
    pairs = [
        (name, float(val))
        for name, val in zip(feature_names, shap_row)
        if abs(float(val)) >= threshold and name in REMEDIATION_KB
    ]
    pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    return pairs


def get_recommendations(shap_row, feature_names, threshold=SHAP_THRESHOLD):
    """
    Return a structured recommendations dict for a single water station.

    Returns
    -------
    dict with keys:
        'active_pollutants' : list of (name, shap_val)
        'recommendations'   : dict mapping pollutant name → list of action dicts
        'priority_summary'  : dict mapping priority level → list of actions
        'top_pollutant'     : str, name of the most impactful pollutant
    """
    active = get_active_pollutants(shap_row, feature_names, threshold)

    if not active:
        return {
            'active_pollutants' : [],
            'recommendations'   : {},
            'priority_summary'  : {'Immediate': [], 'Short Term': [], 'Long Term': []},
            'top_pollutant'     : None,
        }

    recommendations  = {}
    priority_summary = {'Immediate': [], 'Short Term': [], 'Long Term': []}

    for param_name, shap_val in active:
        kb     = REMEDIATION_KB[param_name]
        actions = kb['actions']
        recommendations[param_name] = {
            'shap_value'  : shap_val,
            'description' : kb['description'],
            'cause'       : kb['cause'],
            'health_risk' : kb['health_risk'],
            'actions'     : actions,
        }
        for action in actions:
            priority_summary[action['priority']].append({
                'pollutant' : param_name,
                **action,
            })

    return {
        'active_pollutants' : active,
        'recommendations'   : recommendations,
        'priority_summary'  : priority_summary,
        'top_pollutant'     : active[0][0] if active else None,
    }


def generate_report(station_info, shap_row, feature_names,
                    threshold=SHAP_THRESHOLD):
    """
    Generate a plain-text remediation report for a station.

    Parameters
    ----------
    station_info : dict with keys: Station_Name, State, WQI,
                   Predicted_Class, Confidence_Pct
    shap_row     : np.ndarray
    feature_names: list of str

    Returns
    -------
    str — formatted report text
    """
    recs   = get_recommendations(shap_row, feature_names, threshold)
    lines  = []

    lines.append('=' * 70)
    lines.append('  WATER QUALITY REMEDIATION REPORT')
    lines.append('  Smart Water Quality Monitoring and Alert System')
    lines.append('=' * 70)
    lines.append(f"  Station   : {station_info.get('Station_Name', 'N/A')}")
    lines.append(f"  State     : {station_info.get('State', 'N/A')}")
    lines.append(f"  WQI Score : {station_info.get('WQI', 'N/A')}")
    lines.append(f"  Status    : {station_info.get('Predicted_Class', 'N/A')}")
    lines.append(f"  Confidence: {station_info.get('Confidence_Pct', 'N/A')}%")
    lines.append('=' * 70)

    if not recs['active_pollutants']:
        lines.append('\n  ✅ No parameters above remediation threshold.')
        lines.append('  Water quality is within acceptable limits.')
        return '\n'.join(lines)

    lines.append('\n  IDENTIFIED POLLUTANTS (above SHAP threshold):')
    for name, val in recs['active_pollutants']:
        direction = 'pushing towards Unsafe' if val > 0 else 'reducing risk'
        lines.append(f'    • {name:<22} SHAP = {val:+.4f}  ({direction})')

    for priority in ['Immediate', 'Short Term', 'Long Term']:
        actions = recs['priority_summary'][priority]
        if not actions:
            continue
        icon = PRIORITY_ICON[priority]
        lines.append(f'\n  {icon} {priority.upper()} ACTIONS:')
        lines.append('  ' + '-' * 60)
        for a in actions:
            lines.append(f"  [{a['pollutant']}]")
            lines.append(f"  Department : {a['department']}")
            lines.append(f"  Action     : {a['action']}")
            lines.append(f"  Detail     : {a['detail']}")
            lines.append('')

    lines.append('=' * 70)
    lines.append('  Report generated by Smart Water Quality Monitoring System')
    lines.append('=' * 70)

    return '\n'.join(lines)


def batch_remediation(results_df, shap_vals_unsafe, feature_names,
                      threshold=SHAP_THRESHOLD):
    """
    Run remediation engine across all stations in results_df.

    Parameters
    ----------
    results_df      : pd.DataFrame with prediction results
    shap_vals_unsafe: np.ndarray shape (n_samples, n_features) for Unsafe class
    feature_names   : list of str

    Returns
    -------
    results_df with added columns:
        Active_Pollutants, Top_Pollutant, Immediate_Actions,
        Short_Term_Actions, Long_Term_Actions
    """
    df = results_df.copy()

    active_list  = []
    top_list     = []
    imm_list     = []
    short_list   = []
    long_list    = []

    for i in range(len(df)):
        recs = get_recommendations(shap_vals_unsafe[i], feature_names, threshold)
        active_list.append(', '.join([p for p, _ in recs['active_pollutants']]))
        top_list.append(recs['top_pollutant'] or 'None')
        imm_list.append(len(recs['priority_summary']['Immediate']))
        short_list.append(len(recs['priority_summary']['Short Term']))
        long_list.append(len(recs['priority_summary']['Long Term']))

    df['Active_Pollutants']   = active_list
    df['Top_Pollutant']       = top_list
    df['Immediate_Actions']   = imm_list
    df['Short_Term_Actions']  = short_list
    df['Long_Term_Actions']   = long_list

    return df
