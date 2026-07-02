import re

with open("payments.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace Table Headers
old_th = """                            <th>المستوى</th>
                            <th>المبلغ</th>
                            <th>الخصم</th>
                            <th>الإضافات</th>
                            <th>الإجمالي</th>
                            <th>المتبقي</th>
                            <th>التاريخ</th>
                            <th>الموظف</th>
                            <th>الطالب</th>
                            <th>الجروب</th>
                            <th>الكورس</th>"""
# Let's use regex because we don't know the exact current Arabic text if it was changed by another script.
# The user wants: Course Total, AddOns Total, Discounts Total, Paid Course, Paid AddOns, Remaining Course, Remaining AddOns
# It's better to rewrite the whole payments.html UI part for the table and form.

def replace_table_headers(html):
    # Find the table header block and replace it
    pattern = re.compile(r'<thead>\s*<tr>.*?</tr>\s*</thead>', re.DOTALL)
    new_thead = """<thead>
                        <tr>
                            <th>الطالب</th>
                            <th>المستوى</th>
                            <th>النوع</th>
                            <th>المستحق (كورس+إضافات)</th>
                            <th>المدفوع كورس</th>
                            <th>المدفوع إضافات</th>
                            <th>الخصم</th>
                            <th>المتبقي كورس</th>
                            <th>المتبقي إضافات</th>
                            <th>التاريخ</th>
                            <th>الموظف</th>
                            <th>إجراءات</th>
                        </tr>
                    </thead>"""
    return pattern.sub(new_thead, html)

def replace_payment_form(html):
    # We need to add "Discount Amount" field to the form
    # Find amount paid input
    pattern = re.compile(r'(<div class="form-group">\s*<label><i class="fas fa-money-bill-wave"></i> المبلغ المدفوع:.*?</label>\s*<input type="number" id="amountPaid".*?>\s*</div>)', re.DOTALL)
    
    new_inputs = """\\1
                <div class="form-group">
                    <label><i class="fas fa-percentage"></i> قيمة الخصم:</label>
                    <input type="number" id="discountAmount" placeholder="أدخل قيمة الخصم" oninput="updateTotalFee()">
                </div>"""
    # Just in case we already have a discount field, we don't duplicate. We'll search if it exists.
    if 'id="discountAmount"' not in html and 'id="discount"' not in html:
        html = pattern.sub(new_inputs, html)
    return html

def replace_filters(html):
    # The user wants multi-select filters: Department, Floor, Course, Student, Level.
    # Currently it has statusFilter.
    filters_html = """
                <div class="filter-group">
                    <label><i class="fas fa-building"></i> القسم:</label>
                    <select id="deptFilter" onchange="filterPayments()">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label><i class="fas fa-layer-group"></i> الطابق:</label>
                    <select id="floorFilter" onchange="filterPayments()">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label><i class="fas fa-book"></i> الكورس:</label>
                    <select id="courseFilter" onchange="filterPayments()">
                        <option value="all">الكل</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label><i class="fas fa-user"></i> الطالب:</label>
                    <input type="text" id="studentFilter" placeholder="ابحث باسم الطالب" oninput="filterPayments()">
                </div>
                <div class="filter-group">
                    <label><i class="fas fa-layer-group"></i> المستوى:</label>
                    <input type="number" id="levelFilter" placeholder="رقم المستوى" oninput="filterPayments()" style="width:100px; padding:10px; border-radius:10px; border:1px solid #ddd;">
                </div>
    """
    # Replace the existing filter-group container contents.
    pattern = re.compile(r'<div class="filters-container".*?>.*?</div>\s*</div>', re.DOTALL)
    
    new_filters_container = f"""<div class="filters-container" style="display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;">
        {filters_html}
    </div>"""
    # Actually, the file might just have individual filter-groups. Let's just insert it before the table.
    return html

content = replace_table_headers(content)
content = replace_payment_form(content)
# Let's save it. We will handle JS rendering later.
with open("payments.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated payments.html structure")
