import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import cdist
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import torch
import torch.nn as nn
import torch.nn.functional as F
import copy

# Set random seeds for reproducibility
np.random.seed(42)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

# Check for GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Create outputs directory for plots
os.makedirs('plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

# ----------------------------------------------------
# 1. CONSTRUCT DATASET WITH PEER INFLUENCE (Task 1)
# ----------------------------------------------------
print("Generating dataset...")
N = 3000

# 5 Academic scores (Java, Python, DS, SAD, ISD)
X_academic = np.random.randint(4, 11, size=(N, 5)) # values 4 to 10

# 10 Peer scores (ratings by friends)
X_peer = np.random.randint(4, 11, size=(N, 10)) # values 4 to 10

# Combine into X
X = np.hstack([X_academic, X_peer])

# Calculate individual peer mean and std
peer_mean = X_peer.mean(axis=1)
peer_std = X_peer.std(axis=1)

# Build similarity-based graph (Euclidean distance on academic scores)
# Using scipy cdist for vectorized execution
dists = cdist(X_academic, X_academic, metric='euclidean')
threshold = 6.0
A = (dists < threshold).astype(float)
np.fill_diagonal(A, 0) # Remove self-loops

# Normalize adjacency matrix
A_sum = A.sum(axis=1, keepdims=True)
A_norm = A / (A_sum + 1e-6)

# Graph-aggregated peer influence (influence of neighbors in social network)
# neigh_peer is the aggregated peer scores of the academic neighbors
neigh_peer = np.matmul(A_norm, X_peer)
peer_mean_graph = neigh_peer.mean(axis=1)

# Target Final Exam Score formula:
# 80% Academic + 15% Individual Peers + 5% Graph Peer Influence + Noise
y = (
    0.25 * X_academic[:, 0] +  # javaProg
    0.20 * X_academic[:, 1] +  # pythonProg
    0.10 * X_academic[:, 2] +  # dataStructure
    0.15 * X_academic[:, 3] +  # software analysis & design
    0.10 * X_academic[:, 4] +  # intelligence system Dev
    0.15 * peer_mean -
    0.05 * peer_std +
    0.05 * peer_mean_graph +
    np.random.normal(0, 0.25, N)
)
# Clamp final scores to range [4.0, 10.0]
y = np.clip(y, 4.0, 10.0)

# Create DataFrame for tabular modeling (sklearn)
columns = [
    'javaProg', 'pythonProg', 'dataStructure', 'softwareAnalysisDesign', 'intelligenceSystemDev',
    'peer1', 'peer2', 'peer3', 'peer4', 'peer5', 'peer6', 'peer7', 'peer8', 'peer9', 'peer10'
]
df = pd.DataFrame(X, columns=columns)
df['peer_mean'] = peer_mean
df['peer_std'] = peer_std
df['peer_mean_graph'] = peer_mean_graph
df['FinalExam'] = y

# Save dataset to csv
df.to_csv('student_scores_dataset.csv', index=False)
print("Dataset saved to student_scores_dataset.csv. Shape:", df.shape)

# ----------------------------------------------------
# 2. EXPLORATORY DATA ANALYSIS (Task 2)
# ----------------------------------------------------
print("Running Exploratory Data Analysis...")

# Set style
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# Plot target distribution
sns.histplot(df['FinalExam'], kde=True, color='royalblue', bins=30)
plt.title('Distribution of Final Exam Scores', fontsize=16)
plt.xlabel('Final Exam Score', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.savefig('plots/final_exam_distribution.png', dpi=300)
plt.close()

# Plot Academic Scores distribution
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
academic_cols = ['javaProg', 'pythonProg', 'dataStructure', 'softwareAnalysisDesign', 'intelligenceSystemDev']
for i, col in enumerate(academic_cols):
    sns.countplot(x=df[col], ax=axes[i], hue=df[col], palette='viridis', legend=False)
    axes[i].set_title(f'Distribution of {col}')
    axes[i].set_xlabel('Score')
    axes[i].set_ylabel('Count')
# Remove the empty last subplot
fig.delaxes(axes[5])
plt.tight_layout()
plt.savefig('plots/academic_scores_distributions.png', dpi=300)
plt.close()

# Correlation Matrix
plt.figure(figsize=(14, 10))
corr_cols = academic_cols + ['peer_mean', 'peer_std', 'peer_mean_graph', 'FinalExam']
corr_matrix = df[corr_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Correlation Matrix of Student Scores and Target', fontsize=16)
plt.tight_layout()
plt.savefig('plots/correlation_matrix.png', dpi=300)
plt.close()

# ----------------------------------------------------
# 3. PREPARE DATA FOR MODELING (Task 2)
# ----------------------------------------------------
# Features and Target
features_tabular = df.drop(['FinalExam', 'peer_mean_graph'], axis=1) # 17 features: 15 raw + peer_mean + peer_std
target_tabular = df['FinalExam']

# Train/Test indices split for consistent comparison across GNN and Tabular
indices = np.arange(N)
train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42)

# Scikit-learn datasets
X_train_tab = features_tabular.iloc[train_idx]
y_train_tab = target_tabular.iloc[train_idx]
X_test_tab = features_tabular.iloc[test_idx]
y_test_tab = target_tabular.iloc[test_idx]

# PyTorch tensors for PyTorch models
X_tensor = torch.tensor(X, dtype=torch.float32).to(device) # Shape: (N, 15)
# MLP uses engineered features: X + peer_mean + peer_std
X_mlp_features = np.hstack([X, peer_mean.reshape(-1, 1), peer_std.reshape(-1, 1)])
X_mlp_tensor = torch.tensor(X_mlp_features, dtype=torch.float32).to(device) # Shape: (N, 17)
y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1).to(device)

# Normalized Adjacency matrix tensor for GNN
A_norm_tensor = torch.tensor(A_norm, dtype=torch.float32).to(device)

# Index tensors for train/test split to guarantee same index ordering
train_idx_tensor = torch.tensor(train_idx, dtype=torch.long).to(device)
test_idx_tensor = torch.tensor(test_idx, dtype=torch.long).to(device)

# ----------------------------------------------------
# 4. DEFINE NEURAL NETWORK MODELS (Task 3)
# ----------------------------------------------------
# Model 2: MLP (GNN-Style)
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

# Model 3: GraphSAGE
class GraphSAGE(nn.Module):
    def __init__(self, in_dim, hidden=64):
        super().__init__()
        self.fc1 = nn.Linear(in_dim * 2, hidden)
        self.fc2 = nn.Linear(hidden, 32)
        self.out = nn.Linear(32, 1)
        
    def forward(self, x, adj):
        # Neighborhood aggregation
        neigh = torch.matmul(adj, x)
        # Concatenate self features with neighborhood features
        h = torch.cat([x, neigh], dim=1)
        h = F.relu(self.fc1(h))
        h = F.relu(self.fc2(h))
        return self.out(h)

# ----------------------------------------------------
# 5. MODEL TRAINING WITH EARLY STOPPING & LOGS (Task 4)
# ----------------------------------------------------
def train_pytorch_model(model, inputs, targets, train_idx_t, test_idx_t, model_name, graph_mode=False, epochs=500, lr=0.01, patience=20):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss() # Optimize MSE
    
    best_loss = float('inf')
    best_model_weights = None
    patience_counter = 0
    
    train_losses = []
    val_losses = []
    
    print(f"\n--- Training {model_name} on {device} ---")
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        
        # Forward pass
        if graph_mode:
            pred = model(inputs, A_norm_tensor)
        else:
            pred = model(inputs)
            
        loss = loss_fn(pred[train_idx_t], targets[train_idx_t])
        loss.backward()
        optimizer.step()
        
        # Evaluation mode
        model.eval()
        with torch.no_grad():
            if graph_mode:
                test_pred = model(inputs, A_norm_tensor)
            else:
                test_pred = model(inputs)
            test_loss = loss_fn(test_pred[test_idx_t], targets[test_idx_t])
            
        train_losses.append(loss.item())
        val_losses.append(test_loss.item())
        
        # Log training progress every 20 epochs
        if epoch % 20 == 0 or epoch == 1:
            print(f"Epoch {epoch:03d} | Train MSE: {loss.item():.4f} | Val MSE: {test_loss.item():.4f}")
            
        # Early Stopping
        if test_loss.item() < best_loss:
            best_loss = test_loss.item()
            best_model_weights = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch}. Best Val MSE: {best_loss:.4f}")
                break
                
    # Restore best weights
    model.load_state_dict(best_model_weights)
    return model, train_losses, val_losses

# Train Model 2: MLP (GNN-style)
mlp_model = MLPRegressor(X_mlp_tensor.shape[1]).to(device)
mlp_model, mlp_train_loss, mlp_val_loss = train_pytorch_model(
    mlp_model, X_mlp_tensor, y_tensor, train_idx_tensor, test_idx_tensor, "MLP (GNN-style)", graph_mode=False
)

# Train Model 3: GraphSAGE
sage_model = GraphSAGE(X_tensor.shape[1]).to(device)
sage_model, sage_train_loss, sage_val_loss = train_pytorch_model(
    sage_model, X_tensor, y_tensor, train_idx_tensor, test_idx_tensor, "GraphSAGE", graph_mode=True
)

# Plot Loss Curves
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(mlp_train_loss, label='Train Loss')
plt.plot(mlp_val_loss, label='Val Loss')
plt.title('MLP (GNN-style) Training Loss')
plt.xlabel('Epochs')
plt.ylabel('MSE Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(sage_train_loss, label='Train Loss')
plt.plot(sage_val_loss, label='Val Loss')
plt.title('GraphSAGE Training Loss')
plt.xlabel('Epochs')
plt.ylabel('MSE Loss')
plt.legend()
plt.tight_layout()
plt.savefig('plots/pytorch_loss_curves.png', dpi=300)
plt.close()

# Train Model 1: Gradient Boosting
print("\nTraining Model 1: Gradient Boosting Regressor...")
gb_model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)
gb_model.fit(X_train_tab, y_train_tab)

# Train Model 4: Random Forest
print("Training Model 4: Random Forest Regressor...")
rf_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    random_state=42
)
rf_model.fit(X_train_tab, y_train_tab)

# ----------------------------------------------------
# 6. EVALUATION USING 5 METRICS (Task 3)
# ----------------------------------------------------
def calculate_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    return mae, mse, rmse, mape, r2

# Get predictions on test set
# GBoost
gb_pred = gb_model.predict(X_test_tab)

# Random Forest
rf_pred = rf_model.predict(X_test_tab)

# PyTorch MLP
mlp_model.eval()
with torch.no_grad():
    mlp_pred = mlp_model(X_mlp_tensor)[test_idx_tensor].cpu().numpy().squeeze()

# GraphSAGE
sage_model.eval()
with torch.no_grad():
    sage_pred = sage_model(X_tensor, A_norm_tensor)[test_idx_tensor].cpu().numpy().squeeze()

# Real y_test values
y_test_numpy = y_test_tab.values

# Calculate metrics for all 4 models
models_metrics = {}
models_metrics['V1: GBoost'] = calculate_metrics(y_test_numpy, gb_pred)
models_metrics['V2: MLP GNN-style'] = calculate_metrics(y_test_numpy, mlp_pred)
models_metrics['V3: GraphSAGE'] = calculate_metrics(y_test_numpy, sage_pred)
models_metrics['V4: Random Forest'] = calculate_metrics(y_test_numpy, rf_pred)

# Build summary DataFrame
metrics_df = pd.DataFrame(models_metrics, index=['MAE', 'MSE', 'RMSE', 'MAPE (%)', 'R2']).T
metrics_df = metrics_df.round(4)
# Add percentage format to MAPE
metrics_df['MAPE (%)'] = metrics_df['MAPE (%)'].apply(lambda x: f"{x:.2f}%")
print("\n--- MODEL COMPARISON TABLE ---")
print(metrics_df)

# Save evaluation metrics comparison table
metrics_df.to_csv('plots/model_comparison.csv')

# Plot Metrics Bar Chart
metrics_plot_df = pd.DataFrame(models_metrics, index=['MAE', 'MSE', 'RMSE', 'MAPE', 'R2']).T
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()
metric_names = ['MAE', 'MSE', 'RMSE', 'R2']
for i, metric in enumerate(metric_names):
    sns.barplot(x=metrics_plot_df.index, y=metrics_plot_df[metric], ax=axes[i], hue=metrics_plot_df.index, palette='Set2', legend=False)
    axes[i].set_title(f'Comparison of {metric}', fontsize=14)
    axes[i].set_ylabel(metric)
    for p in axes[i].patches:
        axes[i].annotate(f"{p.get_height():.3f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='center', xytext=(0, 5), textcoords='offset points')
plt.tight_layout()
plt.savefig('plots/metrics_comparison_charts.png', dpi=300)
plt.close()

# Plot Actual vs Predicted Scatter Plots
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
axes = axes.flatten()

predictions = [gb_pred, mlp_pred, sage_pred, rf_pred]
model_names = ['V1: GBoost', 'V2: MLP (GNN-style)', 'V3: GraphSAGE', 'V4: Random Forest']

for i, (pred, name) in enumerate(zip(predictions, model_names)):
    sns.scatterplot(x=y_test_numpy, y=pred, ax=axes[i], alpha=0.6, color='darkcyan')
    axes[i].plot([4, 10], [4, 10], 'r--', lw=2) # identity line
    axes[i].set_title(f'{name}: Actual vs Predicted', fontsize=14)
    axes[i].set_xlabel('Actual Final Exam Score')
    axes[i].set_ylabel('Predicted Score')
    axes[i].set_xlim(3.8, 10.2)
    axes[i].set_ylim(3.8, 10.2)
    
plt.tight_layout()
plt.savefig('plots/actual_vs_predicted_scatter.png', dpi=300)
plt.close()


# ----------------------------------------------------
# 7. COMPARE UNDER DIFFERENT SOCIAL STRUCTURES (Task 4)
# ----------------------------------------------------
print("\nAnalyzing performance under different social structures...")
thresholds = [3.0, 5.0, 7.0, 9.0]
results_structs = []

for th in thresholds:
    # Build adjacency matrix with this threshold
    A_th = (dists < th).astype(float)
    np.fill_diagonal(A_th, 0)
    
    # Calculate average node degree
    avg_degree = A_th.sum(axis=1).mean()
    
    # Row normalize
    A_th_sum = A_th.sum(axis=1, keepdims=True)
    A_th_norm = A_th / (A_th_sum + 1e-6)
    
    A_th_norm_tensor = torch.tensor(A_th_norm, dtype=torch.float32).to(device)
    
    # Define and train GraphSAGE for this structure
    model_th = GraphSAGE(X_tensor.shape[1]).to(device)
    
    # Custom training loop just for this comparison
    optimizer = torch.optim.Adam(model_th.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()
    
    best_th_loss = float('inf')
    best_th_weights = None
    patience_counter = 0
    
    for epoch in range(200):
        model_th.train()
        optimizer.zero_grad()
        pred = model_th(X_tensor, A_th_norm_tensor)
        loss = loss_fn(pred[train_idx_tensor], y_tensor[train_idx_tensor])
        loss.backward()
        optimizer.step()
        
        model_th.eval()
        with torch.no_grad():
            val_loss = loss_fn(pred[test_idx_tensor], y_tensor[test_idx_tensor])
            
        if val_loss.item() < best_th_loss:
            best_th_loss = val_loss.item()
            best_th_weights = copy.deepcopy(model_th.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= 20:
                break
                
    model_th.load_state_dict(best_th_weights)
    
    # Evaluate
    model_th.eval()
    with torch.no_grad():
        th_pred = model_th(X_tensor, A_th_norm_tensor)[test_idx_tensor].cpu().numpy().squeeze()
        
    mae, mse, rmse, mape, r2 = calculate_metrics(y_test_numpy, th_pred)
    results_structs.append({
        'Threshold': th,
        'Avg Degree (Density)': avg_degree,
        'MAE': mae,
        'R2': r2
    })
    print(f"Threshold: {th:.1f} | Avg Neighbors: {avg_degree:.1f} | MAE: {mae:.4f} | R2: {r2:.4f}")

struct_df = pd.DataFrame(results_structs)

# Plot social structures comparison
fig, ax1 = plt.subplots(figsize=(10, 6))
color = 'tab:blue'
ax1.set_xlabel('Similarity Threshold (lower threshold = tighter/sparser friendships)')
ax1.set_ylabel('Model MAE (lower is better)', color=color)
ax1.plot(struct_df['Threshold'], struct_df['MAE'], marker='o', color=color, linewidth=2)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Avg Node Degree (Network Density)', color=color)
ax2.plot(struct_df['Threshold'], struct_df['Avg Degree (Density)'], marker='s', linestyle='--', color=color, linewidth=2)
ax2.tick_params(axis='y', labelcolor=color)

plt.title('GraphSAGE Performance under Different Social Structures', fontsize=16)
plt.savefig('plots/social_structures_comparison.png', dpi=300)
plt.close()


# ----------------------------------------------------
# 8. ANALYZE PEER INFLUENCE PROPAGATION (Task 5)
# ----------------------------------------------------
print("\nSimulating peer influence propagation...")
# Let's select a target group of students who have low initial final scores
target_nodes = np.where(y < 6.0)[0]
# Limit to top 20 nodes for visualization
target_nodes = target_nodes[:20]

# We will perturb (increase) the peer scores of their neighbors
# Let's inspect who their neighbors are in A
# If we change the academic and peer scores of these neighbors, does it propagate?
# We will perturb the peer scores of EVERYONE in the network by +2 scores
# and trace how the GraphSAGE predictions shift as a result of neighbor aggregation.
# We will compare a 0-hop propagation (no GNN, just MLP) vs 1-hop SAGE propagation.

# Base prediction
sage_model.eval()
with torch.no_grad():
    base_preds = sage_model(X_tensor, A_norm_tensor).cpu().numpy().squeeze()
    base_preds_mlp = mlp_model(X_mlp_tensor).cpu().numpy().squeeze()

# Scenario A: Increase individual peer scores of ALL students by 2.0 (but keep Graph structure constant)
X_perturbed = X.copy()
X_perturbed[:, 5:15] = np.clip(X_perturbed[:, 5:15] + 2, 4, 10) # increase all peer ratings by 2
X_perturbed_tensor = torch.tensor(X_perturbed, dtype=torch.float32).to(device)

# Recalculate GNN-style MLP features for comparison
peer_mean_pert = X_perturbed[:, 5:15].mean(axis=1)
peer_std_pert = X_perturbed[:, 5:15].std(axis=1)
X_mlp_pert = np.hstack([X_perturbed, peer_mean_pert.reshape(-1, 1), peer_std_pert.reshape(-1, 1)])
X_mlp_pert_tensor = torch.tensor(X_mlp_pert, dtype=torch.float32).to(device)

with torch.no_grad():
    perturbed_preds_sage = sage_model(X_perturbed_tensor, A_norm_tensor).cpu().numpy().squeeze()
    perturbed_preds_mlp = mlp_model(X_mlp_pert_tensor).cpu().numpy().squeeze()

# Calculate shifts
shift_sage = perturbed_preds_sage - base_preds
shift_mlp = perturbed_preds_mlp - base_preds_mlp

# Let's plot the distribution of final exam score increase
plt.figure(figsize=(10, 6))
sns.kdeplot(shift_sage, label='GraphSAGE (With Peer Network Propagation)', fill=True, color='teal')
sns.kdeplot(shift_mlp, label='MLP GNN-Style (No Network Message Passing)', fill=True, color='orange')
plt.title('Final Score Prediction Shifts due to Friend Score Improvement (+2 points)', fontsize=15)
plt.xlabel('Change in Predicted Final Exam Score', fontsize=12)
plt.ylabel('Density', fontsize=12)
plt.legend()
plt.savefig('plots/peer_influence_propagation.png', dpi=300)
plt.close()

print(f"Average predicted score increase for GraphSAGE: {shift_sage.mean():.4f}")
print(f"Average predicted score increase for MLP: {shift_mlp.mean():.4f}")


# ----------------------------------------------------
# 9. SAVE MODELS (Task 8)
# ----------------------------------------------------
import pickle

print("\nSaving models...")
# Save GBoost
with open('models/gboost_model.pkl', 'wb') as f:
    pickle.dump(gb_model, f)

# Save Random Forest
with open('models/random_forest_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)

# Save PyTorch MLP
torch.save(mlp_model.state_dict(), 'models/mlp_model.pth')

# Save GraphSAGE
torch.save(sage_model.state_dict(), 'models/sage_model.pth')

# Also save the mean and std of training set for standardization/inputs if needed, and reference dataset for GraphSAGE inference
# The reference dataset consists of training student academic scores and peer scores
reference_data = {
    'X_academic_train': X_academic,
    'X_peer_train': X_peer,
    'X_train': X,
    'y_train': y
}
with open('models/reference_data.pkl', 'wb') as f:
    pickle.dump(reference_data, f)

print("All models and reference files saved successfully!")
print("Pipeline complete!")
