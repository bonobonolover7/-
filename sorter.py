from pathlib import Path
from io import BytesIO
import zipfile


def create_zip(uploaded_files, rules):

    memory_file = BytesIO()

    with zipfile.ZipFile(
        memory_file,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for file in uploaded_files:

            filename = file.name

            extension = Path(filename).suffix.lower().replace(".", "")

            moved = False

            for rule in rules:

                folder = rule["folder"].strip()

                if folder == "":
                    folder = "이름없는폴더"

                ext_match = False
                keyword_match = False

                # 확장자 검사
                if len(rule["extensions"]) > 0:

                    ext_match = extension in rule["extensions"]

                # 키워드 검사
                if rule["keywords"].strip():

                    keywords = [
                        k.strip().lower()
                        for k in rule["keywords"].splitlines()
                        if k.strip()
                    ]

                    keyword_match = any(
                        k in filename.lower()
                        for k in keywords
                    )

                # 둘 중 하나만 만족해도 이동
                if ext_match or keyword_match:

                    zipf.writestr(
                        f"{folder}/{filename}",
                        file.getvalue()
                    )

                    moved = True

                    break

            if not moved:

                zipf.writestr(

                    f"미분류/{filename}",

                    file.getvalue()

                )

    memory_file.seek(0)

    return memory_file
