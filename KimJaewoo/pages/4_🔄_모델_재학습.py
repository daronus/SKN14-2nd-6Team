import streamlit as st
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, classification_report
from PIL import Image
import base64
from io import BytesIO
import sys  # sys 모듈 추가

# --- 프로젝트 루트 경로 설정 (다른 페이지들과 동일한 방식) ---
current_dir_retrain = os.path.dirname(os.path.abspath(__file__))
project_root_retrain = os.path.dirname(current_dir_retrain)  # pages 폴더의 부모
if project_root_retrain not in sys.path:
    sys.path.append(project_root_retrain)
# -------------------------------------------------------

# --- 이미지 경로 (app.py와 동일하게) ---
IMG_DIR_RETRAIN = os.path.join(project_root_retrain, "img")
LOGO_PATH_RETRAIN = os.path.join(IMG_DIR_RETRAIN, "logo.png")

# --- CSS (app.py의 헤더 스타일과 유사하게) ---
st.markdown(
    """
    <style>
    .reportview-container { background: #fff; }
    .main .block-container { padding-right: 120px; padding-left: 120px; padding-bottom: 50px; } /* 하단 패딩 추가 */
    .st-emotion-cache-ckbrp0 { padding-left: 120px !important; padding-right: 120px !important; }
    .st-emotion-cache-t1wise { padding-left: 120px !important; padding-right: 120px !important; }
    @media (min-width: calc(736px + 8rem)) {
        .main .block-container, .st-emotion-cache-ckbrp0, .st-emotion-cache-t1wise {
            padding-left: 150px !important; padding-right: 150px !important;
        }
    }
    .stApp > header { display: none; }
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 20px 100px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 100%; position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }
    .logo-img { height: 30px; width: auto; }
    .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; }
    .nav-menu li { margin-left: 30px; }
    .nav-menu a { text-decoration: none; color: #333; font-weight: bold; font-size: 16px; padding: 8px 12px; border-radius: 4px; transition: all 0.3s ease; }
    .nav-menu a:hover { color: #007bff; background-color: #f0f0f0; }
    h2 { color: #004080; margin-top: 20px; margin-bottom: 20px; border-bottom: 2px solid #0055A4; padding-bottom: 10px; text-align: center;} /* 제목 중앙 정렬 */
    /* 파일 업로더 스타일 */
    .stFileUploader label { font-size: 1.1em; font-weight: bold; color: #333; margin-bottom: 10px;}
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #007bff !important; color: white !important;
        border: none; padding: 10px 24px !important; border-radius: 5px !important;
        font-weight: bold; margin-top: 20px !important;
    }
    .stButton>button:hover { background-color: #0056b3 !important; }
    </style>
    """,
    unsafe_allow_html=True
)


# --- 이미지 로드 및 Base64 인코딩 함수 (app.py와 동일) ---
def image_to_base64(img_path):  # 함수 이름 일관성 있게 변경
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            buffered = BytesIO()
            img_format = "PNG" if img_path.lower().endswith(".png") else "JPEG"
            if img.format: img_format = img.format
            img.save(buffered, format=img_format)
            encoded_string = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/{img_format.lower()};base64,{encoded_string}"
        except Exception as e:
            print(f"Error encoding image {img_path}: {e}")
            return ""
    return ""


logo_data_uri_retrain = image_to_base64(LOGO_PATH_RETRAIN)

# --- 헤더 렌더링 (app.py와 동일) ---
if logo_data_uri_retrain:
    st.markdown(
        f"""
        <div class="header-container">
            <div class="logo">
                 <a href="/" target="_self">
                    <img src="{logo_data_uri_retrain}" class="logo-img" alt="PLAY DATA Logo">
                 </a>
            </div>
            <nav class="nav-menu">
                <ul>
                    <li><a href="#">백엔드 캠프</a></li>
                    <li><a href="#">취업지원</a></li>
                    <li><a href="#">스토리</a></li>
                    <li><a href="#">캠퍼스투어</a></li>
                    <li><a href="#">파트너</a></li>
                    <li><a href="#">프리코스</a></li>
                    <li><a href="/input_form" target="_self">학생관리</a></li>
                    <li><a href="#">로그인</a></li>
                </ul>
            </nav>
        </div>
        """,
        unsafe_allow_html=True
    )
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

# --- 기존 재학습 페이지 코드 (ORIGINAL_COLUMNS 등은 app.py에서 가져오거나 여기서 다시 정의) ---
ORIGINAL_COLUMNS_RT = [
    'Marital status', 'Application mode', 'Application order', 'Course',
    'Daytime/evening attendance', 'Previous qualification', 'Nacionality',
    "Mother's qualification", "Father's qualification", "Mother's occupation",
    "Father's occupation", 'Displaced', 'Educational special needs', 'Debtor',
    'Tuition fees up to date', 'Gender', 'Scholarship holder', 'Age', 'International',
    'Curricular units 1st sem (credited)', 'Curricular units 1st sem (enrolled)',
    'Curricular units 1st sem (evaluations)', 'Curricular units 1st sem (approved)',
    'Curricular units 1st sem (grade)', 'Curricular units 1st sem (without evaluations)',
    'Curricular units 2nd sem (credited)', 'Curricular units 2nd sem (enrolled)',
    'Curricular units 2nd sem (evaluations)', 'Curricular units 2nd sem (approved)',
    'Curricular units 2nd sem (grade)', 'Curricular units 2nd sem (without evaluations)',
    'Unemployment rate', 'Inflation rate', 'GDP', 'Target'
]
DROPPED_COLUMNS_FOR_RETRAIN_RT = [
    'Application mode', 'Application order', 'Nacionality',
    "Mother's qualification", "Father's qualification", 'International',
    'Curricular units 1st sem (credited)', 'Curricular units 1st sem (enrolled)',
    'Curricular units 1st sem (evaluations)', 'Curricular units 1st sem (without evaluations)',
    'Curricular units 2nd sem (credited)', 'Curricular units 2nd sem (enrolled)',
    'Curricular units 2nd sem (evaluations)', 'Curricular units 2nd sem (without evaluations)',
    'Unemployment rate', 'Inflation rate', 'GDP'
]
MODEL_FEATURES_RT = [col for col in ORIGINAL_COLUMNS_RT if col not in DROPPED_COLUMNS_FOR_RETRAIN_RT + ['Target']]

st.markdown("<h2>🔄 모델 재학습</h2>", unsafe_allow_html=True)
st.markdown("새로운 학생 데이터를 업로드하여 예측 모델을 재학습할 수 있습니다. 원본 `dataset.csv`와 동일한 전체 컬럼 구조를 가진 파일을 사용해주세요.")

if 'model' not in st.session_state or st.session_state.model is None:
    st.error("모델 로딩에 실패했습니다. 메인 페이지를 확인하거나 앱을 재시작해주세요.")
    st.stop()

uploaded_file_rt = st.file_uploader("재학습용 CSV 파일 업로드", type="csv", key="retrain_uploader_page4")

if uploaded_file_rt is not None:
    try:
        new_data_df_original_rt = pd.read_csv(uploaded_file_rt)
        st.write("### 업로드된 데이터 미리보기 (상위 5행)")
        st.dataframe(new_data_df_original_rt.head(), use_container_width=True)

        missing_cols_rt = [col for col in ORIGINAL_COLUMNS_RT if col not in new_data_df_original_rt.columns]
        if missing_cols_rt:
            st.error(f"오류: 업로드된 파일에 다음 필수 컬럼이 없습니다: {', '.join(missing_cols_rt)}")
            st.stop()

        new_data_df_rt = new_data_df_original_rt[ORIGINAL_COLUMNS_RT].copy()
        target_map_rt = {'Dropout': 0, 'Graduate': 1, 'Enrolled': 2}

        if 'Target' not in new_data_df_rt.columns:
            st.error("오류: 업로드된 파일에 'Target' 컬럼이 존재하지 않습니다.")
            st.stop()

        new_data_df_rt['Target'] = new_data_df_rt['Target'].map(target_map_rt)

        if new_data_df_rt['Target'].isnull().any():
            st.warning("경고: 'Target' 컬럼에 매핑되지 않는 값(예: 'Dropout', 'Graduate', 'Enrolled' 이외)이 포함된 행은 재학습에서 제외됩니다.")
            new_data_df_rt.dropna(subset=['Target'], inplace=True)
            new_data_df_rt['Target'] = new_data_df_rt['Target'].astype(int)

        new_data_df_filtered_rt = new_data_df_rt[new_data_df_rt['Target'] != 2].copy()  # 'Enrolled' 상태 제외

        if new_data_df_filtered_rt.empty:
            st.warning("필터링 후 재학습할 데이터가 없습니다 ('Enrolled' 상태는 재학습에 사용되지 않습니다).")
            st.stop()

        processed_df_for_retrain_rt = new_data_df_filtered_rt.drop(columns=DROPPED_COLUMNS_FOR_RETRAIN_RT,
                                                                   errors='ignore')

        st.write("### 전처리 후 재학습에 사용될 데이터 미리보기 (상위 5행)")
        st.dataframe(processed_df_for_retrain_rt.head(), use_container_width=True)
        st.info(f"총 {len(processed_df_for_retrain_rt)}개의 데이터로 모델 재학습을 진행합니다 (Dropout/Graduate 학생만 해당).")

        if st.button("모델 재학습 시작하기", type="primary", use_container_width=True, key="start_retrain_button_page4"):
            with st.spinner("모델을 재학습 중입니다. 데이터 크기에 따라 시간이 소요될 수 있습니다..."):
                X_new_rt = processed_df_for_retrain_rt.drop('Target', axis=1)
                # 모델이 학습된 컬럼 순서와 동일하게 맞춤
                X_new_rt = X_new_rt[MODEL_FEATURES_RT]
                y_new_rt = processed_df_for_retrain_rt['Target']

                if len(X_new_rt) < 10:  # 최소 데이터 수 검증
                    st.error("오류: 재학습을 위한 데이터가 너무 적습니다 (최소 10개 필요).")
                    st.stop()

                current_pipeline_rt = st.session_state.model
                current_pipeline_rt.fit(X_new_rt, y_new_rt)  # 파이프라인 전체 재학습

                # 재학습된 모델 저장 (project_root_retrain 사용)
                model_path_rt = os.path.join(project_root_retrain, 'models', 'best_model_pipeline.pkl')
                joblib.dump(current_pipeline_rt, model_path_rt)

                # 현재 세션의 모델도 업데이트
                st.session_state.model = current_pipeline_rt

                st.success(f"🎉 모델 재학습이 성공적으로 완료되었습니다! 새 모델이 '{model_path_rt}' 경로에 저장되었으며, 현재 세션에 적용되었습니다.")

                # 재학습된 모델 성능 평가 (선택 사항)
                if len(X_new_rt) >= 20:  # 평가를 위한 충분한 데이터가 있을 경우
                    # 참고: 재학습은 전체 X_new_rt로 진행했으므로, 여기서의 평가는 업로드된 데이터에 대한 일반화 성능을 나타냄
                    preds_new_rt = current_pipeline_rt.predict(X_new_rt)  # 전체 새 데이터로 예측
                    new_f1_rt = f1_score(y_new_rt, preds_new_rt, average='binary')
                    new_acc_rt = accuracy_score(y_new_rt, preds_new_rt)

                    st.subheader("재학습된 모델 성능 (업로드된 전체 새 데이터 기준):")
                    col_metric1, col_metric2 = st.columns(2)
                    col_metric1.metric("F1 Score (binary)", f"{new_f1_rt:.4f}")
                    col_metric2.metric("정확도 (Accuracy)", f"{new_acc_rt:.4f}")
                    st.text("분류 보고서:")
                    st.text(classification_report(y_new_rt, preds_new_rt, target_names=['Dropout', 'Graduate']))
                else:
                    st.info("데이터가 충분하지 않아 업로드된 데이터에 대한 상세 성능 평가는 생략합니다.")
    except Exception as e:
        st.error(f"파일 처리 또는 모델 재학습 중 오류가 발생했습니다: {e}")
        st.exception(e)  # 개발 시 상세 오류 확인용
else:
    st.info("모델을 재학습하려면 위에서 CSV 파일을 업로드해주세요.")