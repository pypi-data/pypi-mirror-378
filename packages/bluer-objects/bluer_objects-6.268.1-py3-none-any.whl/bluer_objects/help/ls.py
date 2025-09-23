from typing import List

from bluer_options.terminal import show_usage


def help_ls(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--delim <space>]",
        "[--log <0>]",
    ]

    usage_1 = show_usage(
        [
            "@ls",
            "[cloud|local]",
            "[.|<object-name>]",
        ]
        + args,
        "ls <object-name>.",
        mono=mono,
    )

    # ---

    args = [
        "[--delim <space>]",
        "[--log <0>]",
        "[--prefix <prefix>]",
    ]

    usage_2 = show_usage(
        [
            "@ls",
            "[cloud|local]",
            "objects",
        ]
        + args,
        "ls objects.",
        mono=mono,
    )

    return "\n".join(
        [
            usage_1,
            usage_2,
        ]
    )
