from io import BytesIO
from pathlib import Path
import zipfile


def _unique_path(path, used_paths):

    if path not in used_paths:
        used_paths.add(path)
        return path

    folder = str(Path(path).parent)
    stem = Path(path).stem
    suffix = Path(path).suffix

    number = 1

    while True:

        new_name = f"{stem} ({number}){suffix}"

        if folder == ".":
            new_path = new_name
        else:
            new_path = f"{folder}/{new_name}"

        if new_path not in used_paths:

            used_paths.add(new_path)

            return new_path

        number += 1


def create_zip(
    uploaded_files,
    rules,
    include_unmatched=True,
    create_empty_folder=True
):

    memory = BytesIO()

    used_paths = set()

    with zipfile.ZipFile(
        memory,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        # -----------------------
        # 빈 폴더 생성
        # -----------------------

        if create_empty_folder:

            for rule in rules:

                folder = rule["folder"].strip()

                if folder:

                    zipf.writestr(folder + "/", b"")

            if include_unmatched:

                zipf.writestr("미분류/", b"")

        # -----------------------
        # 파일 분류
        # -----------------------

        for file in uploaded_files:

            filename = file.name

            extension = Path(filename).suffix.lower().replace(".", "")

            matched = False

            for rule in rules:

                folder = rule["folder"].strip()

                if folder == "":
                    continue

                ext_match = extension in rule["extensions"]

                keyword_match = any(

                    k.lower() in filename.lower()

                    for k in rule["keywords"]

                )
exclude = st.session_state.get(
    "exclude_keywords",
    {}
).get(rule["folder"], [])

exclude_ok = not any(

    k.lower() in filename.lower()

    for k in exclude

)
                if rule["mode"] == "OR":
                    ok = (ext_match or keyword_match) and exclude_ok
                else:
                    ok = (ext_match and keyword_match) and exclude_ok
                if ok:

                    target = f"{folder}/{filename}"

                    target = _unique_path(
                        target,
                        used_paths
                    )

                    zipf.writestr(
                        target,
                        file.getvalue()
                    )

                    matched = True

                    break

            if not matched and include_unmatched:

                target = f"미분류/{filename}"

                target = _unique_path(
                    target,
                    used_paths
                )

                zipf.writestr(
                    target,
                    file.getvalue()
                )

    memory.seek(0)

    return memory
