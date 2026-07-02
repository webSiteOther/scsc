import re

def fix_payments_filters():
    with open('payments.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # The old filter logic in `filterAndRender`
    filter_logic_old = """    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        const deptFilter = document.getElementById('deptFilter').value;
        const levelFilter = document.getElementById('levelFilter').value;
        
        let filtered = [...allPayments];
        if (searchTerm) {
            filtered = filtered.filter(p => p.studentName?.toLowerCase().includes(searchTerm) || 
                allStudents.find(s => s.id === p.studentId)?.code?.toLowerCase().includes(searchTerm));
        }
        if (statusFilter === 'paid') filtered = filtered.filter(p => p.remainingBalance === 0);
        else if (statusFilter === 'partial') filtered = filtered.filter(p => p.remainingBalance > 0 && p.amountPaid > 0);
        else if (statusFilter === 'unpaid') filtered = filtered.filter(p => p.amountPaid === 0 || !p.amountPaid);
        
        renderTable(filtered);
    }"""
    
    filter_logic_new = """    function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        const deptFilter = document.getElementById('deptFilter') ? document.getElementById('deptFilter').value : 'all';
        const levelFilter = document.getElementById('levelFilter').value;
        const floorFilter = document.getElementById('floorFilter') ? document.getElementById('floorFilter').value : 'all';
        const courseFilter = document.getElementById('courseFilter') ? document.getElementById('courseFilter').value : 'all';
        
        let filtered = [...allPayments];
        if (searchTerm) {
            filtered = filtered.filter(p => p.studentName?.toLowerCase().includes(searchTerm) || 
                allStudents.find(s => s.id === p.studentId)?.code?.toLowerCase().includes(searchTerm));
        }
        if (statusFilter === 'paid') filtered = filtered.filter(p => p.remainingBalance === 0);
        else if (statusFilter === 'partial') filtered = filtered.filter(p => p.remainingBalance > 0 && p.amountPaid > 0);
        else if (statusFilter === 'unpaid') filtered = filtered.filter(p => p.amountPaid === 0 || !p.amountPaid);
        
        if (deptFilter !== 'all') {
            filtered = filtered.filter(p => {
                const student = allStudents.find(s => s.id == p.studentId);
                return student && student.deptId == deptFilter;
            });
        }
        
        if (courseFilter !== 'all') {
            filtered = filtered.filter(p => {
                const student = allStudents.find(s => s.id == p.studentId);
                if(!student || !student.groupId) return false;
                const grp = allGroups.find(g => g.id == student.groupId);
                return grp && grp.courseId == courseFilter;
            });
        }
        
        if (floorFilter !== 'all') {
            filtered = filtered.filter(p => {
                const student = allStudents.find(s => s.id == p.studentId);
                if(!student || !student.groupId) return false;
                const grp = allGroups.find(g => g.id == student.groupId);
                if(!grp || !grp.hallId) return false;
                const hall = allHalls.find(h => h.id == grp.hallId);
                return hall && hall.floorNumber == floorFilter;
            });
        }
        
        renderTable(filtered);
    }"""
    
    if "const deptFilter = document.getElementById('deptFilter').value;" in content:
        content = content.replace(filter_logic_old, filter_logic_new)

    with open('payments.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_payments_filters()
