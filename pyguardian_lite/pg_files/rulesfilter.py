import pyguardian_lite.pg_files.rulebook as rulebook


class RulesFilter:

    def __init__(self, yamlconfig):
        self.data_list = yamlconfig
        self.rulesCollection = []
        self.customSeverity = []
        self.formatRules = []
        self.extraRules = []
        self.blocklist = False

    # rulebook pep8naming within naming_convention
    rulebookPep8Naming = rulebook.naming_convention["pep8-naming"]
    # rulebooks of all seperate modules in style_convention
    rulebookStyleIndentation = rulebook.style_convention["indentation"]
    rulebookStyleWhitespaces = rulebook.style_convention["whitespaces"]
    rulebookStyleBlanklines = rulebook.style_convention["blank_lines"]
    rulebookStyleImport = rulebook.style_convention["import"]
    rulebookStyleLinelength = rulebook.style_convention["line_length"]
    rulebookStyleStatement = rulebook.style_convention["statement"]
    rulebookStyleRuntime = rulebook.style_convention["runtime"]
    rulebookStyleLinebreak = rulebook.style_convention["line_break"]
    rulebookStyleDeprecation = rulebook.style_convention["deprecation"]
    rulebookStyleFlowcontrol = rulebook.style_convention["flow_control"]
    rulebookStyleLogicalIssues = rulebook.style_convention["logical_issues"]
    rulebookStyleCodequality = rulebook.style_convention["code_quality"]
    rulebookStyleLogicalOperations = rulebook.style_convention["logical_operations"]
    rulebookStyleCodeComplexity = rulebook.style_convention["code_complexity"]
    rulebookSecurity = rulebook.security["bandit"]

    errorMapPep8 = rulebook.error_map['pep8-naming']
    validSeverity = rulebook.valid_severities
    errorMapSeverity = rulebook.error_severity_map
    errorMapSecurity = rulebook.error_map['bandit']
    errorMap = rulebook.error_map

    def collect_all(self):
        """
        Loads the YAML configuration.
        """
        data = self.data_list
        self.collect_predefined_rules(data)
        self.check_format_rules(data)
        if "naming_conventions" in data:
            # Collect all error codes
            collection = self.collect_naming_conventions(data)
            #Identify the blacklist for formatting
            if self.blocklist:
                blacklist = collection
            else:
                blacklist = self.identify_blacklist(collection, self.errorMapPep8)
            rule_entry = {
                "pep8naming": {
                    "error_codes": collection
                }
            }
            if blacklist:  # Only add blacklist if it is not empty
                rule_entry["pep8naming"]["blacklist"] = blacklist
            self.rulesCollection.append(rule_entry)

        if "style_conventions" in data:
            collection = self.collect_styling_conventions(data)
            blacklist = {}
            rule_entry = {
                "pycodestyle": {
                    "error_codes": collection
                }
            }
            if not self.blocklist:
                for key in collection:
                    result = self.identify_blacklist(collection[str(key)], self.errorMap[str(key)])
                    if result:
                        blacklist[key] = result
                if blacklist:
                    rule_entry["pycodestyle"]["blacklist"] = blacklist
            else:
                rule_entry["pycodestyle"]["blacklist"] = collection
            self.rulesCollection.append(rule_entry)

        if "security" in data:
            collection = self.collect_security_rules(data)
            # Identify the blacklist for formatting
            if self.blocklist:
                blacklist = collection
            else:
                blacklist = self.identify_blacklist(collection, self.errorMapSecurity)
            rule_entry = {
                "bandit": {
                    "error_codes": collection
                }
            }
            if blacklist:  # Only add blacklist if it is not empty
                rule_entry["bandit"]["blacklist"] = blacklist
            self.rulesCollection.append(rule_entry)

        return self.rulesCollection

    def collect_naming_conventions(self, data):
        # Extract error codes based on available type or error_code
        error_codes = []
        for item in data["naming_conventions"]:
            # Only extract rule data if it is enabled
            if item.get("enabled"):
                error_code = item.get("error_code")
                if not error_code and "type" in item:
                    # Look up the error code in the rulebook for the given type
                    type_name = item["type"]
                    error_code = next(
                        (code for t, code in self.rulebookPep8Naming if t == type_name),
                        None,
                    )
                if error_code:
                    self.check_custom_severity(item, error_code)
                    error_codes.append(error_code)
        return error_codes

    def collect_styling_conventions(self, data):
        # Mapping data keys to their respective functions
        function_mapping = {
            "whitespaces": self.collect_whitespace,
            "indentation": self.collect_indentation,
            "blank_lines": self.collect_blankline,
            "import": self.collect_import,
            "line_length": self.collect_linelength,
            "statement": self.collect_statement,
            "runtime": self.collect_runtime,
            "line_break": self.collect_linebreak,
            "deprecation": self.collect_deprecation,
            "flow_control": self.collect_flowcontrol,
            "logical_issues": self.collect_logicalissues,
            "code_quality": self.collect_codequality,
            "logical_operations": self.collect_logicaloperation,
            "code_complexity": self.collect_codecomplexity,
        }
        # Store the error codes in this variable
        error_codes = {}
        # Iterate over the style conventions keys in the input data
        for key in data["style_conventions"]:
            if key in function_mapping:
                # Accumulate the results instead of overwriting
                if key not in error_codes:
                    # Create a key in error_codes and initialize it with an empty list
                    error_codes[key] = []

                specific_function_call = function_mapping[key]  # Retrieve the function based on the key
                error_codes[key].extend(specific_function_call(data)) # Call function and store error codes for that key
            if key == "code_complexity":
                self.collect_complexity(data["style_conventions"]['code_complexity'])
        return error_codes

    def collect_security_rules(self, data):
        error_codes = []
        for item in data["security"]:
            if item.get("enabled"):
                error_code = item.get("error_code")
                if not error_code and "type" in item:
                    # Look up the error code in the rulebook for the given type
                    type_name = item["type"]
                    error_code = next(
                        (code for t, code in self.rulebookSecurity if t == type_name),
                        None,
                    )
                if error_code:
                    self.check_custom_severity(item, error_code)
                    error_codes.append(error_code)
        return error_codes

    def collect_predefined_rules(self, data):
        if data['meta'] and "blocklist" in data['meta']:
            if data['meta']['blocklist']:  # Check if the value of 'blocklist' is True
                self.blocklist = True

    def assemble_codes(self, data, category, key, ruleset) -> list:
        error_codes = []
        for item in data[category][key]:
            if item.get("enabled"):
                error_code = item.get("error_code")
                if not error_code and "type" in item:
                    # Look up the error code in the rulebook for the given type
                    type_name = item["type"]
                    error_code = next(
                        (code for t, code in ruleset if t == type_name),
                        None,
                    )
                if error_code:
                    self.check_custom_severity(item, error_code)
                    error_codes.append(error_code)
                if error_code == "E501":
                    if 'max_line_length' in item:
                        value = item.get("max_line_length")
                        self.extraRules.append({"line_length": value})
                    else:
                        self.extraRules.append({"line_length": 79})

        return error_codes

    @staticmethod
    def identify_blacklist(collected, errormap) -> list:
        """
        Identifies error values in errormap that are not in the yaml and returns them as a list.
        """
        blacklist = [error for error in errormap if error not in collected]
        return blacklist

    def collect_indentation(self, data):
        return self.assemble_codes(data, "style_conventions", "indentation", self.rulebookStyleIndentation)

    def collect_whitespace(self, data):
        return self.assemble_codes(data, "style_conventions", "whitespaces", self.rulebookStyleWhitespaces)

    def collect_blankline(self, data):
        return self.assemble_codes(data, "style_conventions", "blank_lines", self.rulebookStyleBlanklines)

    def collect_import(self, data):
        return self.assemble_codes(data, "style_conventions", "import", self.rulebookStyleImport)

    def collect_linelength(self, data):
        return self.assemble_codes(data, "style_conventions", "line_length", self.rulebookStyleLinelength)

    def collect_statement(self, data):
        return self.assemble_codes(data, "style_conventions", "statement", self.rulebookStyleStatement)

    def collect_runtime(self, data):
        return self.assemble_codes(data, "style_conventions", "runtime", self.rulebookStyleRuntime)

    def collect_linebreak(self, data):
        return self.assemble_codes(data, "style_conventions", "line_break", self.rulebookStyleLinebreak)

    def collect_deprecation(self, data):
        return self.assemble_codes(data, "style_conventions", "deprecation", self.rulebookStyleDeprecation)

    def collect_flowcontrol(self, data):
        return self.assemble_codes(data, "style_conventions", "flow_control", self.rulebookStyleFlowcontrol)

    def collect_logicalissues(self, data):
        return self.assemble_codes(data, "style_conventions", "logical_issues", self.rulebookStyleLogicalIssues)

    def collect_codequality(self, data):
        return self.assemble_codes(data, "style_conventions", "code_quality", self.rulebookStyleCodequality)

    def collect_logicaloperation(self, data):
        return self.assemble_codes(data, "style_conventions", "logical_operations", self.rulebookStyleLogicalOperations)

    def collect_codecomplexity(self, data):
        return self.assemble_codes(data, "style_conventions", "code_complexity", self.rulebookStyleLogicalOperations)

    def collect_complexity(self, data):
        for item in data:
            if 'value' in item:
                value = item.get('value')
                self.extraRules.append({"code_complexity": value})

    def check_format_rules(self, data):
        if 'output' in data:
            for rule, value in data['output'].items():
                self.formatRules.append({rule: value})

    def check_custom_severity(self, item, error_code):
        if 'set.severity' in item:
            severity = item.get('set.severity')
            if severity in self.validSeverity:
                self.customSeverity.append({error_code: severity})
        return item

    def collect_format_rules(self):
        return self.formatRules

    def collect_severity(self):
        return self.customSeverity

    def collect_extra_rules(self):
        return self.extraRules

    def reset(self):
        self.data_list.clear()
        self.rulesCollection.clear()
        self.customSeverity.clear()
        self.formatRules.clear()
        self.extraRules.clear()
        self.blocklist = None  # Bool
