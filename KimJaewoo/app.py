import streamlit as st
from PIL import Image
import os
import joblib
import base64
from io import BytesIO


# --- 공통 변수 및 함수 (기존 앱에서 가져옴) ---
@st.cache_resource
def load_model():
    model_path = os.path.join('models', 'best_model_pipeline.pkl')
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            return model
        except Exception as e:
            st.error(f"모델 로딩 중 오류 발생: {e}")
            return None
    else:
        st.error(f"경로 '{model_path}'에서 모델 파일을 찾을 수 없습니다. 노트북을 실행하여 모델을 먼저 저장해주세요.")
        return None


# ---------------------------------------------

LOGO_PATH = os.path.join("img", "logo.png")
IMG1_PATH = os.path.join("img", "img1.png")

st.set_page_config(
    page_title="PLAY DATA - 학생 학업 여정 지원",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS (제공된 app.py의 스타일 유지)
st.markdown(
    """
    <style>
    .reportview-container { background: #fff; max-width: 100%; overflow-x: hidden; }
    .main .block-container { padding-right: 0; padding-left: 0; padding-bottom: 0; max-width: 100%; }
    .st-emotion-cache-ckbrp0 { width: 100%; position: relative; flex: 1 1 0%; flex-direction: column; }
    .st-emotion-cache-t1wise { padding-left: 0 !important; padding-right: 0 !important; }
    @media (min-width: calc(736px + 8rem)) {
        .st-emotion-cache-t1wise { padding-left: 0 !important; padding-right: 0 !important; }
    }
    .stApp > header { display: none; }
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 25px 120px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 100%; position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }
    .logo-img { height: 30px; width: auto; }
    .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; }
    .nav-menu li { margin-left: 35px; }
    .nav-menu a { text-decoration: none; color: #333; font-weight: bold; font-size: 14px; }
    .hero-section { position: relative; width: 100vw; height: 70vh; display: flex; justify-content: center; align-items: center; flex-direction: column; overflow: hidden; margin-top: 80px; }
    .background-img { width: 100%; height: 100%; object-fit: cover; filter: brightness(50%); position: absolute; z-index: 1; top:0; left:0;}
    .overlay-text { position: relative; color: #fff; text-align: center; z-index: 2; padding: 20px; width: 100%; margin-top: -100px; }
    .overlay-text h1 { font-size: 3.5em; margin-bottom: 10px; font-weight: bold; color: #fff !important; }
    .overlay-text h2 { font-size: 2.5em; font-weight: bold; color: #fff !important;}
    .overlay-text h3 { font-size: 2em; margin-top: 0; font-weight: bold; margin-bottom: 20px; color: #fff !important;}
    .hero-section .stButton>button {
        background-color: white !important; color: #007bff !important; padding: 12px 60px !important;
        border-radius: 30px !important; text-decoration: none !important; font-weight: bold !important;
        font-size: 18px !important; transition: all 0.3s ease !important; border: 1px solid #007bff !important;
        cursor: pointer !important; display: inline-flex !important; align-items: center !important;
    }
    .hero-section .stButton>button:hover {
        background-color: #007bff !important; color: #ffffff !important; transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    .nav-menu a[href="/input_form"] { cursor: pointer; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 세션 상태 초기화 ---
if 'student_info_df' not in st.session_state:
    st.session_state.student_info_df = None
if 'prediction' not in st.session_state:
    st.session_state.prediction = None
if 'probability' not in st.session_state:
    st.session_state.probability = None
if 'model' not in st.session_state:
    st.session_state.model = load_model()
if 'form_input_original' not in st.session_state:
    st.session_state.form_input_original = {}
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""


# ---------------------------------------------

def image_to_base64(img_path):
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            buffered = BytesIO()
            # 이미지 포맷을 원본 파일에 맞게 지정 (PNG가 기본, 필요시 JPEG 등으로 변경)
            img_format = "PNG" if img_path.lower().endswith(".png") else "JPEG"
            if img.format:  # Pillow 객체에서 format 정보가 있으면 사용
                img_format = img.format

            img.save(buffered, format=img_format)
            encoded_string = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/{img_format.lower()};base64,{encoded_string}"
        except Exception as e:
            print(f"Error encoding image {img_path}: {e}")
            return ""
    return ""


logo_data_uri = image_to_base64(LOGO_PATH)
img1_data_uri = image_to_base64(IMG1_PATH)

# --- 헤더 렌더링 ---
if logo_data_uri:
    st.markdown(
        f"""
        <div class="header-container">
            <div class="logo">
                <a href="/" target="_self">
                    <img src="{logo_data_uri}" class="logo-img" alt="PLAY DATA Logo">
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
else:
    st.error("로고 이미지를 로드할 수 없습니다.")

# --- 히어로 섹션 ---
if img1_data_uri:
    st.markdown(
        f"""
        <div class="hero-section">
            <img src="{img1_data_uri}" class="background-img" alt="Background">
            <div class="overlay-text">
                <h1>PLAY DATA 학생 지원 시스템</h1>
                <h3>학업 여정을 예측하고 성공적인 미래를 만듭니다.</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="text-align: center; position: relative; z-index: 2; margin-top: -150px; margin-bottom: 50px;">',
        unsafe_allow_html=True)
    if st.button("학생 정보 입력 및 예측 시작", key="hero_button_start", help="학생 정보 입력 페이지로 이동합니다."):
        st.switch_page("pages/input_form.py")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color: #333;'>PLAY DATA 학생 지원 시스템</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color: #555;'>학업 여정을 예측하고 성공적인 미래를 만듭니다.</h3>", unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; margin-top: 30px;">', unsafe_allow_html=True)
    if st.button("학생 정보 입력 및 예측 시작", key="hero_button_start_no_img"):
        st.switch_page("pages/input_form.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.success("탐색할 페이지를 선택하세요.")
st.sidebar.page_link("pages/input_form.py", label="🧑‍🎓 학생 정보 입력", icon="🧑‍🎓")
st.sidebar.page_link("pages/result.py", label="📈 예측 결과", icon="📈")
st.sidebar.page_link("pages/4_🔄_모델_재학습.py", label="🔄 모델 재학습", icon="🔄")