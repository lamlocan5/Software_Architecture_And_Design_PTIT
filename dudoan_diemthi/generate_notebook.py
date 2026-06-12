import json
import os

notebook_content = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Dự đoán Điểm thi Kết thúc học phần sử dụng Machine Learning & Graph Neural Networks (GNNs)\n",
    "\n",
    "Notebook này trình bày cách dự đoán điểm thi kết thúc học phần của sinh viên thông qua sự kết hợp của **kết quả học tập cá nhân (academic performance)**, **điểm số của bạn bè (peer scores)** và **tín hiệu từ mạng xã hội học tập (social network signals)**.\n",
    "\n",
    "## Các nhiệm vụ chính (5 Tasks):\n",
    "1. **Xây dựng tập dữ liệu kèm ảnh hưởng từ bạn bè**: Tạo hồ sơ giả lập cho 3,000 sinh viên (gồm 5 điểm học tập và 10 điểm của bạn bè) và xây dựng đồ thị mạng lưới dựa trên sự tương đồng học lực.\n",
    "2. **Huấn luyện các mô hình**: Triển khai và huấn luyện 4 mô hình:\n",
    "   - **V1: Gradient Boosting Regressor** (Mô hình học máy dạng cây Boosting truyền thống với đặc trưng trung bình bạn bè)\n",
    "   - **V2: MLP (GNN-style)** (Mạng nơ-ron PyTorch sử dụng đặc trưng cá nhân kết hợp các chỉ số thống kê bạn bè, chạy trên GPU)\n",
    "   - **V3: GraphSAGE GNN** (Mạng nơ-ron đồ thị PyTorch sử dụng phép tổng hợp lân cận, chạy trên GPU)\n",
    "   - **V4: Random Forest Regressor** (Mô hình Baseline dạng rừng ngẫu nhiên)\n",
    "3. **Đánh giá bằng 5 chỉ số**: Tính toán MAE, MSE, RMSE, MAPE và $R^2$ để so sánh các mô hình.\n",
    "4. **So sánh dưới các cấu trúc xã hội khác nhau**: Phân tích hiệu năng của GraphSAGE thay đổi thế nào khi ta biến đổi ngưỡng tương đồng (thay đổi độ thưa/dày đặc của đồ thị mạng lưới bạn bè).\n",
    "5. **Phân tích sự lan truyền ảnh hưởng từ bạn bè**: Mô phỏng kịch bản nhóm bạn tăng điểm (+2 điểm) và phân tích sự lan truyền thay đổi dự đoán trong GraphSAGE (GNN) so với MLP.\n",
    "\n",
    "---"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Thiết lập & Khai báo Thư viện\n",
    "Chúng ta khai báo các thư viện học máy phổ biến, PyTorch, và thiết lập seed ngẫu nhiên nhằm đảm bảo tính tái lập kết quả huấn luyện. Đồng thời kích hoạt tăng tốc GPU (CUDA) nếu khả dụng."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from scipy.spatial.distance import cdist\n",
    "from sklearn.model_selection import train_test_split\n",
    "from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor\n",
    "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n",
    "import torch\n",
    "import torch.nn as nn\n",
    "import torch.nn.functional as F\n",
    "import copy\n",
    "\n",
    "# Thiết lập seed để đảm bảo tính tái lập\n",
    "np.random.seed(42)\n",
    "torch.manual_seed(42)\n",
    "if torch.cuda.is_available():\n",
    "    torch.cuda.manual_seed_all(42)\n",
    "\n",
    "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n",
    "print(f\"Thiết bị huấn luyện sử dụng: {device}\")\n",
    "\n",
    "# Tạo các thư mục lưu kết quả\n",
    "os.makedirs('plots', exist_ok=True)\n",
    "os.makedirs('models', exist_ok=True)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Nhiệm vụ 1: Xây dựng tập dữ liệu kèm ảnh hưởng từ bạn bè\n",
    "\n",
    "Chúng ta tạo tập dữ liệu giả lập cho $N = 3000$ sinh viên. Mỗi sinh viên bao gồm:\n",
    "- 5 điểm số học thuật (Java, Python, Cấu trúc dữ liệu, Phân tích thiết kế hệ thống, Phát triển hệ thống thông minh) có khoảng điểm từ 4 đến 10.\n",
    "- 10 điểm số đánh giá từ bạn bè có khoảng điểm từ 4 đến 10.\n",
    "\n",
    "Chúng ta xây dựng ma trận kề $A$ biểu diễn liên kết bạn bè dựa trên khoảng cách học lực (Euclidean distance). Một liên kết tồn tại nếu khoảng cách nhỏ hơn ngưỡng 6.0. Ma trận sau đó được chuẩn hóa theo dòng.\n",
    "\n",
    "Điểm số FinalExam được sinh dựa trên công thức:\n",
    "$$\\text{Điểm} = 0.25 \\times \\text{Java} + 0.20 \\times \\text{Python} + 0.10 \\times \\text{DS} + 0.15 \\times \\text{SAD} + 0.10 \\times \\text{ISD} + 0.15 \\times \\text{peer\\_mean} - 0.05 \\times \\text{peer\\_std} + 0.05 \\times \\text{peer\\_mean\\_graph} + \\epsilon$$\n",
    "trong đó $\\epsilon \\sim \\mathcal{N}(0, 0.25^2)$ là nhiễu ngẫu nhiên."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "N = 3000\n",
    "\n",
    "# Sinh 5 cột điểm học lực học tập cá nhân\n",
    "X_academic = np.random.randint(4, 11, size=(N, 5))\n",
    "\n",
    "# Sinh 10 điểm từ bạn bè\n",
    "X_peer = np.random.randint(4, 11, size=(N, 10))\n",
    "\n",
    "# Gộp lại thành ma trận đặc trưng thô X\n",
    "X = np.hstack([X_academic, X_peer])\n",
    "\n",
    "# Tính toán thống kê bạn bè trực tiếp\n",
    "peer_mean = X_peer.mean(axis=1)\n",
    "peer_std = X_peer.std(axis=1)\n",
    "\n",
    "# Xây dựng đồ thị liên kết bằng khoảng cách Euclidean (Tối ưu vector hóa)\n",
    "dists = cdist(X_academic, X_academic, metric='euclidean')\n",
    "threshold = 6.0\n",
    "A = (dists < threshold).astype(float)\n",
    "np.fill_diagonal(A, 0) # Loại bỏ tự liên kết với chính mình\n",
    "\n",
    "# Chuẩn hóa ma trận kề theo dòng\n",
    "A_sum = A.sum(axis=1, keepdims=True)\n",
    "A_norm = A / (A_sum + 1e-6)\n",
    "\n",
    "# Tổng hợp ảnh hưởng bạn bè qua đồ thị mạng lưới\n",
    "neigh_peer = np.matmul(A_norm, X_peer)\n",
    "peer_mean_graph = neigh_peer.mean(axis=1)\n",
    "\n",
    "# Tính điểm thi cuối kỳ (Target)\n",
    "y = (\n",
    "    0.25 * X_academic[:, 0] +  # java\n",
    "    0.20 * X_academic[:, 1] +  # python\n",
    "    0.10 * X_academic[:, 2] +  # ds\n",
    "    0.15 * X_academic[:, 3] +  # sad\n",
    "    0.10 * X_academic[:, 4] +  # isd\n",
    "    0.15 * peer_mean -\n",
    "    0.05 * peer_std +\n",
    "    0.05 * peer_mean_graph +\n",
    "    np.random.normal(0, 0.25, N)\n",
    ")\n",
    "y = np.clip(y, 4.0, 10.0) # Giới hạn điểm cuối kỳ trong khoảng thực tế [4, 10]\n",
    "\n",
    "# Tạo Pandas DataFrame để phân tích dữ liệu & huấn luyện mô hình cây\n",
    "columns = [\n",
    "    'javaProg', 'pythonProg', 'dataStructure', 'softwareAnalysisDesign', 'intelligenceSystemDev',\n",
    "    'peer1', 'peer2', 'peer3', 'peer4', 'peer5', 'peer6', 'peer7', 'peer8', 'peer9', 'peer10'\n",
    "]\n",
    "df = pd.DataFrame(X, columns=columns)\n",
    "df['peer_mean'] = peer_mean\n",
    "df['peer_std'] = peer_std\n",
    "df['peer_mean_graph'] = peer_mean_graph\n",
    "df['FinalExam'] = y\n",
    "\n",
    "df.to_csv('student_scores_dataset.csv', index=False)\n",
    "print(\"Đã xây dựng và lưu tập dữ liệu thành công. Kích thước:\", df.shape)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Nhiệm vụ 2: Phân tích Khám phá Dữ liệu (EDA)\n",
    "\n",
    "Chúng ta vẽ biểu đồ phân phối của điểm số FinalExam và các môn học thuật cá nhân, đồng thời tính toán và trực quan hóa ma trận tương quan giữa các đặc trưng."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "sns.set_theme(style=\"whitegrid\")\n",
    "\n",
    "# 1. Vẽ phân phối điểm thi kết thúc học phần\n",
    "plt.figure(figsize=(9, 5))\n",
    "sns.histplot(df['FinalExam'], kde=True, color='royalblue', bins=30)\n",
    "plt.title('Biểu đồ Phân phối Điểm thi Kết thúc học phần', fontsize=15)\n",
    "plt.xlabel('Điểm thi cuối kỳ')\n",
    "plt.ylabel('Số lượng sinh viên')\n",
    "plt.show()\n",
    "\n",
    "# 2. Vẽ phân phối điểm các môn học cá nhân\n",
    "fig, axes = plt.subplots(2, 3, figsize=(14, 8))\n",
    "axes = axes.flatten()\n",
    "academic_cols = ['javaProg', 'pythonProg', 'dataStructure', 'softwareAnalysisDesign', 'intelligenceSystemDev']\n",
    "for i, col in enumerate(academic_cols):\n",
    "    sns.countplot(x=df[col], ax=axes[i], hue=df[col], palette='viridis', legend=False)\n",
    "    axes[i].set_title(f'Phân phối {col}')\n",
    "    axes[i].set_xlabel('Điểm số')\n",
    "    axes[i].set_ylabel('Số lượng')\n",
    "fig.delaxes(axes[5])\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "# 3. Bản đồ nhiệt tương quan (Correlation Heatmap)\n",
    "plt.figure(figsize=(12, 8))\n",
    "corr_cols = academic_cols + ['peer_mean', 'peer_std', 'peer_mean_graph', 'FinalExam']\n",
    "sns.heatmap(df[corr_cols].corr(), annot=True, cmap='coolwarm', fmt=\".2f\", linewidths=0.5)\n",
    "plt.title('Ma Trận Hệ Số Tương Quan', fontsize=15)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Chuẩn bị Dữ liệu cho Mô hình\n",
    "Chúng ta thực hiện chia tập dữ liệu thành 80% train / 20% test. Sau đó chuyển đổi dữ liệu thành các PyTorch Tensor. Để tránh tình trạng lệch vị trí sắp xếp khi đánh giá, ta chuyển đổi `train_idx` và `test_idx` sang Tensor chỉ mục PyTorch."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "features_tabular = df.drop(['FinalExam', 'peer_mean_graph'], axis=1) # 17 đặc trưng: 15 thô + peer_mean + peer_std\n",
    "target_tabular = df['FinalExam']\n",
    "\n",
    "# Chia tập chỉ mục\n",
    "indices = np.arange(N)\n",
    "train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42)\n",
    "\n",
    "# Dữ liệu dạng bảng cho mô hình Scikit-Learn\n",
    "X_train_tab = features_tabular.iloc[train_idx]\n",
    "y_train_tab = target_tabular.iloc[train_idx]\n",
    "X_test_tab = features_tabular.iloc[test_idx]\n",
    "y_test_tab = target_tabular.iloc[test_idx]\n",
    "\n",
    "# Chuyển đổi sang PyTorch Tensor chạy trên GPU\n",
    "X_tensor = torch.tensor(X, dtype=torch.float32).to(device) # Kích thước: (N, 15)\n",
    "X_mlp_features = np.hstack([X, peer_mean.reshape(-1, 1), peer_std.reshape(-1, 1)])\n",
    "X_mlp_tensor = torch.tensor(X_mlp_features, dtype=torch.float32).to(device) # Kích thước: (N, 17)\n",
    "y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1).to(device)\n",
    "\n",
    "A_norm_tensor = torch.tensor(A_norm, dtype=torch.float32).to(device)\n",
    "\n",
    "# Tensor chỉ mục để đồng bộ hóa sắp xếp\n",
    "train_idx_tensor = torch.tensor(train_idx, dtype=torch.long).to(device)\n",
    "test_idx_tensor = torch.tensor(test_idx, dtype=torch.long).to(device)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Nhiệm vụ 3: Định nghĩa Mô hình GNN & MLP trong PyTorch\n",
    "\n",
    "Chúng ta thiết lập hai mô hình nơ-ron chính:\n",
    "1. **MLPRegressor (GNN-style)**: Mô hình MLP nhận đặc trưng học lực và thống kê bạn bè được thiết kế sẵn (mean, std).\n",
    "2. **GraphSAGE**: Mạng nơ-ron đồ thị (GNN) thực hiện phép tích chập tổng hợp lân cận. Đầu ra tại mỗi tầng tích chập kết hợp đặc trưng gốc của sinh viên và đặc trưng tổng hợp từ các sinh viên lân cận tương đồng học lực."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "class MLPRegressor(nn.Module):\n",
    "    def __init__(self, in_dim):\n",
    "        super().__init__()\n",
    "        self.fc1 = nn.Linear(in_dim, 64)\n",
    "        self.fc2 = nn.Linear(64, 32)\n",
    "        self.out = nn.Linear(32, 1)\n",
    "        \n    def forward(self, x):\n",
    "        x = F.relu(self.fc1(x))\n",
    "        x = F.relu(self.fc2(x))\n",
    "        return self.out(x)\n",
    "\n",
    "class GraphSAGE(nn.Module):\n",
    "    def __init__(self, in_dim, hidden=64):\n",
    "        super().__init__()\n",
    "        self.fc1 = nn.Linear(in_dim * 2, hidden)\n",
    "        self.fc2 = nn.Linear(hidden, 32)\n",
    "        self.out = nn.Linear(32, 1)\n",
    "        \n    def forward(self, x, adj):\n",
    "        # Thực hiện phép tích chập tổng hợp lân cận (1-hop)\n",
    "        neigh = torch.matmul(adj, x)\n",
    "        # Ghép (concat) đặc trưng của bản thân nút và đặc trưng lân cận\n",
    "        h = torch.cat([x, neigh], dim=1)\n",
    "        h = F.relu(self.fc1(h))\n",
    "        h = F.relu(self.fc2(h))\n",
    "        return self.out(h)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Nhiệm vụ 4: Huấn luyện Mô hình với Early Stopping & Tối ưu GPU\n",
    "\n",
    "Chúng ta thực hiện huấn luyện các mô hình PyTorch trên GPU (`device`), ghi lại nhật ký huấn luyện (logs) sau mỗi 20 epoch. Áp dụng cơ chế Early Stopping với patience = 20 epochs trên tập validation để bảo toàn trọng số tối ưu nhất."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def train_pytorch_model(model, inputs, targets, train_idx_t, test_idx_t, model_name, graph_mode=False, epochs=500, lr=0.01, patience=20):\n",
    "    optimizer = torch.optim.Adam(model.parameters(), lr=lr)\n",
    "    loss_fn = nn.MSELoss()\n",
    "    \n    best_loss = float('inf')\n",
    "    best_model_weights = None\n",
    "    patience_counter = 0\n",
    "    \n    train_losses = []\n",
    "    val_losses = []\n",
    "    \n    print(f\"--- Đang huấn luyện {model_name} trên {device} ---\")\n",
    "    for epoch in range(1, epochs + 1):\n",
    "        model.train()\n",
    "        optimizer.zero_grad()\n",
    "        \n        if graph_mode:\n            pred = model(inputs, A_norm_tensor)\n        else:\n            pred = model(inputs)\n            \n        loss = loss_fn(pred[train_idx_t], targets[train_idx_t])\n        loss.backward()\n        optimizer.step()\n        \n        # Đánh giá tập validation\n        model.eval()\n        with torch.no_grad():\n            if graph_mode:\n                test_pred = model(inputs, A_norm_tensor)\n            else:\n                test_pred = model(inputs)\n            test_loss = loss_fn(test_pred[test_idx_t], targets[test_idx_t])\n            \n        train_losses.append(loss.item())\n        val_losses.append(test_loss.item())\n        \n        if epoch % 20 == 0 or epoch == 1:\n            print(f\"Epoch {epoch:03d} | Train MSE: {loss.item():.4f} | Val MSE: {test_loss.item():.4f}\")\n            \n        # Kiểm tra Early stopping\n        if test_loss.item() < best_loss:\n            best_loss = test_loss.item()\n            best_model_weights = copy.deepcopy(model.state_dict())\n            patience_counter = 0\n        else:\n            patience_counter += 1\n            if patience_counter >= patience:\n                print(f\"Kích hoạt dừng sớm ở epoch {epoch}. Val MSE tốt nhất: {best_loss:.4f}\")\n                break\n                \n    model.load_state_dict(best_model_weights)\n    return model, train_losses, val_losses\n\n# Huấn luyện MLP (GNN-style)\nmlp_model = MLPRegressor(X_mlp_tensor.shape[1]).to(device)\nmlp_model, mlp_train_loss, mlp_val_loss = train_pytorch_model(\n    mlp_model, X_mlp_tensor, y_tensor, train_idx_tensor, test_idx_tensor, \"MLP (GNN-style)\"\n)\n\n# Huấn luyện GraphSAGE\nsage_model = GraphSAGE(X_tensor.shape[1]).to(device)\nsage_model, sage_train_loss, sage_val_loss = train_pytorch_model(\n    sage_model, X_tensor, y_tensor, train_idx_tensor, test_idx_tensor, \"GraphSAGE\", graph_mode=True\n)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Vẽ đường cong Loss (Training Curves)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(12, 5))\n",
    "plt.subplot(1, 2, 1)\n",
    "plt.plot(mlp_train_loss, label='Train Loss')\n",
    "plt.plot(mlp_val_loss, label='Val Loss')\n",
    "plt.title('Đường cong Loss - MLP (GNN-style)')\n",
    "plt.xlabel('Epochs')\n",
    "plt.ylabel('MSE')\n",
    "plt.legend()\n",
    "\n",
    "plt.subplot(1, 2, 2)\n",
    "plt.plot(sage_train_loss, label='Train Loss')\n",
    "plt.plot(sage_val_loss, label='Val Loss')\n",
    "plt.title('Đường cong Loss - GraphSAGE')\n",
    "plt.xlabel('Epochs')\n",
    "plt.ylabel('MSE')\n",
    "plt.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Huấn luyện các mô hình Baseline Học Máy\n",
    "Chúng ta huấn luyện Mô hình 1: Gradient Boosting Regressor, và Mô hình 4: Random Forest Regressor."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "print(\"Đang huấn luyện Gradient Boosting...\")\n",
    "gb_model = GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42)\n",
    "gb_model.fit(X_train_tab, y_train_tab)\n",
    "\n",
    "print(\"Đang huấn luyện Random Forest...\")\n",
    "rf_model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)\n",
    "rf_model.fit(X_train_tab, y_train_tab)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Nhiệm vụ 3: Đánh giá mô hình bằng 5 chỉ số\n",
    "\n",
    "Chúng ta đánh giá và so sánh 4 mô hình trên tập kiểm thử test (20%) thông qua 5 chỉ số đo lường:\n",
    "- MAE (Sai số tuyệt đối trung bình)\n",
    "- MSE (Sai số bình phương trung bình)\n",
    "- RMSE (Căn sai số bình phương trung bình)\n",
    "- MAPE (Sai số phần trăm tuyệt đối trung bình)\n",
    "- $R^2$ (Hệ số xác định)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "def calculate_metrics(y_true, y_pred):\n",
    "    mae = mean_absolute_error(y_true, y_pred)\n",
    "    mse = mean_squared_error(y_true, y_pred)\n",
    "    rmse = np.sqrt(mse)\n",
    "    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100\n",
    "    r2 = r2_score(y_true, y_pred)\n",
    "    return mae, mse, rmse, mape, r2\n",
    "\n",
    "# Lấy dự đoán của các mô hình trên tập test\n",
    "gb_pred = gb_model.predict(X_test_tab)\n",
    "rf_pred = rf_model.predict(X_test_tab)\n",
    "\n",
    "mlp_model.eval()\n",
    "sage_model.eval()\n",
    "with torch.no_grad():\n",
    "    mlp_pred = mlp_model(X_mlp_tensor)[test_idx_tensor].cpu().numpy().squeeze()\n",
    "    sage_pred = sage_model(X_tensor, A_norm_tensor)[test_idx_tensor].cpu().numpy().squeeze()\n",
    "\n",
    "y_test_numpy = y_test_tab.values\n",
    "\n",
    "# Tổng hợp các chỉ số đánh giá\n",
    "models_metrics = {\n",
    "    'V1: GBoost': calculate_metrics(y_test_numpy, gb_pred),\n",
    "    'V2: MLP GNN-style': calculate_metrics(y_test_numpy, mlp_pred),\n",
    "    'V3: GraphSAGE': calculate_metrics(y_test_numpy, sage_pred),\n",
    "    'V4: Random Forest': calculate_metrics(y_test_numpy, rf_pred)\n",
    "}\n",
    "\n",
    "metrics_df = pd.DataFrame(models_metrics, index=['MAE', 'MSE', 'RMSE', 'MAPE (%)', 'R2']).T\n",
    "metrics_df = metrics_df.round(4)\n",
    "metrics_df['MAPE (%)'] = metrics_df['MAPE (%)'].apply(lambda x: f\"{x:.2f}%\")\n",
    "print(\"--- BẢNG SO SÁNH HIỆU NĂNG MÔ HÌNH ---\")\n",
    "print(metrics_df)\n",
    "\n",
    "# Lưu bảng so sánh\n",
    "metrics_df.to_csv('plots/model_comparison.csv')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Trực quan hóa So sánh Các Chỉ số"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "metrics_plot_df = pd.DataFrame(models_metrics, index=['MAE', 'MSE', 'RMSE', 'MAPE', 'R2']).T\n",
    "fig, axes = plt.subplots(2, 2, figsize=(14, 10))\n",
    "axes = axes.flatten()\n",
    "metric_names = ['MAE', 'MSE', 'RMSE', 'R2']\n",
    "for i, metric in enumerate(metric_names):\n",
    "    sns.barplot(x=metrics_plot_df.index, y=metrics_plot_df[metric], ax=axes[i], hue=metrics_plot_df.index, palette='Set2', legend=False)\n",
    "    axes[i].set_title(f'So sánh chỉ số {metric}', fontsize=13)\n",
    "    axes[i].set_ylabel(metric)\n",
    "    for p in axes[i].patches:\n",
    "        axes[i].annotate(f\"{p.get_height():.3f}\", (p.get_x() + p.get_width() / 2., p.get_height()),\n",
    "                         ha='center', va='center', xytext=(0, 5), textcoords='offset points')\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Biểu đồ phân tán (Scatter Plot): Thực tế vs Dự đoán"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "fig, axes = plt.subplots(2, 2, figsize=(13, 11))\n",
    "axes = axes.flatten()\n",
    "predictions = [gb_pred, mlp_pred, sage_pred, rf_pred]\n",
    "model_names = ['V1: GBoost', 'V2: MLP (GNN-style)', 'V3: GraphSAGE', 'V4: Random Forest']\n",
    "\n",
    "for i, (pred, name) in enumerate(zip(predictions, model_names)):\n",
    "    sns.scatterplot(x=y_test_numpy, y=pred, ax=axes[i], alpha=0.6, color='darkcyan')\n",
    "    axes[i].plot([4, 10], [4, 10], 'r--', lw=2)\n",
    "    axes[i].set_title(f'{name}: Thực tế vs Dự đoán')\n",
    "    axes[i].set_xlabel('Điểm thực tế')\n",
    "    axes[i].set_ylabel('Điểm dự đoán')\n",
    "    axes[i].set_xlim(3.8, 10.2)\n",
    "    axes[i].set_ylim(3.8, 10.2)\n",
    "plt.tight_layout()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Nhiệm vụ 4: So sánh dưới các cấu trúc xã hội khác nhau\n",
    "\n",
    "Chúng ta mô phỏng đồ thị với các ngưỡng khoảng cách học thuật khác nhau $D_{\\text{threshold}} \\in \\{3.0, 5.0, 7.0, 9.0\\}$ nhằm đại diện cho các kiểu cấu trúc mạng lưới lân cận:\n",
    "- **Ngưỡng nhỏ (3.0, 5.0)** đại diện cho đồ thị thưa (chỉ kết nối với những người bạn cực kỳ giống nhau về điểm số).\n",
    "- **Ngưỡng lớn (9.0)** đại diện cho đồ thị dày đặc (hầu như tất cả mọi người đều kết nối, khiến các nút dễ bị đồng hóa đặc trưng và giảm sút độ chính xác).\n",
    "\n",
    "Chúng ta đánh giá sự thay đổi hiệu năng dự đoán của GraphSAGE."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "thresholds = [3.0, 5.0, 7.0, 9.0]\n",
    "results_structs = []\n",
    "\n",
    "for th in thresholds:\n",
    "    A_th = (dists < th).astype(float)\n",
    "    np.fill_diagonal(A_th, 0)\n",
    "    avg_degree = A_th.sum(axis=1).mean()\n",
    "    A_th_norm = A_th / (A_th.sum(axis=1, keepdims=True) + 1e-6)\n",
    "    A_th_norm_tensor = torch.tensor(A_th_norm, dtype=torch.float32).to(device)\n",
    "    \n",
    "    # Huấn luyện mô hình GraphSAGE cho cấu trúc này\n",
    "    model_th = GraphSAGE(X_tensor.shape[1]).to(device)\n",
    "    model_th, _, _ = train_pytorch_model(\n",
    "        model_th, X_tensor, y_tensor, train_idx_tensor, test_idx_tensor, f\"GraphSAGE (Ngưỡng={th})\", \n",
    "        graph_mode=True, patience=15, epochs=150\n",
    "    )\n",
    "    \n",
    "    model_th.eval()\n",
    "    with torch.no_grad():\n",
    "        th_pred = model_th(X_tensor, A_th_norm_tensor)[test_idx_tensor].cpu().numpy().squeeze()\n",
    "    \n",
    "    mae, mse, rmse, mape, r2 = calculate_metrics(y_test_numpy, th_pred)\n",
    "    results_structs.append({\n",
    "        'Ngưỡng': th,\n",
    "        'Bậc trung bình (Mật độ mạng)': avg_degree,\n",
    "        'MAE': mae,\n",
    "        'R2': r2\n",
    "    })\n",
    "\n",
    "struct_df = pd.DataFrame(results_structs)\n",
    "print(struct_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Biểu đồ Phân tích Hiệu Năng GNN theo Cấu Trúc Mạng Xã Hội"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "fig, ax1 = plt.subplots(figsize=(10, 6))\n",
    "color = 'tab:blue'\n",
    "ax1.set_xlabel('Ngưỡng Khoảng Cách Học Lực (Càng thấp = Bạn bè càng giống học lực)')\n",
    "ax1.set_ylabel('Sai số MAE của mô hình', color=color)\n",
    "ax1.plot(struct_df['Ngưỡng'], struct_df['MAE'], marker='o', color=color, linewidth=2)\n",
    "ax1.tick_params(axis='y', labelcolor=color)\n",
    "\n",
    "ax2 = ax1.twinx()\n",
    "color = 'tab:red'\n",
    "ax2.set_ylabel('Bậc trung bình của nút (Số bạn bè liên kết)', color=color)\n",
    "ax2.plot(struct_df['Ngưỡng'], struct_df['Bậc trung bình (Mật độ mạng)'], marker='s', linestyle='--', color=color, linewidth=2)\n",
    "ax2.tick_params(axis='y', labelcolor=color)\n",
    "\n",
    "plt.title('Hiệu Năng GraphSAGE Dưới Các Cấu Trúc Mạng Khác Nhau', fontsize=15)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Nhiệm vụ 5: Phân tích sự lan truyền ảnh hưởng từ bạn bè\n",
    "\n",
    "Chúng ta thực hiện mô phỏng kịch bản khi điểm số bạn bè của tất cả các sinh viên được tăng thêm +2 điểm (ví dụ: nhờ hoạt động học nhóm tích cực giúp nâng cao kết quả học tập). Chúng ta quan sát sự dịch chuyển điểm dự đoán của mô hình MLP (GNN-style) và GraphSAGE:\n",
    "- MLP hoạt động dạng 0-hop (không lan truyền qua liên kết, phản ứng tức thì với trọng số điểm trung bình của bạn bè).\n",
    "- GraphSAGE thực hiện lan truyền qua các liên kết mạng lưới lân cận tương đồng (1-hop message passing), giúp biến đổi điểm số dự đoán một cách tự nhiên và thực tế hơn."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "sage_model.eval()\n",
    "mlp_model.eval()\n",
    "with torch.no_grad():\n",
    "    base_preds_sage = sage_model(X_tensor, A_norm_tensor).cpu().numpy().squeeze()\n",
    "    base_preds_mlp = mlp_model(X_mlp_tensor).cpu().numpy().squeeze()\n",
    "\n",
    "# Kịch bản nhiễu tăng điểm số bạn bè thêm +2\n",
    "X_perturbed = X.copy()\n",
    "X_perturbed[:, 5:15] = np.clip(X_perturbed[:, 5:15] + 2, 4, 10)\n",
    "X_perturbed_tensor = torch.tensor(X_perturbed, dtype=torch.float32).to(device)\n",
    "\n",
    "# Đặc trưng MLP tương ứng khi có nhiễu\n",
    "peer_mean_pert = X_perturbed[:, 5:15].mean(axis=1)\n",
    "peer_std_pert = X_perturbed[:, 5:15].std(axis=1)\n",
    "X_mlp_pert = np.hstack([X_perturbed, peer_mean_pert.reshape(-1, 1), peer_std_pert.reshape(-1, 1)])\n",
    "X_mlp_pert_tensor = torch.tensor(X_mlp_pert, dtype=torch.float32).to(device)\n",
    "\n",
    "with torch.no_grad():\n",
    "    pert_preds_sage = sage_model(X_perturbed_tensor, A_norm_tensor).cpu().numpy().squeeze()\n",
    "    pert_preds_mlp = mlp_model(X_mlp_pert_tensor).cpu().numpy().squeeze()\n",
    "\n",
    "shift_sage = pert_preds_sage - base_preds_sage\n",
    "shift_mlp = pert_preds_mlp - base_preds_mlp\n",
    "\n",
    "print(f\"Điểm tăng trung bình dự đoán bởi GraphSAGE: {shift_sage.mean():.4f}\")\n",
    "print(f\"Điểm tăng trung bình dự đoán bởi MLP GNN-style: {shift_mlp.mean():.4f}\")\n",
    "\n",
    "# Vẽ phân phối mật độ của mức dịch chuyển\n",
    "plt.figure(figsize=(9, 5))\n",
    "sns.kdeplot(shift_sage, label='GraphSAGE (Có lan truyền qua mạng lưới)', fill=True, color='teal')\n",
    "sns.kdeplot(shift_mlp, label='MLP (0-hop, Phản ứng tức thì)', fill=True, color='orange')\n",
    "plt.title('Phân Phối Mức Độ Tăng Điểm Dự Đoán (+2 điểm bạn bè)', fontsize=15)\n",
    "plt.xlabel('Chênh lệch điểm dự đoán (Sau - Trước)')\n",
    "plt.ylabel('Mật độ phân bố')\n",
    "plt.legend()\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Lưu trữ Mô hình Tốt nhất\n",
    "\n",
    "Cuối cùng, chúng ta xuất toàn bộ các trọng số mô hình đã huấn luyện thành công và bộ dữ liệu tham chiếu ra đĩa, giúp ứng dụng Streamlit (`app.py`) có thể tải và chạy dự đoán thời gian thực một cách dễ dàng."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pickle\n",
    "\n",
    "# Lưu Gradient Boosting\n",
    "with open('models/gboost_model.pkl', 'wb') as f:\n",
    "    pickle.dump(gb_model, f)\n",
    "\n",
    "# Lưu Random Forest\n",
    "with open('models/random_forest_model.pkl', 'wb') as f:\n",
    "    pickle.dump(rf_model, f)\n",
    "\n",
    "# Lưu PyTorch MLP\n",
    "torch.save(mlp_model.state_dict(), 'models/mlp_model.pth')\n",
    "\n",
    "# Lưu GraphSAGE\n",
    "torch.save(sage_model.state_dict(), 'models/sage_model.pth')\n",
    "\n",
    "# Lưu tập tham chiếu để thực hiện dự đoán quy nạp (inductive inference) cho nút mới trong GNN\n",
    "reference_data = {\n",
    "    'X_academic_train': X_academic,\n",
    "    'X_peer_train': X_peer,\n",
    "    'X_train': X,\n",
    "    'y_train': y\n",
    "}\n",
    "with open('models/reference_data.pkl', 'wb') as f:\n",
    "    pickle.dump(reference_data, f)\n",
    "\n",
    "print(\"Đã xuất tất cả các mô hình và tập tham chiếu thành công!\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Khởi chạy ứng dụng giao diện (Streamlit App)\n",
    "\n",
    "Để chạy ứng dụng web trực quan giúp nhập điểm sinh viên và dự đoán điểm kết quả thời gian thực bằng các mô hình đã huấn luyện, hãy chạy cell dưới đây. \n",
    "\n",
    "Sau khi chạy, bạn có thể click vào đường link hiển thị (thường là [http://localhost:8501](http://localhost:8501)) để tương tác trên trình duyệt. Để tắt dịch vụ Streamlit, bạn hãy nhấn nút dừng (Interrupt Kernel) trong Jupyter."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "!streamlit run app.py"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbformat_minor": 2,
   "nbformat": 4,
   "language_version": "3.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

# Ghi tệp JSON notebook
with open('student_score_prediction.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, indent=1)

print("Vietnamese Jupyter Notebook created successfully at student_score_prediction.ipynb!")
