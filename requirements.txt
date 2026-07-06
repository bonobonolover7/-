import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="파일 자동 분류기",
    page_icon="📁",
    layout="wide"
)

st.title("📁 파일 자동 분류기")

uploaded_files = st.file_uploader(
    "파일을 선택하세요",
    accept_multiple_files=True
)

# -----------------------------
# 업로드된 확장자 추출
# -----------------------------

extensions = []

if uploaded_files:
    extensions = sorted(
        list({
            Path(file.name).suffix.lower().replace(".", "")
            for file in uploaded_files
            if Path(file.name).suffix != ""
        })
    )

    st.success(f"{len(uploaded_files)}개의 파일 업로드 완료")

    st.write("### 발견된 확장자")

    st.write(extensions)

# -----------------------------
# 규칙 저장
# -----------------------------

if "rules" not in st.session_state:
    st.session_state.rules = []

# -----------------------------
# 규칙 추가 버튼
# -----------------------------

if st.button("➕ 폴더 추가"):

    st.session_state.rules.append(
        {
            "folder": "",
            "extensions": [],
            "keywords": ""
        }
    )

st.divider()

st.header("분류 규칙")

delete_index = None

for i, rule in enumerate(st.session_state.rules):

    with st.container(border=True):

        col1, col2 = st.columns([8,1])

        with col1:

            rule["folder"] = st.text_input(
                "폴더 이름",
                value=rule["folder"],
                key=f"folder_{i}"
            )

        with col2:

            st.write("")

            st.write("")

            if st.button("❌", key=f"delete{i}"):

                delete_index = i

        rule["extensions"] = st.multiselect(
            "확장자",
            extensions,
            default=rule["extensions"],
            key=f"ext_{i}"
        )

        rule["keywords"] = st.text_area(
            "파일명 포함 문자 (한 줄에 하나)",
            value=rule["keywords"],
            key=f"key_{i}",
            height=100
        )

        if len(rule["extensions"]) == 0 and rule["keywords"].strip() == "":

            st.warning("확장자 또는 포함 문자를 하나 이상 입력하세요.")

if delete_index is not None:

    st.session_state.rules.pop(delete_index)

    st.rerun()

st.divider()

st.subheader("현재 규칙")

st.json(st.session_state.rules)
