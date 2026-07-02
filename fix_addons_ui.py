import re

with open("courses.html", "r", encoding="utf-8") as f:
    content = f.read()

# Update Modal UI
old_modal_html = """                <div class="form-group">
                    <label>الكورس المرتبط (اختياري)</label>
                    <select id="addonCourseId">
                        <option value="">بدون ارتباط</option>
                    </select>
                </div>"""

new_modal_html = """                <div class="form-group">
                    <label>القسم المرتبط</label>
                    <select id="addonDeptId">
                        <option value="">بدون ارتباط</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>الكورس المرتبط</label>
                    <select id="addonCourseId">
                        <option value="">بدون ارتباط</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>الحالة</label>
                    <select id="addonStatus">
                        <option value="نشط">نشط</option>
                        <option value="متوقف">متوقف</option>
                    </select>
                </div>"""
if 'addonDeptId' not in content:
    # use regex because Arabic text might differ
    pattern = re.compile(r'<div class="form-group">\s*<label>.*?</label>\s*<select id="addonCourseId">.*?</select>\s*</div>', re.DOTALL)
    content = pattern.sub(new_modal_html, content)

# Update Javascript
js_edit = """            document.getElementById('addonId').value = addon.id;
            document.getElementById('addonName').value = addon.name || '';
            document.getElementById('addonPrice').value = addon.price || 0;
            document.getElementById('addonDeptId').value = addon.deptId || '';
            document.getElementById('addonCourseId').value = addon.courseId || '';
            document.getElementById('addonStatus').value = addon.status || 'نشط';"""
content = re.sub(r"document\.getElementById\('addonId'\)\.value = addon\.id;.*?(?=document\.getElementById\('addonModal'\))", js_edit + "\n            ", content, flags=re.DOTALL)

js_save = """        const data = {
            id: document.getElementById('addonId').value || null,
            name: document.getElementById('addonName').value,
            price: document.getElementById('addonPrice').value,
            deptId: document.getElementById('addonDeptId').value,
            courseId: document.getElementById('addonCourseId').value,
            status: document.getElementById('addonStatus').value
        };"""
content = re.sub(r'const data = \{\s*id: document\.getElementById\(\'addonId\'\)\.value \|\| null,.*?addonCourseId\'\)\.value\s*\};', js_save, content, flags=re.DOTALL)

# Update loadData to populate deptId
# We can find allDepartments.map and duplicate it for addonDeptId
js_populate = """
            const addonDeptSelect = document.getElementById('addonDeptId');
            if(addonDeptSelect) {
                addonDeptSelect.innerHTML = '<option value="">بدون ارتباط</option>' + 
                    allDepartments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }
"""
# just append this inside loadData after allDepartments is set
pattern_load = re.compile(r'allDepartments = [^;]+;')
match = pattern_load.search(content)
if match:
    content = content[:match.end()] + js_populate + content[match.end():]

# Add table headers
pattern_th = re.compile(r'<table class="addons-table">.*?<thead>.*?<tr>(.*?)</tr>.*?</thead>', re.DOTALL)
def replace_th(match):
    return match.group(0).replace('<th>اسم الإضافة</th>', '<th>اسم الإضافة</th>\n<th>القسم</th>\n<th>الحالة</th>')
content = pattern_th.sub(replace_th, content)

# Add table row data
pattern_td = re.compile(r'<td>\$\{s\.name \|\| \'-\'\}</td>')
def replace_td(match):
    return match.group(0) + """\n                <td>${allDepartments.find(d => d.id == s.deptId)?.name || '<span style="color:var(--gray);">بدون</span>'}</td>
                <td><span class="badge ${s.status === 'نشط' ? 'badge-success' : 'badge-danger'}">${s.status || 'نشط'}</span></td>"""
content = pattern_td.sub(replace_td, content)


with open("courses.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated courses.html for addons")
