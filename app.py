import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="파일 자동 분류기",
    page_icon="📂",
    layout="wide"
)

st.title("📂 파일 자동 분류기")

st.write(
    "파일을 업로드하고 원하는 규칙대로 폴더를 만들어 압축파일을 생성합니다."
)

# -------------------------
# Session State
# -------------------------

if "rules" not in st.session_state:
    st.session_state.rules = []

# -------------------------
# 파일 업로드
# -------------------------

uploaded_files = st.file_uploader(
    "파일 선택",
    accept_multiple_files=True
)

extensions = []

if uploaded_files:

    extensions = sorted(
        list({
            Path(file.name).suffix.lower().replace(".", "")
            for file in uploaded_files
            if Path(file.name).suffix != ""
        })
    )

    st.success(f"{len(uploaded_files)}개의 파일이 업로드되었습니다.")

    st.subheader("발견된 확장자")

    st.write(extensions)

# -------------------------
# 규칙 추가
# -------------------------

if st.button("➕ 새 폴더 추가"):

    st.session_state.rules.append({

        "folder": "",

        "extensions": [],

        "keywords": ""

    })

st.divider()

st.header("분류 규칙")

delete = None

for i, rule in enumerate(st.session_state.rules):

    with st.container(border=True):

        col1, col2 = st.columns([9,1])

        with col1:

            folder = st.text_input(

                "폴더 이름",

                value=rule["folder"],

                key=f"folder{i}"

            )

            st.session_state.rules[i]["folder"] = folder

        with col2:

            st.write("")

            st.write("")

            if st.button("❌", key=f"delete{i}"):

                delete = i

        ext = st.multiselect(

            "확장자",

            extensions,

            default=rule["extensions"],

            key=f"ext{i}"

        )

        st.session_state.rules[i]["extensions"] = ext

        keyword = st.text_area(

            "파일명 포함 문자 (한 줄에 하나)",

            value=rule["keywords"],

            height=120,

            key=f"keyword{i}"

        )

        st.session_state.rules[i]["keywords"] = keyword

        if len(ext) == 0 and keyword.strip() == "":

            st.warning("확장자 또는 포함 문자를 하나 이상 입력하세요.")

if delete is not None:

    st.session_state.rules.pop(delete)

    st.rerun()

st.divider()

st.subheader("현재 규칙")

st.json(st.session_state.rules)
