from typing import Dict, Callable
import os


def generate_breadcrumb(path_to_content_file: str) -> str:
    """
    Generates breadcrumb navigation from the file path.
    Example: path_to_content_file 'generated_html/a/b/c/file.html'
    would generate the breadcrumb as:
    '~/a/b/c/file.html' where each part is clickable and links to its index.html
    or the actual file for the last part.
    """
    # Normalize the path to handle '..' and redundant slashes
    norm_path = os.path.normpath(path_to_content_file)

    # Ensure 'generated_html' is in the path and strip everything before it
    try:
        rel_path = norm_path.split("generated_html" + os.sep, 1)[1]
    except IndexError:
        raise ValueError("Path must contain 'generated_html'.")

    parts = rel_path.split(os.sep)
    breadcrumb_html = '<nav class="breadcrumb">\n'
    breadcrumb_html += f'<a href="/index.html">~</a>'

    current_path = "/"
    for part in parts[:-1]:  # all except the last (file)
        current_path += part + "/"
        breadcrumb_html += f'/<a href="{current_path}index.html">{part}</a>'

    # Add the final part (the file itself)
    final_file = parts[-1]
    file_path = current_path + final_file
    breadcrumb_html += f'/<a href="{file_path}">{final_file}</a>'

    breadcrumb_html += "\n</nav>\n"
    return breadcrumb_html

def toolbox_template_conversion(path_to_content_file: str, file_name: str, template_file: str):
    """
    If it's processing a/b/c/file.html, then path_to_content_file refers to that whole path, and 
    file_name refers to file.html, template file refers to the template file being used for file.html
    """
    with open(template_file, "r") as f:
        template_lines = f.readlines()

    # [:-5] removes ".html"
    page_title = " ".join(file_name[:-5].split("_"))

    title_line_index = next(i for i, s in enumerate(template_lines) if "PAGE TITLE" in s)
    template_lines[title_line_index] = template_lines[title_line_index].replace("PAGE TITLE", page_title)

    header_line_index = next(i for i, s in enumerate(template_lines) if "HEADER TITLE" in s)
    template_lines[header_line_index] = template_lines[header_line_index].replace("HEADER TITLE", page_title)

    print(f"DEBUG PATH TO CONTENT FILE {path_to_content_file}")
    # Generate breadcrumb navigation
    breadcrumb_html = generate_breadcrumb(path_to_content_file)

    with open(path_to_content_file, "r") as f:
        content_string = f.read()

    # Insert breadcrumb navigation above the main content
    main_content_area_index = next(i for i, s in enumerate(template_lines) if "CONTENT" in s)
    template_lines[main_content_area_index] = breadcrumb_html + template_lines[main_content_area_index].replace("CONTENT", content_string)

    link_to_file_on_git_index = next(i for i, s in enumerate(template_lines) if "FILENAME" in s)
    # because we do this on a different directory we remove the temporary directory from path
    corrected_path = path_to_content_file.replace("generated_html/", "")
    template_lines[link_to_file_on_git_index] = template_lines[link_to_file_on_git_index].replace("FILENAME", corrected_path)

    with open(path_to_content_file, "w") as f:
        contents = "".join(template_lines)
        f.write(contents)


template_file_to_conversion : Dict[str, Callable[[str, str, str], None]] = {
    "toolbox_template.html": toolbox_template_conversion
}
