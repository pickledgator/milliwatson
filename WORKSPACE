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

# new_git_repository(
#     name = "git_google_search_api",
#     commit = "89c456e5b55433c2de888febb6cf641dd6a71a63",
#     build_file = "third_party/google_search_api.BUILD",
#     remote = "https://github.com/abenassi/Google-Search-API.git",
# )
#
# bind(
#     name = "google_search_api",
#     actual = "@git_google_search_api//:google",
# )
