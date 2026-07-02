def fix_courses_html():
    with open('courses.html', 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_call = "await apiCall('saveAddOn', { addonData: data });"
    new_call = "await apiCall('saveAddOn', data);"
    content = content.replace(old_call, new_call)
    
    with open('courses.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
if __name__ == '__main__':
    fix_courses_html()
