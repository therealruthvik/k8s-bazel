load("@rules_python//python:defs.bzl", "py_binary", "py_library")

# One library that contains ALL helper modules.
# Bazel makes every file in srcs available to anything that deps on this.
py_library(
    name = "checks",
    srcs = [
        "nodes.py",
        "namespaces.py",
        "pods.py",
    ],
)

# The runnable binary — depends on the checks library above
py_binary(
    name = "checker",
    srcs = ["checker.py"],
    main = "checker.py",
    deps = [":checks"],
)