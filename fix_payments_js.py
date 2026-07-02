import re

with open("payments.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace renderTable logic
old_render = re.search(r'function renderTable\(payments\) \{.*?\}\s*\}', content, re.DOTALL)
if old_render:
    new_render = """function renderTable(payments) {
        const tbody = document.getElementById('paymentsTableBody');
        if (!payments || payments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="12" style="text-align: center;">لا توجد بيانات</td></tr>';
            return;
        }
        
        tbody.innerHTML = payments.map(p => {
            const student = allStudents.find(s => s.id == p.studentId);
            const totalDue = (parseFloat(p.totalFee) || 0) + (parseFloat(p.addonsTotal) || 0);
            const remainingCourse = parseFloat(p.remainingCourse) || 0;
            const remainingAddons = parseFloat(p.remainingAddons) || 0;
            const status = (remainingCourse <= 0 && remainingAddons <= 0) ? 'مكتمل' : 'متبقي';
            const statusClass = status === 'مكتمل' ? 'status-paid' : 'status-partial';
            const date = p.paymentDate ? new Date(p.paymentDate).toLocaleDateString('ar-EG') : '-';
            
            // Payment type logic: if amountPaid > 0 -> Course, if addonsPaid > 0 -> Addon, else manual
            let type = "دفعة كورس";
            if ((p.addonsPaid || 0) > 0 && (p.amountPaid || 0) == 0) type = "دفعة إضافات";
            if ((p.amountPaid || 0) == 0 && (p.addonsPaid || 0) == 0 && (p.discount || 0) > 0) type = "تسوية/خصم";

            return `
                <tr>
                    <td><strong>${p.studentName || student?.name || '-'}</strong><br><small style="color: gray;">${student?.code || ''}</small></td>
                    <td>مستوى ${p.levelNumber || 1}</td>
                    <td><span class="badge" style="background:#eef2ff; color:#3730a3; padding:4px 8px; border-radius:8px; font-size:11px;">${type}</span></td>
                    <td>${totalDue.toLocaleString()} ج.م</td>
                    <td><span style="color:var(--success); font-weight:bold;">${(p.amountPaid || 0).toLocaleString()} ج.م</span></td>
                    <td><span style="color:var(--info); font-weight:bold;">${(p.addonsPaid || 0).toLocaleString()} ج.م</span></td>
                    <td><span style="color:var(--danger)">${(p.discount || 0).toLocaleString()} ج.م</span></td>
                    <td><span class="badge ${remainingCourse <= 0 ? 'status-paid' : 'status-danger'}" style="padding:4px 8px; border-radius:8px;">${remainingCourse.toLocaleString()} ج.م</span></td>
                    <td><span class="badge ${remainingAddons <= 0 ? 'status-paid' : 'status-danger'}" style="padding:4px 8px; border-radius:8px;">${remainingAddons.toLocaleString()} ج.م</span></td>
                    <td>${date}</td>
                    <td>${p.createdBy || 1}</td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-delete" onclick="deletePayment(${p.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
    }"""
    content = content.replace(old_render.group(0), new_render)

# Replace submitPayment backend call
old_submit = re.search(r'const data = \{.*?\};', content, re.DOTALL)
if old_submit:
    new_submit = """const data = {
            studentId: document.getElementById('selectedStudentId').value,
            levelNumber: document.getElementById('levelNumber').value,
            amountPaid: document.getElementById('amountPaid').value || 0,
            discount: document.getElementById('discountAmount') ? document.getElementById('discountAmount').value : 0,
            addonsPaid: totalAddons || 0,
            totalLevelFee: document.getElementById('totalLevelFee').dataset.base || 0,
            addonsTotal: document.getElementById('totalLevelFee').dataset.addons || 0,
            notes: document.getElementById('paymentNotes') ? document.getElementById('paymentNotes').value : ''
        };"""
    content = content.replace(old_submit.group(0), new_submit)

with open("payments.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated payments.html JS logic")
