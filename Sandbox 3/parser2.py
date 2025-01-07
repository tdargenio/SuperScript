import tkinter as tk
from tkinter import messagebox
import re

def parse_superscript(code):
    parsed_code = {
        "elements": [],
        "styles": {},
        "texts": {},
        "actions": {},
        "forms": {}
    }
    
    lines = [line.strip() for line in code.split("\n") if line.strip()]
    
    for line in lines:
        if "<3" in line:
            nested_parts = line.split("<3")
            for part in nested_parts:
                part = part.strip()
                if part:
                    parse_command(part, parsed_code)
        else:
            parse_command(line, parsed_code)
    
    # Automatically append forms to the page if not already in actions
    for form_name in list(parsed_code["forms"].keys()):
        if form_name not in parsed_code["actions"].get("page", []):
            if "page" in parsed_code["actions"]:
                parsed_code["actions"]["page"].append(form_name)
            else:
                parsed_code["actions"]["page"] = [form_name]
    
    return parsed_code

def parse_command(command, parsed_code):
    print(f"Parsing command: {command}")  # Debugging: Print the command being parsed

    # Form Creation
    make_form_match = re.match(r"Make a form named (\w+)", command, re.IGNORECASE)
    if make_form_match:
        form_name = make_form_match.group(1)
        parsed_code["forms"][form_name] = {"elements": []}
        parsed_code["elements"].append(form_name)
        parsed_code["styles"][form_name] = {'tagName': 'form'}
        print(f"Created form: {form_name}")  # Debugging: Print created form
        return
    
    # Input Creation
    make_input_match = re.match(r"Make a (\w+[\s\w]*) input named (\w+) inside (\w+)", command, re.IGNORECASE)
    if make_input_match:
        input_type_full = make_input_match.group(1)
        input_type = input_type_full.split()[0]
        input_name = make_input_match.group(2)
        form_name = make_input_match.group(3)
        parsed_code["forms"][form_name]["elements"].append({
            "type": "input",
            "name": input_name,
            "inputType": input_type
        })
        parsed_code["elements"].append(input_name)
        parsed_code["styles"][input_name] = {'tagName': 'input'}
        print(f"Created input: {input_name} of type {input_type} inside {form_name}")
        return
    
    # Set Placeholder
    set_placeholder_match = re.match(r"Set placeholder of (\w+) to '(.*?)'", command, re.IGNORECASE)
    if set_placeholder_match:
        input_name = set_placeholder_match.group(1)
        placeholder_text = set_placeholder_match.group(2)
        for form_name, form_data in parsed_code["forms"].items():
            for elem in form_data["elements"]:
                if elem["name"] == input_name:
                    elem["placeholder"] = placeholder_text
                    print(f"Set placeholder for {input_name} to '{placeholder_text}'")  # Debugging: Print placeholder set
        return
    
    # Button Creation
    make_button_match = re.match(r"Make a (\w+[\s\w]*) button named (\w+) inside (\w+)", command, re.IGNORECASE)
    if make_button_match:
        button_type_full = make_button_match.group(1)
        button_type = button_type_full.split()[0]  # Extract the first word as button type
        button_name = make_button_match.group(2)
        form_name = make_button_match.group(3)
        parsed_code["forms"][form_name]["elements"].append({
            "type": "button",
            "name": button_name,
            "buttonType": button_type
        })
        parsed_code["elements"].append(button_name)
        parsed_code["styles"][button_name] = {'tagName': 'button'}
        print(f"Created button: {button_name} of type {button_type} inside {form_name}")  # Debugging: Print created button
        return
    
    # Event Handling for Form Submission
    when_form_submit_match = re.match(r"When (\w+) is submitted, send data to '(.*?)'", command, re.IGNORECASE)
    if when_form_submit_match:
        form_name = when_form_submit_match.group(1)
        url = when_form_submit_match.group(2)
        parsed_code["forms"][form_name]["onSubmit"] = url
        print(f"Set form submission for {form_name} to send data to '{url}'")  # Debugging: Print form submission handler
        return
    
    # Event Handling for Button Click
    when_button_click_match = re.match(r"When (\w+) is clicked, submit the form", command, re.IGNORECASE)
    if when_button_click_match:
        button_name = when_button_click_match.group(1)
        for form_name, form_data in parsed_code["forms"].items():
            for elem in form_data["elements"]:
                if elem["name"] == button_name:
                    elem["formToSubmit"] = form_name  # Store the form name
                    print(f"Set button {button_name} to submit form {form_name}")  # Debugging: Print button click handler
        return
    
    # Element Creation
    make_a_match = re.match(r"Make a (\w+) named (\w+)", command, re.IGNORECASE)
    if make_a_match:
        element_type = make_a_match.group(1).lower()
        element_name = make_a_match.group(2)
        parsed_code["elements"].append(element_name)
        print(f"Created element: {element_name} of type {element_type}")  # Debugging: Print created element
        # Map element types to HTML elements
        if element_type == 'container':
            parsed_code["styles"][element_name] = {'tagName': 'div'}
        elif element_type == 'button':
            parsed_code["styles"][element_name] = {'tagName': 'button'}
        elif element_type == 'heading':
            parsed_code["styles"][element_name] = {'tagName': 'h1'}
        elif element_type == 'form':
            parsed_code["styles"][element_name] = {'tagName': 'form'}
        return
    
    # Setting Text Content
    make_say_match = re.match(r"Make (\w+) say (.+)", command, re.IGNORECASE)
    if make_say_match:
        element_name = make_say_match.group(1)
        text_content = make_say_match.group(2).strip('"').strip("'").rstrip('.')
        parsed_code["texts"][element_name] = text_content
        print(f"Set text for {element_name} to '{text_content}'")
        return
    
    # Setting Styles
    make_the_match = re.match(r"Make the (\w+) of (\w+) (.+)", command, re.IGNORECASE)
    if make_the_match:
        property_name = make_the_match.group(1)
        element_name = make_the_match.group(2)
        property_value = make_the_match.group(3).rstrip('.')
        if element_name not in parsed_code["styles"]:
            parsed_code["styles"][element_name] = {}
        # Correct width value
        if 'pixels' in property_value:
            property_value = property_value.replace(' pixels', 'px').replace(' wide', '')
        parsed_code["styles"][element_name][property_name] = property_value
        print(f"Set style for {element_name}: {property_name} = {property_value}")  # Debugging: Print style set
        return
    
    # General Make Command
    make_match = re.match(r"Make (\w+) (.+)", command, re.IGNORECASE)
    if make_match:
        element_name = make_match.group(1)
        property_value = make_match.group(2).rstrip('.')
        if 'pixels' in property_value:
            property_name = 'width' if 'wide' in command else 'height'
            property_value = property_value.replace(' pixels', 'px').replace(' wide', '')
        elif property_value.startswith('#') or property_value in ['red', 'blue', 'green']:
            property_name = 'backgroundColor'
        else:
            property_name = 'color'
        if element_name not in parsed_code["styles"]:
            parsed_code["styles"][element_name] = {}
        parsed_code["styles"][element_name][property_name] = property_value
        print(f"Set property for {element_name}: {property_name} = {property_value}")  # Debugging: Print property set
        return
    
    # Appending Elements
    put_match = re.match(r"Put (\w+) inside (\w+)", command, re.IGNORECASE)
    if put_match:
        element_name = put_match.group(1)
        container_name = put_match.group(2)
        if container_name in parsed_code["actions"]:
            parsed_code["actions"][container_name].append(element_name)
        else:
            parsed_code["actions"][container_name] = [element_name]
        print(f"Put {element_name} inside {container_name}")  # Debugging: Print element appended
        return
    
    # Event Handling
    when_match = re.match(r"When (\w+) is (\w+), show (.+)", command, re.IGNORECASE)
    if when_match:
        element_name = when_match.group(1)
        event_name = when_match.group(2)
        message = when_match.group(3).rstrip('.')
        # Remove surrounding quotes from message
        if message.startswith("'") and message.endswith("'"):
            message = message[1:-1]
        event_mappings = {
            'clicked': 'click',
            'hovered': 'mouseover',
            'focused': 'focus'
        }
        event_name = event_mappings.get(event_name, event_name)
        if element_name in parsed_code["actions"]:
            parsed_code["actions"][element_name].append(('event', event_name, message))
        else:
            parsed_code["actions"][element_name] = [('event', event_name, message)]
        print(f"Set event for {element_name}: {event_name} -> show '{message}'")  # Debugging: Print event handler
        return
    
    # Page Commands
    put_page_match = re.match(r"Put (\w+) inside page", command, re.IGNORECASE)
    if put_page_match:
        element_name = put_page_match.group(1)
        if "page" in parsed_code["actions"]:
            parsed_code["actions"]["page"].append(element_name)
        else:
            parsed_code["actions"]["page"] = [element_name]
        print(f"Put {element_name} inside page")  # Debugging: Print element appended to page
        return
    
    # Unknown command
    print(f"Unrecognized command: {command}")  # Debugging: Print unrecognized command

def translate_to_js(parsed_code):
    js_code = ""
    
    # Helper function to convert hyphenated strings to camelCase
    def to_camel_case(snake_str):
        components = snake_str.split('-')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    # Helper function to escape quotes in strings for JavaScript
    def escape_js_string(s):
        return s.replace("'", "\\'").replace('"', '\\"')
    
    # Track appended elements to prevent duplicates
    js_appended_elements = set()
    
    # Create elements
    for element in parsed_code["elements"]:
        element_type = parsed_code["styles"].get(element, {}).get('tagName', element.lower())
        js_code += f"const {element} = document.createElement('{element_type}');\n"
    
    # Set styles
    for element, props in parsed_code["styles"].items():
        for prop, val in props.items():
            if prop == 'tagName':
                continue  # Skip tagName as it's used for element creation
            prop_camel_case = to_camel_case(prop)
            js_code += f"{element}.style.{prop_camel_case} = '{val}';\n"
    
    # Set text content
    for element, text in parsed_code["texts"].items():
        js_code += f"{element}.innerText = \"{escape_js_string(text)}\";\n"
    
    # Generate Form Elements
    for form_name, form_data in parsed_code["forms"].items():
        if "onSubmit" in form_data:
            url = form_data["onSubmit"]
            js_code += f"{form_name}.addEventListener('submit', function(event) {{\n"
            js_code += f"    event.preventDefault();\n"
            js_code += f"    const formData = new FormData({form_name});\n"
            js_code += f"    fetch('{url}', {{\n"
            js_code += f"        method: 'POST',\n"
            js_code += f"        body: formData\n"
            js_code += f"    }})\n"
            js_code += f"    .then(response => response.text())\n"
            js_code += f"    .then(data => console.log(data))\n"
            js_code += f"    .catch(error => console.error('Error:', error));\n"
            js_code += f"}});\n"
        for elem in form_data["elements"]:
            if elem["type"] == "input":
                js_code += f"{elem['name']}.type = '{elem['inputType']}';\n"
                js_code += f"{elem['name']}.placeholder = '{elem['placeholder']}';\n"
                js_code += f"{form_name}.appendChild({elem['name']});\n"
            elif elem["type"] == "button":
                js_code += f"{elem['name']}.type = '{elem['buttonType']}';\n"
                if elem['name'] in parsed_code["texts"]:
                    js_code += f"{elem['name']}.innerText = '{parsed_code['texts'][elem['name']]}';\n"
                if "formToSubmit" in elem:
                    js_code += f"{elem['name']}.form = {elem['formToSubmit']};\n"
                js_code += f"{form_name}.appendChild({elem['name']});\n"
    
    # Append children and event listeners
    for container, actions in parsed_code["actions"].items():
        for action in actions:
            if isinstance(action, tuple) and action[0] == 'event':
                event_name, message = action[1], action[2]
                js_code += f"{container}.addEventListener('{event_name}', function() {{ alert('{message}'); }});\n"
            else:
                if container == "page":
                    if action not in js_appended_elements:
                        js_code += f"document.body.appendChild({action});\n"
                        js_appended_elements.add(action)
                else:
                    if action not in js_appended_elements:
                        js_code += f"{container}.appendChild({action});\n"
                        js_appended_elements.add(action)
    
    return js_code

def run_app():
    root = tk.Tk()
    root.title("Superscript Parser")
    
    input_label = tk.Label(root, text="Paste Superscript Code:")
    input_label.pack(pady=5)
    
    input_box = tk.Text(root, height=10, width=50)
    input_box.pack(pady=5)
    
    parse_button = tk.Button(root, text="Parse and Translate", command=lambda: parse_and_translate(input_box.get("1.0", "end-1c"), parsed_output_box, js_output_box))
    parse_button.pack(pady=10)
    
    parsed_output_label = tk.Label(root, text="Parsed Output:")
    parsed_output_label.pack(pady=5)
    
    parsed_output_box = tk.Text(root, height=5, width=50)
    parsed_output_box.pack(pady=5)
    
    js_output_label = tk.Label(root, text="Translated JavaScript:")
    js_output_label.pack(pady=5)
    
    js_output_scroll = tk.Scrollbar(root)
    js_output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    js_output_box = tk.Text(root, height=10, width=50, yscrollcommand=js_output_scroll.set)
    js_output_box.pack(pady=5)
    js_output_scroll.config(command=js_output_box.yview)
    
    root.mainloop()

def parse_and_translate(input_code, parsed_output_box, js_output_box):
    if not input_code.strip():
        messagebox.showwarning("Input Error", "Please enter Superscript code to parse.")
        return
    
    try:
        parsed_output = parse_superscript(input_code)
        js_code = translate_to_js(parsed_output)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return
    
    parsed_output_box.delete(1.0, "end")
    parsed_output_box.insert("end", str(parsed_output))
    
    js_output_box.delete(1.0, "end")
    js_output_box.insert("end", js_code)

if __name__ == "__main__":
    run_app()