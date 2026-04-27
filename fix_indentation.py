import re

with open('ml_integration.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the GPUAcceleratedMLEngine class and fix indentation
lines = content.split('\n')
in_class = False
in_method = False
fixed_lines = []
for line in lines:
    if line.strip().startswith('class GPUAcceleratedMLEngine:'):
        in_class = True
        fixed_lines.append(line)
    elif in_class:
        if line.strip().startswith('def ') or line.strip().startswith('async def '):
            # Method definition - should be indented 4 spaces
            if line.startswith('        '):
                fixed_lines.append('    ' + line[8:])
            else:
                fixed_lines.append(line)
            in_method = True
        elif in_method and line.strip() and not line.startswith('    ') and not line.startswith('        '):
            # End of method
            in_method = False
            fixed_lines.append(line)
        elif in_method and line.startswith('        '):
            # Method body - should be indented 8 spaces (4 for class + 4 for method)
            fixed_lines.append(line)
        elif in_method and line.startswith('    ') and not line.startswith('        '):
            # Method body that was over-indented - fix to 8 spaces
            fixed_lines.append('    ' + line[4:])
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

with open('ml_integration_fixed.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("Fixed file created as ml_integration_fixed.py")