"""Main module for ChatGPT Query."""

import sys
import webbrowser
from urllib.parse import urlencode

import typed_argparse as tap


class Args(tap.TypedArgs):
    query: list[str] = tap.arg(
        nargs="*", positional=True, help="Query to send to ChatGPT"
    )
    dry: bool = tap.arg(
        "-d",
        "--dry-run",
        help="Print the URL instead of opening it in a browser",
    )

    model: str = tap.arg(
        "-m",
        "--model",
        default="auto",
        help="Specify the model to use.",
    )
    search: bool = tap.arg(
        "-s",
        "--search",
        help="Ask ChatGPT to run search on the query.",
    )


def run(args: Args):
    if not args.query:
        print("No query provided. Please provide a query string. E.g. `chat Hello`.")
        sys.exit(1)

    url_params = {
        "q": " ".join(args.query),
        "model": args.model,
    }
    if args.search:
        url_params["hints"] = "search"
    url = f"https://chat.openai.com/?{urlencode(url_params)}"

    if args.dry:
        print(f"Generated URL: {url}")
        return

    print(f"Opening URL: {url}")
    webbrowser.open(url)


def main() -> None:
    tap.Parser(Args).bind(run).run()


if __name__ == "__main__":
    main()
