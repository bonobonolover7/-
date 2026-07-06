from utils import create_extension_rules
from utils import create_ai_rules
import streamlit as st
from pathlib import Path
from copy import deepcopy

st.set_page_config(
    page_title="Smart File Sorter",
    page_icon="📁",
    layout="wide"
)

# ==============================
# Session
# ==============================

if "rules" not in st.session_state:
    st.session_state.rules = []

if "selected_rule" not in st.session_state:
    st.session_state.selected_rule = None

# ==============================
# Title
# ==============================

st.title("📁 Smart File Sorter")

st.caption(
    "파일을 규칙에 따라 자동으로 분류하고 ZIP으로 다운로드합니다."
)

st.divider()

# ==============================
# Upload
# ==============================

uploaded_files = st.file_uploader(
    "파일 업로드",
    accept_multiple_files=True
)

extensions = []

total_size = 0

if uploaded_files:

    extensions = sorted(
        list({
            Path(f.name).suffix.lower().replace(".", "")
            for f in uploaded_files
            if Path(f.name).suffix != ""
        })
    )

    total_size = sum(
        f.size
        for f in uploaded_files
    )

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "파일",
        len(uploaded_files) if uploaded_files else 0
    )

with col2:

    st.metric(
        "확장자",
        len(extensions)
    )

with col3:

    st.metric(
        "용량(MB)",
        round(total_size/1024/1024,2)
    )

if uploaded_files:

    st.write("### 발견된 확장자")

    st.write(", ".join(extensions))

st.divider()

# ==============================
# Layout
# ==============================

left, right = st.columns([1,3])

# ==============================
# LEFT
# ==============================

with left:

    st.subheader("📁 규칙")

    if st.button("➕ 규칙 추가",use_container_width=True):

        st.session_state.rules.append({

            "folder":"새 폴더",

            "extensions":[],

            "keywords":[],

            "mode":"OR"

        })

        st.session_state.selected_rule=len(
            st.session_state.rules
        )-1

        st.rerun()

    st.write("")

    if len(st.session_state.rules)==0:

        st.info("규칙이 없습니다.")

    else:

        for i,rule in enumerate(
            st.session_state.rules
        ):

            count=0

            if uploaded_files:

                for f in uploaded_files:

                    ext=Path(
                        f.name
                    ).suffix.lower().replace(".","")

                    ext_ok=ext in rule["extensions"]

                    key_ok=any(

                        k.lower() in f.name.lower()

                        for k in rule["keywords"]

                    )

                    if rule["mode"]=="OR":

                        ok=ext_ok or key_ok

                    else:

                        ok=ext_ok and key_ok

                    if ok:

                        count+=1

            text=f"📁 {rule['folder']} ({count})"

            if st.button(

                text,

                key=f"select{i}",

                use_container_width=True

            ):

                st.session_state.selected_rule=i

                st.rerun()

# ==============================
# RIGHT
# ==============================

with right:

    st.subheader("규칙 편집")

    if st.session_state.selected_rule is None:

        st.info("왼쪽에서 규칙을 선택하세요.")

    else:

        rule=st.session_state.rules[
            st.session_state.selected_rule
        ]

        rule["folder"]=st.text_input(

            "폴더 이름",

            value=rule["folder"]

        )

        rule["extensions"]=st.multiselect(

            "확장자",

            options=extensions,

            default=rule["extensions"],

            help="업로드된 파일의 확장자만 표시됩니다."

        )

        text="\n".join(rule["keywords"])

        text=st.text_area(

            "파일명 포함 문자",

            value=text,

            height=120

        )

        rule["keywords"]=[

            x.strip()

            for x in text.splitlines()

            if x.strip()

        ]

        rule["mode"]=st.radio(

            "분류 방식",

            ["OR","AND"],

            horizontal=True,

            index=0 if rule["mode"]=="OR" else 1

        )

        a,b,c,d=st.columns(4)

        with a:

            if st.button("⬆",use_container_width=True):

                idx=st.session_state.selected_rule

                if idx>0:

                    st.session_state.rules[idx],st.session_state.rules[idx-1]=(

                        st.session_state.rules[idx-1],

                        st.session_state.rules[idx]

                    )

                    st.session_state.selected_rule-=1

                    st.rerun()

        with b:

            if st.button("⬇", use_container_width=True):

                idx = st.session_state.selected_rule

                if idx < len(st.session_state.rules) - 1:

                    st.session_state.rules[idx], st.session_state.rules[idx+1] = (

                        st.session_state.rules[idx+1],

                        st.session_state.rules[idx]

                    )

                    st.session_state.selected_rule += 1

                    st.rerun()

        with c:

            if st.button("📄 복제", use_container_width=True):

                idx = st.session_state.selected_rule

                st.session_state.rules.insert(

                    idx + 1,

                    deepcopy(st.session_state.rules[idx])

                )

                st.session_state.selected_rule += 1

                st.rerun()

        with d:

            if st.button("🗑 삭제", use_container_width=True):

                idx = st.session_state.selected_rule

                st.session_state.rules.pop(idx)

                if len(st.session_state.rules) == 0:

                    st.session_state.selected_rule = None

                elif idx >= len(st.session_state.rules):

                    st.session_state.selected_rule = len(st.session_state.rules)-1

                st.rerun()

st.divider()

# ======================================================
# 자동 규칙 생성
# ======================================================

st.subheader("✨ 자동 규칙 생성")

col1, col2 = st.columns(2)

with col1:

    if st.button("✨ 확장자 기준 생성", use_container_width=True):

        if uploaded_files:

            st.session_state.rules = create_extension_rules(uploaded_files)

            st.session_state.selected_rule = 0

            st.rerun()

with col2:

    if st.button("🧠 추천 규칙 생성", use_container_width=True):

        if uploaded_files:

            st.session_state.rules = create_ai_rules(uploaded_files)

            st.session_state.selected_rule = 0

            st.rerun()

st.divider()

# ======================================================
# 규칙 검사
# ======================================================

st.subheader("✅ 규칙 검사")

errors = []

ext_only = {}

keyword_only = {}

combo = {}

for rule in st.session_state.rules:

    folder = rule["folder"].strip()

    extensions_rule = rule["extensions"]

    keywords_rule = [

        x.lower()

        for x in rule["keywords"]

    ]

    if folder == "":

        errors.append("폴더 이름이 비어 있습니다.")

    if len(extensions_rule) == 0 and len(keywords_rule) == 0:

        errors.append(

            f"{folder} : 조건이 없습니다."

        )

        continue

    if extensions_rule and not keywords_rule:

        for ext in extensions_rule:

            if ext in ext_only:

                errors.append(

                    f"'{ext}' 확장자가 중복됩니다."

                )

            else:

                ext_only[ext] = folder

    elif keywords_rule and not extensions_rule:

        for key in keywords_rule:

            if key in keyword_only:

                errors.append(

                    f"'{key}' 키워드가 중복됩니다."

                )

            else:

                keyword_only[key] = folder

    else:

        for ext in extensions_rule:

            for key in keywords_rule:

                pair = (ext, key)

                if pair in combo:

                    errors.append(

                        f"{ext} + {key} 조합이 중복됩니다."

                    )

                else:

                    combo[pair] = folder

if errors:

    for err in errors:

        st.error(err)

else:

    st.success("규칙에 문제가 없습니다.")

st.divider()

# ======================================================
# 규칙 테스트
# ======================================================

st.subheader("🧪 규칙 테스트")

test_name = st.text_input(

    "파일 이름 입력",

    placeholder="dog_final.png"

)

if test_name:

    ext = Path(test_name).suffix.lower().replace(".", "")

    matched = False

    for rule in st.session_state.rules:

        ext_ok = ext in rule["extensions"]

        key_ok = any(

            k.lower() in test_name.lower()

            for k in rule["keywords"]

        )

        if rule["mode"] == "OR":

            ok = ext_ok or key_ok

        else:

            ok = ext_ok and key_ok

        if ok:

            st.success(

                f"'{rule['folder']}' 폴더로 분류됩니다."

            )

            matched = True

            break

    if not matched:

        st.warning("미분류됩니다.")

st.divider()

        with b:

            if st.button("⬇", use_container_width=True):

                idx = st.session_state.selected_rule

                if idx < len(st.session_state.rules) - 1:

                    st.session_state.rules[idx], st.session_state.rules[idx+1] = (

                        st.session_state.rules[idx+1],

                        st.session_state.rules[idx]

                    )

                    st.session_state.selected_rule += 1

                    st.rerun()

        with c:

            if st.button("📄 복제", use_container_width=True):

                idx = st.session_state.selected_rule

                st.session_state.rules.insert(

                    idx + 1,

                    deepcopy(st.session_state.rules[idx])

                )

                st.session_state.selected_rule += 1

                st.rerun()

        with d:

            if st.button("🗑 삭제", use_container_width=True):

                idx = st.session_state.selected_rule

                st.session_state.rules.pop(idx)

                if len(st.session_state.rules) == 0:

                    st.session_state.selected_rule = None

                elif idx >= len(st.session_state.rules):

                    st.session_state.selected_rule = len(st.session_state.rules)-1

                st.rerun()

st.divider()

# ======================================================
# 자동 규칙 생성
# ======================================================

st.subheader("✨ 자동 규칙 생성")

col1, col2 = st.columns([1,3])

with col1:

    if st.button("확장자별 생성", use_container_width=True):

        st.session_state.rules = []

        for ext in extensions:

            st.session_state.rules.append({

                "folder": ext.upper(),

                "extensions": [ext],

                "keywords": [],

                "mode": "OR"

            })

        if st.session_state.rules:

            st.session_state.selected_rule = 0

        st.rerun()

with col2:

    st.caption("업로드된 파일의 확장자를 기준으로 규칙을 자동 생성합니다.")

st.divider()

# ======================================================
# 규칙 검사
# ======================================================

st.subheader("✅ 규칙 검사")

errors = []

ext_only = {}

keyword_only = {}

combo = {}

for rule in st.session_state.rules:

    folder = rule["folder"].strip()

    extensions_rule = rule["extensions"]

    keywords_rule = [

        x.lower()

        for x in rule["keywords"]

    ]

    if folder == "":

        errors.append("폴더 이름이 비어 있습니다.")

    if len(extensions_rule) == 0 and len(keywords_rule) == 0:

        errors.append(

            f"{folder} : 조건이 없습니다."

        )

        continue

    if extensions_rule and not keywords_rule:

        for ext in extensions_rule:

            if ext in ext_only:

                errors.append(

                    f"'{ext}' 확장자가 중복됩니다."

                )

            else:

                ext_only[ext] = folder

    elif keywords_rule and not extensions_rule:

        for key in keywords_rule:

            if key in keyword_only:

                errors.append(

                    f"'{key}' 키워드가 중복됩니다."

                )

            else:

                keyword_only[key] = folder

    else:

        for ext in extensions_rule:

            for key in keywords_rule:

                pair = (ext, key)

                if pair in combo:

                    errors.append(

                        f"{ext} + {key} 조합이 중복됩니다."

                    )

                else:

                    combo[pair] = folder

if errors:

    for err in errors:

        st.error(err)

else:

    st.success("규칙에 문제가 없습니다.")

st.divider()

# ======================================================
# 규칙 테스트
# ======================================================

st.subheader("🧪 규칙 테스트")

test_name = st.text_input(

    "파일 이름 입력",

    placeholder="dog_final.png"

)

if test_name:

    ext = Path(test_name).suffix.lower().replace(".", "")

    matched = False

    for rule in st.session_state.rules:

        ext_ok = ext in rule["extensions"]

        key_ok = any(

            k.lower() in test_name.lower()

            for k in rule["keywords"]

        )

        if rule["mode"] == "OR":

            ok = ext_ok or key_ok

        else:

            ok = ext_ok and key_ok

        if ok:

            st.success(

                f"'{rule['folder']}' 폴더로 분류됩니다."

            )

            matched = True

            break

    if not matched:

        st.warning("미분류됩니다.")

st.divider()

uploaded_files, extensions = upload_section()
