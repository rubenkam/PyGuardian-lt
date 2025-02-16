import tempfile


def generate_tmp_file(code_string):
    """
    Running scans on tmp files is most reliable.
    """
    # Create a temporary file for analysis
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code_string)
        temp_file_name = temp_file.name
    return temp_file_name
