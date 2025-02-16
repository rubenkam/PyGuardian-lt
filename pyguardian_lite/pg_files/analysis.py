import json
import subprocess
import re
from pyguardian_lite.pg_files import tmpfile
import os


class Analysis:
    def __init__(self, src, configuration, extra_rules):
        self.sourcecode = src
        self.configuration = configuration
        self.extra_rules = extra_rules

    output = []
    line_length = 0
    code_complexity = 10

    def full_analysis(self):
        # Create a list of all the main keys in the configuration
        scans = [key for entry in self.configuration for key in entry.keys()]

        if self.extra_rules:
            self.check_extra_rules(self.extra_rules)
        if "pep8naming" in scans:
            # Full analysis of pep8naming
            result = self.analyse_pep8naming()
            self.output.append(self.process_scan_results('pep8naming', result))

        if "pycodestyle" in scans:
            # Direct and filtered analysis of pycodestyle
            result = self.analyse_pycodestyle()
            self.output.append(self.process_scan_results('pycodestyle', result))

        if "bandit" in scans:
            result = self.analyse_bandit()
            self.output.append(self.process_scan_results('bandit', result))

        return self.output

    def check_extra_rules(self, extra_rules):
        if extra_rules:
            for dictionary in extra_rules:
                if 'line_length' in dictionary:
                    self.line_length = dictionary['line_length']
                elif 'code_complexity' in dictionary:
                    self.code_complexity = dictionary['code_complexity']

    @staticmethod
    def process_scan_results(scan, result):
        """
        Process and organize scan results into a structured format.
        """
        structured_output = {
            scan: {
                "result": result.splitlines()  # Split result into a list of lines.
            }
        }
        return structured_output

    def analyse_pep8naming(self):
        temp = tmpfile.generate_tmp_file(self.sourcecode)
        try:
            command = ["flake8", "--select", "N", "--isolated", temp]
            result = subprocess.run(command, capture_output=True, text=True)
            length = len(temp)
            output = ""
            if result.stdout:
                # Use regex to clean up the file path
                output_lines = result.stdout.splitlines()
                for line in output_lines:
                    # Remove file path based on the length of tmp-path but keep error details
                    match = re.match(r'^.{%d}(.*)' % length, line)
                    if match:
                        output += match.group(1) + "\n"

            if result.stderr:
                output += "Flake8 Errors:\n" + result.stderr

            return output.strip()

        except FileNotFoundError:
            return "Error: Flake8 is not installed. Install it using `pip install flake8`."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
        finally:
            if 'temp' in locals() and os.path.exists(temp):
                os.unlink(temp)


    def analyse_pycodestyle(self):
        temp = tmpfile.generate_tmp_file(self.sourcecode)
        # Extract the pycodestyle key's contents
        pycodestyle_data = None
        collected_errors = []
        command_error_codes = ""
        flake8select = "--select=E,W,F,C"
        command = ""
        for item in self.configuration:
            if 'pycodestyle' in item:
                pycodestyle_data = item['pycodestyle']
                break

        if 'blacklist' in pycodestyle_data:
            flake8ignore = "--ignore="
            # Loop through the blacklist dictionary
            for key, error_codes in pycodestyle_data['blacklist'].items():
                collected_errors.extend(error_codes)  # Add all error codes to the collected list

            # Create the command_error_codes string by joining with commas
            command_error_codes = ",".join(collected_errors)
            command = ["flake8", flake8select, flake8ignore+command_error_codes, "--isolated", temp]
        else:
            # Loop through the blacklist dictionary
            for key, error_codes in pycodestyle_data['error_codes'].items():
                collected_errors.extend(error_codes)  # Add all error codes to the collected list
            command_error_codes = ",".join(collected_errors)
            # Create the command_error_codes string by joining with commas
            command = ["flake8", "--select="+command_error_codes, "--isolated", temp]
        if self.line_length:
            # Insert the line length before the temp file argument (-1)
            command.insert(-1, f"--max-line-length={self.line_length}")

        # Check if self.code_complexity is a valid integer
        if isinstance(self.code_complexity, int):
            # If self.code_complexity is negative, use --min-complexity
            if self.code_complexity < 0:
                command.insert(-1, f"--min-complexity={abs(self.code_complexity)}")
            # If self.code_complexity is positive, use --max-complexity
            elif self.code_complexity > 0:
                command.insert(-1, f"--max-complexity={self.code_complexity}")

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            length = len(temp)

            output = ""
            if result.stdout:
                # Use regex to clean up the file path
                output_lines = result.stdout.splitlines()
                for line in output_lines:
                    # Remove file path based on the length of tmp-path but keep error details
                    match = re.match(r'^.{%d}(.*)' % length, line)
                    if match:
                        output += match.group(1) + "\n"

            if result.stderr:
                output += "Flake8 Errors:\n" + result.stderr

            return output.strip()

        except FileNotFoundError:
            return "Error: Flake8 is not installed. Install it using `pip install flake8`."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
        finally:
            if 'temp' in locals() and os.path.exists(temp):
                os.unlink(temp)

    def analyse_bandit(self):
        temp = tmpfile.generate_tmp_file(self.sourcecode)
        # Extract the pycodestyle key's contents
        bandit_data = None
        collected_errors = []
        command_error_codes = ""
        flake8select = "--select=S"
        command = ""
        for item in self.configuration:
            if 'bandit' in item:
                bandit_data = item['bandit']
                break

        if 'blacklist' in bandit_data:
            flake8ignore = "--ignore="
            # Loop through the blacklist dictionary
            for error_codes in bandit_data['blacklist']:
                collected_errors.append(error_codes)  # Add all error codes to the collected list

            # Create the command_error_codes string by joining with commas
            command_error_codes = ",".join(collected_errors)
            command = ["flake8", flake8select, flake8ignore+command_error_codes, "--isolated", temp]
        else:
            #Loop through the blacklist dictionary
            for error_codes in bandit_data['error_codes']:
                collected_errors.append(error_codes)  # Add all error codes to the collected list
            command_error_codes = ",".join(collected_errors)
            #Create the command_error_codes string by joining with commas
            command = ["flake8", "--select="+command_error_codes, "--isolated", temp]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            length = len(temp)
            output = ""
            if result.stdout:
                # Use regex to clean up the file path
                output_lines = result.stdout.splitlines()
                for line in output_lines:
                    # Remove file path based on the length of tmp-path but keep error details
                    match = re.match(r'^.{%d}(.*)' % length, line)
                    if match:
                        output += match.group(1) + "\n"

            if result.stderr:
                output += "Flake8 Errors:\n" + result.stderr

            return output.strip()

        except FileNotFoundError:
            return "Error: Flake8 is not installed. Install it using `pip install flake8`."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
        finally:
            if 'temp' in locals() and os.path.exists(temp):
                os.unlink(temp)

    def reset(self):
        self.sourcecode = ""
        self.configuration.clear()
        self.extra_rules.clear()
