# TODO.md

# Prediction of Final Exam Score Using Machine Learning Models

## Student: Đỗ Ngọc Lâm - B22DCCN476

---

# OVERVIEW

Mục tiêu của project:

Dự đoán điểm thi cuối kỳ (FinalExam) dựa trên:

* Thành tích học tập cá nhân
* Ảnh hưởng từ bạn bè
* Đặc trưng mạng xã hội

So sánh 3 mô hình:

1. HistGradientBoostingRegressor
2. Deep MLP
3. GraphSAGE

Thực hiện đầy đủ các yêu cầu của đề:

* Dataset Construction
* Model Training
* Evaluation
* Social Structure Comparison
* Peer Influence Analysis

---

# PROJECT STRUCTURE

```text
project/

├── data/
│   ├── raw/
│   ├── processed/
│
├── notebooks/
│   ├── 01_data_generation_eda.ipynb
│   └── 02_training_comparison_analysis.ipynb
│
├── figures/
│
├── models/
│
├── results/
│
└── report/
```

---

# NOTEBOOK 1

# 01_data_generation_eda.ipynb

---

# SECTION 1

# IMPORTS & CONFIG

## TODO

Import:

* numpy
* pandas
* matplotlib
* seaborn
* networkx
* sklearn
* scipy

Thiết lập:

```python
# Đỗ Ngọc Lâm - B22DCCN476
np.random.seed(42)
```

---

# SECTION 2

# GENERATE LATENT STUDENT FACTORS

Không sinh dữ liệu ngẫu nhiên đơn giản.

Mỗi sinh viên phải có các yếu tố ẩn:

## ability

Năng lực học tập.

```python
N(0,1)
```

---

## motivation

Mức độ chăm chỉ.

```python
N(0,1)
```

---

## social_activity

Mức độ tham gia xã hội.

```python
N(0,1)
```

---

## study_hours

Số giờ học mỗi tuần.

Sinh từ:

ability + motivation

---

# SECTION 3

# GENERATE ACADEMIC FEATURES

Sinh:

* Java Programming
* Python Programming
* Data Structure
* Software Analysis and Design
* Intelligent System Development

---

## IMPORTANT

Các môn phải tương quan với nhau.

Ví dụ:

Java ảnh hưởng Python.

Data Structure ảnh hưởng Java.

Ability ảnh hưởng toàn bộ.

Không dùng:

```python
randint()
```

---

# SECTION 4

# BUILD SOCIAL NETWORK

Số lượng sinh viên:

```python
N = 10000
```

---

## Graph Construction

Sử dụng:

```python
networkx.barabasi_albert_graph()
```

hoặc

```python
networkx.stochastic_block_model()
```

---

Lưu:

* edge list
* adjacency matrix

---

# SECTION 5

# GENERATE FRIEND SCORES

Mỗi sinh viên:

10 người bạn.

---

Tạo:

```python
friend_1
friend_2
...
friend_10
```

---

# SECTION 6

# PEER INFLUENCE PROPAGATION

Mô phỏng lan truyền ảnh hưởng.

Công thức:

new_score =
0.8 × self_score
+
0.2 × neighbor_average

---

Lặp:

3 vòng

để tạo hiệu ứng xã hội.

---

# SECTION 7

# SOCIAL FEATURES

Tính:

## Degree

```python
degree
```

---

## Clustering Coefficient

```python
clustering_coef
```

---

## PageRank

```python
pagerank
```

---

## Betweenness

```python
betweenness
```

---

## Neighbor Mean Score

```python
neighbor_score_mean
```

---

# SECTION 8

# PEER FEATURES

Tính:

```python
peer_mean
peer_std
peer_max
peer_min
peer_median
peer_range
```

---

# SECTION 9

# GENERATE TARGET

Target:

```python
FinalExam
```

Không sử dụng hàm tuyến tính đơn giản.

Thêm:

* interaction terms
* nonlinear effects

Ví dụ:

Java × Python

PeerMean²

sin(peer_mean)

noise

---

Mục tiêu:

Dataset đủ khó để:

* MLP mạnh hơn Linear
* GraphSAGE mạnh hơn MLP

---

# SECTION 10

# CREATE DATAFRAME

Kiểm tra:

shape

columns

dtype

---

# SECTION 11

# DATA INSPECTION

Hiển thị:

```python
df.head()
```

---

```python
df.sample(10)
```

---

```python
df.describe()
```

---

```python
df.info()
```

---

# SECTION 12

# MISSING VALUES CHECK

Hiển thị:

* số lượng null
* tỷ lệ null

---

# SECTION 13

# TARGET ANALYSIS

Vẽ:

Histogram FinalExam

KDE Plot FinalExam

Boxplot FinalExam

---

# SECTION 14

# FEATURE DISTRIBUTIONS

Vẽ histogram cho:

* Java
* Python
* DataStructure
* SAD
* ISD
* PeerMean

---

# SECTION 15

# CORRELATION ANALYSIS

Heatmap toàn bộ features.

---

Tạo:

Top 20 correlated features với FinalExam.

---

# SECTION 16

# FEATURE RELATIONSHIPS

Scatter:

Java vs FinalExam

Python vs FinalExam

PeerMean vs FinalExam

PageRank vs FinalExam

StudyHours vs FinalExam

---

# SECTION 17

# SOCIAL NETWORK VISUALIZATION

Vẽ graph mẫu:

500 node.

---

Vẽ:

Degree Distribution

---

Vẽ:

Community Structure

---

# SECTION 18

# FEATURE IMPORTANCE EXPLORATION

Mutual Information

---

Random Forest Feature Importance

---

# SECTION 19

# DIMENSIONALITY REDUCTION

PCA

2D Visualization

---

t-SNE

2D Visualization

---

# SECTION 20

# SAVE DATASET

Lưu:

```python
data/processed/dataset.csv
```

---

=================================================
NOTEBOOK 2
==========

# 02_training_comparison_analysis.ipynb

---

# SECTION 1

# DATA LOADING

Load dataset.

---

Train:

70%

Validation:

15%

Test:

15%

---

# SECTION 2

# FEATURE SCALING

StandardScaler

---

# SECTION 3

# MODEL 1

# HISTGRADIENTBOOSTING

---

Huấn luyện:

HistGradientBoostingRegressor

---

Hyperparameters:

* learning_rate
* max_depth
* max_iter
* l2_regularization

---

Early Stopping:

BẬT

---

Validation Monitoring:

BẬT

---

# VISUALIZATION

Learning Curve

Actual vs Predicted

Residual Plot

Residual Distribution

Feature Importance

SHAP Summary

SHAP Bar

---

# METRICS

MAE

MSE

RMSE

MAPE

R²

Adjusted R²

---

Lưu model.

---

# SECTION 4

# MODEL 2

# DEEP MLP

---

Architecture

Input

↓

256

↓

BatchNorm

↓

Dropout

↓

128

↓

BatchNorm

↓

Dropout

↓

64

↓

32

↓

1

---

Loss

HuberLoss

---

Optimizer

AdamW

---

Scheduler

ReduceLROnPlateau

---

EarlyStopping

patience=20

---

ModelCheckpoint

save_best_model.pt

---

# VISUALIZATION

Train Loss

Validation Loss

Learning Curve

Actual vs Predicted

Residual Plot

Error Histogram

Prediction Density

---

# METRICS

MAE

MSE

RMSE

MAPE

R²

Adjusted R²

---

Lưu model.

---

# SECTION 5

# MODEL 3

# GRAPHSAGE

---

Framework

PyTorch Geometric

---

Graph:

Node = Student

Edge = Social Connection

---

Architecture

SAGEConv(32)

↓

BatchNorm

↓

Dropout

↓

SAGEConv(64)

↓

BatchNorm

↓

Dropout

↓

SAGEConv(32)

↓

Linear

↓

Output

---

Training

AdamW

---

EarlyStopping

---

Scheduler

ReduceLROnPlateau

---

Checkpoint

save_best_graphsage.pt

---

# VISUALIZATION

Learning Curve

Actual vs Predicted

Residual Plot

Prediction Error Distribution

Embedding PCA

Embedding t-SNE

---

# METRICS

MAE

MSE

RMSE

MAPE

R²

Adjusted R²

---

# SECTION 6

# CROSS VALIDATION

Thực hiện:

5-fold CV

cho:

* HistGB
* MLP

---

Báo cáo:

mean ± std

---

# SECTION 7

# MODEL COMPARISON

Tạo bảng:

| Model | MAE | RMSE | MAPE | R² |
| ----- | --- | ---- | ---- | -- |

---

Vẽ:

MAE Comparison

RMSE Comparison

MAPE Comparison

R² Comparison

---

Radar Chart

---

Prediction Comparison Plot

---

# SECTION 8

# SOCIAL STRUCTURE COMPARISON

Tạo:

Sparse Graph

Medium Graph

Dense Graph

---

Train lại GraphSAGE.

---

So sánh:

| Graph Type | MAE | RMSE | R² |
| ---------- | --- | ---- | -- |

---

Vẽ:

Bar Charts

Line Charts

---

# SECTION 9

# PEER INFLUENCE ANALYSIS

Phân tích:

PeerMean vs FinalExam

---

Degree vs FinalExam

---

PageRank vs FinalExam

---

Betweenness vs FinalExam

---

NeighborScoreMean vs FinalExam

---

Community vs Score

---

# SECTION 10

# FINAL CONCLUSION

Trả lời trực tiếp 5 câu hỏi của đề:

1. Dataset Construction
2. Model Performance
3. Evaluation Metrics
4. Social Structure Comparison
5. Peer Influence Propagation

---

# EXPECTED OUTPUT

Khoảng:

25 - 35 figures

5 - 10 tables

3 trained models

1 final comparison report

Notebook hoàn chỉnh có thể chạy từ đầu đến cuối mà không cần chỉnh sửa code.
