git_repository(
    name = "io_bazel_rules_python",
    commit = "3e167dcfb17356c68588715ed324c5e9b76f391d",
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
