import os
import json
from collections import Counter

def traverse_yaml_files(root_dir):
    """
    Traverse through the specified directory and its subdirectories starting from the root_dir,
    and collect paths to all YAML files.
    
    Args:
        root_dir (str): The root directory from which to start traversing.
        
    Returns:
        List[str]: A list of paths to all YAML files within the specified path.
    """
    yaml_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.yaml'):
                yaml_files.append(os.path.join(dirpath, filename))
    return yaml_files

def return_doc_to_text_value(yaml_files):
    """
    Extract the value of 'doc_to_text' from each YAML file in the list, 
    unless 'doc_to_text' is not present or its value is a function.
    
    Args:
        yaml_files (List[str]): A list of paths to YAML files.
        
    Returns:
        List[str]: A list of 'doc_to_text' values from the YAML files.
    """
    import yaml

    class NoFunctionLoader(yaml.SafeLoader):
        pass

    def no_function_constructor(loader, node):
        return None

    NoFunctionLoader.add_constructor('!function', no_function_constructor)

    doc_to_text_values = []
    for file_path in yaml_files:
        with open(file_path, 'r') as file:
            yaml_content = yaml.load(file, Loader=NoFunctionLoader)
            doc_to_text = yaml_content.get('doc_to_text')
            if doc_to_text and not isinstance(doc_to_text, dict) and not str(doc_to_text).startswith('!function'):
                doc_to_text_values.append(doc_to_text)
    return doc_to_text_values


def process_and_save_doc_to_text_counter(directory: str, output_file: str) -> None:
    """
    Traverse YAML files in the specified directory, process 'doc_to_text' values,
    and save the frequency of these values to a JSON file.

    Args:
        directory (str): The directory to traverse for YAML files.
        output_file (str): The file path to save the JSON output.
    """
    yaml_files = traverse_yaml_files(directory)
    doc_to_text_values = return_doc_to_text_value(yaml_files)
    doc_to_text_counter = Counter(doc_to_text_values)

    # Filter out entries with less than 3 occurrences
    filtered_doc_to_text_counter = {k: v for k, v in doc_to_text_counter.items() if v >= 3}

    # Sort the counter by frequency from most common to least common
    sorted_doc_to_text_counter = dict(Counter(filtered_doc_to_text_counter).most_common())

    # Convert the sorted counter to a JSON string with pretty formatting
    json_output = json.dumps(sorted_doc_to_text_counter, indent=4, ensure_ascii=False)

    output_file = "./msc_utils/" + output_file
    # Save the JSON output to a file
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json_file.write(json_output)


process_and_save_doc_to_text_counter("./lm_eval/tasks/", 'doc_to_text_values_counter.json')