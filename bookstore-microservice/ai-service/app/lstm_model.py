import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from django.conf import settings

# Define the 5-layer LSTM neural network
class LSTMRecommender(nn.Module):
    """
    A 5-layer neural network architecture for item sequence prediction:
    1. Embedding Layer: maps item IDs to dense vectors.
    2, 3, 4. Stacked LSTM (3 layers): processes the sequence of item embeddings.
    5. Fully Connected Output Layer: outputs scores/logits for each potential item.
    """
    def __init__(self, num_items, embedding_dim=64, hidden_dim=128):
        super().__init__()
        # Layer 1: Embedding Layer
        self.embedding = nn.Embedding(num_items, embedding_dim, padding_idx=0)
        
        # Layers 2, 3, 4: Stacked LSTM Layer (3 layers stacked internally)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=3, batch_first=True)
        
        # Layer 5: Dense Output Projection Layer
        self.fc = nn.Linear(hidden_dim, num_items)

    def forward(self, x):
        # x shape: [batch_size, seq_len]
        embeds = self.embedding(x) # shape: [batch_size, seq_len, embedding_dim]
        lstm_out, _ = self.lstm(embeds) # shape: [batch_size, seq_len, hidden_dim]
        # We take the output of the last sequence step
        last_step = lstm_out[:, -1, :] # shape: [batch_size, hidden_dim]
        logits = self.fc(last_step) # shape: [batch_size, num_items]
        return logits


def get_model_path():
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'lstm_model.pt')


def train_lstm_model(behaviors=None, num_epochs=5, batch_size=8):
    """
    Train the LSTM model on interaction sequences.
    If behaviors is empty/None, generates synthetic interaction patterns to bootstrap training.
    """
    # 1. Determine Vocabulary Size (Item IDs)
    # We support up to product ID 1000 dynamically
    num_items = 1000 
    
    # 2. Extract sequences from user behaviors
    sequences = []
    targets = []
    
    if behaviors and len(behaviors) >= 5:
        # Group behaviors by user_id
        user_history = {}
        for b in behaviors:
            uid = b.user_id
            pid = b.product_id
            user_history.setdefault(uid, []).append(pid)
            
        # Build sequences (e.g. sequence window of 5 items to predict 6th item)
        window_size = 5
        for uid, items in user_history.items():
            if len(items) > window_size:
                for i in range(len(items) - window_size):
                    sequences.append(items[i:i+window_size])
                    targets.append(items[i+window_size])
                    
    # 3. Generate synthetic data if not enough real data is present
    if len(sequences) < 5:
        print("Not enough user behavior data for training. Seeding synthetic sequence data...")
        # Simple cyclic sequential interactions: user views book 1 -> 2 -> 3 -> 4 -> 5 predicts 6
        for i in range(1, 20):
            seq = [i, i+1, i+2, i+3, i+4]
            target = i+5
            sequences.append(seq)
            targets.append(target)
            
    # Convert to PyTorch tensors
    X_train = torch.tensor(sequences, dtype=torch.long)
    y_train = torch.tensor(targets, dtype=torch.long)
    
    # Instantiate model, loss, optimizer
    model = LSTMRecommender(num_items=num_items)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)
    
    # Training Loop
    model.train()
    dataset_size = len(X_train)
    for epoch in range(num_epochs):
        epoch_loss = 0
        permutation = torch.randperm(dataset_size)
        for i in range(0, dataset_size, batch_size):
            indices = permutation[i:i+batch_size]
            batch_x, batch_y = X_train[indices], y_train[indices]
            
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(batch_x)
        print(f"Epoch {epoch+1}/{num_epochs} Loss: {epoch_loss/dataset_size:.4f}")
        
    # Save the model
    model_path = get_model_path()
    torch.save(model.state_dict(), model_path)
    print(f"LSTM model saved successfully to {model_path}!")
    return model


def get_lstm_recommendations(user_id, user_history, limit=10):
    """
    Predict next items based on user history sequence.
    """
    model_path = get_model_path()
    num_items = 1000
    model = LSTMRecommender(num_items=num_items)
    
    if os.path.exists(model_path):
        try:
            model.load_state_dict(torch.load(model_path))
        except Exception as e:
            print(f"Error loading LSTM model weights: {e}. Re-training model...")
            model = train_lstm_model()
    else:
        print("LSTM model weights not found. Auto-training...")
        model = train_lstm_model()
        
    model.eval()
    
    # Prepare sequence input
    window_size = 5
    if not user_history:
        # Fallback to random popular items or dummy history
        user_history = [1, 2, 3, 4, 5]
        
    # Pad or slice history to exact window size
    if len(user_history) < window_size:
        seq = [0] * (window_size - len(user_history)) + user_history
    else:
        seq = user_history[-window_size:]
        
    seq_tensor = torch.tensor([seq], dtype=torch.long)
    
    with torch.no_grad():
        logits = model(seq_tensor)
        # Apply softmax to get probability scores
        probs = torch.softmax(logits, dim=1).numpy()[0]
        
    # Get top items, excluding padding item 0 and items already in the input sequence
    exclude = set(seq)
    exclude.add(0)
    
    sorted_indices = np.argsort(probs)[::-1]
    recommendations = []
    
    for idx in sorted_indices:
        item_id = int(idx)
        if item_id not in exclude:
            recommendations.append((item_id, float(probs[item_id])))
        if len(recommendations) >= limit:
            break
            
    return recommendations
