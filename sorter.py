from pathlib import Path
from io import BytesIO
import zipfile


def match_rule(filename, extension, rule):
    """
    규칙과 파일이 일치하는지 확인
    """

    ext_match = False
    keyword_match = False

    if rule["extensions"]:
        ext_match = extension in rule["extensions"]

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

    if rule["extensions"] and rule["keywords"].strip():
        return ext_match or keyword_match

    return ext_match or keyword_match


def create_zip(uploaded_files, rules):

    memory_file = BytesIO()

    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:

        for file in uploaded_files:

            filename = file.name

            extension = Path(filename).suffix.lower().replace(".", "")

            matched = False

            for rule in rules:

                if match_rule(filename, extension, rule):

                    folder = rule["folder"].strip()

                    if folder == "":
                        folder = "Unnamed"

                    zf.writestr(
                        f"{folder}/{filename}",
                        file.getvalue()
                    )

                    matched = True
                    break

            if not matched:

                zf.writestr(
                    f"미분류/{filename}",
                    file.getvalue()
                )

    memory_file.seek(0)

    return memory_file
