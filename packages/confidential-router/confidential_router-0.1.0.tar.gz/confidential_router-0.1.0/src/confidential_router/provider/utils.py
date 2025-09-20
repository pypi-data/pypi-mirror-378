import re

def parse_string_args(input_string):
    """
    Parse a string containing a main text and command-line style arguments.
    
    Args:
        input_string (str): String in format "main text --arg1 value1 --arg2 value2"
    
    Returns:
        tuple: (main_string, args_dict)
            - main_string: The text before the first --argument
            - args_dict: Dictionary of argument name -> value pairs
    
    Example:
        >>> parse_string_args("an image of a cat --args1 a --args2 b")
        ("an image of a cat", {"args1": "a", "args2": "b"})
    """
    
    # Split the string at the first occurrence of --
    parts = input_string.split('--', 1)
    
    # Main string is everything before the first --
    main_string = parts[0].strip()
    
    # Initialize empty args dict
    args_dict = {}
    
    # If there are arguments to parse
    if len(parts) > 1:
        args_part = '--' + parts[1]
        
        # Find all --arg value patterns
        # This regex captures --argument_name followed by the value (until next -- or end)
        pattern = r'--(\w+)\s+([^-]+?)(?=\s+--|$)'
        matches = re.findall(pattern, args_part)
        
        # Build the args dictionary
        for arg_name, arg_value in matches:
            args_dict[arg_name] = arg_value.strip()
    
    return main_string, args_dict