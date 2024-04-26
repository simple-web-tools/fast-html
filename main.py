import os
import shutil

script_directory = os.path.dirname(os.path.realpath(__file__))

generated_directory = script_directory + "/generated_html"
content_directory = script_directory + "/content"

def get_end_of_path(path):
    return os.path.basename(os.path.normpath(path))

def convert_content_to_valid_html(path_to_content_file: str, file_name: str):
    """
    given a path to a content file it uses the template to create a valid html file
    this also changes the title to be the name of the file with underscores replaced by spaces
    """
    with open("sample_template.html", "r") as f:
        template_lines = f.readlines()

    title_line_index = next(i for i, s in enumerate(template_lines) if "<title>" in s)

    # [:-5] removes ".html"
    page_title = " ".join(file_name[:-5].split("_"))

    print(template_lines[title_line_index])
    template_lines[title_line_index] = template_lines[title_line_index].replace("Page Title", page_title)

    # add + 2 because we want an extra line right after the body
    line_index_right_after_body = next(i for i, s in enumerate(template_lines) if "<body>" in s) + 2 

    with open(path_to_content_file, "r") as f:
        content_string = f.read()

    template_lines.insert(line_index_right_after_body, content_string)

    with open(path_to_content_file, "w") as f:
        contents = "".join(template_lines)
        f.write(contents)

def re_create_genererated_directory():
    if os.path.exists(generated_directory):
        shutil.rmtree(generated_directory)
    shutil.copytree(content_directory, generated_directory)

def convert_all_content_files_to_valid_html():
    for dir_path, dir_names, file_names in os.walk(generated_directory):

        directory_name = get_end_of_path(dir_path)
        relative_directory_path = os.path.relpath(dir_path, script_directory)
        print(directory_name, relative_directory_path)

        for file_name in file_names:
            full_path = os.path.join(dir_path, file_name)
            is_html_file = file_name[-4:] == "html"

            if is_html_file:
                convert_content_to_valid_html(full_path, file_name)
                print(file_name)
                # html_files.append(relative_file_path)

if __name__ == "__main__":
    re_create_genererated_directory()
    convert_all_content_files_to_valid_html();
