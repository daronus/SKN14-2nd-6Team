import streamlit as st
from PIL import Image
import os
import joblib  # 모델 로드를 위해 추가 (st.session_state.model 사용)
import base64
import pandas as pd
from io import BytesIO
import sys

# 프로젝트 루트 경로를 sys.path에 추가
current_dir_input = os.path.dirname(os.path.abspath(__file__))
project_root_input = os.path.dirname(current_dir_input)
if project_root_input not in sys.path:
    sys.path.append(project_root_input)

from utils import mappings  # utils 폴더의 mappings.py 임포트

# --- 이미지 경로 ---
IMG_DIR = os.path.join(project_root_input, "img")
LOGO_PATH = os.path.join(IMG_DIR, "logo.png")
USER_IMG_PATH = os.path.join(IMG_DIR, "user_img.png")
# 모델은 app.py에서 로드하여 st.session_state.model 에 저장된 것을 사용

# 페이지 설정
st.set_page_config(
    page_title="학생 정보 입력 - PLAY DATA",
    layout="wide",
    initial_sidebar_state="collapsed"  # 사이드바 기본적으로 닫힘
)

# --- CSS (기존 input_form.py의 스타일 유지, 헤더 부분은 app.py와 동일하게) ---
st.markdown(
    """
    <style>
    .reportview-container { background: #fff; max-width: 100%; overflow-x: hidden; }
    .main .block-container { padding-right: 180px; padding-left: 180px; padding-bottom: 0; max-width: 100%;}
    .st-emotion-cache-ckbrp0 { padding-left: 180px !important; padding-right: 180px !important; }
    .st-emotion-cache-t1wise { padding-left: 180px !important; padding-right: 180px !important; }
    @media (min-width: calc(736px + 8rem)) {
        .main .block-container, .st-emotion-cache-ckbrp0, .st-emotion-cache-t1wise {
            padding-left: 200px !important; padding-right: 200px !important;
        }
    }
    .stApp > header { display: none; }
    /* 헤더 스타일 (app.py와 동일) */
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 25px 120px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 100%; position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }
    .logo-img { height: 30px; width: auto; }
    .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; }
    .nav-menu li { margin-left: 35px; }
    .nav-menu a { text-decoration: none; color: #333; font-weight: bold; font-size: 14px; }
    .nav-menu a[href="/input_form"] { cursor: pointer; }

    /* Form 요소들 간격 및 버튼 스타일 (input_form.py 고유 스타일) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        height: 42px !important; border-radius: 5px !important; border: 1px solid #ced4da !important;
        padding: 0.375rem 0.75rem !important; font-size: 1rem;
    }
    .stButton>button {
        border: none; padding: 10px 20px !important; border-radius: 5px !important;
        font-weight: bold; transition: background-color 0.3s ease;
        width: auto !important; margin-top: 10px;
    }
    .stButton>button[data-testid*="stButton-secondary"] {
        background-color: #6c757d !important; color: white !important;
    }
    .stButton>button[data-testid*="stButton-secondary"]:hover {
        background-color: #5a6268 !important;
    }
    .stButton>button[kind="primary"] {
        width: calc(100% - 20px) !important; margin: 30px 10px 0 10px !important;
        background-color: #007bff !important; color: white !important;
        padding: 12px 24px !important; font-size: 1.1em !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #0056b3 !important;
    }

    h4 { text-align: left; font-weight: bold; color: #004080; margin-bottom: 25px; margin-top: 10px; font-size: 1.8em;}
    h5 { color: #0055A4; margin-top: 25px; margin-bottom: 15px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px;}

    .profile-img-container-input {
        width: 100%; height: auto; display: flex; flex-direction: column;
        justify-content: flex-start; align-items: center; gap: 20px; padding-top: 10px;
    }
    .user_img-input {
        position: relative; width: 150px; height: 150px; border-radius: 50%;
        background: #f0f2f6; overflow: hidden; display: flex;
        justify-content: center; align-items: center; border: 3px solid #007bff;
    }
    .user-img-input-actual { width: 100%; height: 100%; object-fit: cover; }
    </style>
    """,
    unsafe_allow_html=True
)


# --- 이미지 로드 및 Base64 인코딩 함수 (app.py와 동일) ---
def image_to_base64(img_path):
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            buffered = BytesIO()
            img_format = "PNG" if img_path.lower().endswith(".png") else "JPEG"
            if img.format:
                img_format = img.format
            img.save(buffered, format=img_format)
            encoded_string = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/{img_format.lower()};base64,{encoded_string}"
        except Exception as e:
            print(f"Error encoding image {img_path}: {e}")
            return ""
    return ""


logo_data_uri_input = image_to_base64(LOGO_PATH)
user_img_data_uri_input = image_to_base64(USER_IMG_PATH)

# --- 헤더 렌더링 (app.py와 동일) ---
if logo_data_uri_input:
    st.markdown(
        f"""
        <div class="header-container">
            <div class="logo">
                 <a href="/" target="_self">
                    <img src="{logo_data_uri_input}" class="logo-img" alt="PLAY DATA Logo">
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

# --- 모델 확인 ---
if 'model' not in st.session_state or st.session_state.model is None:
    st.error("모델이 로드되지 않았습니다. 메인 페이지를 통해 다시 시도해주세요.")
    st.stop()

# --- MODEL_FEATURES_INPUT_ORDER 및 FEATURE_DETAILS_INPUT_FORM (이전 답변과 동일) ---
MODEL_FEATURES_INPUT_ORDER = [
    'Marital status', 'Course', 'Daytime/evening attendance', 'Previous qualification',
    "Mother's occupation", "Father's occupation", 'Displaced', 'Educational special needs', 'Debtor',
    'Tuition fees up to date', 'Gender', 'Scholarship holder', 'Age',
    'Curricular units 1st sem (approved)', 'Curricular units 1st sem (grade)',
    'Curricular units 2nd sem (approved)', 'Curricular units 2nd sem (grade)'
]
FEATURE_DETAILS_INPUT_FORM = {
    'Marital status': {"label": "결혼 상태", "options_map": mappings.marital_status_map, "default_key": 1,
                       "type": "select"},
    'Course': {"label": "수강 과정", "options_map": mappings.course_map, "default_key": 9, "type": "select"},
    'Daytime/evening attendance': {"label": "주/야간 수업", "options_map": mappings.attendance_map, "default_key": 1,
                                   "type": "select"},
    'Previous qualification': {"label": "이전 학력", "options_map": mappings.previous_qualification_map, "default_key": 1,
                               "type": "select"},
    "Mother's occupation": {"label": "어머니 직업", "options_map": mappings.occupation_map, "default_key": 12,
                            "type": "select"},
    "Father's occupation": {"label": "아버지 직업", "options_map": mappings.occupation_map, "default_key": 12,
                            "type": "select"},
    'Displaced': {"label": "이재민 여부", "options_map": mappings.yes_no_map, "default_key": 0, "type": "select"},
    'Educational special needs': {"label": "특수 교육 필요 여부", "options_map": mappings.yes_no_map, "default_key": 0,
                                  "type": "select"},
    'Debtor': {"label": "학자금 연체 여부", "options_map": mappings.yes_no_map, "default_key": 0, "type": "select"},
    'Tuition fees up to date': {"label": "등록금 납부 여부", "options_map": mappings.yes_no_map, "default_key": 1,
                                "type": "select"},
    'Gender': {"label": "성별", "options_map": mappings.gender_map, "default_key": 1, "type": "select"},
    'Scholarship holder': {"label": "장학금 수혜 여부", "options_map": mappings.scholarship_holder_map, "default_key": 0,
                           "type": "select"},
    'Age': {"label": "입학 시 나이", "min": 17, "max": 70, "default": 20, "type": "int"},
    'Curricular units 1st sem (approved)': {"label": "1학기 이수 학점", "min": 0, "max": 26, "default": 0, "type": "int"},
    'Curricular units 1st sem (grade)': {"label": "1학기 평균 성적", "min": 0.0, "max": 20.0, "default": 0.0, "type": "float",
                                         "step": 0.01, "format": "%.2f"},
    'Curricular units 2nd sem (approved)': {"label": "2학기 이수 학점", "min": 0, "max": 20, "default": 0, "type": "int"},
    'Curricular units 2nd sem (grade)': {"label": "2학기 평균 성적", "min": 0.0, "max": 20.0, "default": 0.0, "type": "float",
                                         "step": 0.01, "format": "%.2f"}
}
# ----------------------------------------------------------

# --- 더미 데이터 정의 (이전 답변과 동일) ---
DUMMY_DATA_DROPOUT_FORM = {
    'Marital status': 1, 'Course': 2, 'Daytime/evening attendance': 1, 'Previous qualification': 1,
    "Mother's occupation": 10, "Father's occupation": 10, 'Displaced': 1, 'Educational special needs': 0, 'Debtor': 1,
    'Tuition fees up to date': 0, 'Gender': 1, 'Scholarship holder': 0, 'Age': 19,
    'Curricular units 1st sem (approved)': 0, 'Curricular units 1st sem (grade)': 0.0,
    'Curricular units 2nd sem (approved)': 0, 'Curricular units 2nd sem (grade)': 0.0
}
DUMMY_DATA_GRADUATE_FORM = {
    'Marital status': 1, 'Course': 11, 'Daytime/evening attendance': 1, 'Previous qualification': 1,
    "Mother's occupation": 4, "Father's occupation": 4, 'Displaced': 0, 'Educational special needs': 0, 'Debtor': 0,
    'Tuition fees up to date': 1, 'Gender': 0, 'Scholarship holder': 1, 'Age': 18,
    'Curricular units 1st sem (approved)': 6, 'Curricular units 1st sem (grade)': 15.50,
    'Curricular units 2nd sem (approved)': 6, 'Curricular units 2nd sem (grade)': 16.00
}
# ----------------------------------------------------------

# --- 폼 위젯용 세션 상태 초기화 (이전 답변과 동일) ---
for feature_key in MODEL_FEATURES_INPUT_ORDER:
    session_key_form = f"form_{feature_key}"
    if session_key_form not in st.session_state:
        detail = FEATURE_DETAILS_INPUT_FORM[feature_key]
        st.session_state[session_key_form] = detail.get("default_key", detail.get("default"))


# ----------------------------------------------------------

# --- 더미 데이터 로드 함수 (이전 답변과 동일) ---
def load_dummy_data_to_form(dummy_profile):
    for key, value in dummy_profile.items():
        session_key_form = f"form_{key}"
        if session_key_form in st.session_state:
            st.session_state[session_key_form] = value


# ----------------------------------------------------------

st.markdown('<h4>학생 정보 입력</h4>', unsafe_allow_html=True)

# --- 더미 데이터 버튼 (이전 답변과 동일) ---
st.markdown("<h6>✨ 빠른 입력을 위해 더미 데이터를 활용해보세요.</h6>", unsafe_allow_html=True)
dummy_cols_form = st.columns(3)
if dummy_cols_form[0].button("중퇴 위험군 학생 예시", use_container_width=True, key="dummy_dropout_btn_form"):
    load_dummy_data_to_form(DUMMY_DATA_DROPOUT_FORM)
if dummy_cols_form[1].button("졸업 예상군 학생 예시", use_container_width=True, key="dummy_graduate_btn_form"):
    load_dummy_data_to_form(DUMMY_DATA_GRADUATE_FORM)
if dummy_cols_form[2].button("입력 초기화", use_container_width=True, key="dummy_reset_btn_form"):
    for feature in MODEL_FEATURES_INPUT_ORDER:
        session_key_form = f"form_{feature}"
        detail = FEATURE_DETAILS_INPUT_FORM[feature]
        st.session_state[session_key_form] = detail.get("default_key", detail.get("default"))
st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
# ----------------------------------------------------------

# --- 입력 폼 시작 (제공된 input_form.py의 레이아웃 구조 활용) ---
with st.form("student_data_entry_form_final"):
    form_col_left_main, form_col_right_main = st.columns([1, 2.2], gap="large")  # 비율 조정 가능

    with form_col_left_main:  # 프로필 이미지 및 학생 이름
        st.markdown(f"""
            <div class="profile-img-container-input">
                <div class="user_img-input">
                    <img src="{user_img_data_uri_input if user_img_data_uri_input else 'https://via.placeholder.com/120?text=No+Image'}" class="user-img-input-actual" alt="User Image">
                </div>
            </div>
        """, unsafe_allow_html=True)
        student_name_form_input = st.text_input(
            "학생 이름",
            value=st.session_state.get("student_name", ""),
            placeholder="이름을 입력하세요",
            key="name_input_in_form_page"  # 폼 내에서 유니크한 키
        )

    with form_col_right_main:  # 나머지 입력 필드들
        # MODEL_FEATURES_INPUT_ORDER에 정의된 모든 필드를 생성
        # UI 가독성을 위해 섹션으로 나누어 표시

        st.markdown("<h5>기본 인적 사항</h5>", unsafe_allow_html=True)
        form_cols_basic = st.columns(2)
        basic_info_keys = ['Age', 'Gender', 'Marital status']
        for i, key in enumerate(basic_info_keys):
            detail = FEATURE_DETAILS_INPUT_FORM[key]
            session_key = f"form_{key}"
            current_val = st.session_state.get(session_key)
            with form_cols_basic[i % 2]:
                if detail["type"] == "select":
                    options_dict = detail["options_map"]
                    options_keys_list = list(options_dict.keys())
                    default_idx = options_keys_list.index(
                        current_val) if current_val in options_keys_list else options_keys_list.index(
                        detail["default_key"])
                    st.selectbox(label=detail["label"], options=options_keys_list,
                                 format_func=lambda k_opt: options_dict[k_opt], index=default_idx, key=session_key)
                elif detail["type"] == "int":
                    st.number_input(label=detail["label"], min_value=detail["min"], max_value=detail["max"],
                                    value=int(current_val), step=1, key=session_key)

        st.markdown("<h5>학업 배경 및 환경</h5>", unsafe_allow_html=True)
        form_cols_academic = st.columns(2)
        academic_env_keys = ['Course', 'Daytime/evening attendance', 'Previous qualification', "Mother's occupation",
                             "Father's occupation", 'Displaced', 'Educational special needs']
        for i, key in enumerate(academic_env_keys):
            detail = FEATURE_DETAILS_INPUT_FORM[key]
            session_key = f"form_{key}"
            current_val = st.session_state.get(session_key)
            with form_cols_academic[i % 2]:
                if detail["type"] == "select":
                    options_dict = detail["options_map"]
                    options_keys_list = list(options_dict.keys())
                    default_idx = options_keys_list.index(
                        current_val) if current_val in options_keys_list else options_keys_list.index(
                        detail["default_key"])
                    st.selectbox(label=detail["label"], options=options_keys_list,
                                 format_func=lambda k_opt: options_dict[k_opt], index=default_idx, key=session_key)

        st.markdown("<h5>재정 상태</h5>", unsafe_allow_html=True)
        form_cols_financial = st.columns(3)  # 3열로 변경
        financial_keys = ['Debtor', 'Tuition fees up to date', 'Scholarship holder']
        for i, key in enumerate(financial_keys):
            detail = FEATURE_DETAILS_INPUT_FORM[key]
            session_key = f"form_{key}"
            current_val = st.session_state.get(session_key)
            with form_cols_financial[i]:  # 각 필드를 새 컬럼에
                if detail["type"] == "select":
                    options_dict = detail["options_map"]
                    options_keys_list = list(options_dict.keys())
                    default_idx = options_keys_list.index(
                        current_val) if current_val in options_keys_list else options_keys_list.index(
                        detail["default_key"])
                    st.selectbox(label=detail["label"], options=options_keys_list,
                                 format_func=lambda k_opt: options_dict[k_opt], index=default_idx, key=session_key)

        st.markdown("<h5>성적 정보</h5>", unsafe_allow_html=True)
        form_cols_grades = st.columns(2)
        grade_keys_approved = ['Curricular units 1st sem (approved)', 'Curricular units 2nd sem (approved)']
        grade_keys_gradeval = ['Curricular units 1st sem (grade)', 'Curricular units 2nd sem (grade)']

        with form_cols_grades[0]:
            for key in grade_keys_approved:
                detail = FEATURE_DETAILS_INPUT_FORM[key]
                session_key = f"form_{key}"
                current_val = st.session_state.get(session_key)
                st.number_input(label=detail["label"], min_value=detail["min"], max_value=detail["max"],
                                value=int(current_val), step=1, key=session_key)
        with form_cols_grades[1]:
            for key in grade_keys_gradeval:
                detail = FEATURE_DETAILS_INPUT_FORM[key]
                session_key = f"form_{key}"
                current_val = st.session_state.get(session_key)
                st.number_input(label=detail["label"], min_value=float(detail["min"]), max_value=float(detail["max"]),
                                value=float(current_val), step=0.01, format="%.2f", key=session_key)

    # --- 폼 제출 버튼 ---
    form_button_cols_submit = st.columns([0.8, 1.5, 0.8])  # 중앙 정렬을 위한 컬럼
    with form_button_cols_submit[1]:
        form_submitted_final = st.form_submit_button("예측 결과 확인", use_container_width=True, type="primary")

if form_submitted_final:
    st.session_state.student_name = st.session_state.name_input_in_form_page  # 학생 이름 최종 저장

    if not st.session_state.student_name.strip():
        st.error("❗ 학생 이름을 입력해주세요.")
    else:
        model_input_data_submit = {}
        form_input_original_labels_submit = {'Student Name': st.session_state.student_name}

        for feature_key in MODEL_FEATURES_INPUT_ORDER:
            session_key = f"form_{feature_key}"
            user_selected_value_submit = st.session_state[session_key]
            detail_submit = FEATURE_DETAILS_INPUT_FORM[feature_key]

            # 모델 입력값: selectbox의 경우 key(숫자), number_input은 숫자 그대로
            model_input_data_submit[feature_key] = user_selected_value_submit

            # 결과 표시용 레이블: selectbox의 경우 value(한글)
            if detail_submit["type"] == "select":
                form_input_original_labels_submit[feature_key] = detail_submit["options_map"].get(
                    user_selected_value_submit, "N/A")
            else:  # int, float
                form_input_original_labels_submit[feature_key] = user_selected_value_submit

        student_df_for_model = pd.DataFrame([model_input_data_submit], columns=MODEL_FEATURES_INPUT_ORDER)

        st.session_state.form_input_original = form_input_original_labels_submit
        st.session_state.student_info_df = student_df_for_model

        st.success("✅ 정보가 성공적으로 처리되었습니다. 결과 페이지로 이동합니다...")
        st.switch_page("pages/result.py")
