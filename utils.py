from pathlib import Path
from collections import Counter
import re

# 기본 확장자 그룹
EXTENSION_GROUPS = {
    "사진": [
        "png", "jpg", "jpeg", "gif", "bmp",
        "webp", "tif", "tiff", "heic", "raw"
    ],
    "영상": [
        "mp4", "mov", "avi", "mkv", "wmv",
        "flv", "webm", "m4v"
    ],
    "PSD": ["psd"],
    "PDN": ["pdn"],
    "After Effects": ["aep"],
    "Premiere": ["prproj"],
    "Illustrator": ["ai"],
    "Photoshop": ["psb"],
    "PDF": ["pdf"],
    "압축파일": [
        "zip", "rar", "7z", "tar", "gz"
    ]
}


def get_extensions(uploaded_files):

    exts = set()

    for file in uploaded_files:

        ext = Path(file.name).suffix.lower().replace(".", "")

        if ext:

            exts.add(ext)

    return sorted(exts)


def create_extension_rules(uploaded_files):

    extensions = get_extensions(uploaded_files)

    rules = []

    used = set()

    for folder, ext_list in EXTENSION_GROUPS.items():

        selected = []

        for ext in ext_list:

            if ext in extensions:

                selected.append(ext)

                used.add(ext)

        if selected:

            rules.append({

                "folder": folder,

                "extensions": selected,

                "keywords": [],

                "mode": "OR"

            })

    # 나머지 확장자

    for ext in extensions:

        if ext not in used:

            rules.append({

                "folder": ext.upper(),

                "extensions": [ext],

                "keywords": [],

                "mode": "OR"

            })

    return rules


def suggest_keywords(uploaded_files):

    words = []

    for file in uploaded_files:

        name = Path(file.name).stem.lower()

        parts = re.split(r"[_\-\s\.]+", name)

        for p in parts:

            if len(p) >= 4:

                words.append(p)

    counter = Counter(words)

    return [

        word

        for word, count in counter.items()

        if count >= 2

    ]


def create_ai_rules(uploaded_files):

    rules = create_extension_rules(uploaded_files)

    keywords = suggest_keywords(uploaded_files)

    added = set()

    for word in keywords:

        if word in added:

            continue

        matched_ext = set()

        count = 0

        for file in uploaded_files:

            if word in file.name.lower():

                ext = Path(file.name).suffix.lower().replace(".", "")

                matched_ext.add(ext)

                count += 1

        if count >= 2:

            rules.append({

                "folder": word,

                "extensions": list(matched_ext),

                "keywords": [word],

                "mode": "AND"

            })

            added.add(word)

    return rules


def classify(filename, rules):

    ext = Path(filename).suffix.lower().replace(".", "")

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

            return rule["folder"]

    return "미분류"
