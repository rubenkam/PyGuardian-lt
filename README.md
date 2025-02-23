Build on flake8, pep8naming, pycodestyle, pyflakes, mccabe and bandit

Create your own simplified yaml that serves as your code policy.

Checks are categorized under:

  naming_conventions (pep8naming)
  style_conventions (Pycodestyle, Pyflakes & Mccabe)
  security (Bandit)

Features:

  enable/disable specific errors
  Either use the original type or error_code to add a check
  Add your own information per check or in the meta (doesnt get included in the scan)
  Add your custom severity (Critical, Error, Warning, Hint, Info, Debug)
  Default = whitelist, blocklist = true means your blocking every check in the list, unless specific checks are disabled.

  
