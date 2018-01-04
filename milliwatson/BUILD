load("@milliwatson_deps//:requirements.bzl", "requirement")

py_binary(
    name = "ocr",
    srcs = ["ocr.py"],
    default_python_version = "PY3",
    deps = [
        requirement("pytesseract"),
        requirement("Pillow"),
        requirement("opencv-python"),
    ],
)

py_binary(
    name = "query",
    srcs = ["query.py"],
    default_python_version = "PY3",
    deps = [
        requirement("Google-Search-API"),
        requirement("termcolor"),
    ],
)

py_binary(
    name = "milliwatson",
    srcs = ["milliwatson.py"],
    default_python_version = "PY3",
    deps = [
        ":ocr",
        ":query",
        requirement("simplejson"),
        requirement("future"),
    ],
)
