import re

def fix_payments_html():
    with open('payments.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add allDepartments, allFloors
    if 'let allDepartments = [];' not in content:
        content = content.replace('let allAddOns = [];', 'let allAddOns = [];\n    let allDepartments = [];\n    let allFloors = [];')

    # 2. Update loadData to fetch them
    old_api = """const [paymentsRes, studentsRes, coursesRes, groupsRes, addonsRes] = await Promise.all([
                apiCall('getAllPayments'),
                apiCall('getAllStudents'),
                apiCall('getAllCourses'),
                apiCall('getAllGroups'),
                apiCall('getAllAddOns')
            ]);"""
    new_api = """const [paymentsRes, studentsRes, coursesRes, groupsRes, addonsRes, deptsRes, floorsRes] = await Promise.all([
                apiCall('getAllPayments'),
                apiCall('getAllStudents'),
                apiCall('getAllCourses'),
                apiCall('getAllGroups'),
                apiCall('getAllAddOns'),
                apiCall('getAllDepartments'),
                apiCall('getAllFloors')
            ]);"""
    content = content.replace(old_api, new_api)

    old_res = """allAddOns = addonsRes || [];"""
    new_res = """allAddOns = addonsRes || [];
            allDepartments = deptsRes || [];
            allFloors = floorsRes || [];"""
    content = content.replace(old_res, new_res)

    # 3. Fix the filters in HTML (add Floor, Dept, Course)
    filters_html_old = """<div class="filters-section">
                <div class="filter-group">
                    <label>القسم</label>
                    <select id="deptFilter">
                        <option value="all">الكل</option>
                    </select>
                </div>"""
    filters_html_new = """<div class="filters-section">
                <div class="filter-group">
                    <label>الدور</label>
                    <select id="floorFilter">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>القسم</label>
                    <select id="deptFilter">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>الكورس</label>
                    <select id="courseFilter">
                        <option value="all">الكل</option>
                    </select>
                </div>"""
    if filters_html_old in content:
        content = content.replace(filters_html_old, filters_html_new)

    # 4. Populate filters in JS
    pop_old = """const deptFilter = document.getElementById('deptFilter');
            const uniqueDepts = [...new Set(allStudents.map(s => s.deptId).filter(Boolean))];
            deptFilter.innerHTML = '<option value="all">الكل</option>';
            // Note: In payments.html we might not have allDepartments fetched, but we can just use simple dept IDs
            // or fetch departments if needed. To keep it simple we just show IDs or fetch them.
            // Let's just create options for 1 to 10 for now, or just leave it.
            uniqueDepts.forEach(d => {
                deptFilter.innerHTML += `<option value="${d}">قسم ${d}</option>`;
            });"""
    pop_new = """const floorFilter = document.getElementById('floorFilter');
            if(floorFilter) {
                floorFilter.innerHTML = '<option value="all">كل الأدوار</option>' + 
                    allFloors.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
            }
            const deptFilter = document.getElementById('deptFilter');
            if(deptFilter) {
                deptFilter.innerHTML = '<option value="all">كل الأقسام</option>' + 
                    allDepartments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }
            const courseFilter = document.getElementById('courseFilter');
            if(courseFilter) {
                courseFilter.innerHTML = '<option value="all">كل الكورسات</option>' + 
                    allCourses.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
            }"""
    if pop_old in content:
        content = content.replace(pop_old, pop_new)
    elif "const deptFilter = document.getElementById('deptFilter');" in content:
        # replace block using regex
        content = re.sub(r"const deptFilter = document.getElementById\('deptFilter'\);.*?\}\);", pop_new, content, flags=re.DOTALL)

    # 5. Fix filterAndRender to actually use them
    filter_func_old = """const deptFilter = document.getElementById('deptFilter')?.value || 'all';"""
    filter_func_new = """const deptFilter = document.getElementById('deptFilter')?.value || 'all';
        const floorFilter = document.getElementById('floorFilter')?.value || 'all';
        const courseFilter = document.getElementById('courseFilter')?.value || 'all';"""
    if filter_func_old in content:
        content = content.replace(filter_func_old, filter_func_new)

    filter_logic_old = """if (deptFilter !== 'all') {
            filtered = filtered.filter(p => {
                const student = allStudents.find(s => s.id == p.studentId);
                return student && student.deptId == deptFilter;
            });
        }"""
    filter_logic_new = """if (deptFilter !== 'all') {
            filtered = filtered.filter(p => {
                const student = allStudents.find(s => s.id == p.studentId);
                return student && student.deptId == deptFilter;
            });
        }
        if (floorFilter !== 'all') {
            // Need to link payment -> student -> group -> hall -> floor? Or student -> floor?
            // usually group has hallId, hall has floorNumber.
            filtered = filtered.filter(p => {
                const student = allStudents.find(s => s.id == p.studentId);
                if(!student || !student.groupId) return false;
                const grp = allGroups.find(g => g.id == student.groupId);
                if(!grp || !grp.hallId) return false;
                // Since we don't fetch halls in payments.html, we can't perfectly filter by floor here unless we fetch halls.
                return true; 
            });
        }
        if (courseFilter !== 'all') {
            filtered = filtered.filter(p => {
                const student = allStudents.find(s => s.id == p.studentId);
                if(!student || !student.groupId) return false;
                const grp = allGroups.find(g => g.id == student.groupId);
                return grp && grp.courseId == courseFilter;
            });
        }"""
    if filter_logic_old in content:
        content = content.replace(filter_logic_old, filter_logic_new)

    # Need to fetch Halls to filter by floor properly
    if "apiCall('getAllFloors')" in content and "apiCall('getAllHalls')" not in content:
        content = content.replace("apiCall('getAllFloors')", "apiCall('getAllFloors'),\n                apiCall('getAllHalls')")
        content = content.replace("const [paymentsRes, studentsRes, coursesRes, groupsRes, addonsRes, deptsRes, floorsRes] = await Promise.all([", "const [paymentsRes, studentsRes, coursesRes, groupsRes, addonsRes, deptsRes, floorsRes, hallsRes] = await Promise.all([")
        content = content.replace("allFloors = floorsRes || [];", "allFloors = floorsRes || [];\n            allHalls = hallsRes || [];")
        if 'let allHalls = [];' not in content:
            content = content.replace('let allFloors = [];', 'let allFloors = [];\n    let allHalls = [];')
        
        # fix the filter logic for floor
        fix_floor = """// Since we don't fetch halls in payments.html, we can't perfectly filter by floor here unless we fetch halls.
                return true;"""
        new_fix_floor = """const hall = allHalls.find(h => h.id == grp.hallId);
                return hall && hall.floorNumber == floorFilter;"""
        content = content.replace(fix_floor, new_fix_floor)

    # 6. Fix Save Payment
    save_old = """const paymentData = {
            studentId: document.getElementById('selectedStudentId').value,
            levelNumber: parseInt(document.getElementById('levelNumber').value, 10) || 1,
            totalLevelFee: parseFloat(document.getElementById('totalLevelFee').value) || 0,
            amountPaid: parseFloat(document.getElementById('amountPaid').value) || 0,
            paymentDate: document.getElementById('paymentDate').value,
            createdBy: currentUser.id
        };"""
    save_new = """// Calculate Addons
        let totalAddons = 0;
        document.querySelectorAll('.addon-checkbox:checked').forEach(cb => {
            totalAddons += parseFloat(cb.dataset.price) || 0;
        });
        
        const paymentData = {
            studentId: document.getElementById('selectedStudentId').value,
            levelNumber: parseInt(document.getElementById('levelNumber').value, 10) || 1,
            totalLevelFee: parseFloat(document.getElementById('totalLevelFee').value) || 0,
            amountPaid: parseFloat(document.getElementById('amountPaid').value) || 0,
            discount: parseFloat(document.getElementById('discountAmount').value) || 0,
            addonsPaid: totalAddons,
            paymentDate: document.getElementById('paymentDate').value,
            createdBy: currentUser.id
        };"""
    content = content.replace(save_old, save_new)

    # 7. Setup Addons listeners (fix missing function that renders checkboxes)
    # The previous code might have had `togglePaymentType` missing or incorrect.
    
    with open('payments.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_payments_html()
