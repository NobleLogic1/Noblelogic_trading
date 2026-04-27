with open('ml_integration.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Replace 8 spaces with 4 spaces for the GPUAcceleratedMLEngine class methods
import re
# Find the class and fix indentation
pattern = r'(class GPUAcceleratedMLEngine:.*?)(?=^class|^#|^$|^\w)'
match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
if match:
    class_content = match.group(1)
    # Replace method definitions from 8 spaces to 4 spaces
    class_content = re.sub(r'^        (def|async def)', r'    \1', class_content, flags=re.MULTILINE)
    # Replace method body from 12 spaces to 8 spaces  
    class_content = re.sub(r'^            ', r'        ', class_content, flags=re.MULTILINE)
    content = content.replace(match.group(1), class_content)

with open('ml_integration_fixed2.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed file created as ml_integration_fixed2.py')