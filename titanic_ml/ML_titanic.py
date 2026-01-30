import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, f1_score, roc_auc_score

# ========================
# 데이터 가져오기
# ========================

data = pd.read_csv('./test/train.csv')

print(data.head())

# 분석에 사용할 'Survived', 'Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'SibSp', 'Parch', 'Name' 컬럼만 남김
df = data[['Survived', 'Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'SibSp', 'Parch', 'Name']].copy()


# ========================
# 결측치 처리
# ========================

# 결측치 확인
print("\n========== 결측치 확인 ==========\n", df.isnull().sum())

# Age 결측치 중앙값으로 채움
df['Age'] = df['Age'].fillna(df['Age'].median())

# Embarked 결측치 최빈값으로 채움
df['Embarked'] = df['Embarked'].fillna(df['Embarked'].mode()[0])

# 다시 결측치 확인
print("\n========== 결측치 처리 후 재확인 ==========\n", df.isnull().sum())


# ========================
# 데이터 준비 (전처리)
# ========================

# ======================== Title 컬럼 추가 ========================

# Name에서 콤마 뒤 ~ 점(.) 앞: "Mr", "Mrs" 같은 호칭만 추출
df["Title"] = df["Name"].str.extract(r",\s*([^\.]+)\.", expand=False)

# 흔치 않은 Title은 Rare로 묶어서 과적합/희소성 줄이기
title_map = {
    "Mlle": "Miss",
    "Ms": "Miss",
    "Mme": "Mrs",
}
df["Title"] = df["Title"].replace(title_map)

common_titles = ["Mr", "Mrs", "Miss", "Master"]
df["Title"] = df["Title"].where(df["Title"].isin(common_titles), "Rare")

# =================================================================

# FamilySize 컬럼 추가: 본인 포함 가족 수 컬럼 추가
df["FamilySize"] = df["SibSp"] + df["Parch"] + 1

# IsAlone컬럼 추가: 혼자인지(1) 아닌지(0)
df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

# Age 컬럼의 male, female을 숫자 0,1 로 변환 
df["Sex"] = df["Sex"].map({"male": 0, "female": 1})

# ======================== X, y 데이터 지정 ========================

X = df[['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'FamilySize', 'IsAlone', 'Title']]
y = df['Survived']

# Embarked 컬럼은 값들이 문자열이라 모델이 못 쓰기 때문에 더미변수로 변환
X = pd.get_dummies(X, columns=['Embarked', 'Title'], drop_first=True, dtype=int)

print("\n========== 데이터 준비 완료 ==========\n", X.head())


# ========================
# 훈련 / 테스트 데이터 분리
# ========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2, random_state=42, stratify=y)

# ========================
# 스케일링
# ========================

# 트리용 데이터 (스케일링 X)
X_train_tree = X_train.copy()
X_test_tree  = X_test.copy()

# 선형/SVC용 데이터 (스케일링 O)
scaler = StandardScaler()

# Title/Embarked 더미는 스케일링 필요가 없기 때문에 엄밀하게 스케일링 대상 컬럼을 제한
num_cols = ['Pclass','Sex','Age','Fare','FamilySize','IsAlone']

X_train_scaled = scaler.fit_transform(X_train[num_cols])
X_test_scaled  = scaler.transform(X_test[num_cols])


# ========================
# Logistic Regression + GridSearch
# ========================
lr = LogisticRegression(max_iter=2000)

param_lr = {
    "C": [0.1, 1, 10],
}

grid_lr = GridSearchCV(
                  estimator=lr,
                  param_grid=param_lr,
                  cv=5, # 5-fold 교차검증 (기본값)
                  scoring="roc_auc", # AUC가 가장 큰 파라미터 조합으로 성능 비교
                  n_jobs=-1, 
                  verbose=1
                  )
grid_lr.fit(X_train_scaled, y_train)

# 베스트 모델
best_lr = grid_lr.best_estimator_

print("\n========== LR 베스트 조합 ==========\n", grid_lr.best_params_)
print("\n========== LR 베스트 스코어(AUC, CV) ==========\n", grid_lr.best_score_)


# ========================
# RandomForest + GridSearch
# ========================
rf = RandomForestClassifier(random_state=42)

param_rf = {
    "n_estimators": [200, 500],
    "max_depth": [None, 4, 8],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2]
}
grid_rf = GridSearchCV(
                estimator=rf,
                param_grid=param_rf,
                cv=5,
                scoring="roc_auc",
                n_jobs=-1,
                verbose=1
            )

grid_rf.fit(X_train_tree, y_train)

# 베스트 모델
best_rf = grid_rf.best_estimator_

print("\n========== RF 베스트 조합 ==========\n", grid_rf.best_params_)
print("\n========== RF 베스트 스코어(AUC, CV) ==========\n", grid_rf.best_score_)


# ========================
# SVC + GridSearch
# ========================
svc = SVC(probability=True)

param_svc = {
    "C": [0.1, 1, 10],
    "kernel": ["rbf", "linear"],
    "gamma": ["scale", "auto"]
}

grid_svc = GridSearchCV(
                estimator=svc,
                param_grid=param_svc,
                cv=5,
                scoring="roc_auc",
                n_jobs=-1,
                verbose=1
            )

grid_svc.fit(X_train_scaled, y_train)

# 베스트 모델
best_svc = grid_svc.best_estimator_

print("\n========== SVC 베스트 조합 ==========\n", grid_svc.best_params_)
print("\n========== SVC 베스트 스코어(AUC, CV) ==========\n", grid_svc.best_score_)


# ========================
# 테스트셋 확인 !!
# ========================

def test_auc(model, Xte, yte):
    proba = model.predict_proba(Xte)[:, 1]
    return roc_auc_score(yte, proba)


print("\n========== 테스트셋 확인! ==========\n")

print("LR  Test AUC:", test_auc(best_lr,  X_test_scaled, y_test))
print("RF  Test AUC:", test_auc(best_rf,  X_test_tree,   y_test))
print("SVC Test AUC:", test_auc(best_svc, X_test_scaled, y_test))

# ========================
# 시각화 ( ROC곡선 )
# ========================
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt

# 모델 이름, 모델 객체, 테스트데이터, 그래프 색
# 그래프에 출력 편하게 하기 위해 리스트로 정리
models = [
    ("Logistic Regression", best_lr,  X_test_scaled, 'steelblue'),
    ("Random Forest",       best_rf,  X_test_tree, 'tomato'),
    ("SVC",                 best_svc, X_test_scaled, 'mediumseagreen')
]

# ============================ 전체 겹쳐서 보기 ============================

plt.figure(figsize=(7, 6))

for name, model, Xte, color in models:
    proba = model.predict_proba(Xte)[:, 1] # 생존(1) 확률만
    fpr, tpr, _ = roc_curve(y_test, proba) # x축, y축 좌표 지정
    roc_auc = auc(fpr, tpr)                # AUC 값 계산

    plt.plot(fpr, tpr, 
             color=color, #그래프 색 설정
             label=f"{name} (AUC={roc_auc:.3f})" # 모델이름 + AUC 점수를 라벨로 붙임
             )

plt.xlabel("FPR")
plt.ylabel("TPR")
plt.title("ROC Curves (Titanic)")
plt.legend()

# ============================ 각각 분리해서 보기 ============================

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# axes는 subplot 3개짜리 리스트 / models도 3개짜리 리스트 = zip으로 묶기
'''
(첫번째 축, 첫번째 모델) = 로지스틱
(두번째 축, 두번째 모델) = 랜덤포레스트
(세번째 축, 세번째 모델) = SVC
'''
for ax, (name, model, Xte, color) in zip(axes, models):
    proba = model.predict_proba(Xte)[:, 1] # 생존(1) 확률만
    fpr, tpr, _ = roc_curve(y_test, proba) # x축, y축 좌표 지정
    roc_auc = auc(fpr, tpr)                # AUC 값 계산

    ax.plot(fpr, tpr, 
            color=color,
            label=f"AUC={roc_auc:.3f}") # 모델이름 + AUC 점수를 라벨로 붙임
    
    ax.set_title(name)
    ax.set_xlabel("FPR")
    ax.legend(loc="lower right")

axes[0].set_ylabel("TPR")
fig.suptitle("ROC Curves (Separated)")
plt.tight_layout()

plt.show()

# ========================
# 시각화 ( Confusion Matrix )
# ========================

fig, axes = plt.subplots(1, 3, figsize=(18, 7))

for ax, (name, model, Xte, color) in zip(axes, models):
    proba = model.predict_proba(Xte)[:, 1]
    y_pred = (proba >= 0.5).astype(int)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[0, 1])
    disp.plot(ax=ax, values_format="d", cmap="Blues", colorbar=False)

    # 숫자(셀 내부) 글씨 키우기
    for t in disp.text_.ravel():
        t.set_fontsize(16)
        t.set_fontweight("bold")

    # 타이틀에 핵심 지표 같이 표시
    acc = accuracy_score(y_test, y_pred)
    f1  = f1_score(y_test, y_pred)

    ax.set_title(f"{name}\nACC={acc:.3f} | F1={f1:.3f}", fontsize=14, fontweight="bold")

plt.tight_layout()
plt.show()