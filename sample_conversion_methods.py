from typing import Dict, Callable

def toolbox_template_conversion(path_to_content_file: str, file_name: str, template_file: str):
    with open(template_file, "r") as f:
        template_lines = f.readlines()

    # [:-5] removes ".html"
    page_title = " ".join(file_name[:-5].split("_"))

    title_line_index = next(i for i, s in enumerate(template_lines) if "PAGE TITLE" in s)
    template_lines[title_line_index] = template_lines[title_line_index].replace("PAGE TITLE", page_title)

    header_line_index = next(i for i, s in enumerate(template_lines) if "HEADER TITLE" in s)
    template_lines[header_line_index] = template_lines[header_line_index].replace("HEADER TITLE", page_title)

    with open(path_to_content_file, "r") as f:
        content_string = f.read()

    main_content_area_index = next(i for i, s in enumerate(template_lines) if "CONTENT" in s)
    template_lines[main_content_area_index] = template_lines[main_content_area_index].replace("CONTENT", content_string)

    link_to_file_on_git_index = next(i for i, s in enumerate(template_lines) if "FILENAME" in s)
    template_lines[link_to_file_on_git_index] = template_lines[link_to_file_on_git_index].replace("FILENAME", file_name)

    with open(path_to_content_file, "w") as f:
        contents = "".join(template_lines)
        f.write(contents)


template_file_to_conversion : Dict[str, Callable[[str, str, str], None]] = {
    "toolbox_template.html": toolbox_template_conversion
}

