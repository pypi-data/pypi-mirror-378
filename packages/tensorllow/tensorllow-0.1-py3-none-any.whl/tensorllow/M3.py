import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

df = pd.read_csv('breast-cancer.csv').dropna()
df['Status'] = df['Status'].map({'Alive':0,'Dead':1})

y = df['Status'].values
X = pd.get_dummies(df.drop(columns=['Status']), drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler().fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

model = LogisticRegression(solver='lbfgs', max_iter=2000)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("ROC-AUC Score:", roc_auc_score(y_test, model.predict_proba(X_test)[:,1]))

pd.Series(model.coef_[0], index=X.columns).nlargest(10).plot(kind='barh', title='Top 10 Influential Features')
plt.xlabel('Coefficient Value')
plt.tight_layout()
plt.show()
