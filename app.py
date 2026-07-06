import streamlit as st
from pathlib import Path

# ----------------------------------
# 페이지 설정
# ----------------------------------

st.set_page_config(
    page_title="파일 자동 분류기",
    page_icon="📁",
    layout="wide"
)

st.title("📁 파일 자동 분류기")

st.caption(
    "업로드한 파일을 규칙에 따라 자동으로 폴더별 분류하여 ZIP으로 만들어 줍니다."
)

# ----------------------------------
# Session State
# ----------------------------------

if "rules" not in st.session_state:
    st.session_state.rules = []

# ----------------------------------
# 파일 업로드
# ----------------------------------

st.header("📂 파일 업로드")

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

    total_size = sum(file.size for file in uploaded_files)

    st.success(f"{len(uploaded_files)}개의 파일 업로드")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "파일 개수",
            len(uploaded_files)
        )

    with c2:

        st.metric(
            "총 용량(MB)",
            round(total_size / 1024 / 1024, 2)
        )

    st.write("### 발견된 확장자")

    st.write(", ".join(extensions))

else:

    st.info("파일을 업로드하세요.")

st.divider()

# ----------------------------------
# 규칙
# ----------------------------------

st.header("📋 분류 규칙")

col1, col2 = st.columns([1,6])

with col1:

    if st.button("➕ 규칙 추가"):

        st.session_state.rules.append({

            "folder": "",

            "extensions": [],

            "keywords": [],

            "mode":"OR"

        })

        st.rerun()

with col2:

    st.write(f"현재 규칙 : {len(st.session_state.rules)}개")

delete_index = None

move_up = None

move_down = None

copy_index = None

for i, rule in enumerate(st.session_state.rules):

    with st.expander(
        f"📁 규칙 {i+1}",
        expanded=True
    ):

        rule["folder"] = st.text_input(

            "폴더 이름",

            value=rule["folder"],

            key=f"folder{i}"

        )

        rule["extensions"] = st.multiselect(

            "확장자",

            extensions,

            default=rule["extensions"],

            key=f"ext{i}"

        )

        keyword_text = st.text_area(

            "파일명 포함 문자 (한 줄에 하나)",

            value="\n".join(rule["keywords"]),

            key=f"key{i}",

            height=120

        )

        rule["keywords"] = [

            x.strip()

            for x in keyword_text.splitlines()

            if x.strip()

        ]

        rule["mode"] = st.radio(

            "분류 방식",

            ["OR","AND"],

            horizontal=True,

            key=f"mode{i}"

        )

        c1,c2,c3,c4 = st.columns(4)

        with c1:

            if st.button("⬆",key=f"up{i}"):

                move_up=i

        with c2:

            if st.button("⬇",key=f"down{i}"):

                move_down=i

        with c3:

            if st.button("📄 복제",key=f"copy{i}"):

                copy_index=i

        with c4:

            if st.button("🗑 삭제",key=f"del{i}"):

                delete_index=i

if delete_index is not None:

    st.session_state.rules.pop(delete_index)

    st.rerun()

if copy_index is not None:

    import copy

    st.session_state.rules.insert(

        copy_index+1,

        copy.deepcopy(

            st.session_state.rules[copy_index]

        )

    )

    st.rerun()

if move_up is not None:

    if move_up>0:

        st.session_state.rules[move_up],st.session_state.rules[move_up-1]=(

            st.session_state.rules[move_up-1],

            st.session_state.rules[move_up]

        )

        st.rerun()

if move_down is not None:

    if move_down<len(st.session_state.rules)-1:

        st.session_state.rules[move_down],st.session_state.rules[move_down+1]=(

            st.session_state.rules[move_down+1],

            st.session_state.rules[move_down]

        )

        st.rerun()

st.divider()

# =====================================================

st.header("✅ 규칙 검사")

errors = []

ext_only = {}
keyword_only = {}
combo = {}

for idx, rule in enumerate(st.session_state.rules):

    folder = rule["folder"].strip()

    extensions = rule["extensions"]

    keywords = [k.lower() for k in rule["keywords"]]

    # 폴더 이름 검사
    if folder == "":
        errors.append(f"{idx+1}번째 규칙의 폴더 이름이 비어 있습니다.")

    # 조건 검사
    if len(extensions) == 0 and len(keywords) == 0:
        errors.append(f"{folder or idx+1} : 확장자 또는 키워드를 하나 이상 입력하세요.")
        continue

    # ----------------------------
    # 확장자만 사용하는 규칙
    # ----------------------------
    if extensions and not keywords:

        for ext in extensions:

            if ext in ext_only:

                errors.append(
                    f"'{ext}' 확장자는 '{ext_only[ext]}' 규칙과 중복됩니다."
                )

            else:

                ext_only[ext] = folder

    # ----------------------------
    # 키워드만 사용하는 규칙
    # ----------------------------
    elif keywords and not extensions:

        for key in keywords:

            if key in keyword_only:

                errors.append(
                    f"'{key}' 키워드는 '{keyword_only[key]}' 규칙과 중복됩니다."
                )

            else:

                keyword_only[key] = folder

    # ----------------------------
    # 둘 다 사용하는 규칙
    # ----------------------------
    else:

        for ext in extensions:

            for key in keywords:

                pair = (ext, key)

                if pair in combo:

                    errors.append(
                        f"'{ext}+{key}' 조합이 중복되었습니다."
                    )

                else:

                    combo[pair] = folder

if errors:

    for err in errors:

        st.error(err)

else:

    st.success("규칙에 문제가 없습니다.")

