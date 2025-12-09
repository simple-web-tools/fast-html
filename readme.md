# fast html

Most templating language are almost easy enough for non-programmers to use. I go against that here, this is for programmers who want the power of a real programming language to do templating.

## what you can do

Simply create html files without caring about any of the required tags to be valid html:

`content/banana_file.html`
```html
<h1>Bananas</h1>

<p>they taste good</p>
```

then simply run `python main.py --base-dir content --gen-dir generated_html` and you get a new directory called `generated_html` which contains `bananas.html`: 
```html
 <!DOCTYPE html>
<html>
<head>

<title>banana file</title>

</head>
<body>

<h1>Bananas</h1>

<p>they taste good</p>

</body>
</html> 
 ```

---

This kind of program is nice if you have a blog, and you want to focus on writing content. Also if you have a large collection of blog posts if they all use a hardcoded header then you have to change many of the files to reflect any changes that you want to have happen.

This program is also a nice alternative to having to use complex blog software when you only want to achieve something basic.

# how it works

The way we get this done is by taking the short-form html file and a template, for example here is the template that was used:

```html
<!DOCTYPE html>
<html>
<head>

<title>Page Title</title>

</head>
<body>


</body>
</html> 
```

there is then a function which takes takes in the fast html file and the template as strings and then combines the two of them, the script will walk the entire directory doing this whenever it finds an html file.

# config file

As seen you have to specify your base dir and generated dir each time you run the program, so to make this easier you can put this information in a config file. Do it like this:

```ini
[paths]
base-dir = ../content
gen-dir = generated_html
base-template-file = ../templates/toolbox_template.html
```

the syntax of the config file is the same as the name of the arguments to the command line program which you can check out with `python main.py -h`.

# custom template behavior

In the example of `banana_file.html` you'll notice that the way the short-form html was converted into valid html was in a specific fashion (through the built in function). 

fast-html allows you to specify your own custom template files, for each custom template file you specify you have to provide a function which takes the template file and puts the content of the short-form html in it to form a valid html file. 

Specifically you have to create a python file where you define a variable called `template_file_to_conversion` which maps the name of each custom template to a function of the form 

```py
def toolbox_template_conversion(path_to_content_file: str, file_name: str, template_file: str)
```

Note: the name of the function doesn't matter, it just has to have the same signature

That function above (which is predefined in `sample_conversion_methods.py`) converts the file located at `path_to_content_file` to a valid html file. Note that this file path will be inside the of your generated html dir so don't worry about overwriting actual content.

Once you've created your custom implementation you can specify that this template be used through the command line option `--custom-template-conversion-file` or you can also specify it through the config file.

When creating your own conversion logic I recommend first just grabbing the existing sample logic and then modifying that: 
```bash
cp fast-html/header_and_link_to_edit_template.html cpp_manual_template.html
cp fast-html/sample_conversion_methods.py cpp_manual_template_conversion_logic.py
``` 

## tutorial

### write the basic html template you want on all your html files
Add in any links to css or javascript you want to use, also throw in some placeholder strings you can easily grab onto later

`html/my_custom_template.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TITLE</title>
    <link rel="stylesheet" href="/cjm-css/styles.css">
</head>
<body>
    <div class="wrapper">
        BODY
    </div>
</body>
</html>
```

### write your conversion code

This is what makes fast-html so good, you simply now get to write the template conversion code in python, meaning that you pretty much have no restrictions as to what you have to do next, you can generate dynamic content, make network requests, etc...

Next create a python file that does the conversion, adhereing to the following signature and constructing the dictionary at the bottom like so:
`html/custom_template_conversion.py`
```py
import os
from typing import Dict, Callable

def custom_template_conversion(path_to_content_file: str, file_name: str, template_file: str):
    """
    First your regular html directory is copied to a different directory, then for each file in the
    new directory, this function gets called on each triple of the form:
        (path_to_content_file, file_name, template_file)

    For example, it could look like:
        (generated_html/mystuff.html, mystuff.html, my_custom_template.html)

    Notes:
    - you can configure fast-html to use different templates for different directories or files.
    - since this function is being called over all files in a new fresh copied directory so the paths
    given will be within this copied directory, and over-writing on the file path `path_to_content_file` is
    a safe operation
    """
    # open the template
    with open(template_file, "r") as f:
        template_lines = f.readlines()

    # generate a page title
    file_name = os.path.splitext(os.path.basename(file_name))[0]
    page_title = file_name.replace('_', ' ')

    # replace the title with the generated title
    title_line_index = next(i for i, s in enumerate(template_lines) if "<title>TITLE</title>" in s)
    template_lines[title_line_index] = template_lines[title_line_index].replace("TITLE", page_title)

    # open the file with the actual content in it
    with open(path_to_content_file, "r") as f:
            content_string = f.read()

    # replace the body in the template with the body in the content file
    main_content_area_index = next(i for i, s in enumerate(template_lines) if "BODY" in s)
    template_lines[main_content_area_index] = template_lines[main_content_area_index].replace("BODY", content_string)

    with open(path_to_content_file, "w") as f:
        contents = "".join(template_lines)
        f.write(contents)

template_file_to_conversion : Dict[str, Callable[[str, str, str], None]] = {
    "my_custom_template.html": cpptbx_template_conversion
}
```
then I run

```sh
python scripts/fast-html/main.py -custom-template-conversion-file html/custom_template_conversion.py --base-template-file html/my_custom_template.html --base-dir html/ --gen-dir generated_html
```

### going faster
The first step to going faster is to make a config file storing your commands in a config file:
`html/fast_html_config.txt`
```ini
[settings]
custom-template-conversion-file = html/fast_html_template_conversion.py
base-template-file = html/cpp_tbx_template.html
base-dir = html/
gen-dir = generated_html
```
and then just run: 
```sh
python scripts/fast-html/main.py --config-file html/fast_html_config.txt
```
You'll probably have noticed that running that command everytime you change stuff can become a pain, so be sure to turn on `devel` mode.
