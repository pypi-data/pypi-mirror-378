import os
import shutil

__all__ = [
    'svm', 'random_forest', 'knn', 'decision_tree', 'kmeans',
    'logistic_regression',
    'customers_data', 'students_data'
]

def customers_data():
    target_file = "customers.csv"
    if not os.path.exists(target_file):
        package_data_path = os.path.join(os.path.dirname(__file__), 'data', 'customers.csv')
        shutil.copy(package_data_path, target_file)

def students_data():
    target_file = "student_performance.csv"
    if not os.path.exists(target_file):
        package_data_path = os.path.join(os.path.dirname(__file__), 'data', 'student_performance.csv')
        shutil.copy(package_data_path, target_file)


def write_model_file(filename, content):
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


def delete_entry_py():
    entry_path = "entry.py"
    if os.path.exists(entry_path):
        os.remove(entry_path)


def svm():
    # STEP 1: Ensure dataset
    customers_data()

    # STEP 2: Write clean model code (no data setup inside)
    code = '''import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

data = pd.read_csv("customers.csv")

y = (data["Spending_Score"] > 50).astype(int)
X = data[["Age", "Spending_Score"]]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = SVC(kernel="linear")
model.fit(X_train, y_train)

plt.figure(figsize=(8,5))
plt.scatter(X["Age"], X["Spending_Score"], c=y, cmap="coolwarm", edgecolor="k")
plt.xlabel("Age")
plt.ylabel("Spending Score")
plt.title("SVM: High Spenders (Score > 50)")
plt.show()'''

    write_model_file("svm_model.py", code)

    # STEP 3: Delete launcher
    delete_entry_py()


def random_forest():
    customers_data()

    code = '''import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

data = pd.read_csv("customers.csv")

y = (data["Spending_Score"] > 50).astype(int)
X = data[["Age", "Annual_Income_(k$)"]]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))'''

    write_model_file("random_forest_model.py", code)
    delete_entry_py()


def knn():
    customers_data()

    code = '''import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

data = pd.read_csv("customers.csv")

y = (data["Spending_Score"] > 50).astype(int)
X = data[["Age", "Spending_Score"]]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = KNeighborsClassifier(n_neighbors=3)
model.fit(X_train, y_train)

plt.figure(figsize=(8,5))
plt.scatter(X["Age"], X["Spending_Score"], c=y, cmap="plasma", edgecolor="k")
plt.xlabel("Age")
plt.ylabel("Spending Score")
plt.title("KNN: High Spenders (Score > 50)")
plt.show()'''

    write_model_file("knn_model.py", code)
    delete_entry_py()


def kmeans():
    customers_data()

    code = '''import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

data = pd.read_csv("customers.csv")

X = data[["Annual_Income_(k$)", "Spending_Score"]]
model = KMeans(n_clusters=5, random_state=42)
data["Cluster"] = model.fit_predict(X)

plt.figure(figsize=(8,5))
scatter = plt.scatter(X["Annual_Income_(k$)"], X["Spending_Score"], c=data["Cluster"], cmap="viridis", s=50, edgecolor="k")
plt.xlabel("Annual Income (k$)")
plt.ylabel("Spending Score")
plt.title("Customer Segments (KMeans Clusters)")
plt.colorbar(scatter, label="Cluster ID")
plt.grid(True, alpha=0.3)
plt.show()

print("\\nCluster Centers:")
print(model.cluster_centers_)'''

    write_model_file("kmeans_model.py", code)
    delete_entry_py()


def logistic_regression():
    students_data()

    code = '''import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

data = pd.read_csv("student_performance.csv")

le = LabelEncoder()
data["Extra_Classes"] = le.fit_transform(data["Extra_Classes"])
data["Pass_Fail"] = (data["Pass_Fail"] == "Pass").astype(int)

X = data[["Hours_Studied", "Attendance (%)", "Extra_Classes"]]
y = data["Pass_Fail"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

print("Coefficients:")
print("Hours_Studied:", model.coef_[0][0])
print("Attendance:", model.coef_[0][1])
print("Extra_Classes (Yes=1):", model.coef_[0][2])'''

    write_model_file("logistic_regression_model.py", code)
    delete_entry_py()


def decision_tree():
    students_data()

    code = '''import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

data = pd.read_csv("student_performance.csv")

data["Extra_Classes"] = (data["Extra_Classes"] == "Yes").astype(int)
data["Pass_Fail"] = (data["Pass_Fail"] == "Pass").astype(int)

X = data[["Hours_Studied", "Attendance (%)", "Extra_Classes"]]
y = data["Pass_Fail"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)

plt.figure(figsize=(12,8))
plot_tree(model, feature_names=X.columns, class_names=["Fail", "Pass"], filled=True)
plt.title("Student Pass/Fail Decision Tree")
plt.show()'''

    write_model_file("decision_tree_model.py", code)
    delete_entry_py()