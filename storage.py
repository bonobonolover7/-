from pathlib import Path

INVALID_FOLDER_CHARS = set('<>:"/\\|?*')

WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4",
    "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4",
    "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}


def validate_rules(rules):

    errors = []

    folder_names = set()

    extension_only = {}

    keyword_only = {}

    combination = {}

    for index, rule in enumerate(rules):

        folder = rule["folder"].strip()

        extensions = list(
            dict.fromkeys(
                [x.lower() for x in rule["extensions"]]
            )
        )

        keywords = list(
            dict.fromkeys(
                [x.lower().strip() for x in rule["keywords"]]
            )
        )

        rule["extensions"] = extensions
        rule["keywords"] = keywords

        # -----------------------------
        # 폴더 이름
        # -----------------------------

        if folder == "":

            errors.append(
                f"{index+1}번째 규칙 : 폴더 이름이 비어 있습니다."
            )

            continue

        if folder.upper() in WINDOWS_RESERVED_NAMES:

            errors.append(
                f"{folder} : Windows 예약어입니다."
            )

        for c in folder:

            if c in INVALID_FOLDER_CHARS:

                errors.append(
                    f"{folder} : 사용할 수 없는 문자가 있습니다."
                )

                break

        if folder in folder_names:

            errors.append(
                f"{folder} : 같은 폴더 이름이 존재합니다."
            )

        folder_names.add(folder)

        # -----------------------------
        # 조건
        # -----------------------------

        if len(extensions) == 0 and len(keywords) == 0:

            errors.append(
                f"{folder} : 조건이 없습니다."
            )

            continue

        # -----------------------------
        # 확장자만
        # -----------------------------

        if extensions and not keywords:

            for ext in extensions:

                if ext in extension_only:

                    errors.append(

                        f"{ext} 확장자는 "

                        f"{extension_only[ext]} 와 중복됩니다."

                    )

                else:

                    extension_only[ext] = folder

        # -----------------------------
        # 키워드만
        # -----------------------------

        elif keywords and not extensions:

            for key in keywords:

                if key in keyword_only:

                    errors.append(

                        f"{key} 키워드는 "

                        f"{keyword_only[key]} 와 중복됩니다."

                    )

                else:

                    keyword_only[key] = folder

        # -----------------------------
        # 둘 다
        # -----------------------------

        else:

            for ext in extensions:

                for key in keywords:

                    pair = (ext, key)

                    if pair in combination:

                        errors.append(

                            f"{ext} + {key} 조합이 "

                            f"{combination[pair]} 와 중복됩니다."

                        )

                    else:

                        combination[pair] = folder

    return errors


def validate_filename(filename, rules):

    ext = Path(filename).suffix.lower().replace(".", "")

    matched = []

    for rule in rules:

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

            matched.append(rule["folder"])

    return matched
