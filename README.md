PyGuardian (lite) 

Custom and simple static analyser, powered by flake8 -> pep8naming, pycodestyle, pyflakes, mccabe and bandit
Customizable and automatic analysis with a simplified yaml template

yaml template categories:
  Naming conventions
  Style conventions
  Security

The yaml file is your custom policy list containing all the rules you want to run.

disable/enable specific errors and simply override a severity with set.severity = "critical"

  - name: "Class Naming Convention"
    description: "Class names should use CapWords convention. (Also known as CamelCase)"
    type: "class-names-capwords"
    enabled: true # Or false  
    error_code: "N801"
    set.severity: "critical"  

Possible severity's:

  "critical": "Very severe issue requiring immediate action",
  "error": "Critical issue preventing execution or functionality",
  "warning": "Potential issue that should be addressed",
  "info": "Informational message, typically non-disruptive",
  "hint": "Suggestion or tip that can be helpful but isn't crucial",
  "debug": "Detailed, often low-priority information useful for debugging"

Make a blocklist to only block errors with blocklist = true in the meta info:

meta:
  author: "JohnDoe"
  policy: "Developers standards"
  description: "I turned this yaml into a blocklist"
  blocklist: true

Simplify the yaml, only need the type or the error_code:

  - name: "Class Naming Convention"
    error_code: "N801"

