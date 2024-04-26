# fast html

Simply create html files without caring about any of the required tags to be valid html:

`content/bananas.html`
```html
<h1>Bananas</h1>

<p>they taste good</p>
```

then simply run `main.py` and you get a new directory called `generated_html` which contains `bananas.html`: 
```html
 <!DOCTYPE html>
<html>
<head>

<title>bananas</title>

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
