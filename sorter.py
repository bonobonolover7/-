from io import BytesIO
from pathlib import Path
import zipfile


def create_zip(uploaded_files, rules, include_unmatched=True):

    memory = BytesIO()

    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as zipf:

        for file in uploaded_files:

            filename = file.name

            extension = Path(filename).suffix.lower().replace(".", "")

            moved = False

            for rule in rules:

                folder = rule["folder"].strip()

                if folder == "":
                    continue

                ext_match = extension in rule["extensions"]

                keyword_match = any(
                    k.lower() in filename.lower()
                    for k in rule["keywords"]
                )

                if rule["mode"] == "OR":

                    ok = ext_match or keyword_match

                else:

                    ok = ext_match and keyword_match

                if ok:

                    zipf.writestr(
                        f"{folder}/{filename}",
                        file.getvalue()
                    )

                    moved = True

                    break

            if not moved and include_unmatched:

                zipf.writestr(
                    f"미분류/{filename}",
                    file.getvalue()
                )

    memory.seek(0)

    return memory
