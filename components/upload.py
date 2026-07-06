import streamlit as st
from pathlib import Path

from core.utils import (
    create_extension_rules,
    create_ai_rules
)


def upload_section():

    st.header("📂 파일 업로드")

    uploaded_files = st.file_uploader(

        "파일을 드래그하거나 선택하세요.",

        accept_multiple_files=True,

        label_visibility="collapsed"

    )

    extensions = []

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

                len(uploaded_files)

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

        st.write("### 발견된 확장자")

        st.write(", ".join(extensions))

        st.divider()

        st.subheader("⚡ 자동 규칙 생성")

        left, right = st.columns(2)

        with left:

            if st.button(

                "✨ 확장자 기준",

                use_container_width=True

            ):

                st.session_state.rules = create_extension_rules(

                    uploaded_files

                )

                st.session_state.selected_rule = 0

                st.rerun()

        with right:

            if st.button(

                "🧠 추천 규칙",

                use_container_width=True

            ):

                st.session_state.rules = create_ai_rules(

                    uploaded_files

                )

                st.session_state.selected_rule = 0

                st.rerun()

        st.divider()

        st.subheader("🔍 파일 검색")

        keyword = st.text_input(

            "파일 이름 검색"

        )

        if keyword:

            result = [

                f

                for f in uploaded_files

                if keyword.lower() in f.name.lower()

            ]

            st.write(

                f"검색 결과 : {len(result)}개"

            )

            for file in result:

                st.write(

                    "📄",

                    file.name

                )

    else:

        st.info(

            "파일을 업로드해주세요."

        )

    return uploaded_files, extensions
