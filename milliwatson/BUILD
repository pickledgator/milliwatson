load("@milliwatson_deps//:requirements.bzl", "requirement")

py_binary(
    name = "ocr",
    srcs = ["ocr.py"],
    deps = [
	    requirement("pytesseract"),
      requirement("Pillow"),
      requirement("opencv-python"),
    ]
)

py_binary(
    name = "query",
    srcs = ["query.py"],
    deps = [
      requirement("google"),
      requirement("termcolor")
    ],
)

py_binary(
    name = "milliwatson",
    srcs = ["milliwatson.py"],
    deps = [
      ":ocr",
      ":query",
      requirement("simplejson"),
      requirement("future"),
      requirement("google"),
    ],
    default_python_version = "PY3"
)
