import argparse
from pprint import pprint

from .infer_service import load_structure_service


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True)
    args = parser.parse_args()

    result = load_structure_service().infer(args.name)
    pprint(result)


if __name__ == '__main__':
    main()
