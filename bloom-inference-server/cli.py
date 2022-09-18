import argparse
import json
import sys

import utils
from models import get_model_class
from utils import CLI, get_argument_parser, parse_generate_kwargs, print_rank_n


def get_args() -> argparse.Namespace:
    parser = get_argument_parser()

    group = parser.add_argument_group(title="launch config")
    group.add_argument("--shutdown_command", required=False,
                       type=str, default="__shutdown__", help="This string will exit the script")

    args = utils.get_args(parser, CLI)

    return args


def main() -> None:
    args = get_args()

    model = get_model_class(args.deployment_framework)(args)

    generate_kwargs = args.generate_kwargs

    while (True):
        try:
            input_text = input("Input text: ")

            if (input_text == args.shutdown_command):
                model.shutdown()

            if (input("change generate_kwargs? [y/n] ") == "y"):
                while (True):
                    try:
                        generate_kwargs = json.loads(
                            input("Generate kwargs: "))
                        break
                    except KeyboardInterrupt:
                        model.shutdown()
                    except Exception as e:
                        e_type, e_message, _ = sys.exc_info()
                        print("error =", e_type.__name__)
                        print("message =", e_message)
                        continue

            request = parse_generate_kwargs([input_text], generate_kwargs)

            request.preprocess()

            response = model.generate(request)

            print_rank_n("Output text:", response.text[0])
            print_rank_n("Generated tokens:", response.num_generated_tokens[0])
        except KeyboardInterrupt:
            model.shutdown()


if (__name__ == "__main__"):
    main()
