import argparse
from langgraph.types import Command


def main():
    print("Hello from multi-agent-project!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Learning Accelerator")
    parser.add_argument("goal", nargs='?', default="Learn Python closures and decorators from scratch")
    parser.add_argument("--resume", metavar="SESSION_ID", help="Resume an existing session by ID")
    args = parser.parse_args()
    