import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from interpret.glassbox import ExplainableBoostingClassifier
import joblib

def train_ebm_model():
    print("Loading feature vectors...")
    df = pd.read_csv('feature_vectors.csv')

    # Define features and target
    X = df.drop(columns=['Gstin', 'fraud_label'])
    y = df['fraud_label']

    print(f"Dataset class distribution:\n{y.value_counts(normalize=True) * 100}")

    # 80/20 Stratified Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    print("Training Explainable Boosting Machine (EBM)...")
    ebm = ExplainableBoostingClassifier(random_state=42, n_jobs=-1, interactions=5)
    ebm.fit(X_train, y_train)

    # Evaluation
    y_pred = ebm.predict(X_test)
    y_prob = ebm.predict_proba(X_test)[:, 1]
    
    print("\n--- Model Evaluation ---")
    print(f"AUC-ROC Score: {roc_auc_score(y_test, y_prob):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save the model for FastAPI Orchestration
    joblib.dump(ebm, 'daksha_ebm.pkl')
    print("Model saved to disk as 'daksha_ebm.pkl'")

if __name__ == "__main__":
    train_ebm_model()