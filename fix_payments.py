import os

filepath = "c:/Users/shahd/Downloads/ss/payments.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# HTML Updates
old_html = """                <div class="form-group">
                    <label>تاريخ الدفع</label>
                    <input type="date" id="paymentDate">
                </div>"""
new_html = """                <div class="form-group" id="addOnsContainer" style="display: none; background: #f8f9fa; padding: 10px; border-radius: 8px;">
                    <label style="margin-bottom: 10px;">إضافات الكورس (اختياري)</label>
                    <div id="addOnsCheckboxes" style="display: flex; flex-direction: column; gap: 8px;"></div>
                </div>
                <div class="form-group">
                    <label>تاريخ الدفع</label>
                    <input type="date" id="paymentDate">
                </div>"""
content = content.replace(old_html, new_html)

# JS Updates
# Variables
content = content.replace('let allStudents = [];', 'let allStudents = [];\n    let allCourses = [];\n    let allGroups = [];\n    let allAddOns = [];')

# loadData
old_loadData = """    async function loadData() {
        showLoading(true);
        try {
            allPayments = await apiCall('getAllPayments');
            allStudents = await apiCall('getAllStudents');
            
            updateStats();
            updateCharts();
            filterAndRender();
        } catch(e) { 
            console.error(e); 
            // Error handled in apiCall
        }
        showLoading(false);
    }"""
new_loadData = """    async function loadData() {
        showLoading(true);
        try {
            const [paymentsRes, studentsRes, coursesRes, groupsRes, addonsRes] = await Promise.all([
                apiCall('getAllPayments'),
                apiCall('getAllStudents'),
                apiCall('getAllCourses'),
                apiCall('getAllGroups'),
                apiCall('getAllAddOns')
            ]);
            allPayments = paymentsRes || [];
            allStudents = studentsRes || [];
            allCourses = coursesRes || [];
            allGroups = groupsRes || [];
            allAddOns = addonsRes || [];
            
            updateStats();
            updateCharts();
            filterAndRender();
        } catch(e) {}
        showLoading(false);
    }"""
content = content.replace(old_loadData, new_loadData)

# selectStudent
old_selectStudent = """    function selectStudent(id, name, code) {
        document.getElementById('selectedStudentId').value = id;
        document.getElementById('selectedStudentName').value = `${name} (${code})`;
        document.getElementById('studentSearchSection').style.display = 'none';
        document.getElementById('paymentFormSection').style.display = 'block';
        document.getElementById('savePayment').style.display = 'block';
        document.getElementById('paymentDate').valueAsDate = new Date();
    }"""
new_selectStudent = """    function selectStudent(id, name, code) {
        document.getElementById('selectedStudentId').value = id;
        document.getElementById('selectedStudentName').value = `${name} (${code})`;
        document.getElementById('studentSearchSection').style.display = 'none';
        document.getElementById('paymentFormSection').style.display = 'block';
        document.getElementById('savePayment').style.display = 'block';
        document.getElementById('paymentDate').valueAsDate = new Date();
        
        const student = allStudents.find(s => s.id == id);
        let courseFee = 0;
        let courseId = null;
        if (student && student.groupId) {
            const group = allGroups.find(g => g.id == student.groupId);
            if (group && group.courseId) {
                courseId = group.courseId;
                const course = allCourses.find(c => c.id == courseId);
                if (course) courseFee = course.pricePerLevel || 0;
            }
        }
        
        document.getElementById('totalLevelFee').value = courseFee;
        document.getElementById('totalLevelFee').setAttribute('data-base', courseFee);
        
        const addonsContainer = document.getElementById('addOnsContainer');
        const addonsCb = document.getElementById('addOnsCheckboxes');
        addonsCb.innerHTML = '';
        
        if (courseId) {
            const courseAddOns = allAddOns.filter(a => a.courseId == courseId || !a.courseId);
            if (courseAddOns.length > 0) {
                addonsContainer.style.display = 'block';
                addonsCb.innerHTML = courseAddOns.map(a => `
                    <label style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; padding: 5px; background: white; border-radius: 5px; border: 1px solid #eee;">
                        <span><input type="checkbox" class="addon-cb" value="${a.price || 0}" data-id="${a.id}" onchange="updateTotalFee()"> ${a.name}</span>
                        <span style="color: var(--primary-blue); font-weight: bold;">+${a.price || 0} ج.م</span>
                    </label>
                `).join('');
            } else {
                addonsContainer.style.display = 'none';
            }
        } else {
            addonsContainer.style.display = 'none';
        }
        
        togglePaymentType();
    }

    window.updateTotalFee = function() {
        const baseFee = parseFloat(document.getElementById('totalLevelFee').getAttribute('data-base')) || 0;
        let addonsTotal = 0;
        document.querySelectorAll('.addon-cb:checked').forEach(cb => {
            addonsTotal += parseFloat(cb.value) || 0;
        });
        
        document.getElementById('totalLevelFee').value = baseFee + addonsTotal;
        togglePaymentType();
    };"""
content = content.replace(old_selectStudent, new_selectStudent)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated payments.html AddOns logic")
