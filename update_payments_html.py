import re

def modify_payments_html():
    with open('payments.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add filters for Department and Level
    filters_marker = """<select id="statusFilter">
                        <option value="all">الكل</option>
                        <option value="paid">مدفوع بالكامل</option>
                        <option value="partial">مدفوع جزئياً</option>
                        <option value="unpaid">غير مدفوع</option>
                    </select>
                </div>"""
    new_filters = filters_marker + """
                <div class="filter-group">
                    <label><i class="fas fa-filter"></i> القسم:</label>
                    <select id="deptFilter">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label><i class="fas fa-filter"></i> المستوى:</label>
                    <select id="levelFilter">
                        <option value="all">الكل</option>
                        <option value="1">مستوى 1</option>
                        <option value="2">مستوى 2</option>
                        <option value="3">مستوى 3</option>
                        <option value="4">مستوى 4</option>
                        <option value="5">مستوى 5</option>
                        <option value="6">مستوى 6</option>
                    </select>
                </div>"""
    content = content.replace(filters_marker, new_filters)

    # 2. Update table headers
    table_headers = """<th>المبلغ المدفوع</th>
                            <th>إجمالي المستوى</th>"""
    new_table_headers = """<th>المبلغ المدفوع</th>
                            <th>الخصم</th>
                            <th>الإضافات</th>
                            <th>إجمالي المستوى</th>"""
    content = content.replace(table_headers, new_table_headers)
    
    colspan_old = 'colspan="9"'
    colspan_new = 'colspan="11"'
    content = content.replace(colspan_old, colspan_new)

    # 3. Add discount input to modal
    amount_paid_html = """<div class="form-group">
                    <label>المبلغ المدفوع (ج.م)</label>
                    <input type="number" id="amountPaid" placeholder="أدخل المبلغ" readonly style="background: #e9ecef;">
                    <small id="remainingAmount" style="color: var(--danger); font-weight: bold; display: none; margin-top: 5px;">المتبقي: 0 ج.م</small>
                </div>"""
    new_amount_paid_html = amount_paid_html + """
                <div class="form-group">
                    <label>قيمة الخصم (ج.م) - اختياري</label>
                    <input type="number" id="discountAmount" placeholder="أدخل قيمة الخصم" value="0" oninput="togglePaymentType()">
                </div>"""
    content = content.replace(amount_paid_html, new_amount_paid_html)

    # 4. Modify updateTotalFee so addons don't increase totalLevelFee
    update_total_old = """document.getElementById('totalLevelFee').value = baseFee + addonsTotal;"""
    update_total_new = """document.getElementById('totalLevelFee').value = baseFee;
        document.getElementById('totalLevelFee').setAttribute('data-addons', addonsTotal);"""
    content = content.replace(update_total_old, update_total_new)

    # 5. Populate department filter in updateStats or filterAndRender
    # Let's insert dept filter population inside the API fetch part
    api_fetch_end = """allAddOns = addonsRes || [];"""
    new_api_fetch_end = api_fetch_end + """
            // Populate department filter
            const deptFilter = document.getElementById('deptFilter');
            const uniqueDepts = [...new Set(allStudents.map(s => s.deptId).filter(Boolean))];
            deptFilter.innerHTML = '<option value="all">الكل</option>';
            // Note: In payments.html we might not have allDepartments fetched, but we can just use simple dept IDs
            // or fetch departments if needed. To keep it simple we just show IDs or fetch them.
            // Let's just create options for 1 to 10 for now, or just leave it.
            uniqueDepts.forEach(d => {
                deptFilter.innerHTML += `<option value="${d}">قسم ${d}</option>`;
            });
"""
    content = content.replace(api_fetch_end, new_api_fetch_end)

    # 6. Listeners for new filters
    listeners_old = """document.getElementById('statusFilter').addEventListener('change', () => filterAndRender());"""
    listeners_new = listeners_old + """
        document.getElementById('deptFilter').addEventListener('change', () => filterAndRender());
        document.getElementById('levelFilter').addEventListener('change', () => filterAndRender());"""
    content = content.replace(listeners_old, listeners_new)

    # 7. Modify filterAndRender to use new filters
    filter_old = """const statusFilter = document.getElementById('statusFilter').value;"""
    filter_new = filter_old + """
        const deptFilter = document.getElementById('deptFilter').value;
        const levelFilter = document.getElementById('levelFilter').value;"""
    content = content.replace(filter_old, filter_new)

    filter_logic_old = """if (statusFilter !== 'all') {
            if (statusFilter === 'paid' && p.remainingBalance > 0) match = false;
            if (statusFilter === 'partial' && (p.amountPaid === 0 || p.remainingBalance === 0)) match = false;
            if (statusFilter === 'unpaid' && p.amountPaid > 0) match = false;
        }"""
    filter_logic_new = filter_logic_old + """
        if (deptFilter !== 'all') {
            const student = allStudents.find(s => s.id === p.studentId);
            if (!student || student.deptId != deptFilter) match = false;
        }
        if (levelFilter !== 'all' && p.levelNumber != levelFilter) match = false;
"""
    content = content.replace(filter_logic_old, filter_logic_new)

    # 8. Add discount and addons to renderTable
    render_old = """<td>${(p.amountPaid || 0).toLocaleString()} ج.م</td>
                    <td>${(p.totalFee || 0).toLocaleString()} ج.م</td>"""
    render_new = """<td>${(p.amountPaid || 0).toLocaleString()} ج.م</td>
                    <td><span style="color:var(--success)">${(p.discount || 0).toLocaleString()} ج.م</span></td>
                    <td><span style="color:var(--info)">${(p.addonsPaid || 0).toLocaleString()} ج.م</span></td>
                    <td>${(p.totalFee || 0).toLocaleString()} ج.م</td>"""
    content = content.replace(render_old, render_new)

    # 9. Modify togglePaymentType to calculate remaining correctly with discount
    toggle_old = """const amount = parseFloat(document.getElementById('amountPaid').value) || 0;
        const total = parseFloat(document.getElementById('totalLevelFee').value) || 0;"""
    toggle_new = """const amount = parseFloat(document.getElementById('amountPaid').value) || 0;
        const total = parseFloat(document.getElementById('totalLevelFee').value) || 0;
        const discount = parseFloat(document.getElementById('discountAmount').value) || 0;"""
    content = content.replace(toggle_old, toggle_new)
    
    toggle_rem_old = """const remaining = Math.max(0, total - amount);"""
    toggle_rem_new = """const remaining = Math.max(0, total - amount - discount);"""
    content = content.replace(toggle_rem_old, toggle_rem_new)

    toggle_full_old = """document.getElementById('amountPaid').value = total;
            document.getElementById('remainingAmount').textContent = `المتبقي: 0 ج.م`;"""
    toggle_full_new = """document.getElementById('amountPaid').value = Math.max(0, total - discount);
            document.getElementById('remainingAmount').textContent = `المتبقي: 0 ج.م`;"""
    content = content.replace(toggle_full_old, toggle_full_new)

    # 10. Update savePayment
    save_btn_old = """const data = {
                studentId,
                levelNumber: document.getElementById('levelNumber').value,
                amountPaid: document.getElementById('amountPaid').value,
                totalLevelFee: document.getElementById('totalLevelFee').value,
                paymentDate: document.getElementById('paymentDate').value,
                createdBy: currentUser.id
            };"""
    save_btn_new = """const addonsPaid = parseFloat(document.getElementById('totalLevelFee').getAttribute('data-addons')) || 0;
            const data = {
                studentId,
                levelNumber: document.getElementById('levelNumber').value,
                amountPaid: document.getElementById('amountPaid').value,
                discount: document.getElementById('discountAmount').value || 0,
                addonsPaid: addonsPaid,
                totalLevelFee: document.getElementById('totalLevelFee').value,
                paymentDate: document.getElementById('paymentDate').value,
                createdBy: currentUser.id
            };"""
    content = content.replace(save_btn_old, save_btn_new)

    with open('payments.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    modify_payments_html()
