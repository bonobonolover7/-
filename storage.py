import json


# =====================================================
# 규칙(JSON) 저장
# =====================================================

def export_rules(rules):

    return json.dumps(
        rules,
        indent=4,
        ensure_ascii=False
    )


# =====================================================
# 규칙(JSON) 불러오기
# =====================================================

def import_rules(file):

    if hasattr(file, "read"):

        data = json.loads(
            file.read().decode("utf-8")
        )

    else:

        data = json.loads(file)

    if not isinstance(data, list):

        raise ValueError("올바른 rules.json이 아닙니다.")

    return data


# =====================================================
# 프로젝트(.sfs) 저장
# =====================================================

def export_project(

    rules,

    zip_name,

    include_unmatched,

    create_empty_folder

):

    project = {

        "version": "1.0",

        "rules": rules,

        "settings": {

            "zip_name": zip_name,

            "include_unmatched": include_unmatched,

            "create_empty_folder": create_empty_folder

        }

    }

    return json.dumps(

        project,

        indent=4,

        ensure_ascii=False

    )


# =====================================================
# 프로젝트(.sfs) 불러오기
# =====================================================

def import_project(file):

    if hasattr(file, "read"):

        project = json.loads(

            file.read().decode("utf-8")

        )

    else:

        project = json.loads(file)

    if not isinstance(project, dict):

        raise ValueError("프로젝트 파일이 아닙니다.")

    if "rules" not in project:

        raise ValueError("rules 정보가 없습니다.")

    if "settings" not in project:

        project["settings"] = {}

    return {

        "rules": project["rules"],

        "zip_name": project["settings"].get(

            "zip_name",

            "분류결과"

        ),

        "include_unmatched": project["settings"].get(

            "include_unmatched",

            True

        ),

        "create_empty_folder": project["settings"].get(

            "create_empty_folder",

            True

        )

    }
