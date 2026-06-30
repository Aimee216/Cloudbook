import json, os

js_code = open(os.path.join(os.path.dirname(__file__), 'frontend', 'modules_template.js'), 'r', encoding='utf-8').read()
with open(os.path.join(os.path.dirname(__file__), 'frontend', 'modules.js'), 'w', encoding='utf-8') as f:
    f.write(js_code)
print('OK')
