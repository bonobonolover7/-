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

# ======================================================
# 통계
# ======================================================

st.divider()

st.subheader("📊 통계")

if uploaded_files:

    folder_counts = {}

    extension_counts = {}

    unmatched = 0

    for rule in st.session_state.rules:
        folder_counts[rule["folder"]] = 0

    for file in uploaded_files:

        filename = file.name

        ext = Path(filename).suffix.lower().replace(".", "")

        extension_counts[ext] = extension_counts.get(ext, 0) + 1

        found = False

        for rule in st.session_state.rules:

            ext_ok = ext in rule["extensions"]

            key_ok = any(

                k.lower() in filename.lower()

                for k in rule["keywords"]

            )

            if rule["mode"] == "OR":
                ok = ext_ok or key_ok
            else:
                ok = ext_ok and key_ok

            if ok:

                folder_counts[rule["folder"]] += 1

                found = True

                break

        if not found:

            unmatched += 1

    c1, c2 = st.columns(2)

    with c1:

        st.write("### 📁 폴더별 파일 수")

        for folder, count in folder_counts.items():

            st.write(f"**{folder}** : {count}개")

        st.write(f"**미분류** : {unmatched}개")

    with c2:

        st.write("### 📄 확장자 통계")

        for ext, count in sorted(extension_counts.items()):

            st.write(f".{ext} : {count}개")

st.divider()

# ======================================================
# 전체 파일 검색
# ======================================================

st.subheader("🔍 전체 파일 검색")

search = st.text_input(
    "검색어 입력",
    key="global_search"
)

if uploaded_files:

    files = uploaded_files

    if search:

        files = [

            f

            for f in uploaded_files

            if search.lower() in f.name.lower()

        ]

    st.write(f"검색 결과 : {len(files)}개")

    for file in files:

        ext = Path(file.name).suffix.lower().replace(".", "")

        folder = "미분류"

        for rule in st.session_state.rules:

            ext_ok = ext in rule["extensions"]

            key_ok = any(

                k.lower() in file.name.lower()

                for k in rule["keywords"]

            )

            if rule["mode"] == "OR":
                ok = ext_ok or key_ok
            else:
                ok = ext_ok and key_ok

            if ok:

                folder = rule["folder"]

                break

        st.write(f"📄 {file.name} → **{folder}**")

# ======================================================
# 규칙 꾸미기
# ======================================================

st.divider()

st.subheader("🎨 규칙 꾸미기")

ICONS = [
    "📁","🖼️","🎬","🎵","📄",
    "📦","⭐","🎨","💼","🧩",
    "📚","📝","🛠️","💻","📷"
]

COLORS = [
    "🔴","🟠","🟡","🟢",
    "🔵","🟣","⚫","⚪","🟤"
]

if "rule_style" not in st.session_state:
    st.session_state.rule_style = {}

if st.session_state.rules:

    names = [
        r["folder"]
        for r in st.session_state.rules
    ]

    selected = st.selectbox(
        "꾸밀 규칙",
        names
    )

    idx = names.index(selected)

    style = st.session_state.rule_style.get(

        selected,

        {
            "icon":"📁",
            "color":"🔵",
            "favorite":False
        }

    )

    c1,c2,c3 = st.columns(3)

    with c1:

        style["icon"] = st.selectbox(

            "아이콘",

            ICONS,

            index=ICONS.index(style["icon"])

        )

    with c2:

        style["color"] = st.selectbox(

            "색상",

            COLORS,

            index=COLORS.index(style["color"])

        )

    with c3:

        style["favorite"] = st.checkbox(

            "즐겨찾기",

            value=style["favorite"]

        )

    st.session_state.rule_style[selected]=style

st.divider()

st.subheader("📋 규칙 목록")

if st.session_state.rules:

    display=[]

    for rule in st.session_state.rules:

        style=st.session_state.rule_style.get(

            rule["folder"],

            {

                "icon":"📁",

                "color":"🔵",

                "favorite":False

            }

        )

        display.append(

            (

                style["favorite"],

                style["icon"],

                style["color"],

                rule

            )

        )

    display.sort(

        key=lambda x:(not x[0],x[3]["folder"])

    )

    for fav,icon,color,rule in display:

        st.info(

            f"{color} {icon} **{rule['folder']}**"

        )

# ======================================================
# 고급 규칙 설정
# ======================================================

st.divider()

st.subheader("⚙️ 고급 규칙")

if "exclude_keywords" not in st.session_state:
    st.session_state.exclude_keywords = {}

if "priority" not in st.session_state:
    st.session_state.priority = {}

if st.session_state.rules:

    names = [
        r["folder"]
        for r in st.session_state.rules
    ]

    folder = st.selectbox(
        "규칙 선택",
        names,
        key="advanced_rule"
    )

    rule = next(
        r
        for r in st.session_state.rules
        if r["folder"] == folder
    )

    st.write("### 🚫 제외 키워드")

    exclude = "\n".join(

        st.session_state.exclude_keywords.get(
            folder,
            []
        )

    )

    exclude = st.text_area(

        "파일명에 포함되면 제외",

        value=exclude,

        key=f"exclude_{folder}"

    )

    st.session_state.exclude_keywords[folder] = [

        x.strip()

        for x in exclude.splitlines()

        if x.strip()

    ]

    st.write("### ⭐ 우선순위")

    st.session_state.priority[folder] = st.slider(

        "숫자가 클수록 먼저 검사",

        1,

        100,

        value=st.session_state.priority.get(
            folder,
            50
        ),

        key=f"priority_{folder}"

    )

st.divider()

# ======================================================
# 규칙 충돌 검사
# ======================================================

st.subheader("🚨 충돌 검사")

conflicts = []

for i in range(len(st.session_state.rules)):

    r1 = st.session_state.rules[i]

    for j in range(i+1, len(st.session_state.rules)):

        r2 = st.session_state.rules[j]

        ext_overlap = set(r1["extensions"]) & set(r2["extensions"])

        key_overlap = set(

            map(str.lower, r1["keywords"])

        ) & set(

            map(str.lower, r2["keywords"])

        )

        if ext_overlap and not r1["keywords"] and not r2["keywords"]:

            conflicts.append(

                f"{r1['folder']} ↔ {r2['folder']} : 확장자 {', '.join(ext_overlap)}"

            )

        if key_overlap and not r1["extensions"] and not r2["extensions"]:

            conflicts.append(

                f"{r1['folder']} ↔ {r2['folder']} : 키워드 {', '.join(key_overlap)}"

            )

if conflicts:

    for c in conflicts:

        st.error(c)

else:

    st.success("충돌 없음 ✅")

