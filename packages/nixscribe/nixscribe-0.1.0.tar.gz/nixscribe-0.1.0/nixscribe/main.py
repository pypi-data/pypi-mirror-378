import argparse
import sys
import os
from . import editor


def check_file_existence(file: str) -> bool:
    return os.path.exists(file)


def main():
    parser = argparse.ArgumentParser(
        prog="nixscribe",
        description="CLI Text Editor that supports file read/write and creation",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--create", nargs=1, metavar="FILE", help="Create a new file at specified path"
    )
    group.add_argument(
        "--read", nargs=1, metavar="FILE", help="Read contents of the file"
    )
    group.add_argument(
        "--edit", nargs=1, metavar="FILE", help="Edit contents of the file"
    )

    args = parser.parse_args()

    if args.create:
        action = "create"
        file_path = args.create[0]
    elif args.read:
        action = "read"
        file_path = args.read[0]
    elif args.edit:
        action = "edit"
        file_path = args.edit[0]
    else:
        print("Error: No valid action provided.")
        sys.exit(1)

    if action != "create":
        if check_file_existence(file_path):
            if action == "read":
                if os.path.getsize(file_path) > 0:
                    editor.view(file_path)
                else:
                    print("Error: Specified file is empty.")
                    sys.exit(1)
            elif action == "edit":
                editor.edit(file_path)
        else:
            print("Error: Specified file does not exist.")
            sys.exit(1)
    elif action == "create":
        editor.create(file_path)


if __name__ == "__main__":
    main()
