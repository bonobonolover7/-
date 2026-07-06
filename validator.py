def validate_rules(rules):

    errors = []

    ext_only = set()
    keyword_only = set()
    combo = set()

    for rule in rules:

        exts = rule["extensions"]

        keywords = [
            x.strip().lower()
            for x in rule["keywords"].splitlines()
            if x.strip()
        ]

        # 조건 없음
        if len(exts) == 0 and len(keywords) == 0:

            errors.append(
                "조건이 없는 규칙이 있습니다."
            )

            continue

        # 확장자만
        if len(exts) > 0 and len(keywords) == 0:

            for e in exts:

                if e in ext_only:

                    errors.append(
                        f"{e} 확장자가 중복되었습니다."
                    )

                ext_only.add(e)

        # 키워드만
        elif len(exts) == 0:

            for k in keywords:

                if k in keyword_only:

                    errors.append(
                        f"{k} 키워드가 중복되었습니다."
                    )

                keyword_only.add(k)

        # 둘 다
        else:

            for e in exts:

                for k in keywords:

                    pair = (e, k)

                    if pair in combo:

                        errors.append(
                            f"{e}+{k} 조합이 중복되었습니다."
                        )

                    combo.add(pair)

    return errors
