"""
Pipeline 2: Domain Classification
Classifies knowledge items (rules/facts) into 5 domains using ML algorithms
Uses TF-IDF vectorization with Naive Bayes and Decision Tree classifiers
"""

import json
import os
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
import pandas as pd

# Pipeline2 directory paths
PIPELINE2_DIR = Path(__file__).parent
MODELS_DIR = PIPELINE2_DIR / "models"
TRAINING_DATA_DIR = PIPELINE2_DIR / "training_data"
LABELED_DATA_FILE = TRAINING_DATA_DIR / "labeled_data.json"

# Model file paths
VECTORIZER_FILE = MODELS_DIR / "tfidf_vectorizer.pkl"
NB_MODEL_FILE = MODELS_DIR / "naive_bayes_model.pkl"
DT_MODEL_FILE = MODELS_DIR / "decision_tree_model.pkl"
EVALUATION_FILE = MODELS_DIR / "evaluation_results.json"

# Domains
DOMAINS = ["social", "economy", "infrastructure", "health", "culture_art"]

class DomainClassifier:
    """Main classifier orchestrating training and prediction"""

    def __init__(self):
        self.vectorizer = None
        self.nb_model = None
        self.dt_model = None
        self.selected_algorithm = None
        self.evaluation_results = {}
        self._load_models()

    def _load_models(self):
        """Load pre-trained models if they exist"""
        try:
            if VECTORIZER_FILE.exists():
                self.vectorizer = joblib.load(VECTORIZER_FILE)
            if NB_MODEL_FILE.exists():
                self.nb_model = joblib.load(NB_MODEL_FILE)
            if DT_MODEL_FILE.exists():
                self.dt_model = joblib.load(DT_MODEL_FILE)
            if EVALUATION_FILE.exists():
                with open(EVALUATION_FILE, 'r') as f:
                    self.evaluation_results = json.load(f)
                    self.selected_algorithm = self.evaluation_results.get("selected_algorithm")
        except Exception as e:
            print(f"⚠️  Could not load models: {str(e)}")

    def train(self) -> Dict:
        """
        Train both classifiers and evaluate with stratified 5-fold CV
        Returns evaluation metrics and selected algorithm
        """
        print("\n" + "="*60)
        print("PIPELINE 2: DOMAIN CLASSIFICATION TRAINING")
        print("="*60)

        # Load training data
        try:
            with open(LABELED_DATA_FILE, 'r') as f:
                labeled_data = json.load(f)
        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"Training data not found: {LABELED_DATA_FILE}",
                "success": False
            }

        if len(labeled_data) == 0:
            return {
                "status": "error",
                "message": "Training data is empty",
                "success": False
            }

        # Extract texts and labels
        texts = [item["text"] for item in labeled_data]
        labels = [item["domain"] for item in labeled_data]

        print(f"\n📊 Training Data Statistics:")
        print(f"  Total samples: {len(texts)}")
        for domain in DOMAINS:
            count = labels.count(domain)
            print(f"  {domain}: {count} samples")

        # Create TF-IDF vectorizer
        print(f"\n🔧 Creating TF-IDF Vectorizer (ngram_range=(1,2), sublinear_tf=True)...")
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            max_features=1000,
            min_df=1,
            max_df=0.9,
            stop_words='english'
        )

        # Vectorize texts
        X = self.vectorizer.fit_transform(texts)
        y = np.array(labels)

        print(f"  ✅ Vectorizer created: {X.shape[1]} features")

        # Setup stratified k-fold cross-validation
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Train Naive Bayes
        print(f"\n🤖 Training Naive Bayes Classifier...")
        nb_clf = MultinomialNB()
        nb_scores = cross_validate(
            nb_clf, X, y, cv=skf,
            scoring=['f1_macro', 'precision_macro', 'recall_macro'],
            return_train_score=False
        )

        nb_f1_mean = nb_scores['test_f1_macro'].mean()
        nb_f1_std = nb_scores['test_f1_macro'].std()
        print(f"  ✅ Naive Bayes Macro F1: {nb_f1_mean:.4f} (±{nb_f1_std:.4f})")
        print(f"     Precision: {nb_scores['test_precision_macro'].mean():.4f}")
        print(f"     Recall: {nb_scores['test_recall_macro'].mean():.4f}")

        # Train Decision Tree
        print(f"\n🌳 Training Decision Tree Classifier (criterion=gini, max_depth=10)...")
        dt_clf = DecisionTreeClassifier(
            criterion='gini',
            max_depth=10,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42
        )
        dt_scores = cross_validate(
            dt_clf, X, y, cv=skf,
            scoring=['f1_macro', 'precision_macro', 'recall_macro'],
            return_train_score=False
        )

        dt_f1_mean = dt_scores['test_f1_macro'].mean()
        dt_f1_std = dt_scores['test_f1_macro'].std()
        print(f"  ✅ Decision Tree Macro F1: {dt_f1_mean:.4f} (±{dt_f1_std:.4f})")
        print(f"     Precision: {dt_scores['test_precision_macro'].mean():.4f}")
        print(f"     Recall: {dt_scores['test_recall_macro'].mean():.4f}")

        # Select best algorithm
        if nb_f1_mean >= dt_f1_mean:
            self.selected_algorithm = "naive_bayes"
            best_f1 = nb_f1_mean
            print(f"\n🏆 Selected: NAIVE BAYES (F1: {nb_f1_mean:.4f} vs {dt_f1_mean:.4f})")
        else:
            self.selected_algorithm = "decision_tree"
            best_f1 = dt_f1_mean
            print(f"\n🏆 Selected: DECISION TREE (F1: {dt_f1_mean:.4f} vs {nb_f1_mean:.4f})")

        # Train final models on full data
        print(f"\n📝 Training final models on full dataset...")
        self.nb_model = MultinomialNB()
        self.nb_model.fit(X, y)

        self.dt_model = DecisionTreeClassifier(
            criterion='gini',
            max_depth=10,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42
        )
        self.dt_model.fit(X, y)

        # Save models
        print(f"\n💾 Saving models...")
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, VECTORIZER_FILE)
        joblib.dump(self.nb_model, NB_MODEL_FILE)
        joblib.dump(self.dt_model, DT_MODEL_FILE)
        print(f"  ✅ Models saved to {MODELS_DIR}")

        # Save evaluation results
        self.evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "training_samples": len(texts),
            "naive_bayes": {
                "macro_f1": float(nb_f1_mean),
                "macro_f1_std": float(nb_f1_std),
                "macro_precision": float(nb_scores['test_precision_macro'].mean()),
                "macro_recall": float(nb_scores['test_recall_macro'].mean())
            },
            "decision_tree": {
                "macro_f1": float(dt_f1_mean),
                "macro_f1_std": float(dt_f1_std),
                "macro_precision": float(dt_scores['test_precision_macro'].mean()),
                "macro_recall": float(dt_scores['test_recall_macro'].mean())
            },
            "selected_algorithm": self.selected_algorithm,
            "best_macro_f1": float(best_f1)
        }

        with open(EVALUATION_FILE, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2)

        print(f"  ✅ Evaluation results saved to {EVALUATION_FILE}")
        print("\n" + "="*60 + "\n")

        return {
            "status": "success",
            "success": True,
            "message": f"Training completed. Selected algorithm: {self.selected_algorithm}",
            "naive_bayes_f1": float(nb_f1_mean),
            "decision_tree_f1": float(dt_f1_mean),
            "selected_algorithm": self.selected_algorithm,
            "evaluation_results": self.evaluation_results
        }

    def predict(self, texts: List[str]) -> List[Dict]:
        """
        Predict domain for given texts using selected algorithm
        Args:
            texts: List of text strings to classify
        Returns:
            List of dicts with text, predicted_domain, confidence, algorithm_used
        """
        if not self.vectorizer or not self.selected_algorithm:
            raise ValueError("Models not trained. Call train() first.")

        if self.selected_algorithm == "naive_bayes" and not self.nb_model:
            raise ValueError("Naive Bayes model not available")
        if self.selected_algorithm == "decision_tree" and not self.dt_model:
            raise ValueError("Decision Tree model not available")

        # Vectorize texts
        X = self.vectorizer.transform(texts)

        # Get predictions
        if self.selected_algorithm == "naive_bayes":
            predictions = self.nb_model.predict(X)
            # Get confidence scores (max probability)
            proba = self.nb_model.predict_proba(X)
            confidences = np.max(proba, axis=1)
        else:  # decision_tree
            predictions = self.dt_model.predict(X)
            proba = self.dt_model.predict_proba(X)
            confidences = np.max(proba, axis=1)

        # Format results
        results = []
        for text, prediction, confidence in zip(texts, predictions, confidences):
            results.append({
                "text": text,
                "predicted_domain": prediction,
                "confidence": float(confidence),
                "algorithm_used": self.selected_algorithm
            })

        return results

    def predict_single(self, text: str) -> Dict:
        """Predict domain for single text"""
        results = self.predict([text])
        return results[0] if results else None

    def get_domains(self) -> List[str]:
        """Get list of available domains"""
        return DOMAINS

    def get_evaluation_results(self) -> Dict:
        """Get stored evaluation results"""
        return self.evaluation_results


# Initialize global classifier
classifier = DomainClassifier()
