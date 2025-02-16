import argparse
import json
import sys
from pyguardian_lite.core import run_analysis
from pyguardian_lite.config import load_config
from pyguardian_lite.config import add_policy

def main():
    parser = argparse.ArgumentParser(description="PipeGuardian-lite CLI")
    parser.add_argument("--addPolicy", help="Path to the custom YAML file to add as policy")
    parser.add_argument("file", nargs="?", help="Python file to analyze")

    args = parser.parse_args()
    
    # Check if neither argument is provided
    if not args.addPolicy and not args.file:
        custom_error_message()

    # If no arguments are provided, show the custom error message
    if len(sys.argv) == 1:
        custom_error_message()

    # Handle addPolicy independently
    if args.addPolicy:
        add_policy(args.addPolicy)
        return  # Exit after adding the policy

    config = load_config()
    results = run_analysis(args.file, config)

    print(json.dumps(results))  # Output for VS Code to parse


# Custom error message handler
def custom_error_message():
    print("Add a python file for analysis, or update your PipeGuardian policy with --addPolicy")
    sys.exit(1)