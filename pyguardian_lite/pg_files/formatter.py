import re
import pyguardian_lite.pg_files.rulebook as rulebook


class OutputFormatter:

    def __init__(self, analysis, configuration, custom_severity, reformat_rules):
        self.analysis = analysis
        self.configuration = configuration
        self.custom_severity = custom_severity
        self.reformat_rules = reformat_rules
        self.default_format = []

    def reformat_output(self):
        scans = [key for entry in self.analysis for key in entry.keys()]

        if "pep8naming" in scans:
            # Find the specific dictionary with the scan results and pass it to reformat_pep8naming
            pep8naming_analysis = next(entry['pep8naming'] for entry in self.analysis if "pep8naming" in entry)
            configuration = next((entry['pep8naming'] for entry in self.configuration if "pep8naming" in entry), None)
            output = self.reformat_pep8naming(pep8naming_analysis, configuration)  # Pass only the dictionary
            self.default_reformat(output, "naming_conventions")

        if "pycodestyle" in scans:
            output = []
            pycodestyle_analysis = next(entry['pycodestyle'] for entry in self.analysis if "pycodestyle" in entry)
            for error in pycodestyle_analysis['result']:
                output.append(error)
            self.default_reformat(output, "style_conventions")

        if "bandit" in scans:
            output = []
            pycodestyle_analysis = next(entry['bandit'] for entry in self.analysis if "bandit" in entry)
            for error in pycodestyle_analysis['result']:
                output.append(error)
            self.default_reformat(output, "security")

    def default_reformat(self, collection, parentkey):
        output = collection
        default_output = {}

        for error in output:
            regex_error = error
            # Find all error codes in the error message using regex
            match = re.search(r"(:\d+:\d+:) ([A-Za-z]\d{3}) ", regex_error)
            severity = ""
            if match:
                error_code = match.group(2)  # Extract the error code (like: S101)
                if self.custom_severity:
                    for dictionary in self.custom_severity:
                        for key, value in dictionary.items():
                            if key == error_code:
                                severity = value
                # If severity is not yet defined, then we collect the default severity
                elif not severity:
                    # Check if severity is a warning error
                    if error_code in rulebook.error_warning_collection:
                        severity = "warning"
            if not severity:
                severity = "error"

            default_output.setdefault(severity, []).append(error)

        # Wrap that up under the parent key
        parent_entry_default = {
            parentkey: self.group_errors_by_severity(default_output)
        }
        # Add it to the default collection
        self.default_format.append(parent_entry_default)

    @staticmethod
    def reformat_pep8naming(partial_analysis, configuration):
        output = []
        if 'blacklist' in configuration:
            blacklist = configuration['blacklist']

            # Define regex pattern to extract the error code
            pattern = r':\d+:\d+: (\w{4})'  # Matches ':line:position: error_code'

            # Loop through the result list and check each error code
            for error in partial_analysis['result']:
                # Use regex to find the error code
                match = re.search(pattern, error)
                if match:
                    # Extract the error code from the match object
                    error_code = match.group(1)
                    # Check if error code is not in blacklist
                    if error_code not in blacklist:
                        # Add error message to output list if not blacklisted
                        output.append(error)
        else:
            output = partial_analysis['result']
        # Return the filtered output
        return output

    @staticmethod
    def reformat_toggle_line(error):
        reformat_lines = ""
        match = re.match(r":(\d+):(\d+): (.+)", error)
        if match:
            line, position, message = match.groups()
            reformat_lines = f"Line {line} at position {position}: {message}"
        else:
            reformat_lines = error
        return reformat_lines

    @staticmethod
    def reformat_error_code(error):
        reformat_errors = error
        cleaned_error = re.sub(r"(:\d+:\d+:) [A-Za-z]\d{3} ", r"\1 ", error)
        if cleaned_error:
            reformat_errors = cleaned_error

        return reformat_errors

    @staticmethod
    def group_errors_by_severity(errors):

        valid_severities = rulebook.valid_severities

        ordered_severities = list(valid_severities.keys())
        grouped_errors = {severity: [] for severity in ordered_severities}

        # Normalize input into a list of dictionaries
        if isinstance(errors, dict):
            errors = [errors]

        for error_dict in errors:
            for severity, messages in error_dict.items():
                if severity in grouped_errors:
                    grouped_errors[severity].extend(messages)

        # Remove empty lists from the result
        grouped_errors = {k: v for k, v in grouped_errors.items() if v}

        return grouped_errors

    @staticmethod
    def order_error_messages(error_messages):
        lp_index = []

        for index, error in enumerate(error_messages):
            match = re.match(r":(\d+):(\d+): (.+)", error)
            if match:
                line, position, message = match.groups()
                lp_index.append({"line": line, "position": position, "index": index})
            else:
                return error_messages

        # Sort lp_index based on line number first, then position
        sorted_lp_index = sorted(lp_index, key=lambda x: (int(x['line']), int(x['position'])))

        # Reorder error_messages based on sorted_lp_index
        ordered_errors = [error_messages[item['index']] for item in sorted_lp_index]

        return ordered_errors

    def collect_default_output(self):
        if self.default_format:
            return self.default_format

    def reset(self):
        self.analysis.clear()
        self.configuration.clear()
        self.custom_severity.clear()
        self.reformat_rules.clear()
        self.default_format.clear()
