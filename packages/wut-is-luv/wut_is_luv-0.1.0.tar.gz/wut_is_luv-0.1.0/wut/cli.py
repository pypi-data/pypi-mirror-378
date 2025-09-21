import argparse

OUTPUT = "bb dont hurt me dont hurt me no more "

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wut-is-luv",
        description="Prints the only correct answer to the only correct question."
    )
    
    parser.add_argument("is_", choices=["is"], help=argparse.SUPPRESS, metavar="is")
    parser.add_argument("luv", choices=["luv"], help=argparse.SUPPRESS)

    parser.parse_args()
    print(OUTPUT)

if __name__ == "__main__":
    main()
