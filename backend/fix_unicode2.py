import re

# Read the file
with open('app/services/invoice_processing_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode emojis with ASCII text
content = re.sub(r'❌', '[ERROR]', content)
content = re.sub(r'✅', '[SUCCESS]', content)
content = re.sub(r'🔍', '[INFO]', content)
content = re.sub(r'📊', '[INFO]', content)
content = re.sub(r'⚠️', '[WARNING]', content)
content = re.sub(r'🔄', '[PROCESSING]', content)

# Write back
with open('app/services/invoice_processing_service.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed Unicode emojis in invoice processing service')
