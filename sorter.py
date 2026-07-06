from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def _match_rule(filename, ext, rule, exclude_keywords):

    ext_ok = ext in rule["extensions"]

    key_ok = any(
        k.lower() in filename.lower()
        for k in rule["keywords"]
    )

    exclude = exclude_keywords.get(
        rule["folder"],
        []
    )

    exclude_ok = not any(
        k.lower() in filename.lower()
        for k in exclude
    )

    if rule["mode"] == "OR":
        return (ext_ok or key_ok) and exclude_ok

    return (ext_ok and key_ok) and exclude_ok


def _unique_name(path, used):

    if path not in used:

        used.add(path)

        return path

    p = Path(path)

    stem = p.stem

    suffix = p.suffix

    number = 1

    while True:

        new = str(

            p.with_name(

                f"{stem} ({number}){suffix}"

            )

        )

        if new not in used:

            used.add(new)

            return new

        number += 1


def create_zip(

    uploaded_files,

    rules,

    include_unmatched=True,

    create_empty_folder=True,

    priority=None,

    exclude_keywords=None

):

    if priority is None:

        priority = {}

    if exclude_keywords is None:

        exclude_keywords = {}

    # -------------------------

    ordered = sorted(

        rules,

        key=lambda r: priority.get(

            r["folder"],

            50

        ),

        reverse=True

    )

    memory = BytesIO()

    used_paths = set()

    stats = {}

    log = []

    with ZipFile(

        memory,

        "w",

        ZIP_DEFLATED

    ) as zipf:

        # 빈 폴더

        if create_empty_folder:

            for rule in ordered:

                folder = rule["folder"] + "/"

                zipf.writestr(folder, "")

                stats[rule["folder"]] = 0

        unmatched = 0

        for file in uploaded_files:

            filename = file.name

            ext = Path(filename).suffix.lower().replace(".", "")

            target = None

            for rule in ordered:

                if _match_rule(

                    filename,

                    ext,

                    rule,

                    exclude_keywords

                ):

                    target = rule["folder"]

                    break

            if target is None:

                if include_unmatched:

                    target = "미분류"

                else:

                    log.append(

                        f"SKIP : {filename}"

                    )

                    continue

            zip_path = _unique_name(

                f"{target}/{filename}",

                used_paths

            )

            zipf.writestr(

                zip_path,

                file.getvalue()

            )

            if target == "미분류":

                unmatched += 1

            else:

                stats[target] = stats.get(

                    target,

                    0

                ) + 1

            log.append(

                f"{filename} -> {target}"

            )

    memory.seek(0)

    return {

        "zip": memory,

        "stats": stats,

        "unmatched": unmatched,

        "log": log

    }
