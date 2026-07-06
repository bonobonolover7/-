import json
from copy import deepcopy
from pathlib import Path

import streamlit as st

from sorter import create_zip
from validator import validate_rules, validate_filename
from storage import (
    export_rules,
    import_rules,
    export_project,
    import_project
)
from utils import (
    create_extension_rules,
    create_ai_rules
)

# =====================================================
# 페이지 설정
# =====================================================

st.set_page_config(
    page_title="Smart File Sorter",
    page_icon="📁",
    layout="wide"
)

# =====================================================
# SessionState 초기화
# =====================================================

DEFAULTS = {
    "rules": [],
    "selected_rule": None,
    "exclude_keywords": {},
    "rule_style": {},
    "priority": {}
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = deepcopy(value)

# =====================================================
# 제목
# =====================================================

st.title("📁 Smart File Sorter")

st.caption(
    "규칙을 만들어 파일을 자동으로 분류하고 ZIP으로 다운로드합니다."
)

st.divider()

# =====================================================
# 파일 업로드
# =====================================================

uploaded_files = st.file_uploader(
    "파일 업로드",
    accept_multiple_files=True
)

extensions = []

total_size = 0

if uploaded_files:

    extensions = sorted({

        Path(f.name).suffix.lower().replace(".", "")

        for f in uploaded_files

        if Path(f.name).suffix

    })

    total_size = sum(
        f.size
        for f in uploaded_files
    )

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "파일",
        len(uploaded_files) if uploaded_files else 0
    )

with c2:

    st.metric(
        "확장자",
        len(extensions)
    )

with c3:

    st.metric(
        "용량(MB)",
        round(total_size / 1024 / 1024, 2)
    )

if uploaded_files:

    st.write("### 발견된 확장자")

    st.write(", ".join(extensions))

st.divider()

# =====================================================
# 자동 규칙 생성
# =====================================================

st.subheader("✨ 자동 규칙 생성")

left_auto, right_auto = st.columns(2)

with left_auto:

    if st.button(
        "✨ 확장자 기준 생성",
        use_container_width=True
    ):

        if uploaded_files:

            st.session_state.rules = create_extension_rules(
                uploaded_files
            )

            st.session_state.selected_rule = 0

            st.rerun()

with right_auto:

    if st.button(
        "🧠 추천 규칙 생성",
        use_container_width=True
    ):

        if uploaded_files:

            st.session_state.rules = create_ai_rules(
                uploaded_files
            )

            st.session_state.selected_rule = 0

            st.rerun()

st.divider()

# =====================================================
# 메인 레이아웃
# =====================================================

left, right = st.columns([1, 3])

# =====================================================
# 왼쪽
# =====================================================

with left:

    st.subheader("📁 규칙")

    if st.button(
        "➕ 규칙 추가",
        use_container_width=True
    ):

        st.session_state.rules.append({

            "folder": "새 폴더",

            "extensions": [],

            "keywords": [],

            "mode": "OR"

        })

        st.session_state.selected_rule = len(
            st.session_state.rules
        ) - 1

        st.rerun()

    st.write("")

    if not st.session_state.rules:

        st.info("규칙이 없습니다.")

    else:

        search = st.text_input(
            "🔍 규칙 검색"
        )

        for i, rule in enumerate(
            st.session_state.rules
        ):

            if search:

                if search.lower() not in rule["folder"].lower():
                    continue

            count = 0

            if uploaded_files:

                for file in uploaded_files:

                    ext = Path(file.name).suffix.lower().replace(".", "")

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
                        count += 1

            label = f"📁 {rule['folder']} ({count})"

            if st.button(
                label,
                key=f"rule_{i}",
                use_container_width=True
            ):

                st.session_state.selected_rule = i

                st.rerun()

# =====================================================
# 오른쪽
# =====================================================

with right:

    st.subheader("⚙️ 규칙 편집")

    if st.session_state.selected_rule is None:

        st.info("왼쪽에서 규칙을 선택하세요.")

    else:

        rule = st.session_state.rules[
            st.session_state.selected_rule
        ]

        # -------------------------
        # 폴더 이름
        # -------------------------

        rule["folder"] = st.text_input(

            "📁 폴더 이름",

            value=rule["folder"]

        )

        # -------------------------
        # 확장자
        # -------------------------

        rule["extensions"] = st.multiselect(

            "확장자",

            options=extensions,

            default=rule["extensions"]

        )

        # -------------------------
        # 포함 키워드
        # -------------------------

        keyword_text = "\n".join(

            rule["keywords"]

        )

        keyword_text = st.text_area(

            "파일명 포함 키워드",

            value=keyword_text,

            height=120

        )

        rule["keywords"] = [

            x.strip()

            for x in keyword_text.splitlines()

            if x.strip()

        ]

        # -------------------------
        # 제외 키워드
        # -------------------------

        exclude = "\n".join(

            st.session_state.exclude_keywords.get(

                rule["folder"],

                []

            )

        )

        exclude = st.text_area(

            "제외 키워드",

            value=exclude,

            height=100

        )

        st.session_state.exclude_keywords[

            rule["folder"]

        ] = [

            x.strip()

            for x in exclude.splitlines()

            if x.strip()

        ]

        # -------------------------
        # 분류 방식
        # -------------------------

        rule["mode"] = st.radio(

            "분류 방식",

            ["OR", "AND"],

            horizontal=True,

            index=0 if rule["mode"] == "OR" else 1

        )

        # -------------------------
        # 우선순위
        # -------------------------

        st.session_state.priority[

            rule["folder"]

        ] = st.slider(

            "우선순위",

            1,

            100,

            value=st.session_state.priority.get(

                rule["folder"],

                50

            )

        )

        st.divider()

        # -------------------------
        # 버튼
        # -------------------------

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            if st.button(

                "⬆",

                use_container_width=True

            ):

                idx = st.session_state.selected_rule

                if idx > 0:

                    st.session_state.rules[idx], st.session_state.rules[idx-1] = (

                        st.session_state.rules[idx-1],

                        st.session_state.rules[idx]

                    )

                    st.session_state.selected_rule -= 1

                    st.rerun()

        with c2:

            if st.button(

                "⬇",

                use_container_width=True

            ):

                idx = st.session_state.selected_rule

                if idx < len(st.session_state.rules)-1:

                    st.session_state.rules[idx], st.session_state.rules[idx+1] = (

                        st.session_state.rules[idx+1],

                        st.session_state.rules[idx]

                    )

                    st.session_state.selected_rule += 1

                    st.rerun()

        with c3:

            if st.button(

                "📄 복제",

                use_container_width=True

            ):

                idx = st.session_state.selected_rule

                st.session_state.rules.insert(

                    idx+1,

                    deepcopy(

                        st.session_state.rules[idx]

                    )

                )

                st.session_state.selected_rule += 1

                st.rerun()

        with c4:

            if st.button(

                "🗑 삭제",

                use_container_width=True

            ):

                idx = st.session_state.selected_rule

                st.session_state.rules.pop(idx)

                if len(st.session_state.rules):

                    st.session_state.selected_rule = min(

                        idx,

                        len(st.session_state.rules)-1

                    )

                else:

                    st.session_state.selected_rule = None

                st.rerun()

st.divider()

# =====================================================
# 규칙 검사
# =====================================================

st.subheader("✅ 규칙 검사")

errors = validate_rules(

    st.session_state.rules

)

if errors:

    for err in errors:

        st.error(err)

else:

    st.success(

        "규칙에 문제가 없습니다."

    )

st.divider()

# =====================================================
# 규칙 테스트
# =====================================================

st.subheader("🧪 규칙 테스트")

test_name = st.text_input(

    "파일 이름 입력",

    placeholder="dog_final.png"

)

if test_name:

    result = validate_filename(

        test_name,

        st.session_state.rules

    )

    if result:

        st.success(

            " → ".join(result)

        )

    else:

        st.warning(

            "미분류"

        )

# =====================================================
# 실시간 분류 미리보기
# =====================================================

st.divider()

st.subheader("👀 분류 미리보기")

if uploaded_files:

    preview = {}

    for rule in st.session_state.rules:

        preview[rule["folder"]] = []

    preview["미분류"] = []

    for file in uploaded_files:

        filename = file.name

        ext = Path(filename).suffix.lower().replace(".", "")

        assigned = False

        for rule in st.session_state.rules:

            ext_ok = ext in rule["extensions"]

            key_ok = any(

                k.lower() in filename.lower()

                for k in rule["keywords"]

            )

            exclude = st.session_state.exclude_keywords.get(

                rule["folder"],

                []

            )

            exclude_ok = not any(

                k.lower() in filename.lower()

                for k in exclude

            )

            if rule["mode"] == "OR":

                ok = (ext_ok or key_ok) and exclude_ok

            else:

                ok = (ext_ok and key_ok) and exclude_ok

            if ok:

                preview[rule["folder"]].append(filename)

                assigned = True

                break

        if not assigned:

            preview["미분류"].append(filename)

    for folder, files in preview.items():

        with st.expander(f"📁 {folder} ({len(files)})"):

            if files:

                for name in files:

                    st.write("📄", name)

            else:

                st.caption("파일 없음")

else:

    st.info("파일을 업로드하면 미리보기가 표시됩니다.")

st.divider()

# =====================================================
# 통계
# =====================================================

st.subheader("📊 통계")

if uploaded_files:

    col1, col2 = st.columns(2)

    folder_counts = {}

    ext_counts = {}

    for rule in st.session_state.rules:

        folder_counts[rule["folder"]] = 0

    folder_counts["미분류"] = 0

    for file in uploaded_files:

        ext = Path(file.name).suffix.lower().replace(".", "")

        ext_counts[ext] = ext_counts.get(ext, 0) + 1

        matched = False

        for rule in st.session_state.rules:

            ext_ok = ext in rule["extensions"]

            key_ok = any(

                k.lower() in file.name.lower()

                for k in rule["keywords"]

            )

            exclude = st.session_state.exclude_keywords.get(

                rule["folder"],

                []

            )

            exclude_ok = not any(

                k.lower() in file.name.lower()

                for k in exclude

            )

            if rule["mode"] == "OR":

                ok = (ext_ok or key_ok) and exclude_ok

            else:

                ok = (ext_ok and key_ok) and exclude_ok

            if ok:

                folder_counts[rule["folder"]] += 1

                matched = True

                break

        if not matched:

            folder_counts["미분류"] += 1

    with col1:

        st.write("### 📁 폴더별")

        for folder, count in folder_counts.items():

            st.write(f"**{folder}** : {count}")

    with col2:

        st.write("### 📄 확장자별")

        for ext, count in sorted(ext_counts.items()):

            st.write(f".{ext} : {count}")

st.divider()

# =====================================================
# 전체 파일 검색
# =====================================================

st.subheader("🔍 파일 검색")

search = st.text_input(

    "파일명 검색",

    key="search_all"

)

if uploaded_files:

    for file in uploaded_files:

        if search:

            if search.lower() not in file.name.lower():

                continue

        st.write("📄", file.name)

# =====================================================
# 저장 / 불러오기
# =====================================================

st.divider()

st.subheader("💾 저장 / 불러오기")

left_save, right_save = st.columns(2)

# -------------------------------
# 왼쪽
# -------------------------------

with left_save:

    st.write("### 규칙(JSON)")

    json_text = export_rules(
        st.session_state.rules
    )

    st.download_button(

        "📥 rules.json 다운로드",

        data=json_text,

        file_name="rules.json",

        mime="application/json",

        use_container_width=True

    )

    rule_file = st.file_uploader(

        "rules.json 불러오기",

        type=["json"],

        key="rule_json"

    )

    if rule_file is not None:

        try:

            st.session_state.rules = import_rules(
                rule_file
            )

            if st.session_state.rules:

                st.session_state.selected_rule = 0

            st.success("불러왔습니다.")

            st.rerun()

        except Exception as e:

            st.error(str(e))

# -------------------------------
# 오른쪽
# -------------------------------

with right_save:

    st.write("### 프로젝트(.sfs)")

    zip_name = st.text_input(

        "ZIP 파일 이름",

        value="분류결과"

    )

    include_unmatched = st.checkbox(

        "미분류 포함",

        value=True

    )

    create_empty_folder = st.checkbox(

        "빈 폴더 생성",

        value=True

    )

    project = export_project(

        st.session_state.rules,

        zip_name,

        include_unmatched,

        create_empty_folder

    )

    st.download_button(

        "📦 프로젝트 저장",

        data=project,

        file_name="project.sfs",

        mime="application/octet-stream",

        use_container_width=True

    )

    project_file = st.file_uploader(

        "프로젝트 열기",

        type=["sfs"],

        key="project_open"

    )

    if project_file is not None:

        try:

            data = import_project(
                project_file
            )

            st.session_state.rules = data["rules"]

            if st.session_state.rules:

                st.session_state.selected_rule = 0

            st.success("프로젝트를 불러왔습니다.")

            st.rerun()

        except Exception as e:

            st.error(str(e))

st.divider()

# =====================================================
# ZIP 생성
# =====================================================

st.subheader("📦 ZIP 생성")

if uploaded_files:

    errors = validate_rules(
        st.session_state.rules
    )

    if errors:

        st.warning(
            "규칙 오류를 먼저 수정하세요."
        )

    else:

        if st.button("📦 ZIP 만들기", use_container_width=True):

            try:

                result = create_zip(
                    uploaded_files,
                    st.session_state.rules,
                    include_unmatched=include_unmatched,
                    create_empty_folder=create_empty_folder,
                    priority=st.session_state.priority,
                    exclude_keywords=st.session_state.exclude_keywords
                )

                st.download_button(
                    "⬇ ZIP 다운로드",
                    data=result["zip"],
                    file_name=f"{zip_name}.zip",
                    mime="application/zip",
                    use_container_width=True
                )

            except Exception as e:

                st.error(str(e))

else:

    st.info("파일을 업로드하세요.")
# =====================================================
# 규칙 복사 / 붙여넣기
# =====================================================

st.divider()

st.subheader("📋 규칙 관리")

if "rule_clipboard" not in st.session_state:
    st.session_state.rule_clipboard = None

col1, col2 = st.columns(2)

with col1:

    if (
        st.session_state.selected_rule is not None
        and st.button("📄 선택한 규칙 복사", use_container_width=True)
    ):

        st.session_state.rule_clipboard = deepcopy(
            st.session_state.rules[
                st.session_state.selected_rule
            ]
        )

        st.success("복사되었습니다.")

with col2:

    if st.button("📥 붙여넣기", use_container_width=True):

        if st.session_state.rule_clipboard is None:

            st.warning("복사된 규칙이 없습니다.")

        else:

            new_rule = deepcopy(
                st.session_state.rule_clipboard
            )

            new_rule["folder"] += "_copy"

            st.session_state.rules.append(new_rule)

            st.session_state.selected_rule = (
                len(st.session_state.rules) - 1
            )

            st.success("붙여넣기 완료")

            st.rerun()

# =====================================================
# 프로젝트 정보
# =====================================================

st.divider()

st.subheader("📈 프로젝트 정보")

if uploaded_files:

    total_files = len(uploaded_files)

    matched = 0

    for file in uploaded_files:

        if validate_filename(
            file.name,
            st.session_state.rules
        ):

            matched += 1

    percent = 0

    if total_files:

        percent = matched / total_files

    st.progress(percent)

    st.write(
        f"분류 완료 : {matched} / {total_files}"
    )

    st.write(
        f"미분류 : {total_files - matched}"
    )

else:

    st.info("파일을 업로드하면 진행률이 표시됩니다.")

# =====================================================
# 최종 검사
# =====================================================

st.divider()

st.subheader("🔎 최종 검사")

errors = validate_rules(
    st.session_state.rules
)

if errors:

    st.error("프로젝트에 오류가 있습니다.")

    for e in errors:

        st.write("•", e)

else:

    st.success("모든 규칙이 정상입니다.")

# =====================================================
# 정보
# =====================================================

st.divider()

with st.expander("ℹ 프로그램 정보"):

    st.write("Smart File Sorter")

    st.write("Version 1.0")

    st.write("기능")

    st.write("- 파일 자동 분류")

    st.write("- 확장자 조건")

    st.write("- 파일명 키워드")

    st.write("- 제외 키워드")

    st.write("- OR / AND 조건")

    st.write("- 프로젝트 저장")

    st.write("- ZIP 생성")

# =====================================================
# Footer
# =====================================================

st.divider()

st.caption("Made with ❤️ using Streamlit")
