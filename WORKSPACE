git_repository(
    name = "io_bazel_rules_python",
    commit = "44711d8ef543f6232aec8445fb5adce9a04767f9",
    remote = "https://github.com/bazelbuild/rules_python.git",
)

load("@io_bazel_rules_python//python:pip.bzl", "pip_repositories")

pip_repositories()

load("@io_bazel_rules_python//python:pip.bzl", "pip_import")

pip_import(
    name = "milliwatson_deps",
    requirements = "//:requirements.txt",
)

load("@milliwatson_deps//:requirements.bzl", "pip_install")

pip_install()
