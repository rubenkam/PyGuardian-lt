import os
import re
from pyguardian_lite.pg_files.rulesfilter import RulesFilter
from pyguardian_lite.pg_files.analysis import Analysis
from pyguardian_lite.pg_files.formatter import OutputFormatter


def run_analysis(file, config):
    vscode_output = []

    with open(file, 'r') as file:
        code_string = file.read()

    policy = config

    fetch_rules = RulesFilter(policy)
    errors_and_rules = fetch_rules.collect_all()
    # Collect the 'custom' severity list
    custom_severity_list = fetch_rules.collect_severity()
    # Collect extra rules that are defined within the yaml blocks
    extra_rules = fetch_rules.collect_extra_rules()
    # Collect the format rules
    format_rules = fetch_rules.collect_format_rules()

    analysis = Analysis(code_string, errors_and_rules, extra_rules)
    scan_output = analysis.full_analysis()

    formatter = OutputFormatter(scan_output, errors_and_rules, custom_severity_list, format_rules)
    formatter.reformat_output()
    collect = formatter.collect_default_output()

    result = collect
    filename = os.path.basename(file.name)

    # Loop through categories
    for category_data in result:
        for category, severity_data in category_data.items():
            for severity, errors in severity_data.items():
                for error in errors:
                    match = re.match(r":(\d+):(\d+): (.+)", error)
                    if match:
                        line, position, message = match.groups()
                        vscode_entry = {
                            "file": filename,
                            "line": int(line),
                            "position": int(position),
                            "severity": severity,
                            "message": message,
                            "category": category
                        }
                        vscode_output.append(vscode_entry)
    try:
        fetch_rules.reset()
        analysis.reset()
        formatter.reset()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        return vscode_output
