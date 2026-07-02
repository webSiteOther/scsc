import re

def fix_students_html():
    with open('students.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Add allDepartments
    if 'let allDepartments = [];' not in content:
        content = content.replace('let allAddOns = [];', 'let allAddOns = [];\n    let allDepartments = [];')

    # Update loadData
    old_api = """const [sRes, gRes, pRes, cRes, aRes] = await Promise.all([
                apiCall('getAllStudents'),
                apiCall('getAllGroups'),
                apiCall('getAllPayments'),
                apiCall('getAllCourses'),
                apiCall('getAllAddOns')
            ]);"""
    new_api = """const [sRes, gRes, pRes, cRes, aRes, dRes] = await Promise.all([
                apiCall('getAllStudents'),
                apiCall('getAllGroups'),
                apiCall('getAllPayments'),
                apiCall('getAllCourses'),
                apiCall('getAllAddOns'),
                apiCall('getAllDepartments')
            ]);"""
    content = content.replace(old_api, new_api)

    old_res = """allAddOns = aRes || [];"""
    new_res = """allAddOns = aRes || [];
            allDepartments = dRes || [];
            
            // Populate Dept Filter
            const deptFilter = document.getElementById('deptFilter');
            if(deptFilter) {
                deptFilter.innerHTML = '<option value="all">الكل</option>' + 
                    allDepartments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }
            
            // Populate add student modal dept
            const studentDept = document.getElementById('studentDept');
            if(studentDept) {
                studentDept.innerHTML = '<option value="">اختر القسم</option>' + 
                    allDepartments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }"""
    content = content.replace(old_res, new_res)

    # Replace hardcoded dept mapping
    old_dept_map = """const deptNames = {1: 'تقنية المعلومات (IT)', 2: 'اللغات (LANG)', 3: 'إدارة الأعمال (BUS)', 4: 'التصميم (GD)'};
            const dept = deptNames[s.deptId] || '-';"""
    new_dept_map = """const deptObj = allDepartments.find(d => d.id == s.deptId);
            const dept = deptObj ? deptObj.name : '-';"""
    content = content.replace(old_dept_map, new_dept_map)

    with open('students.html', 'w', encoding='utf-8') as f:
        f.write(content)

def fix_courses_html():
    with open('courses.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace allDepts fetch and population
    old_api = """const [cRes, dRes, aRes] = await Promise.all([
                apiCall('getAllCourses'),
                apiCall('getAllDepartments'),
                apiCall('getAllAddOns')
            ]);
            allCourses = cRes || [];
            allDepts = dRes || [];
            allAddOns = aRes || [];"""
    new_api = """const [cRes, dRes, aRes] = await Promise.all([
                apiCall('getAllCourses'),
                apiCall('getAllDepartments'),
                apiCall('getAllAddOns')
            ]);
            allCourses = cRes || [];
            allDepts = dRes || [];
            allAddOns = aRes || [];
            
            const deptFilter = document.getElementById('deptFilter');
            if(deptFilter) {
                deptFilter.innerHTML = '<option value="all">الكل</option>' + 
                    allDepts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }
            const courseDeptId = document.getElementById('courseDeptId');
            if(courseDeptId) {
                courseDeptId.innerHTML = '<option value="">اختر القسم</option>' + 
                    allDepts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }"""
    
    if old_api in content:
        content = content.replace(old_api, new_api)
    else:
        # just replace the population part if API already handles it
        pass

    old_dept_map = """const deptNames = {1: 'تقنية المعلومات (IT)', 2: 'اللغات (LANG)', 3: 'إدارة الأعمال (BUS)', 4: 'التصميم (GD)'};
            const deptName = deptNames[c.deptId] || 'غير محدد';"""
    new_dept_map = """const deptObj = allDepts.find(d => d.id == c.deptId);
            const deptName = deptObj ? deptObj.name : 'غير محدد';"""
    content = content.replace(old_dept_map, new_dept_map)

    # Fix saveCourse API call
    old_save_course = """await apiCall('saveCourse', { courseData: data });"""
    new_save_course = """await apiCall('saveCourse', data);"""
    content = content.replace(old_save_course, new_save_course)

    with open('courses.html', 'w', encoding='utf-8') as f:
        f.write(content)

def fix_student_profile():
    with open('student_profile.html', 'r', encoding='utf-8') as f:
        content = f.read()

    old_api = """const [sRes, gRes, pRes, cRes, aRes] = await Promise.all([
                apiCall('getAllStudents'),
                apiCall('getAllGroups'),
                apiCall('getAllPayments'),
                apiCall('getAllCourses'),
                apiCall('getAllAddOns')
            ]);"""
    new_api = """const [sRes, gRes, pRes, cRes, aRes, dRes] = await Promise.all([
                apiCall('getAllStudents'),
                apiCall('getAllGroups'),
                apiCall('getAllPayments'),
                apiCall('getAllCourses'),
                apiCall('getAllAddOns'),
                apiCall('getAllDepartments')
            ]);
            const allDepartments = dRes || [];"""
    content = content.replace(old_api, new_api)

    old_dept_map = """const deptNames = {1: 'تقنية المعلومات (IT)', 2: 'اللغات (LANG)', 3: 'إدارة الأعمال (BUS)', 4: 'التصميم (GD)'};
            document.getElementById('stDept').textContent = deptNames[student.deptId] || '-';"""
    new_dept_map = """const deptObj = allDepartments.find(d => d.id == student.deptId);
            document.getElementById('stDept').textContent = deptObj ? deptObj.name : '-';"""
    content = content.replace(old_dept_map, new_dept_map)

    with open('student_profile.html', 'w', encoding='utf-8') as f:
        f.write(content)

def fix_schedule():
    with open('schedule.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Add allDepartments
    if 'let allDepartments = [];' not in content:
        content = content.replace('let allCourses = [];', 'let allCourses = [];\n    let allDepartments = [];')

    # fetch API
    old_api = """const [bRes, hRes, tRes, gRes, fRes, cRes] = await Promise.all([
                apiCall('getAllBookings'),
                apiCall('getAllHalls'),
                apiCall('getAllTrainers'),
                apiCall('getAllGroups'),
                apiCall('getAllFloors'),
                apiCall('getAllCourses')
            ]);"""
    new_api = """const [bRes, hRes, tRes, gRes, fRes, cRes, dRes] = await Promise.all([
                apiCall('getAllBookings'),
                apiCall('getAllHalls'),
                apiCall('getAllTrainers'),
                apiCall('getAllGroups'),
                apiCall('getAllFloors'),
                apiCall('getAllCourses'),
                apiCall('getAllDepartments')
            ]);"""
    content = content.replace(old_api, new_api)

    old_res = """allCourses = cRes || [];"""
    new_res = """allCourses = cRes || [];
            allDepartments = dRes || [];
            
            const deptFilter = document.getElementById('deptFilter');
            if(deptFilter) {
                deptFilter.innerHTML = '<option value="all">كل الأقسام</option>' + 
                    allDepartments.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
            }"""
    content = content.replace(old_res, new_res)

    old_dept_map = """const deptNames = {1: 'تقنية المعلومات (IT)', 2: 'اللغات (LANG)', 3: 'إدارة الأعمال (BUS)', 4: 'التصميم (GD)'};"""
    new_dept_map = """"""
    content = content.replace(old_dept_map, new_dept_map)
    
    old_dept_print = """return course ? deptNames[course.deptId] : '-';"""
    new_dept_print = """if(!course) return '-'; const deptObj = allDepartments.find(d => d.id == course.deptId); return deptObj ? deptObj.name : '-';"""
    content = content.replace(old_dept_print, new_dept_print)

    with open('schedule.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_students_html()
    fix_courses_html()
    fix_student_profile()
    fix_schedule()
