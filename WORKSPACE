git_repository(
    name = "io_bazel_rules_python",
    remote = "https://github.com/bazelbuild/rules_python.git",
    # NOT VALID!  Replace this with a Git commit SHA.
    commit = "3e167dcfb17356c68588715ed324c5e9b76f391d",
)

# Only needed for PIP support:
load("@io_bazel_rules_python//python:pip.bzl", "pip_repositories")
pip_repositories()


load("@io_bazel_rules_python//python:pip.bzl", "pip_import")
# This rule translates the specified requirements.txt into
# @my_deps//:requirements.bzl, which itself exposes a pip_install method.
pip_import(
   name = "my_deps",
   requirements = "//:requirements.txt",
)
# Load the pip_install symbol for my_deps, and create the dependencies'
# repositories.
load("@my_deps//:requirements.bzl", "pip_install")
pip_install()
