import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.spatial.distance import cdist
import os

# Set page configurations
st.set_page_config(
    page_title="Final Score Predictor - ML & GNNs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# CUSTOM STYLING (Premium Look)
# ----------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2E5BFF, #FF3D71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.15rem;
        color: #707E94;
        margin-bottom: 2.5rem;
    }
    
    .card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        backdrop-filter: blur(4px);
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border-top: 5px solid;
    }
    
    .metric-val {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .metric-name {
        font-size: 0.95rem;
        text-transform: uppercase;
        color: #6C7A89;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# DEFINE MODEL CLASSES (Must match training code)
# ----------------------------------------------------
class MLPRegressor(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.out = nn.Linear(32, 1)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.out(x)

class GraphSAGE(nn.Module):
    def __init__(self, in_dim, hidden=64):
        super().__init__()
        self.fc1 = nn.Linear(in_dim * 2, hidden)
        self.fc2 = nn.Linear(hidden, 32)
        self.out = nn.Linear(32, 1)
        
    def forward(self, x, adj):
        neigh = torch.matmul(adj, x)
        h = torch.cat([x, neigh], dim=1)
        h = F.relu(self.fc1(h))
        h = F.relu(self.fc2(h))
        return self.out(h)

# ----------------------------------------------------
# LOAD MODELS & REFERENCE DATA (Cached)
# ----------------------------------------------------
@st.cache_resource
def load_saved_models():
    # Tabular models
    with open('models/gboost_model.pkl', 'rb') as f:
        gb_model = pickle.load(f)
    with open('models/random_forest_model.pkl', 'rb') as f:
        rf_model = pickle.load(f)
        
    # PyTorch models
    mlp_model = MLPRegressor(17) # 15 raw + peer_mean + peer_std
    mlp_model.load_state_dict(torch.load('models/mlp_model.pth', map_location=torch.device('cpu')))
    mlp_model.eval()
    
    sage_model = GraphSAGE(15) # 15 raw
    sage_model.load_state_dict(torch.load('models/sage_model.pth', map_location=torch.device('cpu')))
    sage_model.eval()
    
    # Reference training dataset
    with open('models/reference_data.pkl', 'rb') as f:
        ref_data = pickle.load(f)
        
    return gb_model, rf_model, mlp_model, sage_model, ref_data

try:
    gb_model, rf_model, mlp_model, sage_model, ref_data = load_saved_models()
    models_loaded = True
except Exception as e:
    st.error(f"Error loading models: {e}. Please ensure you have run the training notebook/script first to save model weights.")
    models_loaded = False

# ----------------------------------------------------
# UI HEADER
# ----------------------------------------------------
st.markdown('<div class="main-title">Student Final Exam Score Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Predict academic outcomes using individual performance and social peer network propagation</div>', unsafe_allow_html=True)

# Main columns
col_inputs, col_results = st.columns([4, 5])

with col_inputs:
    st.markdown('<div class="card"><h3>1. Academic Performance (Out of 10)</h3></div>', unsafe_allow_html=True)
    
    # 5 Academic inputs
    st.write("Enter the student's scores for the 5 key academic subjects:")
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        s_java = st.number_input("Java Programming", min_value=0.0, max_value=10.0, value=7.4, step=0.1)
        s_python = st.number_input("Python Programming", min_value=0.0, max_value=10.0, value=8.8, step=0.1)
        s_ds = st.number_input("Data Structures & Algorithms", min_value=0.0, max_value=10.0, value=6.5, step=0.1)
    with col_sub2:
        s_sad = st.number_input("Software Analysis & Design", min_value=0.0, max_value=10.0, value=6.5, step=0.1)
        s_isd = st.number_input("Intelligent Systems Dev", min_value=0.0, max_value=10.0, value=7.7, step=0.1)
        
    st.markdown('<div class="card" style="margin-top: 1rem;"><h3>2. Peer Scores (Friend Ratings)</h3></div>', unsafe_allow_html=True)
    st.write("Enter the scores/ratings of 10 of the student's close friends:")
    
    # Grid of 10 number inputs for friends
    peer_scores = []
    p_cols = st.columns(5)
    for idx in range(10):
        col_idx = idx % 5
        with p_cols[col_idx]:
            p_val = st.number_input(f"Friend {idx+1}", min_value=0.0, max_value=10.0, value=7.0, step=0.1, key=f"friend_{idx}")
            peer_scores.append(p_val)

    # Prediction Trigger
    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button("🔮 PREDICT FINAL EXAM SCORE", use_container_width=True)

with col_results:
    if not models_loaded:
        st.info("Waiting for models to be loaded...")
    elif predict_clicked:
        # Preprocessing user inputs
        x_academic = np.array([s_java, s_python, s_ds, s_sad, s_isd])
        x_peer = np.array(peer_scores)
        x_raw = np.concatenate([x_academic, x_peer]) # (15,)
        
        # Summary peer features
        peer_mean = x_peer.mean()
        peer_std = x_peer.std()
        
        # Tabular features (17,)
        x_tab = np.concatenate([x_raw, [peer_mean, peer_std]])
        x_tab_df = pd.DataFrame([x_tab], columns=[
            'javaProg', 'pythonProg', 'dataStructure', 'softwareAnalysisDesign', 'intelligenceSystemDev',
            'peer1', 'peer2', 'peer3', 'peer4', 'peer5', 'peer6', 'peer7', 'peer8', 'peer9', 'peer10',
            'peer_mean', 'peer_std'
        ])
        
        # ----------------------------------------------------
        # RUN INFERENCE
        # ----------------------------------------------------
        # 1. Gradient Boosting
        pred_gb = gb_model.predict(x_tab_df)[0]
        
        # 2. Random Forest
        pred_rf = rf_model.predict(x_tab_df)[0]
        
        # 3. MLP (GNN-style)
        x_mlp_tensor = torch.tensor([x_tab], dtype=torch.float32)
        with torch.no_grad():
            pred_mlp = mlp_model(x_mlp_tensor).item()
            
        # 4. GraphSAGE (Inductive Inference)
        # Load training matrices
        X_academic_train = ref_data['X_academic_train'] # (3000, 5)
        X_train = ref_data['X_train'] # (3000, 15)
        
        # Stack new student features to original training set
        X_new = np.vstack([X_train, x_raw]) # (3001, 15)
        X_academic_new = np.vstack([X_academic_train, x_academic]) # (3001, 5)
        
        # Re-evaluate similarity graph for 3001 nodes
        dists_full = cdist(X_academic_new, X_academic_new, metric='euclidean')
        A_new = (dists_full < 6.0).astype(float)
        np.fill_diagonal(A_new, 0)
        A_new_norm = A_new / (A_new.sum(axis=1, keepdims=True) + 1e-6)
        
        # Execute GraphSAGE
        X_new_tensor = torch.tensor(X_new, dtype=torch.float32)
        A_new_norm_tensor = torch.tensor(A_new_norm, dtype=torch.float32)
        with torch.no_grad():
            preds_sage = sage_model(X_new_tensor, A_new_norm_tensor)
            pred_sage = preds_sage[-1].item() # prediction for the new node
            
        # Clamp predictions
        pred_gb = np.clip(pred_gb, 4.0, 10.0)
        pred_rf = np.clip(pred_rf, 4.0, 10.0)
        pred_mlp = np.clip(pred_mlp, 4.0, 10.0)
        pred_sage = np.clip(pred_sage, 4.0, 10.0)

        # ----------------------------------------------------
        # DISPLAY RESULTS
        # ----------------------------------------------------
        st.markdown('<h3>Prediction Results</h3>', unsafe_allow_html=True)
        
        # Display cards in a 4-column row
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.markdown(f"""
            <div class="metric-card" style="border-top-color: #2E5BFF; background-color: rgba(46, 91, 255, 0.05);">
                <div class="metric-name">V3: GraphSAGE</div>
                <div class="metric-val" style="color: #2E5BFF;">{pred_sage:.2f}</div>
                <div style="font-size: 0.75rem; color: #707E94;">GNN (MAE: 0.207)</div>
            </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class="metric-card" style="border-top-color: #4CAF50; background-color: rgba(76, 175, 80, 0.05);">
                <div class="metric-name">V2: MLP</div>
                <div class="metric-val" style="color: #4CAF50;">{pred_mlp:.2f}</div>
                <div style="font-size: 0.75rem; color: #707E94;">GNN-Style (MAE: 0.207)</div>
            </div>
            """, unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""
            <div class="metric-card" style="border-top-color: #FF9F1C; background-color: rgba(255, 159, 28, 0.05);">
                <div class="metric-name">V1: GBoost</div>
                <div class="metric-val" style="color: #FF9F1C;">{pred_gb:.2f}</div>
                <div style="font-size: 0.75rem; color: #707E94;">Tabular (MAE: 0.224)</div>
            </div>
            """, unsafe_allow_html=True)
        with mc4:
            st.markdown(f"""
            <div class="metric-card" style="border-top-color: #9C27B0; background-color: rgba(156, 39, 176, 0.05);">
                <div class="metric-name">V4: RF</div>
                <div class="metric-val" style="color: #9C27B0;">{pred_rf:.2f}</div>
                <div style="font-size: 0.75rem; color: #707E94;">Ensemble (MAE: 0.268)</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Social peer influence breakdown
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("**Social Influence Summary:**")
        st.write(f"- **Student Academic Core average**: `{x_academic.mean():.2f}/10`")
        st.write(f"- **Friend Group Average Score (Direct)**: `{peer_mean:.2f}/10` (Variation: `{peer_std:.2f}`)")
        
        # Calculate how many academic peers (similar students) are in the network
        my_dists = np.linalg.norm(X_academic_train - x_academic, axis=1)
        num_neighbors = np.sum(my_dists < 6.0)
        st.write(f"- **Academic Neighbors in network**: `{num_neighbors}` students (students with similar grades)")

        # Plot Prediction Distribution relative to training data
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("**Student Placement in Score Distribution:**")
        fig, ax = plt.subplots(figsize=(8, 3.5))
        sns.kdeplot(ref_data['y_train'], fill=True, color='gray', label='All Students Distribution', ax=ax, alpha=0.3)
        ax.axvline(pred_sage, color='#2E5BFF', linestyle='--', linewidth=2, label=f'GraphSAGE Prediction ({pred_sage:.2f})')
        ax.axvline(x_academic.mean(), color='orange', linestyle=':', linewidth=2, label=f'Academic Average ({x_academic.mean():.2f})')
        ax.set_title("Where this Student Stands", fontsize=11)
        ax.set_xlabel("Predicted Final Score")
        ax.set_ylabel("Density")
        ax.legend(fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        
    else:
        st.markdown("""
        <div class="card" style="text-align: center; color: #707E94; padding: 60px 20px;">
            <span style="font-size: 3rem;">👈</span>
            <h4 style="margin-top: 15px;">Configure the scores and click the button to run the prediction!</h4>
            <p>Our backend will execute inference on Gradient Boosting, MLP, Random Forest, and a GraphSAGE GNN.</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------
# SIDEBAR CONTENT (MODEL DETAILS)
# ----------------------------------------------------
with st.sidebar:
    st.markdown("## Info & Comparison")
    st.write("This application predicts final scores based on the research option exercise: *Prediction of Final Exam Score Using Machine Learning Models*.")
    
    # Model evaluation table
    if os.path.exists('plots/model_comparison.csv'):
        st.markdown("### Model Comparison (Test Set)")
        comp_df = pd.read_csv('plots/model_comparison.csv', index_col=0)
        st.dataframe(comp_df, use_container_width=True)
    
    st.markdown("### Network Parameters")
    st.write("- **Similarity Metric**: Euclidean distance on 5 academic scores.")
    st.write("- **Adjacency Threshold**: `< 6.0` (indicates academic similarity).")
    st.write("- **Dataset size**: `3000` students.")
    st.write("- **PyTorch Device**: `GPU (CUDA)` used during training.")
    
    st.write("---")
    st.caption("Developed for Software Architecture and Design - PTIT")
