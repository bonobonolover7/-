import json


def export_rules(rules):

    return json.dumps(
        rules,
        ensure_ascii=False,
        indent=4
    )


def import_rules(uploaded_file):

    return json.load(uploaded_file)
