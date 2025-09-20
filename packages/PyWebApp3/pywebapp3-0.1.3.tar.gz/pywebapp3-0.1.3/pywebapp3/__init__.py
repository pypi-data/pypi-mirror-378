import os, base64, json, uuid
from flask import Flask, request, jsonify, send_from_directory

# ========== Uploads Folder ==========
UPLOAD_DIR = "pyweb_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ========== Style Manager ==========
class StyleManager:
    def __init__(self):
        self.rules = {"body": [], "id": {}, "class": {}}
        self.media_queries = {}
        
    def body(self, rule): 
        self.rules["body"].append(rule)
        
    def add_id(self, eid, rule): 
        self.rules["id"].setdefault(eid, []).append(rule)
        
    def add_class(self, cls, rule): 
        self.rules["class"].setdefault(cls, []).append(rule)
        
    def add_media_query(self, query, rules):
        self.media_queries[query] = rules
        
    def _smart_add(self, target, rule):
        if target == "body": 
            self.body(rule)
        elif target.startswith("."): 
            self.add_class(target[1:], rule)
        elif target.startswith("#"): 
            self.add_id(target[1:], rule)
        else: 
            self.add_id(target, rule)
            
    # Helper methods
    def position(self, target, value): 
        self._smart_add(target, f"position:{value};")
        
    def display(self, target, value): 
        self._smart_add(target, f"display:{value};")
        
    def padding(self, target, value): 
        self._smart_add(target, f"padding:{value};")
        
    def margin(self, target, value): 
        self._smart_add(target, f"margin:{value};")
        
    def color(self, target, value): 
        self._smart_add(target, f"color:{value};")
        
    def background(self, target, value): 
        self._smart_add(target, f"background:{value};")
        
    def width(self, target, value): 
        self._smart_add(target, f"width:{value};")
        
    def height(self, target, value): 
        self._smart_add(target, f"height:{value};")
        
    def border(self, target, value): 
        self._smart_add(target, f"border:{value};")
        
    def radius(self, target, value): 
        self._smart_add(target, f"border-radius:{value};")
        
    def fontsize(self, target, value): 
        self._smart_add(target, f"font-size:{value};")
        
    def fontweight(self, target, value): 
        self._smart_add(target, f"font-weight:{value};")
        
    def textalign(self, target, value): 
        self._smart_add(target, f"text-align:{value};")
        
    def top(self, target, value): 
        self._smart_add(target, f"top:{value}; position:absolute;")
        
    def left(self, target, value): 
        self._smart_add(target, f"left:{value}; position:absolute;")
        
    def right(self, target, value): 
        self._smart_add(target, f"right:{value}; position:absolute;")
        
    def bottom(self, target, value): 
        self._smart_add(target, f"bottom:{value}; position:absolute;")
        
    def flex(self, target, value): 
        self._smart_add(target, f"flex:{value};")
        
    def flex_direction(self, target, value): 
        self._smart_add(target, f"flex-direction:{value};")
        
    def justify_content(self, target, value): 
        self._smart_add(target, f"justify-content:{value};")
        
    def align_items(self, target, value): 
        self._smart_add(target, f"align-items:{value};")
        
    def gap(self, target, value): 
        self._smart_add(target, f"gap:{value};")
        
    def shadow(self, target, value): 
        self._smart_add(target, f"box-shadow:{value};")
        
    def transition(self, target, value): 
        self._smart_add(target, f"transition:{value};")
        
    def opacity(self, target, value): 
        self._smart_add(target, f"opacity:{value};")
        
    def zindex(self, target, value): 
        self._smart_add(target, f"z-index:{value};")
        
    def cursor(self, target, value): 
        self._smart_add(target, f"cursor:{value};")
        
    # Media Query Helper
    def qurell(self, breakpoint, rules_dict):
        """
        Add responsive media queries easily
        breakpoint: max-width in pixels or common names ('mobile', 'tablet', 'desktop')
        rules_dict: dictionary of CSS rules {selector: rules}
        
        Example:
        style.qurell('mobile', {'.card': 'width: 100%; margin: 10px 0;'})
        style.qurell(768, {'body': 'font-size: 14px;'})
        """
        # Convert common names to pixel values
        breakpoint_map = {
            'mobile': 480,
            'tablet': 768,
            'small-desktop': 1024,
            'desktop': 1200,
            'large': 1440
        }
        
        if isinstance(breakpoint, str) and breakpoint in breakpoint_map:
            max_width = breakpoint_map[breakpoint]
        elif isinstance(breakpoint, str) and breakpoint.endswith('px'):
            max_width = int(breakpoint.replace('px', ''))
        elif isinstance(breakpoint, int):
            max_width = breakpoint
        else:
            raise ValueError(f"Invalid breakpoint: {breakpoint}")
        
        # Build the media query rules
        query_rules = ""
        for selector, rules in rules_dict.items():
            query_rules += f"{selector} {{{rules}}} "
        
        self.add_media_query(f"max-width: {max_width}px", query_rules)
        
    def render(self):
        css = ""
        # Add body rules
        if self.rules["body"]: 
            css += f"body{{{''.join(self.rules['body'])}}}\n"
            
        # Add ID rules
        for eid, rules in self.rules["id"].items(): 
            css += f"#{eid}{{{''.join(rules)}}}\n"
            
        # Add class rules
        for cls, rules in self.rules["class"].items(): 
            css += f".{cls}{{{''.join(rules)}}}\n"
            
        # Add media queries
        for query, rules in self.media_queries.items():
            css += f"@media({query}){{{rules}}}\n"
            
        # Default Theme + Responsive
        css += """
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; 
               margin: 0; padding: 0; background-color: #f5f5f5; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 15px; }
        .row { display: flex; flex-wrap: wrap; margin: -10px; }
        .row > div { padding: 10px; }
        [class*="col-"] { flex: 1; }
        .col-1 { flex: 0 0 8.33%; max-width: 8.33%; }
        .col-2 { flex: 0 0 16.66%; max-width: 16.66%; }
        .col-3 { flex: 0 0 25%; max-width: 25%; }
        .col-4 { flex: 0 0 33.33%; max-width: 33.33%; }
        .col-5 { flex: 0 0 41.66%; max-width: 41.66%; }
        .col-6 { flex: 0 0 50%; max-width: 50%; }
        .col-7 { flex: 0 0 58.33%; max-width: 58.33%; }
        .col-8 { flex: 0 0 66.66%; max-width: 66.66%; }
        .col-9 { flex: 0 0 75%; max-width: 75%; }
        .col-10 { flex: 0 0 83.33%; max-width: 83.33%; }
        .col-11 { flex: 0 0 91.66%; max-width: 91.66%; }
        .col-12 { flex: 0 0 100%; max-width: 100%; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #fff; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 10px 0; transition: transform 0.2s, box-shadow 0.2s; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .navbar { display: flex; justify-content: space-between; align-items: center; 
                  padding: 15px 20px; background: #007BFF; color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar a { color: white; margin: 0 15px; text-decoration: none; font-weight: 500; }
        .navbar a:hover { text-decoration: underline; }
        button { background: #007BFF; color: white; padding: 10px 20px; border: none; 
                 border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.2s; }
        button:hover { background: #0056b3; }
        button.secondary { background: #6c757d; }
        button.secondary:hover { background: #5a6268; }
        button.success { background: #28a745; }
        button.success:hover { background: #218838; }
        button.danger { background: #dc3545; }
        button.danger:hover { background: #c82333; }
        input, select, textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; 
                                  width: 100%; font-size: 16px; margin: 5px 0; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #007BFF; box-shadow: 0 0 0 2px rgba(0,123,255,0.25); }
        label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group { margin-bottom: 15px; }
        img, video { max-width: 100%; height: auto; border-radius: 4px; }
        ul { list-style-type: disc; padding-left: 20px; }
        li { margin: 8px 0; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: 600; }
        tr:hover { background-color: #f5f5f5; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                 background-color: rgba(0,0,0,0.5); z-index: 1000; }
        .modal-content { background-color: #fff; margin: 10% auto; padding: 20px; border-radius: 8px; 
                         width: 80%; max-width: 600px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .close { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: #000; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-danger { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .alert-info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .badge { display: inline-block; padding: 3px 8px; font-size: 12px; font-weight: 700; 
                 line-height: 1; text-align: center; white-space: nowrap; vertical-align: baseline; 
                 border-radius: 10px; }
        .badge-primary { background-color: #007bff; color: white; }
        .badge-secondary { background-color: #6c757d; color: white; }
        .badge-success { background-color: #28a745; color: white; }
        .badge-danger { background-color: #dc3545; color: white; }
        .badge-warning { background-color: #ffc107; color: #212529; }
        .badge-info { background-color: #17a2b8; color: white; }
        .progress { height: 20px; background-color: #e9ecef; border-radius: 4px; overflow: hidden; }
        .progress-bar { height: 100%; background-color: #007bff; text-align: center; line-height: 20px; color: white; }
        .tooltip { position: relative; display: inline-block; }
        .tooltip .tooltiptext { visibility: hidden; width: 120px; background-color: #555; color: #fff; 
                                text-align: center; border-radius: 6px; padding: 5px; position: absolute; 
                                z-index: 1; bottom: 125%; left: 50%; margin-left: -60px; opacity: 0; transition: opacity 0.3s; }
        .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; 
                   width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        """
        return css

style = StyleManager()

# ========== Base Classes ==========
class Element:
    def render(self): 
        raise NotImplementedError("Subclasses must implement render()")
        
    def scripts(self): 
        return ""
        
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

class Page:
    def __init__(self, name):
        self.name = name
        self.elements = []
        self.routes = {}
        
    def add(self, el): 
        self.elements.append(el)
        
    def on(self, eid, event, handler): 
        self.routes[(eid, event)] = handler
        
    def get(self, eid):
        for e in self.elements:
            if getattr(e, "id", None) == eid: 
                return e
            # Check children recursively
            if hasattr(e, 'children'):
                for child in e.children:
                    if getattr(child, "id", None) == eid:
                        return child
        return None
        
    def render(self):
        body = "\n".join([e.render() for e in self.elements])
        scripts = "".join([e.scripts() for e in self.elements])
        return body, scripts

class App:
    def __init__(self, name="PyWeb App"):
        self.name = name
        self.pages = {}
        self.current = "home"
        self.session_data = {}
        
    def add_page(self, page_name):
        page = Page(page_name)
        self.pages[page_name] = page
        return page
        
    def navigate(self, page_name):
        if page_name in self.pages: 
            self.current = page_name
            
    def current_page(self):
        return self.pages.get(self.current)
        
    def render(self):
        page = self.current_page()
        if not page: 
            return "<h1>Page Not Found</h1>"
            
        body, scripts = page.render()
        session_id = str(uuid.uuid4())
        self.session_data[session_id] = {"page": self.current}
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <title>{self.name} - {self.current}</title>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
          <style>{style.render()}</style>
        </head>
        <body>
          {body}
          <script>
            let session_id = "{session_id}";
            
            async function pyweb_emit(id, event, value=null){{
                let res = await fetch('/_pyweb_event', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        id: id, 
                        event: event, 
                        value: value, 
                        page: "{self.current}",
                        session_id: session_id
                    }})
                }});
                let data = await res.json();
                if(data.update) {{
                    for(let [eid, html] of Object.entries(data.update)){{
                        let el = document.getElementById(eid); 
                        if(el) el.outerHTML = html;
                    }}
                }}
                if(data.redirect) {{
                    window.location.href = data.redirect;
                }}
                if(data.script) {{
                    eval(data.script);
                }}
            }}
            
            async function pyweb_navigate(page_name){{
                let res = await fetch('/_pyweb_navigate', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{
                        page: page_name,
                        session_id: session_id
                    }})
                }});
                let data = await res.json();
                if(data.status === 'ok') {{
                    window.location.reload();
                }}
            }}
            
            {scripts}
          </script>
        </body>
        </html>
        """

def create_app(name="PyWeb App"): 
    return App(name)

# ========== Components ==========
class Div(Element):
    def __init__(self, id=None, class_name=None, style=None):
        self.id = id
        self.class_name = class_name
        self.style = style
        self.children = []
        
    def add(self, el): 
        self.children.append(el)
        
    def render(self): 
        style_attr = f' style="{self.style}"' if self.style else ""
        return f'<div id="{self.id or ""}" class="{self.class_name or ""}"{style_attr}>' + \
               "".join([c.render() for c in self.children]) + "</div>"
               
    def scripts(self): 
        return "".join([c.scripts() for c in self.children])

class Text(Element):
    def __init__(self, text, id=None, tag="p", class_name=None, style=None):
        self.text = text
        self.id = id
        self.style=style
        self.tag = tag
        self.class_name = class_name
        
    def render(self): 
        return f'<{self.tag} id="{self.id or ""}" class="{self.class_name or ""}" style="{self.style or ""}">{self.text}</{self.tag}>'

class Heading(Text):
    def __init__(self, text, level=1, id=None, class_name=None, style=None):
        super().__init__(text, id, f"h{level}", class_name, style)

class Button(Element):
    def __init__(self, text, id, class_name=None, style=None):
        self.text = text
        self.id = id
        self.class_name = class_name
        self.style = style
        
    def render(self): 
        style_attr = f' style="{self.style}"' if self.style else ""
        return f'<button id="{self.id}" class="{self.class_name or ""}"{style_attr}>{self.text}</button>'
        
    def scripts(self): 
        return f'document.getElementById("{self.id}").onclick=()=>pyweb_emit("{self.id}","click");'

class NavButton(Button):
    def __init__(self, text, id, target_page, class_name=None):
        super().__init__(text, id, class_name)
        self.target_page = target_page

    def scripts(self):
        return f'document.getElementById("{self.id}").onclick=()=>pyweb_navigate("{self.target_page}");'

class Input(Element):
    def __init__(self, id, input_type="text", placeholder="", value="", class_name=None, style=None):
        self.id = id
        self.style = style
        self.type = input_type
        self.placeholder = placeholder
        self.value = value
        self.class_name = class_name
        
    def render(self): 
        return f'<input type="{self.type}" id="{self.id}" placeholder="{self.placeholder}" value="{self.value}" style="{self.style or ""}" class="{self.class_name or ""}"/>'
        
    def scripts(self): 
        if self.type in ["text", "email", "password", "number"]:
            return f'''
            document.getElementById("{self.id}").onchange=(e)=>pyweb_emit("{self.id}","change",e.target.value);
            document.getElementById("{self.id}").oninput=(e)=>pyweb_emit("{self.id}","input",e.target.value);
            '''
        elif self.type in ["checkbox", "radio"]:
            return f'''
            document.getElementById("{self.id}").onchange=(e)=>pyweb_emit("{self.id}","change",e.target.checked);
            '''
        return ""

class TextArea(Element):
    def __init__(self, id, placeholder="", value="", rows=4, class_name=None, style=None):
        self.id = id
        self.placeholder = placeholder
        self.value = value
        self.rows = rows
        self.style = style
        self.class_name = class_name
        
    def render(self): 
        return f'<textarea id="{self.id}" placeholder="{self.placeholder}" rows="{self.rows}" class="{self.class_name or ""}" style="{self.style or ""}">{self.value}</textarea>'
        
    def scripts(self): 
        return f'''
        document.getElementById("{self.id}").onchange=(e)=>pyweb_emit("{self.id}","change",e.target.value);
        document.getElementById("{self.id}").oninput=(e)=>pyweb_emit("{self.id}","input",e.target.value);
        '''

class Select(Element):
    def __init__(self, id, options, selected=None, class_name=None, style=None):
        self.id = id
        self.options = options  # List of (value, text) tuples
        self.selected = selected
        self.class_name = class_name
        self.style = style
        
    def render(self): 
        options_html = ""
        for value, text in self.options:
            selected_attr = " selected" if value == self.selected else ""
            options_html += f'<option value="{value}"{selected_attr}>{text}</option>'
            
        return f'<select id="{self.id}" class="{self.class_name or ""}" style="{self.style or ""}">{options_html}</select>'
        
    def scripts(self): 
        return f'''
        document.getElementById("{self.id}").onchange=(e)=>pyweb_emit("{self.id}","change",e.target.value);
        '''

class Image(Element):
    def __init__(self, src=None, id=None, alt="", width=None, height=None, class_name=None, style=None):
        self.src = src
        self.id = id
        self.alt = alt
        self.width = width
        self.height = height
        self.class_name = class_name
        self.style = style
        
    def render(self):
        w = f' width="{self.width}"' if self.width else ""
        h = f' height="{self.height}"' if self.height else ""
        cls = f' class="{self.class_name}"' if self.class_name else ""
        return f'<img id="{self.id or ""}" style="{self.style or ""}" src="{self.src or ""}" alt="{self.alt}"{w}{h}{cls}/>'

class Video(Element):
    def __init__(self, src=None, id=None, controls=True, width=None, height=None, class_name=None, style=None):
        self.src = src
        self.id = id
        self.controls = controls
        self.width = width
        self.style = style
        self.height = height
        self.class_name = class_name
        
    def render(self):
        ctrl = "controls" if self.controls else ""
        w = f' width="{self.width}"' if self.width else ""
        h = f' height="{self.height}"' if self.height else ""
        cls = f' class="{self.class_name}"' if self.class_name else ""
        return f'<video id="{self.id or ""}" style="{self.style or ""}" src="{self.src or ""}" {ctrl}{w}{h}{cls}></video>'

class InputFile(Element):
    def __init__(self, id, accept=None, class_name=None, style=None):
        self.id = id
        self.accept = accept
        self.class_name = class_name
        self.style = style
        
    def render(self): 
        accept_attr = f' accept="{self.accept}"' if self.accept else ""
        cls = f' class="{self.class_name}"' if self.class_name else ""
        return f'<input type="file" style="{self.style or ""}" id="{self.id}"{accept_attr}{cls}/>'
        
    def scripts(self):
        return f'''
        document.getElementById("{self.id}").onchange=(e)=>{{
            let file=e.target.files[0];
            let reader=new FileReader();
            reader.onload=function(){{ pyweb_emit("{self.id}","file",reader.result); }};
            reader.readAsDataURL(file);
        }};
        '''

class UL(Element):
    def __init__(self, id=None, class_name=None):
        self.id = id
        self.class_name = class_name
        self.children = []
        
    def add(self, el): 
        self.children.append(el)
        
    def render(self): 
        cls = f' class="{self.class_name}"' if self.class_name else ""
        return f'<ul id="{self.id or ""}"{cls}>' + "".join([c.render() for c in self.children]) + "</ul>"

class LI(Element):
    def __init__(self, text, id=None, class_name=None):
        self.text = text
        self.id = id
        self.class_name = class_name
        
    def render(self): 
        cls = f' class="{self.class_name}"' if self.class_name else ""
        return f'<li id="{self.id or ""}"{cls}>{self.text}</li>'

class Table(Element):
    def __init__(self, id=None, class_name=None, headers=None, data=None):
        self.id = id
        self.class_name = class_name
        self.headers = headers or []
        self.data = data or []
        
    def render(self):
        cls = f' class="{self.class_name}"' if self.class_name else ""
        headers_html = "".join([f"<th>{h}</th>" for h in self.headers])
        rows_html = ""
        
        for row in self.data:
            rows_html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
            
        return f'<table id="{self.id or ""}"{cls}><thead><tr>{headers_html}</tr></thead><tbody>{rows_html}</tbody></table>'

class Form(Element):
    def __init__(self, id=None, class_name=None, action="", method="POST"):
        self.id = id
        self.class_name = class_name
        self.action = action
        self.method = method
        self.children = []
        
    def add(self, el): 
        self.children.append(el)
        
    def render(self): 
        cls = f' class="{self.class_name}"' if self.class_name else ""
        return f'<form id="{self.id or ""}" action="{self.action}" method="{self.method}"{cls}>' + \
               "".join([c.render() for c in self.children]) + "</form>"
               
    def scripts(self): 
        form_script = f'''
        document.getElementById("{self.id}").onsubmit = (e) => {{
            e.preventDefault();
            let formData = new FormData(e.target);
            let data = Object.fromEntries(formData.entries());
            pyweb_emit("{self.id}", "submit", data);
        }};
        '''
        return form_script + "".join([c.scripts() for c in self.children])

class Modal(Element):
    def __init__(self, id, title, content, show_close=True):
        self.id = id
        self.title = title
        self.content = content
        self.show_close = show_close
        
    def render(self):
        close_btn = '<span class="close">&times;</span>' if self.show_close else ''
        return f'''
        <div id="{self.id}" class="modal">
            <div class="modal-content">
                {close_btn}
                <h2>{self.title}</h2>
                <div>{self.content.render() if hasattr(self.content, 'render') else self.content}</div>
            </div>
        </div>
        '''
        
    def scripts(self):
        close_script = f'''
        document.querySelector("#{self.id} .close").onclick = function() {{
            document.getElementById("{self.id}").style.display = "none";
        }};
        window.onclick = function(event) {{
            if (event.target == document.getElementById("{self.id}")) {{
                document.getElementById("{self.id}").style.display = "none";
            }}
        }};
        ''' if self.show_close else ''
        
        content_script = self.content.scripts() if hasattr(self.content, 'scripts') else ''
        return close_script + content_script

class Alert(Element):
    def __init__(self, id, message, alert_type="info", dismissible=True):
        self.id = id
        self.message = message
        self.type = alert_type
        self.dismissible = dismissible
        
    def render(self):
        dismiss_btn = '<button type="button" class="close" data-dismiss="alert">&times;</button>' if self.dismissible else ''
        return f'<div id="{self.id}" class="alert alert-{self.type}">{dismiss_btn}{self.message}</div>'
        
    def scripts(self):
        if self.dismissible:
            return f'''
            document.querySelector("#{self.id} .close").onclick = function() {{
                document.getElementById("{self.id}").style.display = "none";
            }};
            '''
        return ""

class Progress(Element):
    def __init__(self, id, value=0, max=100, class_name=None):
        self.id = id
        self.value = value
        self.max = max
        self.class_name = class_name
        
    def render(self):
        cls = f' class="{self.class_name}"' if self.class_name else ''
        return f'''
        <div id="{self.id}"{cls}>
            <div class="progress">
                <div class="progress-bar" role="progressbar" style="width: {self.value}%;" 
                     aria-valuenow="{self.value}" aria-valuemin="0" aria-valuemax="{self.max}">
                    {self.value}%
                </div>
            </div>
        </div>
        '''

# ========== Flask Integration ==========
def serve_pyweb(app: App):
    flaskapp = Flask(__name__)
    
    @flaskapp.route("/")
    def index(): 
        return app.render()

    @flaskapp.route("/_pyweb_event", methods=["POST"])
    def handle_event():
        data = request.json
        eid = data["id"]
        event = data["event"]
        value = data.get("value")
        page_name = data.get("page", app.current)
        session_id = data.get("session_id")
        
        updates = {}
        redirect = None
        script = None
        
        page_obj = app.pages.get(page_name)
        if not page_obj:
            return jsonify({"update": {}})
            
        # Handle file decoding
        if event == "file" and value:
            try:
                header, b64 = value.split(",", 1)
                if "image" in header:
                    ext = "png"
                elif "video" in header:
                    ext = "mp4"
                elif "pdf" in header:
                    ext = "pdf"
                else:
                    ext = "bin"
                    
                filename = f"{eid}_{session_id or 'default'}.{ext}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(b64))
                    
                el = page_obj.get(eid)
                if el and isinstance(el, (Image, Video)):
                    el.src = f"/uploads/{filename}"
                    updates[eid] = el.render()
            except Exception as e:
                print("File decode error:", e)
                
        # Call user-defined event handler
        handler = page_obj.routes.get((eid, event))
        if handler:
            result = handler(page_obj, eid, event, value, updates)
            if result and isinstance(result, dict):
                if "redirect" in result:
                    redirect = result["redirect"]
                if "script" in result:
                    script = result["script"]
                    
        return jsonify({"update": updates, "redirect": redirect, "script": script})

    @flaskapp.route("/_pyweb_navigate", methods=["POST"])
    def navigate_page():
        data = request.json
        page_name = data.get("page")
        session_id = data.get("session_id")
        
        if session_id and session_id in app.session_data:
            app.session_data[session_id]["page"] = page_name
            
        if page_name in app.pages:
            app.navigate(page_name)
            
        return jsonify({"status": "ok"})

    @flaskapp.route("/uploads/<path:filename>")
    def serve_file(filename):
        return send_from_directory(UPLOAD_DIR, filename)

    return flaskapp