import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import os
import base64
from io import BytesIO
from PIL import Image
import sys

# 프로젝트 루트 경로를 sys.path에 추가
current_dir_result = os.path.dirname(os.path.abspath(__file__))
project_root_result = os.path.dirname(current_dir_result)
if project_root_result not in sys.path:
    sys.path.append(project_root_result)

from utils import mappings  # mappings.py 임포트

# --- 이미지 경로 ---
IMG_DIR_RES = os.path.join(project_root_result, "img")
LOGO_PATH_RES = os.path.join(IMG_DIR_RES, "logo.png")
USER_IMG_PATH_RES = os.path.join(IMG_DIR_RES, "user_img.png")

st.set_page_config(
    page_title="예측 결과 - PLAY DATA",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS (제공된 last_p.py 및 이전 result.py 스타일 조합) ---
st.markdown(
    """
    <style>
    /* ... (이전 답변의 result.py CSS 중 필요한 부분과 last_p.py CSS 조합) ... */
    .reportview-container { background: #fff; max-width: 100%; overflow-x: hidden; }
    .main .block-container { padding-right: 100px; padding-left: 100px; padding-bottom: 50px; max-width: 100%;} /* 패딩 조정 */
    .st-emotion-cache-ckbrp0 { padding-left: 100px !important; padding-right: 100px !important; }
    .st-emotion-cache-t1wise { padding-left: 100px !important; padding-right: 100px !important; }
    @media (min-width: calc(736px + 8rem)) {
        .main .block-container, .st-emotion-cache-ckbrp0, .st-emotion-cache-t1wise {
            padding-left: 120px !important; padding-right: 120px !important;
        }
    }
    .stApp > header { display: none; }
    .header-container { display: flex; justify-content: space-between; align-items: center; padding: 20px 100px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); width: 100%; position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }
    .logo-img { height: 30px; width: auto; }
    .nav-menu ul { list-style: none; margin: 0; padding: 0; display: flex; }
    .nav-menu li { margin-left: 30px; }
    .nav-menu a { text-decoration: none; color: #333; font-weight: bold; font-size: 16px; padding: 8px 12px; border-radius: 4px; transition: all 0.3s ease; }
    .nav-menu a:hover { color: #007bff; background-color: #f0f0f0; }

    .student-name-title-result { font-weight:bold; font-size:28px; margin-bottom:25px; color: #004080; text-align: center; padding-bottom:15px; border-bottom: 2px solid #004080;}

    .profile-section-container { display: flex; align-items: flex-start; gap: 30px; margin-bottom: 25px; padding: 20px; background-color: #f8f9fa; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);}
    .profile-image-area { flex-basis: 200px; flex-shrink: 0; text-align: center; }
    .profile-img-display { width:160px; height:160px; border-radius:50%; object-fit:cover; border: 4px solid #007bff; margin-bottom:10px;}
    .student-name-img-label { font-weight:bold; font-size:20px; color: #333;}

    .student-info-table-area { flex-grow: 1; }
    .info-table-custom {width:100%; border-collapse:collapse; font-size:14px; background-color: white;}
    .info-table-custom th, .info-table-custom td {border:1px solid #e0e0e0; padding:10px 12px; text-align:left; }
    .info-table-custom th {background:#f0f2f5; font-weight:600; color: #495057;}

    .prediction-card { background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.08); margin-top: 15px;}
    .prediction-card-title { font-size: 1.4em; font-weight: bold; margin-bottom: 10px; color: #0055A4;}
    .highlight-text-dropout { color: crimson; font-size: 1.6em; font-weight: bold; }
    .highlight-text-graduate { color: mediumseagreen; font-size: 1.6em; font-weight: bold; }
    .advice-section { font-size: 1.0em; line-height: 1.6; color: #333; margin-top: 10px;}

    h3.analysis-title { color: #0055A4; font-size: 1.8em; margin-top: 35px; margin-bottom: 20px; border-bottom: 2px solid #0055A4; padding-bottom: 8px;}
    .stTabs [data-baseweb="tab-list"] { gap: 20px; background-color: #e9ecef; border-radius: 8px; padding: 6px;}
	.stTabs [data-baseweb="tab"] { height: 45px; background-color: transparent; border-radius: 6px; font-weight: 500; font-size: 1.1em; color: #495057;}
	.stTabs [aria-selected="true"] { background-color: #007bff; color: white;}
    .stButton>button { /* 페이지 이동 버튼 */
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
def image_to_base64(img_path):
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            buffered = BytesIO()
            img_format = "PNG" if img_path.lower().endswith(".png") else "JPEG"
            if img.format: img_format = img.format
            img.save(buffered, format=img_format)
            encoded_string = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/{img_format.lower()};base64,{encoded_string}"
        except:
            return ""
    return ""


logo_data_uri_res = image_to_base64(LOGO_PATH_RES)
user_img_data_uri_res = image_to_base64(USER_IMG_PATH_RES)

# --- 헤더 렌더링 (app.py와 동일) ---
if logo_data_uri_res:
    st.markdown(
        f"""
        <div class="header-container">
            <div class="logo">
                 <a href="/" target="_self">
                    <img src="{logo_data_uri_res}" class="logo-img" alt="PLAY DATA Logo">
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

# --- 데이터 및 모델 확인 (기존 result.py와 동일) ---
if 'model' not in st.session_state or st.session_state.model is None:
    st.error("모델 로딩 오류.")
    st.stop()
if 'student_info_df' not in st.session_state or st.session_state.student_info_df is None:
    st.warning("학생 정보가 없습니다. '학생 정보 입력' 페이지에서 정보를 먼저 입력해주세요.")
    st.stop()
if 'form_input_original' not in st.session_state or not st.session_state.form_input_original:
    st.warning("표시할 학생 원본 정보가 없습니다.")
    st.stop()

model_res_page = st.session_state.model
student_df_to_predict_page = st.session_state.student_info_df
student_original_labels_page = st.session_state.form_input_original
student_name_page = student_original_labels_page.get("Student Name", "정보 없음")

# --- 예측 수행 (기존 result.py와 동일) ---
try:
    probabilities_page = model_res_page.predict_proba(student_df_to_predict_page)
    prediction_page = model_res_page.predict(student_df_to_predict_page)[0]
    prob_dropout_page = probabilities_page[0, 0]
    prob_graduate_page = probabilities_page[0, 1]
except Exception as e:
    st.error(f"예측 실행 중 오류: {e}")
    st.stop()

# --- 학생 정보 및 예측 결과 표시 (제공된 last_p.py 디자인 적용 + 기존 기능 통합) ---
st.markdown(f"<div class='student-name-title-result'>{student_name_page} 님의 예측 결과</div>", unsafe_allow_html=True)

st.markdown("<div class='profile-section-container'>", unsafe_allow_html=True)  # 전체 컨테이너 시작
# 왼쪽: 프로필 이미지
st.markdown("<div class='profile-image-area'>", unsafe_allow_html=True)
if user_img_data_uri_res:
    st.markdown(f'<img src="{user_img_data_uri_res}" class="profile-img-display" alt="User Image">',
                unsafe_allow_html=True)
else:
    st.markdown(
        f'<div style="width:160px; height:160px; border-radius:50%; background:#e9ecef; display:flex; align-items:center; justify-content:center; margin-bottom:10px; border: 3px solid #007bff;"><span style="font-size:1.3em; color:#adb5bd;">No Img</span></div>',
        unsafe_allow_html=True)
st.markdown(f"<div class='student-name-img-label'>{student_name_page}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # profile-image-area 닫기

# 오른쪽: 정보 테이블
st.markdown("<div class='student-info-table-area'>", unsafe_allow_html=True)
# FEATURE_DETAILS_INPUT_FORM은 input_form.py에 정의되어 있어야 함 (또는 여기서 다시 정의)
# 여기서는 input_form.py의 것을 참조한다고 가정
# 테이블 생성 로직 (2열로 표시)
table_items = []
for key, label_detail in mappings.get_feature_details_for_display().items():  # mappings.py 에 이 함수 추가 필요
    value = student_original_labels_page.get(key, "N/A")
    table_items.append({"항목": label_detail["label"], "내용": value})

# 2열로 나누기
half = (len(table_items) + 1) // 2
left_items = table_items[:half]
right_items = table_items[half:]

table_html = '<table class="info-table-custom">'
for i in range(max(len(left_items), len(right_items))):
    table_html += "<tr>"
    if i < len(left_items):
        table_html += f"<th>{left_items[i]['항목']}</th><td>{left_items[i]['내용']}</td>"
    else:
        table_html += "<th></th><td></td>"  # 빈 셀

    if i < len(right_items):
        table_html += f"<th>{right_items[i]['항목']}</th><td>{right_items[i]['내용']}</td>"
    else:
        table_html += "<th></th><td></td>"
    table_html += "</tr>"
table_html += "</table>"
st.markdown(table_html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)  # student-info-table-area 닫기
st.markdown("</div>", unsafe_allow_html=True)  # profile-section-container 닫기

# 예측 결과 및 조언 카드
st.markdown("<div class='prediction-card'>", unsafe_allow_html=True)
st.markdown("<div class='prediction-card-title'>종합 예측 및 조언</div>", unsafe_allow_html=True)
if prediction_page == 1:  # Graduate
    st.markdown(f"<p class='highlight-text-graduate'>🎓 졸업이 예상됩니다.</p>", unsafe_allow_html=True)
    if prob_graduate_page > prob_dropout_page and prob_graduate_page > 0.6:
        st.balloons()
        st.toast('🎉 훌륭한 학생입니다! 졸업 가능성이 매우 높습니다! 🎉', icon='🥳')

    advice = "이 학생은 학업을 성공적으로 마칠 가능성이 높습니다. 지속적인 격려와 함께, 혹시 모를 어려움은 없는지 주기적으로 관심을 가져주시면 더욱 좋겠습니다."
    if prob_graduate_page >= 0.75:
        advice = "👍 **매우 긍정적:** " + advice
    elif prob_graduate_page >= 0.6:
        advice = "긍정적: " + advice
    else:
        advice = "주의 관찰: 졸업이 예상되지만, 안심하기는 이릅니다. 꾸준한 관심과 지원이 필요합니다."
    st.markdown(f"<div class='advice-section'>{advice}</div>", unsafe_allow_html=True)
else:  # Dropout
    st.markdown(f"<p class='highlight-text-dropout'>😥 중퇴가 예상됩니다.</p>", unsafe_allow_html=True)
    advice = "이 학생은 학업 중도 포기 가능성이 있습니다. 선제적인 상담과 지원을 통해 학업을 지속할 수 있도록 도와주세요."
    if prob_dropout_page >= 0.75:
        advice = "🚨 **긴급 상담 필요:** 중퇴 위험이 매우 높습니다. 즉각적인 개별 상담을 통해 어려움을 파악하고, 맞춤형 학습 지원 및 정서적 지원 방안을 마련해야 합니다."
    elif prob_dropout_page >= 0.6:
        advice = "⚠️ **주의 및 상담 권고:** " + advice
    else:
        advice = "관찰 필요: 중퇴가 예상되지만, 아직 변화의 여지가 있습니다. 학생의 강점을 격려하고 약점을 보완할 수 있도록 지원해주세요."
    st.markdown(f"<div class='advice-section'>{advice}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 상세 분석 탭 (기존 기능 유지) ---
st.markdown("<h3 class='analysis-title'>상세 분석 자료</h3>", unsafe_allow_html=True)
tab1_res_page, tab2_res_page, tab3_res_page = st.tabs(["📊 예측 확률 분포", "📚 성적 비교", "⚠️ 주요 영향 요인"])

with tab1_res_page:
    st.markdown("<h5>중퇴 및 졸업 예측 확률</h5>", unsafe_allow_html=True)
    labels_proba_page = ['중퇴 확률', '졸업 확률']
    values_proba_page = [prob_dropout_page, prob_graduate_page]

    fig_proba_res_tab_page = go.Figure()
    fig_proba_res_tab_page.add_trace(go.Bar(
        y=[''], x=[values_proba_page[0]], name=labels_proba_page[0], orientation='h',
        marker=dict(color='crimson', line=dict(color='darkred', width=1)),
        text=[f"{values_proba_page[0]:.1%}"], textposition='inside', insidetextanchor='middle', textfont_size=14
    ))
    fig_proba_res_tab_page.add_trace(go.Bar(
        y=[''], x=[values_proba_page[1]], name=labels_proba_page[1], orientation='h',
        marker=dict(color='mediumseagreen', line=dict(color='darkgreen', width=1)),
        text=[f"{values_proba_page[1]:.1%}"], textposition='inside', insidetextanchor='middle', textfont_size=14
    ))
    fig_proba_res_tab_page.update_layout(
        barmode='stack', xaxis_title="확률", height=180,
        margin=dict(l=0, r=0, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        xaxis=dict(tickformat=".0%", range=[0, 1]), yaxis_visible=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#333")
    )
    st.plotly_chart(fig_proba_res_tab_page, use_container_width=True)

with tab2_res_page:
    st.markdown("<h5>학생 성적과 과정 평균 비교</h5>", unsafe_allow_html=True)
    student_course_code_page = str(student_df_to_predict_page['Course'].iloc[0])
    student_grade_1st_page = student_df_to_predict_page['Curricular units 1st sem (grade)'].iloc[0]
    student_grade_2nd_page = student_df_to_predict_page['Curricular units 2nd sem (grade)'].iloc[0]
    student_avg_grade_page = (student_grade_1st_page + student_grade_2nd_page) / 2 if (
                                                                                                  student_grade_1st_page + student_grade_2nd_page) > 0 else 0.0


    @st.cache_data
    def load_course_averages_page():
        json_path_page = os.path.join(project_root_result, 'data', 'course_averages.json')
        try:
            with open(json_path_page, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None


    course_averages_data_page = load_course_averages_page()
    if course_averages_data_page:
        course_specific_averages_page = course_averages_data_page.get(student_course_code_page,
                                                                      course_averages_data_page.get('overall'))
        if course_specific_averages_page:
            class_avg_1_page = course_specific_averages_page.get('sem1_avg', 12.0)
            class_avg_2_page = course_specific_averages_page.get('sem2_avg', 12.0)
            class_avg_o_page = course_specific_averages_page.get('annual_avg', 12.0)

            categories_page = ['1학기 성적', '2학기 성적', '연 평균 성적']
            student_grades_page = [student_grade_1st_page, student_grade_2nd_page, student_avg_grade_page]
            course_avg_plot_page = [class_avg_1_page, class_avg_2_page, class_avg_o_page]

            fig_grades_page = go.Figure()
            fig_grades_page.add_trace(go.Bar(name='해당 학생', x=categories_page, y=student_grades_page,
                                             marker_color='royalblue', text=[f"{g:.2f}" for g in student_grades_page],
                                             textposition='outside'))
            course_label_page = mappings.course_map.get(int(student_course_code_page), student_course_code_page)
            fig_grades_page.add_trace(go.Bar(name=f"과정 '{course_label_page}' 평균",
                                             x=categories_page, y=course_avg_plot_page,
                                             marker_color='lightsalmon',
                                             text=[f"{g:.2f}" for g in course_avg_plot_page],
                                             textposition='outside'))
            fig_grades_page.update_layout(
                barmode='group', yaxis_title="평균 성적", legend_title_text='구분', height=380,
                yaxis_range=[0, 20], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(t=50)  # 그래프 제목과 축 제목 공간 확보
            )
            st.plotly_chart(fig_grades_page, use_container_width=True)
        else:
            st.warning("과정 평균 성적 정보를 찾을 수 없습니다.")
    else:
        st.warning("과정별 평균 성적 데이터를 로드하지 못했습니다.")

with tab3_res_page:
    st.markdown("<h5>예측에 영향을 미치는 주요 요인 (예시)</h5>", unsafe_allow_html=True)
    st.info("아래는 모델 예측에 영향을 미쳤을 수 있는 학생의 주요 특성입니다. 실제 모델은 더 복잡한 관계를 고려합니다.")
    factors_display_page = []

    original_input_for_factors = st.session_state.form_input_original  # 한글 레이블로 된 입력값

    if original_input_for_factors.get('Tuition fees up to date') == '아니오':
        factors_display_page.append(("🔴 등록금 미납", "등록금 미납은 중퇴 위험을 높일 수 있습니다."))
    if original_input_for_factors.get('Debtor') == '예':
        factors_display_page.append(("🔴 학자금 연체", "학자금 연체는 학업 지속에 부정적 영향을 줄 수 있습니다."))

    s1_approved_page = student_df_to_predict_page['Curricular units 1st sem (approved)'].iloc[0]
    s1_grade_page = student_df_to_predict_page['Curricular units 1st sem (grade)'].iloc[0]
    if s1_approved_page < 2 or s1_grade_page < 10.0:
        factors_display_page.append(
            ("🟡 1학기 학업 부진", f"1학기 이수 학점({s1_approved_page}개) 또는 평균 성적({s1_grade_page:.2f}점)이 낮아 주의가 필요합니다."))

    if original_input_for_factors.get('Scholarship holder') == '수혜' and prediction_page == 1:
        factors_display_page.append(("🟢 장학금 수혜", "장학금 수혜는 학업 성취에 긍정적 요인입니다."))

    if not factors_display_page:
        st.write("현재 정보로는 특별히 강조되는 위험/긍정 요인이 명확하지 않습니다.")
    else:
        for factor_title, factor_desc in factors_display_page:
            with st.expander(factor_title):
                st.write(factor_desc)
    st.caption("이 분석은 일반적인 경향에 기반한 예시이며, 실제 모델은 더 많은 변수를 고려합니다.")

st.markdown("<hr style='margin-top:40px; margin-bottom:20px;'>", unsafe_allow_html=True)
if st.button("다른 학생 정보 입력", use_container_width=True, key="go_back_to_input_btn_bottom_result_page"):
    st.session_state.student_info_df = None
    st.session_state.form_input_original = None
    st.switch_page("pages/input_form.py")