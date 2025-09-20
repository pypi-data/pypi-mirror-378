# PyWeb Framework - Build Responsive Web Apps with Python

PyWeb is a Python-based web framework that allows you to build responsive, modern web applications using only Python code. No HTML, CSS, or JavaScript knowledge required!

## 📋 Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Components](#components)
- [Responsive Design](#responsive-design)
- [Event Handling](#event-handling)
- [Examples](#examples)
- [API Reference](#api-reference)

## 🌟 Overview

PyWeb lets you create web applications using Python classes and methods. It includes:

- **Pythonic component system** - Build UI with Python classes
- **Built-in responsive design** - Easy media queries with `qurell()`
- **Event handling** - Handle user interactions with Python functions
- **File uploads** - Built-in support for image/video uploads
- **No frontend knowledge required** - Everything is done in Python

## 🚀 Installation

1. **Install required dependencies:**
```bash
pip install flask
```

2. **Create a new Python file and import PyWeb:**
```python
from pyweb import create_app, serve_pyweb, StyleManager, Div, Text, Button, Input
```

## ⚡ Quick Start

Here's a simple "Hello World" application:

```python
from pyweb import create_app, serve_pyweb, Div, Text, Button

def create_app():
    app = create_app("My First App")
    home = app.add_page("home")
    
    # Create a simple page
    container = Div(class_name="container")
    container.add(Text("Hello, PyWeb!", tag="h1"))
    container.add(Text("Welcome to your first PyWeb application"))
    
    # Add a button
    btn = Button("Click Me!", "my_button")
    container.add(btn)
    
    # Add button click handler
    def on_button_click(page, eid, event, value, updates):
        updates["my_button"] = Button("Clicked!", "my_button").render()
    
    home.on("my_button", "click", on_button_click)
    home.add(container)
    
    return app

if __name__ == "__main__":
    app = create_app()
    flask_app = serve_pyweb(app)
    flask_app.run(debug=True, port=5000)
```

Run with: `python app.py` and visit `http://localhost:5000`

## 🧠 Core Concepts

### 1. Application Structure
```python
app = create_app("App Name")          # Create main application
page = app.add_page("page_name")      # Add a page
app.navigate("page_name")             # Navigate between pages
```

### 2. Components
Build UI by adding components to pages:
```python
page.add(Text("Hello World"))         # Add text
page.add(Button("Click", "btn_id"))   # Add button with ID
page.add(Div().add(Text("Nested")))   # Nested components
```

### 3. Styling
Use the StyleManager for CSS:
```python
style = StyleManager()
style.background("body", "#f0f0f0")
style.color(".card", "white")
style.padding("button", "10px 20px")
```

## 🎨 Responsive Design

PyWeb makes responsive design easy with the `qurell()` function:

### Basic Usage
```python
style.qurell('mobile', {
    '.card': 'width: 100%; margin: 10px 0;',
    'h1': 'font-size: 24px;'
})

style.qurell('tablet', {
    '.card': 'width: 48%; margin: 1%;',
    'h1': 'font-size: 28px;'
})

style.qurell('desktop', {
    '.card': 'width: 31%; margin: 1%;', 
    'h1': 'font-size: 32px;'
})
```

### Supported Breakpoints
- `'mobile'` - 480px
- `'tablet'` - 768px  
- `'small-desktop'` - 1024px
- `'desktop'` - 1200px
- `'large'` - 1440px
- Custom pixels: `600`, `1024`, `'900px'`

### Responsive Grid System
PyWeb includes a built-in 12-column grid system:
```python
row = Div(class_name="row")
col1 = Div(class_name="col-6")  # 50% width
col2 = Div(class_name="col-6")  # 50% width
row.add(col1)
row.add(col2)
```

## 🧩 Components

### Basic Components
```python
# Text elements
Text("Hello", tag="h1")              # Heading
Text("Paragraph", tag="p")           # Paragraph
Text("Span", tag="span")             # Inline text

# Buttons and inputs
Button("Submit", "btn_id")
Input("input_id", "text", "Placeholder")
TextArea("textarea_id", "Message")
Select("select_id", [("opt1", "Option 1"), ("opt2", "Option 2")])

# Media
Image("image.jpg", "img_id")
Video("video.mp4", "video_id")
InputFile("file_upload", "image/*")

# Containers
Div("container_id", "my-class")
UL().add(LI("Item 1")).add(LI("Item 2"))
```

### Forms
```python
form = Form("my_form", action="/submit")
form.add(Input("name", "text", "Your Name"))
form.add(Button("Submit", "submit_btn"))

def on_form_submit(page, eid, event, value, updates):
    print("Form data:", value)  # Access form data

page.on("my_form", "submit", on_form_submit)
```

## 🎯 Event Handling

### Handling Events
```python
def on_click(page, eid, event, value, updates):
    # Update components
    updates[eid] = Button("Clicked!", eid).render()
    # Or return redirect/script
    return {"redirect": "/new-page"}

page.on("button_id", "click", on_click)
```

### Supported Events
- `"click"` - Button clicks
- `"change"` - Input changes
- `"input"` - Real-time input
- `"submit"` - Form submissions
- `"file"` - File uploads

### File Uploads
```python
file_input = InputFile("uploader", "image/*")

def on_file_upload(page, eid, event, value, updates):
    # value contains base64 encoded file
    if "image" in value:
        # Process image
        updates["preview"] = Image(value, "preview_img").render()

page.on("uploader", "file", on_file_upload)
```

## 📱 Example: Responsive Blog

```python
from pyweb import create_app, serve_pyweb, StyleManager, Div, Text, Heading, Image

def create_blog():
    app = create_app("My Blog")
    home = app.add_page("home")
    
    # Responsive styling
    style = StyleManager()
    style.qurell('mobile', {
        '.post': 'width: 100%; margin: 10px 0;',
        '.sidebar': 'display: none;',
        'h1': 'font-size: 24px;'
    })
    
    style.qurell('tablet', {
        '.post': 'width: 48%; margin: 1%;',
        '.sidebar': 'width: 30%;',
        'h1': 'font-size: 28px;'
    })
    
    style.qurell('desktop', {
        '.post': 'width: 31%; margin: 1%;',
        '.sidebar': 'width: 25%;',
        'h1': 'font-size: 32px;'
    })
    
    # Layout
    container = Div(class_name="container")
    header = Div(class_name="header")
    header.add(Heading("My Responsive Blog", level=1))
    
    content = Div(class_name="row")
    posts = Div(class_name="col-8")
    sidebar = Div(class_name="col-4 sidebar")
    
    # Add blog posts
    for i in range(3):
        post = Div(class_name="card post")
        post.add(Heading(f"Blog Post {i+1}", level=2))
        post.add(Text("This is a blog post content..."))
        posts.add(post)
    
    # Add sidebar
    sidebar.add(Heading("Categories", level=3))
    sidebar.add(Text("• Python"))
    sidebar.add(Text("• Web Development"))
    sidebar.add(Text("• Responsive Design"))
    
    content.add(posts)
    content.add(sidebar)
    container.add(header)
    container.add(content)
    home.add(container)
    
    return app

if __name__ == "__main__":
    app = create_blog()
    flask_app = serve_pyweb(app)
    flask_app.run(debug=True, port=5000)
```

## 🔧 API Reference

### StyleManager Methods
- `.color(target, value)` - Text color
- `.background(target, value)` - Background
- `.padding(target, value)` - Padding
- `.margin(target, value)` - Margin
- `.width(target, value)` - Width
- `.height(target, value)` - Height
- `.qurell(breakpoint, rules)` - Media queries

### Component Properties
Most components support:
- `id` - Unique identifier
- `class_name` - CSS class
- `style` - Inline styles
- Event handlers via `.on()`

### App Navigation
```python
app.navigate("page_name")  # Switch pages
NavButton("Go Home", "home_btn", "home")  # Navigation button
```

## 🚀 Deployment

1. **Run locally:**
```bash
python app.py
```

2. **For production, use a WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:flask_app
```

## 💡 Tips & Best Practices

1. **Use the grid system** for responsive layouts
2. **Leverage qurell()** for device-specific styling
3. **Keep event handlers simple** - delegate complex logic to other functions
4. **Use consistent naming** for IDs and classes
5. **Test on multiple screen sizes** during development

## 🆘 Getting Help

If you encounter issues:
1. Check that Flask is installed
2. Verify component IDs are unique
3. Ensure event handlers are properly connected with `.on()`

## 📝 License

PyWeb is open source and free to use for any project.

---

**Happy coding!** With PyWeb, you can build beautiful, responsive web applications using the Python you already know and love.