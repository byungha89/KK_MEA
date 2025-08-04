import streamlit as st
import os
from pathlib import Path

# --- 1. 기본 설정 ---
st.set_page_config(page_title="영업 지원 대시보드", layout="centered")

# 데이터 폴더 경로 및 카테고리 정의
DATA_PATH = Path("data")
CATEGORIES = {
    "카탈로그": "catalog",
    "매뉴얼": "manual",
    "동영상": "video",
    "어플리케이션": "application"
}

# --- 2. 세션 상태 초기화 ---
# 'view': 사용자 화면 전환 (main, 카탈로그, 매뉴얼 등)
if 'view' not in st.session_state:
    st.session_state.view = 'main'
# 'admin_login': 관리자 로그인 상태
if 'admin_login' not in st.session_state:
    st.session_state.admin_login = False

# --- 3. 관리자 모드 (사이드바) ---
st.sidebar.title("🔐 관리자 모드")

# 로그인 상태가 아닐 때
if not st.session_state.admin_login:
    password = st.sidebar.text_input("비밀번호", type="password")
    if st.sidebar.button("로그인"):
        # 실제 운영 시에는 더 안전한 비밀번호를 사용하세요.
        if password == "1234":
            st.session_state.admin_login = True
            st.rerun() # 로그인 성공 시 페이지 새로고침
        else:
            st.sidebar.error("비밀번호가 올바르지 않습니다.")
# 로그인 상태일 때
else:
    st.sidebar.success("관리자 모드로 로그인되었습니다.")
    if st.sidebar.button("로그아웃"):
        st.session_state.admin_login = False
        st.session_state.view = 'main' # 로그아웃 시 메인 화면으로
        st.rerun()

# --- 4. 함수 정의 ---

def display_files(category_name, folder_name):
    """(사용자용) 선택된 카테고리의 파일 목록을 화면에 표시하는 함수"""
    st.header(f"📂 {category_name} 목록")

    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.view = 'main'
        st.rerun()

    folder_path = DATA_PATH / folder_name
    if not folder_path.exists():
        st.warning(f"'{folder_path}' 폴더를 찾을 수 없습니다.")
        return

    files = os.listdir(folder_path)
    if not files:
        st.info("표시할 파일이 없습니다.")
        return

    for file_name in files:
        file_path = folder_path / file_name
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        st.markdown("---")
        st.subheader(file_name)

        if file_name.lower().endswith('.pdf'):
            if st.button(f"📄 '{file_name}' 미리보기", key=f"view_{file_name}"):
                st.pdf_viewer(str(file_path))
        elif file_name.lower().endswith(('.mp4', '.mov')):
            st.video(file_bytes)
        else:
            st.download_button(
                label=f"📦 '{file_name}' 다운로드",
                data=file_bytes,
                file_name=file_name,
                key=f"download_{file_name}"
            )

def admin_page():
    """(관리자용) 파일 업로드 페이지를 표시하는 함수"""
    st.title("🛠️ 관리자 페이지: 파일 업로드")
    st.markdown("---")

    # 1. 업로드할 카테고리 선택
    category_to_upload = st.selectbox(
        "파일을 업로드할 카테고리를 선택하세요.",
        options=list(CATEGORIES.keys())
    )

    # 2. 파일 업로더 위젯 (여러 파일 동시 업로드 가능)
    uploaded_files = st.file_uploader(
        "여기에 파일을 드래그하거나 클릭하여 선택하세요.",
        accept_multiple_files=True,
        key="admin_uploader"
    )

    if uploaded_files:
        if st.button("선택한 파일 업로드", type="primary"):
            folder_name = CATEGORIES[category_to_upload]
            save_path = DATA_PATH / folder_name
            save_path.mkdir(exist_ok=True) # 폴더 없으면 생성

            with st.spinner("파일을 업로드하는 중입니다..."):
                for file in uploaded_files:
                    file_path = save_path / file.name
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    st.success(f"✅ '{file.name}' 파일을 '{category_to_upload}' 카테고리에 저장했습니다.")

# --- 5. 메인 화면 표시 로직 ---

# 관리자 모드일 경우
if st.session_state.admin_login:
    admin_page()

# 사용자 모드일 경우
else:
    if st.session_state.view == 'main':
        st.title("🚀 영업 지원 프로그램")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("카탈로그", use_container_width=True, type="primary"):
                st.session_state.view = '카탈로그'
                st.rerun()
            if st.button("동영상", use_container_width=True):
                st.session_state.view = '동영상'
                st.rerun()
        with col2:
            if st.button("매뉴얼", use_container_width=True, type="primary"):
                st.session_state.view = '매뉴얼'
                st.rerun()
            if st.button("어플리케이션", use_container_width=True):
                st.session_state.view = '어플리케이션'
                st.rerun()
    else:
        category_name = st.session_state.view
        folder_name = CATEGORIES[category_name]
        display_files(category_name, folder_name)
