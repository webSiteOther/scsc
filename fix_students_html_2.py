import re

def fix_students_html():
    with open('students.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix viewStudent
    old_view = """    function viewStudent(id) {
        const student = allStudents.find(s => s.id == id);
        if (student) {
            showToast(`الطالب: ${student.name} | الكود: ${student.code} | الهاتف: ${student.phone} | المدرسة: ${student.school || '-'} | العمر: ${student.age || '-'}`, 'info');
        }
    }"""
    new_view = """    function viewStudent(id) {
        window.location.href = 'student_profile.html?id=' + id;
    }"""
    # Just in case the exact string doesn't match, let's use regex
    content = re.sub(r'function viewStudent\(id\) \{[\s\S]*?\}', new_view, content, count=1)

    # Fix deptName
    old_dept = """const deptName = {1: 'IT', 2: 'LANG', 3: 'BUS', 4: 'GD'}[s.deptId] || '-';"""
    new_dept = """const deptObj = allDepartments.find(d => d.id == s.deptId);
            const deptName = deptObj ? deptObj.name : '-';"""
    content = content.replace(old_dept, new_dept)

    with open('students.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_students_html()
