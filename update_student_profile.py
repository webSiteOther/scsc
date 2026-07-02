import re

def modify_student_profile():
    with open('student_profile.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Payments table header and row to include discount and addons
    headers_old = """<th>المبلغ المدفوع</th>
                            <th>المتبقي</th>"""
    headers_new = """<th>المبلغ المدفوع</th>
                            <th>قيمة الخصم</th>
                            <th>مدفوعات الإضافات</th>
                            <th>المتبقي</th>"""
    content = content.replace(headers_old, headers_new)

    row_old = """<td><span class="badge badge-success">${p.amountPaid || 0} ج.م</span></td>
                        <td><span class="badge ${isPaid ? 'badge-success' : 'badge-danger'}">${p.remainingBalance || 0} ج.م</span></td>"""
    row_new = """<td><span class="badge badge-success">${p.amountPaid || 0} ج.م</span></td>
                        <td><span style="color: var(--success); font-weight: bold;">${p.discount || 0} ج.م</span></td>
                        <td><span style="color: var(--info); font-weight: bold;">${p.addonsPaid || 0} ج.م</span></td>
                        <td><span class="badge ${isPaid ? 'badge-success' : 'badge-danger'}">${p.remainingBalance || 0} ج.م</span></td>"""
    content = content.replace(row_old, row_new)
    
    colspan_old = 'colspan="5"'
    colspan_new = 'colspan="7"'
    content = content.replace(colspan_old, colspan_new)

    # 2. Fix AddOns logic since addonsPaid is a number, not IDs
    addons_old = """// AddOns
            let paidAddonIds = new Set();
            payments.forEach(p => {
                if (p.addonsPaid) {
                    let ids = p.addonsPaid.split(',').map(aid => parseInt(aid.trim()));
                    ids.forEach(aid => { if(!isNaN(aid)) paidAddonIds.add(aid); });
                }
            });
            
            const addList = document.getElementById('stAddonsList');
            if (paidAddonIds.size > 0) {
                addList.innerHTML = Array.from(paidAddonIds).map(aid => {
                    const addon = (aRes || []).find(a => a.id == aid);
                    if (addon) {
                        return `<li style="background: #eef2ff; padding: 10px 20px; border-radius: 12px; border: 1px solid #c7d2fe; color: #3730a3; font-weight: bold;"><i class="fas fa-check-circle" style="color: var(--success); margin-left: 5px;"></i> ${addon.name} <span style="background: white; padding: 2px 8px; border-radius: 10px; margin-right: 10px; font-size: 12px;">${addon.price} ج.م</span></li>`;
                    }
                    return '';
                }).join('');
            } else {
                addList.innerHTML = `<li style="color: var(--gray); width: 100%; text-align: center;">لم يتم دفع أية إضافات</li>`;
            }"""

    addons_new = """// AddOns logic simplified since addonsPaid is an aggregated number
            const addList = document.getElementById('stAddonsList');
            let totalAddonsPaid = payments.reduce((acc, p) => acc + (parseFloat(p.addonsPaid) || 0), 0);
            if (totalAddonsPaid > 0) {
                addList.innerHTML = `<li style="background: #eef2ff; padding: 10px 20px; border-radius: 12px; border: 1px solid #c7d2fe; color: #3730a3; font-weight: bold;"><i class="fas fa-check-circle" style="color: var(--success); margin-left: 5px;"></i> إجمالي مدفوعات الإضافات <span style="background: white; padding: 2px 8px; border-radius: 10px; margin-right: 10px; font-size: 12px;">${totalAddonsPaid} ج.م</span></li>`;
            } else {
                addList.innerHTML = `<li style="color: var(--gray); width: 100%; text-align: center;">لم يتم دفع أية إضافات</li>`;
            }"""
    content = content.replace(addons_old, addons_new)

    with open('student_profile.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    modify_student_profile()
