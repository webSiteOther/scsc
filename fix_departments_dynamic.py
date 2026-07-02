import re
import glob

def fix_departments_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find <select id="deptFilter"> or <select id="departmentId"> or similar and strip hardcoded options
    # Wait, we can just replace any <option> inside a select that is known to be a department dropdown
    # Actually, we can use a regex to replace the inner content of known department selects
    
    select_ids = ['deptFilter', 'departmentId', 'deptId', 'department']
    for s_id in select_ids:
        # Regex to find the select block
        pattern = re.compile(f'(<select[^>]*id="{s_id}"[^>]*>)(.*?)(</select>)', re.DOTALL)
        
        def replace_options(match):
            # Keep only the first option if it has value="" or value="all", otherwise empty
            inner = match.group(2)
            first_option = ""
            if 'value="all"' in inner or 'value=""' in inner:
                opt_match = re.search(r'<option value="(all|)">.*?</option>', inner)
                if opt_match:
                    first_option = opt_match.group(0) + "\n"
            return match.group(1) + "\n" + first_option + match.group(3)
            
        content = pattern.sub(replace_options, content)

    # Now make sure loadData or the equivalent populates it
    # Search for allDepartments usage or add it
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

for file in ['students.html', 'courses.html', 'schedule.html', 'reports.html']:
    fix_departments_html(file)

print("Fixed hardcoded departments in HTML files.")
