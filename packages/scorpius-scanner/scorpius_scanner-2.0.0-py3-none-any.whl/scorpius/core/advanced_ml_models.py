#!/usr/bin/env python3
"""
Scorpius Advanced ML Models
State-of-the-art machine learning models for vulnerability detection
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, BertConfig
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import networkx as nx
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

logger = logging.getLogger(__name__)

@dataclass
class ModelPrediction:
    """Model prediction result"""
    vulnerability_type: str
    confidence: float
    severity: str
    explanation: str
    features_used: List[str]

class CodeBERTClassifier(nn.Module):
    """CodeBERT-based vulnerability classifier"""
    
    def __init__(self, num_classes: int = 10, hidden_size: int = 768):
        super().__init__()
        self.codebert = AutoModel.from_pretrained('microsoft/codebert-base')
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 4, num_classes)
        )
        
    def forward(self, input_ids, attention_mask):
        outputs = self.codebert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        logits = self.classifier(pooled_output)
        return logits

class GraphNeuralNetwork(nn.Module):
    """Graph Neural Network for code structure analysis"""
    
    def __init__(self, input_dim: int = 128, hidden_dim: int = 256, num_classes: int = 10):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        
        # Graph convolution layers
        self.conv1 = nn.Linear(input_dim, hidden_dim)
        self.conv2 = nn.Linear(hidden_dim, hidden_dim)
        self.conv3 = nn.Linear(hidden_dim, hidden_dim)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, num_classes)
        )
        
    def forward(self, node_features, edge_index):
        # Graph convolution
        x = F.relu(self.conv1(node_features))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        
        # Global pooling
        x = torch.mean(x, dim=0, keepdim=True)
        
        # Classification
        logits = self.classifier(x)
        return logits

class TransformerEncoder(nn.Module):
    """Transformer encoder for sequence analysis"""
    
    def __init__(self, vocab_size: int = 30000, d_model: int = 512, nhead: int = 8, num_layers: int = 6, num_classes: int = 10):
        super().__init__()
        self.d_model = d_model
        
        # Embedding layers
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = nn.Embedding(1000, d_model)  # Max sequence length
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(d_model // 2, num_classes)
        )
        
    def forward(self, input_ids):
        seq_len = input_ids.size(1)
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        
        # Embeddings
        token_emb = self.token_embedding(input_ids)
        pos_emb = self.position_embedding(positions)
        x = token_emb + pos_emb
        
        # Transformer encoding
        x = self.transformer(x)
        
        # Global pooling and classification
        x = torch.mean(x, dim=1)  # Average pooling
        logits = self.classifier(x)
        
        return logits

class AdvancedMLModels:
    """
    Advanced machine learning models for vulnerability detection
    """
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize models
        self.codebert_model = None
        self.gnn_model = None
        self.transformer_model = None
        self.ensemble_models = {
            'random_forest': RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=200, random_state=42),
            'neural_network': MLPClassifier(hidden_layer_sizes=(1024, 512, 256), random_state=42, max_iter=1000)
        }
        
        # Tokenizers
        self.codebert_tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
        
        # Model configurations
        self.vulnerability_classes = [
            'reentrancy', 'access_control', 'oracle_manipulation', 'flash_loan_attack',
            'integer_overflow', 'governance_attack', 'dos_attack', 'front_running',
            'signature_replay', 'unchecked_call'
        ]
        
        self.severity_classes = ['Low', 'Medium', 'High', 'Critical']
        
    def initialize_models(self):
        """Initialize all ML models"""
        
        logger.info("Initializing advanced ML models...")
        
        # Initialize CodeBERT model
        self.codebert_model = CodeBERTClassifier(
            num_classes=len(self.vulnerability_classes)
        ).to(self.device)
        
        # Initialize GNN model
        self.gnn_model = GraphNeuralNetwork(
            input_dim=128,
            hidden_dim=256,
            num_classes=len(self.vulnerability_classes)
        ).to(self.device)
        
        # Initialize Transformer model
        self.transformer_model = TransformerEncoder(
            vocab_size=30000,
            d_model=512,
            nhead=8,
            num_layers=6,
            num_classes=len(self.vulnerability_classes)
        ).to(self.device)
        
        logger.info("✅ Advanced ML models initialized")
    
    def train_codebert_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train CodeBERT model on vulnerability data"""
        
        logger.info("Training CodeBERT model...")
        
        # Prepare training data
        texts = [item['code'] for item in training_data]
        labels = [self.vulnerability_classes.index(item['vulnerability']) for item in training_data]
        
        # Tokenize
        encodings = self.codebert_tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        
        # Convert to tensors
        input_ids = encodings['input_ids'].to(self.device)
        attention_mask = encodings['attention_mask'].to(self.device)
        labels = torch.tensor(labels, dtype=torch.long).to(self.device)
        
        # Training setup
        optimizer = torch.optim.AdamW(self.codebert_model.parameters(), lr=2e-5)
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        self.codebert_model.train()
        for epoch in range(3):  # 3 epochs
            optimizer.zero_grad()
            logits = self.codebert_model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            
            logger.info(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")
        
        # Evaluate
        self.codebert_model.eval()
        with torch.no_grad():
            logits = self.codebert_model(input_ids, attention_mask)
            predictions = torch.argmax(logits, dim=1)
            accuracy = (predictions == labels).float().mean().item()
        
        training_results = {
            'model_type': 'CodeBERT',
            'final_loss': loss.item(),
            'accuracy': accuracy,
            'epochs': 3,
            'training_samples': len(training_data)
        }
        
        logger.info(f"✅ CodeBERT training complete. Accuracy: {accuracy:.4f}")
        return training_results
    
    def train_gnn_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train Graph Neural Network model"""
        
        logger.info("Training GNN model...")
        
        # Prepare graph data
        graphs = []
        labels = []
        
        for item in training_data:
            # Create graph from code structure
            graph = self._code_to_graph(item['code'])
            graphs.append(graph)
            labels.append(self.vulnerability_classes.index(item['vulnerability']))
        
        # Training setup
        optimizer = torch.optim.Adam(self.gnn_model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        self.gnn_model.train()
        for epoch in range(50):  # 50 epochs for GNN
            total_loss = 0
            
            for i, (graph, label) in enumerate(zip(graphs, labels)):
                optimizer.zero_grad()
                
                # Extract node features and edge index from graph
                node_features, edge_index = self._graph_to_tensor(graph)
                node_features = node_features.to(self.device)
                edge_index = edge_index.to(self.device)
                label_tensor = torch.tensor([label], dtype=torch.long).to(self.device)
                
                logits = self.gnn_model(node_features, edge_index)
                loss = criterion(logits, label_tensor)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}, Loss: {total_loss / len(graphs):.4f}")
        
        training_results = {
            'model_type': 'GraphNeuralNetwork',
            'final_loss': total_loss / len(graphs),
            'epochs': 50,
            'training_samples': len(training_data)
        }
        
        logger.info("✅ GNN training complete")
        return training_results
    
    def train_transformer_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train Transformer model"""
        
        logger.info("Training Transformer model...")
        
        # Prepare training data
        texts = [item['code'] for item in training_data]
        labels = [self.vulnerability_classes.index(item['vulnerability']) for item in training_data]
        
        # Create vocabulary and tokenize
        vocab = self._create_vocabulary(texts)
        tokenized = [self._tokenize_code(text, vocab) for text in texts]
        
        # Convert to tensors
        max_len = max(len(tokens) for tokens in tokenized)
        padded = [tokens + [0] * (max_len - len(tokens)) for tokens in tokenized]
        
        input_ids = torch.tensor(padded, dtype=torch.long).to(self.device)
        labels = torch.tensor(labels, dtype=torch.long).to(self.device)
        
        # Training setup
        optimizer = torch.optim.Adam(self.transformer_model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        self.transformer_model.train()
        for epoch in range(20):  # 20 epochs
            optimizer.zero_grad()
            logits = self.transformer_model(input_ids)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            
            if epoch % 5 == 0:
                logger.info(f"Epoch {epoch}, Loss: {loss.item():.4f}")
        
        training_results = {
            'model_type': 'Transformer',
            'final_loss': loss.item(),
            'epochs': 20,
            'training_samples': len(training_data)
        }
        
        logger.info("✅ Transformer training complete")
        return training_results
    
    def train_ensemble_models(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train ensemble models"""
        
        logger.info("Training ensemble models...")
        
        # Prepare features
        X = []
        y = []
        
        for item in training_data:
            features = self._extract_features(item['code'])
            X.append(features)
            y.append(item['vulnerability'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Train each model
        results = {}
        
        for name, model in self.ensemble_models.items():
            logger.info(f"Training {name}...")
            model.fit(X, y)
            
            # Evaluate
            score = model.score(X, y)
            results[name] = {
                'accuracy': score,
                'model_type': name
            }
            
            logger.info(f"{name} accuracy: {score:.4f}")
        
        logger.info("✅ Ensemble models training complete")
        return results
    
    def predict_vulnerability(self, contract_code: str) -> List[ModelPrediction]:
        """Predict vulnerabilities using all models"""
        
        predictions = []
        
        # CodeBERT prediction
        if self.codebert_model:
            cb_pred = self._predict_codebert(contract_code)
            predictions.append(cb_pred)
        
        # GNN prediction
        if self.gnn_model:
            gnn_pred = self._predict_gnn(contract_code)
            predictions.append(gnn_pred)
        
        # Transformer prediction
        if self.transformer_model:
            tf_pred = self._predict_transformer(contract_code)
            predictions.append(tf_pred)
        
        # Ensemble predictions
        ensemble_preds = self._predict_ensemble(contract_code)
        predictions.extend(ensemble_preds)
        
        return predictions
    
    def _predict_codebert(self, contract_code: str) -> ModelPrediction:
        """Predict using CodeBERT model"""
        
        self.codebert_model.eval()
        
        # Tokenize
        encoding = self.codebert_tokenizer(
            contract_code,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.codebert_model(input_ids, attention_mask)
            probabilities = F.softmax(logits, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)
            
            vuln_type = self.vulnerability_classes[predicted_class.item()]
            conf = confidence.item()
        
        return ModelPrediction(
            vulnerability_type=vuln_type,
            confidence=conf,
            severity=self._get_severity(vuln_type),
            explanation=f"CodeBERT detected {vuln_type} with {conf:.2f} confidence",
            features_used=['semantic_embeddings', 'code_structure']
        )
    
    def _predict_gnn(self, contract_code: str) -> ModelPrediction:
        """Predict using GNN model"""
        
        self.gnn_model.eval()
        
        # Convert code to graph
        graph = self._code_to_graph(contract_code)
        node_features, edge_index = self._graph_to_tensor(graph)
        node_features = node_features.to(self.device)
        edge_index = edge_index.to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.gnn_model(node_features, edge_index)
            probabilities = F.softmax(logits, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)
            
            vuln_type = self.vulnerability_classes[predicted_class.item()]
            conf = confidence.item()
        
        return ModelPrediction(
            vulnerability_type=vuln_type,
            confidence=conf,
            severity=self._get_severity(vuln_type),
            explanation=f"GNN detected {vuln_type} with {conf:.2f} confidence",
            features_used=['control_flow_graph', 'data_dependencies']
        )
    
    def _predict_transformer(self, contract_code: str) -> ModelPrediction:
        """Predict using Transformer model"""
        
        self.transformer_model.eval()
        
        # Tokenize
        vocab = self._create_vocabulary([contract_code])
        tokens = self._tokenize_code(contract_code, vocab)
        
        # Pad to fixed length
        max_len = 512
        padded = tokens + [0] * (max_len - len(tokens))
        input_ids = torch.tensor([padded], dtype=torch.long).to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.transformer_model(input_ids)
            probabilities = F.softmax(logits, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)
            
            vuln_type = self.vulnerability_classes[predicted_class.item()]
            conf = confidence.item()
        
        return ModelPrediction(
            vulnerability_type=vuln_type,
            confidence=conf,
            severity=self._get_severity(vuln_type),
            explanation=f"Transformer detected {vuln_type} with {conf:.2f} confidence",
            features_used=['sequence_patterns', 'attention_weights']
        )
    
    def _predict_ensemble(self, contract_code: str) -> List[ModelPrediction]:
        """Predict using ensemble models"""
        
        predictions = []
        features = self._extract_features(contract_code)
        
        for name, model in self.ensemble_models.items():
            try:
                pred_class = model.predict([features])[0]
                confidence = model.predict_proba([features])[0].max()
                
                vuln_type = pred_class if isinstance(pred_class, str) else self.vulnerability_classes[pred_class]
                
                predictions.append(ModelPrediction(
                    vulnerability_type=vuln_type,
                    confidence=confidence,
                    severity=self._get_severity(vuln_type),
                    explanation=f"{name} detected {vuln_type} with {confidence:.2f} confidence",
                    features_used=['traditional_features', 'pattern_matching']
                ))
            except Exception as e:
                logger.warning(f"Ensemble prediction failed for {name}: {e}")
        
        return predictions
    
    def _code_to_graph(self, contract_code: str) -> nx.Graph:
        """Convert code to graph representation"""
        
        graph = nx.DiGraph()
        
        # Extract functions and their relationships
        functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)', contract_code)
        
        for i, func in enumerate(functions):
            graph.add_node(f"func_{i}", type='function', name=func)
        
        # Add edges based on function calls
        for i, func in enumerate(functions):
            func_pattern = rf'function\s+{func}\s*\([^)]*\)\s*(?:external|public|internal|private)?\s*(?:view|pure|payable)?\s*(?:returns\s*\([^)]*\))?\s*\{{([^}}]+)\}}'
            func_match = re.search(func_pattern, contract_code, re.DOTALL)
            
            if func_match:
                func_body = func_match.group(1)
                called_functions = re.findall(r'(\w+)\s*\(', func_body)
                
                for called_func in called_functions:
                    if called_func in functions:
                        target_idx = functions.index(called_func)
                        graph.add_edge(f"func_{i}", f"func_{target_idx}", type='call')
        
        return graph
    
    def _graph_to_tensor(self, graph: nx.Graph) -> Tuple[torch.Tensor, torch.Tensor]:
        """Convert graph to tensor representation"""
        
        # Node features (simple one-hot encoding)
        num_nodes = len(graph.nodes)
        node_features = torch.eye(num_nodes)
        
        # Edge index
        edge_list = list(graph.edges)
        if edge_list:
            edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
        else:
            edge_index = torch.empty((2, 0), dtype=torch.long)
        
        return node_features, edge_index
    
    def _create_vocabulary(self, texts: List[str]) -> Dict[str, int]:
        """Create vocabulary from texts"""
        
        vocab = {'<PAD>': 0, '<UNK>': 1}
        
        # Extract tokens
        all_tokens = set()
        for text in texts:
            tokens = re.findall(r'\w+', text.lower())
            all_tokens.update(tokens)
        
        # Build vocabulary
        for i, token in enumerate(sorted(all_tokens)):
            vocab[token] = i + 2
        
        return vocab
    
    def _tokenize_code(self, code: str, vocab: Dict[str, int]) -> List[int]:
        """Tokenize code using vocabulary"""
        
        tokens = re.findall(r'\w+', code.lower())
        return [vocab.get(token, vocab['<UNK>']) for token in tokens]
    
    def _extract_features(self, contract_code: str) -> List[float]:
        """Extract traditional features from contract code"""
        
        features = []
        
        # Basic metrics
        features.append(len(contract_code))  # Code length
        features.append(contract_code.count('\n'))  # Line count
        features.append(len(re.findall(r'function\s+\w+', contract_code)))  # Function count
        
        # Vulnerability indicators
        features.append(len(re.findall(r'\.call\s*\(', contract_code)))  # External calls
        features.append(len(re.findall(r'\.transfer\s*\(', contract_code)))  # Transfers
        features.append(len(re.findall(r'require\s*\(', contract_code)))  # Assertions
        features.append(len(re.findall(r'msg\.sender', contract_code)))  # User inputs
        features.append(len(re.findall(r'tx\.origin', contract_code)))  # Transaction origin
        features.append(len(re.findall(r'block\.timestamp', contract_code)))  # Block timestamp
        
        # Complexity metrics
        features.append(len(re.findall(r'\bif\b', contract_code)))  # Conditionals
        features.append(len(re.findall(r'\bfor\b', contract_code)))  # Loops
        features.append(len(re.findall(r'\bwhile\b', contract_code)))  # While loops
        
        return features
    
    def _get_severity(self, vulnerability_type: str) -> str:
        """Get severity for vulnerability type"""
        
        severity_map = {
            'reentrancy': 'High',
            'access_control': 'High',
            'oracle_manipulation': 'Critical',
            'flash_loan_attack': 'Critical',
            'integer_overflow': 'High',
            'governance_attack': 'Critical',
            'dos_attack': 'Medium',
            'front_running': 'Medium',
            'signature_replay': 'High',
            'unchecked_call': 'Medium'
        }
        
        return severity_map.get(vulnerability_type, 'Medium')
    
    def save_models(self, model_dir: str):
        """Save all trained models"""
        
        model_path = Path(model_dir)
        model_path.mkdir(exist_ok=True)
        
        # Save PyTorch models
        if self.codebert_model:
            torch.save(self.codebert_model.state_dict(), model_path / 'codebert_model.pth')
        
        if self.gnn_model:
            torch.save(self.gnn_model.state_dict(), model_path / 'gnn_model.pth')
        
        if self.transformer_model:
            torch.save(self.transformer_model.state_dict(), model_path / 'transformer_model.pth')
        
        # Save ensemble models
        for name, model in self.ensemble_models.items():
            joblib.dump(model, model_path / f'{name}_model.joblib')
        
        logger.info(f"✅ Models saved to {model_dir}")
    
    def load_models(self, model_dir: str):
        """Load all trained models"""
        
        model_path = Path(model_dir)
        
        # Load PyTorch models
        if (model_path / 'codebert_model.pth').exists():
            self.codebert_model = CodeBERTClassifier(num_classes=len(self.vulnerability_classes))
            self.codebert_model.load_state_dict(torch.load(model_path / 'codebert_model.pth', map_location=self.device))
            self.codebert_model.to(self.device)
        
        if (model_path / 'gnn_model.pth').exists():
            self.gnn_model = GraphNeuralNetwork(num_classes=len(self.vulnerability_classes))
            self.gnn_model.load_state_dict(torch.load(model_path / 'gnn_model.pth', map_location=self.device))
            self.gnn_model.to(self.device)
        
        if (model_path / 'transformer_model.pth').exists():
            self.transformer_model = TransformerEncoder(num_classes=len(self.vulnerability_classes))
            self.transformer_model.load_state_dict(torch.load(model_path / 'transformer_model.pth', map_location=self.device))
            self.transformer_model.to(self.device)
        
        # Load ensemble models
        for name in ['random_forest', 'gradient_boosting', 'neural_network']:
            model_file = model_path / f'{name}_model.joblib'
            if model_file.exists():
                self.ensemble_models[name] = joblib.load(model_file)
        
        logger.info(f"✅ Models loaded from {model_dir}")
