import os
import shutil
import argparse 
import configparser
import importlib.util
import sys

def create_argparser_and_get_args():
    parser = argparse.ArgumentParser(prog="fast-html", description="Create html content fast. Note that this program will not overwrite your files, it simply generates valid html from short form html", epilog="visit www.cuppajoeman.com for more information")

    parser.add_argument("--base-dir", help="the base directory which fast-html will recursively operate on, path is relative to the fast-html directory")
    parser.add_argument("--gen-dir", help="the directory that fast-html will output the modified files, path is relative to the fast-html directory")
    parser.add_argument("--base-template-file", help="the base template file to be used on all short-form html files by default")
    parser.add_argument("--config-file", help="a fast-html config file, can be used to store configuraiton to speed up usage.")
    parser.add_argument("--custom-template-conversion-file", help="a python file which create a variable with the name 'template_file_to_conversion' which is a dictionary mapping the name of a template file to a function which replaces a short-form html file with a valid html file. Check the readme for a specific example of this.")

    args = parser.parse_args()
    return args

def config_file_exists(config_file_path: str) -> bool:
    return os.path.exists(config_file_path)


def get_config_object(config_file_path: str) -> configparser.ConfigParser:
    'precondition: config_file_exists(path) holds true'
    assert(config_file_exists(config_file_path))

    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def config_has_enough_info(config) -> bool:
    # Check if the 'Paths' section and 'source' key exist
    if 'paths' not in config:
        print("you need to specify the paths section in your config file")
        return False
    else:
        if 'base-dir' not in config['paths']:
            print("you need to specify the base-dir attribute in the config file")
            return False
        if 'gen-dir' not in config['paths']:
            print("you need to specify the gen-dir attribute in the config file")
            return False
    return True


def get_required_options_from_config_file(config: configparser.ConfigParser):
    'precondition: config_has_enough_info(config) holds true'
    assert config_has_enough_info(config), "config file is missing some information"

    # Access the source and destination paths
    base_dir = config['paths']['base-dir']
    gen_dir = config['paths']['gen-dir']

    return base_dir, gen_dir 

script_directory = os.path.dirname(os.path.realpath(__file__))

def get_end_of_path(path):
    return os.path.basename(os.path.normpath(path))

def convert_content_to_valid_html(path_to_content_file: str, file_name: str, template_file_path: str, custom_conversion_module = None):
    """
    given a path to a content file use the specified template file to create a valid html file
    """
    if custom_conversion_module:
        template_file_name = get_end_of_path(template_file_path)
        conversion_dict = custom_conversion_module.template_file_to_conversion
        assert template_file_name in conversion_dict, f"the template {template_file_name} doesn't have an entry in the conversion dictionary, the dictionary contains the following keys: {conversion_dict.keys()}"

        conversion_func = conversion_dict[template_file_name]
        conversion_func(path_to_content_file, file_name, template_file_path)
    else:
        with open(template_file_path, "r") as f:
            template_lines = f.readlines()

        title_line_index = next(i for i, s in enumerate(template_lines) if "<title>" in s)

        # [:-5] removes ".html"
        page_title = " ".join(file_name[:-5].split("_"))

        template_lines[title_line_index] = template_lines[title_line_index].replace("Page Title", page_title)

        # add + 2 because we want an extra line right after the body
        line_index_right_after_body = next(i for i, s in enumerate(template_lines) if "<body>" in s) + 2 

        with open(path_to_content_file, "r") as f:
            content_string = f.read()

        template_lines.insert(line_index_right_after_body, content_string)

        with open(path_to_content_file, "w") as f:
            contents = "".join(template_lines)
            f.write(contents)

def re_create_generated_directory(content_directory, generated_directory):
    if os.path.exists(generated_directory):
        shutil.rmtree(generated_directory)
    shutil.copytree(content_directory, generated_directory)

def convert_all_content_files_to_valid_html(generated_directory: str, base_template_file: str, custom_conversion_module = None):
    for dir_path, dir_names, file_names in os.walk(generated_directory):

        # directory_name = get_end_of_path(dir_path)
        # relative_directory_path = os.path.relpath(dir_path, script_directory)
        print(f"\n==== starting work on {dir_path} ====")

        at_least_one_html_file = False

        for file_name in file_names:
            full_path = os.path.join(dir_path, file_name)
            is_html_file = file_name[-4:] == "html"

            if is_html_file:
                at_least_one_html_file = True
                convert_content_to_valid_html(full_path, file_name, base_template_file, custom_conversion_module)
                print(f"~~~> converting {file_name} to valid html using {base_template_file}")

        if not at_least_one_html_file:
            print("No html files in here, nothing to do")

        print(f"==== done with {dir_path} ====")

def attempt_to_get_custom_conversion_module():
    custom_conversion_module = None

    custom_template_conversion_file = None
    if args.custom_template_conversion_file:
        custom_template_conversion_file = args.custom_template_conversion_file
    else:
        if args.config_file is not None:
            config = get_config_object(args.config_file)
            if config.has_option("paths", "custom-template-conversion-file"):
                custom_template_conversion_file = config["paths"]["custom-template-conversion-file"]

    if custom_template_conversion_file is not None:
        module_name = "custom_conversion_module"
        spec = importlib.util.spec_from_file_location(module_name, custom_template_conversion_file)
        assert spec is not None, "spec loading failed"
        if spec is not None:
            custom_conversion_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = custom_conversion_module
            spec.loader.exec_module(custom_conversion_module)

    return custom_conversion_module

if __name__ == "__main__":
    args = create_argparser_and_get_args()
    
    custom_conversion_module = attempt_to_get_custom_conversion_module()


    if args.base_dir and args.gen_dir: # good this is valid
        base_template_file = args.base_template_file if args.base_template_file else "sample_template.html"
        re_create_generated_directory(args.base_dir, args.gen_dir)
        convert_all_content_files_to_valid_html(args.gen_dir, base_template_file, custom_conversion_module);
    else:
        if args.config_file is None:
            print("Error: You must specify base-dir, gen-dir and base-template-file. Alternatively you can specify this in a config.ini file")
        else:
            print("using config file")
            config = get_config_object(args.config_file)
            base_dir, gen_dir = get_required_options_from_config_file(config)

            if config.has_option("paths", "base-template-file"):
                base_template_file = config["paths"]["base-template-file"]
            else:
                base_template_file = "sample_template.html"

            re_create_generated_directory(base_dir, gen_dir)
            convert_all_content_files_to_valid_html(gen_dir, base_template_file, custom_conversion_module);
