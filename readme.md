# fast html

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

## example

Here is an example configuration for one of my projects which you can use to write your own:

`template_conversion.py`
```py
from typing import Dict, Callable

def openmath_template_conversion(path_to_content_file: str, file_name: str, template_file: str):
    """
    If it's processing a/b/c/file.html, then path_to_content_file refers to that whole path, and 
    file_name refers to file.html, template_file refers to the template file being used for file.html
    """
    with open(template_file, "r") as f:
        template_lines = f.readlines()

    file_name = os.path.splitext(os.path.basename(file_name))[0]
    page_title = file_name.replace('_', ' ')

    title_line_index = next(i for i, s in enumerate(template_lines) if "<title>PAGE TITLE</title>" in s)
    template_lines[title_line_index] = template_lines[title_line_index].replace("PAGE TITLE", page_title)

    with open(path_to_content_file, "r") as f:
            content_string = f.read()

    main_content_area_index = next(i for i, s in enumerate(template_lines) if "CONTENT" in s)
    template_lines[main_content_area_index] = breadcrumb_html + template_lines[main_content_area_index].replace("CONTENT", content_string)

    with open(path_to_content_file, "w") as f:
        contents = "".join(template_lines)
        contents = setup_page(contents)
        f.write(contents)


template_file_to_conversion : Dict[str, Callable[[str, str, str], None]] = {
    "openmath_template.html": openmath_template_conversion
}
```

then I run `fast-html/main.py --custom-template-conversion-file template_conversion.py --base-template-file templates/openmath_template.html `
