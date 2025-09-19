import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset
import numpy as np
from importlib import resources

# -----------------------------
# Model Loading Helper
# -----------------------------
def get_model_path():
    """Return path to exoplanet_model.pth inside package or use EXSO_MODEL_PATH override."""
    env_path = os.environ.get("EXSO_MODEL_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Load from package using importlib.resources
    try:
        with resources.path("exso_sdk.model_data", "exoplanet_model.pth") as model_path:
            return str(model_path)
    except (ImportError, FileNotFoundError):
        # Fallback for development or if package data is not available
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(current_dir, "model_data")
        model_path = os.path.join(model_dir, "exoplanet_model.pth")
        
        if os.path.exists(model_path):
            return model_path
        else:
            raise FileNotFoundError(f"Model file not found at {model_path}")

# -----------------------------
# Dataset
# -----------------------------
class ExoplanetDataset(Dataset):
    def __init__(self, df, feature_cols, target_col=None):
        self.X = df[feature_cols].values.astype(np.float32)
        self.y = df[target_col].values.astype(np.float32) if target_col else None

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if self.y is not None:
            return self.X[idx], self.y[idx]
        else:
            return self.X[idx]

# -----------------------------
# Model Definition - Transformer-based
# -----------------------------
class ExoplanetTransformer(nn.Module):
    def __init__(self, input_dim=16, hidden_dim=128, num_classes=3, num_layers=4):
        super(ExoplanetTransformer, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        
        # Feature embedding
        self.feature_emb = nn.Linear(input_dim, hidden_dim)
        
        # Missing value embedding
        self.missing_emb = nn.Parameter(torch.randn(hidden_dim))
        
        # CLS token
        self.cls_token = nn.Parameter(torch.randn(1, hidden_dim))
        
        # Value projection
        self.value_proj = nn.Linear(1, hidden_dim)
        
        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=8,
            dim_feedforward=512,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Layer normalization
        self.norm = nn.LayerNorm(hidden_dim)
        
        # Classification head
        self.head = nn.Linear(hidden_dim, num_classes)
        
    def forward(self, x, mask=None):
        batch_size = x.size(0)
        
        # Feature embedding
        x_emb = self.feature_emb(x)  # [batch_size, input_dim] -> [batch_size, hidden_dim]
        
        # Add missing value embedding if mask is provided
        if mask is not None:
            missing_mask = mask.unsqueeze(-1).expand_as(x_emb)
            x_emb = torch.where(missing_mask, self.missing_emb.unsqueeze(0).expand_as(x_emb), x_emb)
        
        # Add CLS token
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)  # [batch_size, 1, hidden_dim]
        x_with_cls = torch.cat([cls_tokens, x_emb.unsqueeze(1)], dim=1)  # [batch_size, 2, hidden_dim]
        
        # Value projection
        x_proj = self.value_proj(torch.ones(batch_size, 2, 1).to(x.device))  # [batch_size, 2, hidden_dim]
        x_final = x_with_cls + x_proj
        
        # Transformer encoding
        x_transformed = self.transformer(x_final)
        
        # Use CLS token for classification
        cls_output = x_transformed[:, 0]  # [batch_size, hidden_dim]
        
        # Layer normalization and classification
        x_norm = self.norm(cls_output)
        logits = self.head(x_norm)
        
        return logits

class SimpleNN(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_classes=3):
        super(SimpleNN, self).__init__()
        self.feature = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
        )
        self.classifier = nn.Linear(hidden_dim//2, num_classes)

    def forward(self, x):
        x = self.feature(x)
        logits = self.classifier(x)
        return logits

def build_model(input_dim, config=None):
    # Use SimpleNN for compatibility with saved model
    hidden_dim = config.get("hidden_dim", 64) if config else 64
    num_classes = config.get("num_classes", 3) if config else 3
    return SimpleNN(input_dim, hidden_dim, num_classes)

# -----------------------------
# Training / Evaluation
# -----------------------------
def train_model(model, train_loader, val_loader, config):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.get('lr', 1e-3))
    epochs = config.get('epochs', 10)
    best_val_loss = float('inf')

    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device).long()
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * X_batch.size(0)
        train_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_val, y_val in val_loader:
                X_val, y_val = X_val.to(device), y_val.to(device).long()
                logits = model(X_val)
                loss = criterion(logits, y_val)
                val_loss += loss.item() * X_val.size(0)
        val_loss /= len(val_loader.dataset)

        print(f"Epoch {epoch+1}/{epochs} Train Loss: {train_loss:.4f} Val Loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            save_model(model)
            print("Saved best model")

def evaluate_model(model, data_loader):
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for X_batch, y_batch in data_loader:
            X_batch = X_batch.to(device)
            logits = model(X_batch).cpu()
            preds = logits.argmax(dim=1).numpy()
            y_true.extend(y_batch.numpy())
            y_pred.extend(preds)
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='macro', zero_division=0),
        'recall': recall_score(y_true, y_pred, average='macro', zero_division=0),
        'f1': f1_score(y_true, y_pred, average='macro', zero_division=0),
        'confusion_matrix': confusion_matrix(y_true, y_pred),
        'auc': None  # omitted for multiclass
    }

def predict(model, sample):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()
    if not isinstance(sample, torch.Tensor):
        sample = torch.tensor(sample, dtype=torch.float32)
    sample = sample.to(device)
    with torch.no_grad():
        logits = model(sample.unsqueeze(0)).cpu()
        probs = torch.softmax(logits, dim=1).squeeze(0)
        pred_class = int(torch.argmax(probs).item())
    return pred_class, probs.numpy()

# -----------------------------
# Save / Load
# -----------------------------
def save_model(model, path=None):
    if path is None:
        path = get_model_path()
    torch.save(model.state_dict(), path)

def load_model(input_dim, config=None, path=None):
    if path is None:
        path = get_model_path()
    
    # Load the saved model data
    checkpoint = torch.load(path, map_location='cpu')
    
    # Check if it's a checkpoint with model_state_dict or just state_dict
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        state_dict = checkpoint['model_state_dict']
        # Also extract scaler if available
        scaler = checkpoint.get('scaler', None)
        features = checkpoint.get('features', None)
    else:
        state_dict = checkpoint
        scaler = None
        features = None
    
    # Create model with correct architecture
    model = build_model(input_dim, config)
    
    # Load the state dict
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    
    return model
