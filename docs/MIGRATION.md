# Data Migration Guide

## Step-by-Step Process
1. **Source Connection**  
   ![Connection Wizard](static/description/screenshots/connection_wizard.png)

2. **Field Mapping**  
   Use AI-assist or manual drag-drop:  
   ![Mapping Interface](static/description/screenshots/mapping.png)

3. **Transformation Rules**  
   ```python
   # Sample custom transform
   def clean_phone(original):
       return original.replace(' ', '').removeprefix('+0')