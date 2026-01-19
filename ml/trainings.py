import os, json, joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score

# internal_medicine = 내과
# ob_gyns = 산부인과
# pediatrics = 소아청소년과
# emergency_medicine = 응급의학과
# 출처 https://www.aihub.or.kr/aihubdata/data/view.do?pageIndex=1&currMenu=115&topMenu=100&srchOptnCnd=OPTNCND001&searchKeyword=&srchDetailCnd=DETAILCND001&srchOrder=ORDER001&srchPagePer=20&srchDataRealmCode=REALM002&srchDataRealmCode=REALM006&aihubDataSe=data&dataSetSn=71875

# 데이터 구성
# (1) qa_id: 질의응답별 고유 id
# (2) domain: 의료분야
# (3) q_type: 질문 유형
# (4) question: 질문
# (5) answer: 답변

internal_medicine = r"C:\Users\김경민\Desktop\medical_data\TL_내과"
ob_gyns = r"C:\Users\김경민\Desktop\medical_data\TL_산부인과"
pediatrics = r"C:\Users\김경민\Desktop\medical_data\TL_소아청소년과"
emergency_medicine = r"C:\Users\김경민\Desktop\medical_data\TL_응급의학과"

medicine_folder_list = [internal_medicine, ob_gyns, pediatrics, emergency_medicine]

rows = []

for medicine_folder in medicine_folder_list:
    for filename in os.listdir(medicine_folder):
        if not filename.endswith(".json"):
            continue
        
        # 파일 주소
        file_path = os.path.join(medicine_folder, filename)

        with open(file_path, "r", encoding="utf-8-sig") as file:
            data = json.load(file)

            rows.append({
            "qa_id": data["qa_id"],
            "domain": data["domain"],
            "q_type": data["q_type"],
            "question": data["question"],
            "answer": data["answer"],
        })

df = pd.DataFrame(rows)

X, y = df["question"], df["domain"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.3,
    random_state=42,
    stratify=y 
)

pipeline = Pipeline([
    ('tfidfverctor', TfidfVectorizer(stop_words='english', min_df=3, max_df=600)),
    ('logisticrefression', LogisticRegression())
])

params = {
    'tfidfverctor__ngram_range': [(1, 2)],
    'logisticrefression__C': [5]
}

grid_search_cv = GridSearchCV(pipeline, param_grid=params, scoring='accuracy', cv=3, verbose=1)
grid_search_cv.fit(X_train, y_train)

print(grid_search_cv.best_params_, grid_search_cv.best_score_)

pred = grid_search_cv.predict(X_test)

print(f"정확도 : {accuracy_score(y_test, pred)}")

os.makedirs("mldata", exist_ok=True)
joblib.dump(grid_search_cv.best_estimator_, "mldata/domain_pipeline.joblib")
