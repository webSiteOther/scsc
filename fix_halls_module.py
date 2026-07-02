import re

with open("code.gs", "r", encoding="utf-8") as f:
    code = f.read()

# Fix saveHall in code.gs
old_save_hall = re.search(r'function saveHall\(hallData\) \{.*?return \{ success: true, message: "تم إضافة القاعة بنجاح" \};\s*\}', code, re.DOTALL)
if not old_save_hall:
    old_save_hall = re.search(r'function saveHall\(hallData\) \{.*?(?=function deleteHall)', code, re.DOTALL)

if old_save_hall:
    new_save_hall = """function saveHall(hallData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Halls");
  if (!sheet) return { success: false, message: "Sheet not found" };
  if (!hallData || !hallData.name || !hallData.floorNumber) return { success: false, message: "بيانات ناقصة" };
  
  var data = sheet.getDataRange().getValues();
  if (hallData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == hallData.id) {
        sheet.getRange(i+1, 2).setValue(hallData.name);
        sheet.getRange(i+1, 3).setValue(safeInt(hallData.floorNumber, ''));
        sheet.getRange(i+1, 4).setValue(hallData.type || 'عادية');
        sheet.getRange(i+1, 5).setValue(safeInt(hallData.capacity, 0));
        sheet.getRange(i+1, 6).setValue(hallData.status || 'متاح');
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    var newId = sheet.getLastRow();
    if(data.length > 1) {
       newId = safeInt(data[data.length-1][0], 0) + 1;
    } else {
       newId = 1;
    }
    var lastRow = sheet.getLastRow();
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(hallData.name);
    sheet.getRange(lastRow + 1, 3).setValue(safeInt(hallData.floorNumber, ''));
    sheet.getRange(lastRow + 1, 4).setValue(hallData.type || 'عادية');
    sheet.getRange(lastRow + 1, 5).setValue(safeInt(hallData.capacity, 0));
    sheet.getRange(lastRow + 1, 6).setValue(hallData.status || 'متاح');
    return { success: true, message: "تم الإضافة بنجاح" };
  }
}
"""
    code = code.replace(old_save_hall.group(0), new_save_hall)

with open("code.gs", "w", encoding="utf-8") as f:
    f.write(code)

with open("floors.html", "r", encoding="utf-8") as f:
    html = f.read()

# Fix UI for Halls Modal
new_status_field = """                <div class="form-group">
                    <label>السعة</label>
                    <input type="number" id="hallCapacity" value="20" min="1">
                </div>
                <div class="form-group">
                    <label>الحالة</label>
                    <select id="hallStatus">
                        <option value="متاح">متاح</option>
                        <option value="صيانة">صيانة</option>
                    </select>
                </div>"""
html = re.sub(r'<div class="form-group">\s*<label>.*?capacity.*?</label>\s*<input[^>]*id="hallCapacity"[^>]*>\s*</div>', new_status_field, html, flags=re.IGNORECASE)

if 'id="hallStatus"' not in html:
    # It might not have had capacity block matching regex, let's inject before submit buttons
    html = re.sub(r'(<div class="modal-footer">)', new_status_field + r'\n            \1', html)

# Fix Halls table header
if '<th>الحالة</th>' not in html:
    html = re.sub(r'(<th>السعة</th>\s*<th>الإجراءات</th>)', r'<th>السعة</th>\n                            <th>الحالة</th>\n                            <th>الإجراءات</th>', html)

# Fix Javascript editHall
js_edit = """            document.getElementById('hallId').value = hall.id;
            document.getElementById('hallName').value = hall.name || '';
            document.getElementById('hallFloorId').value = hall.floorNumber || '';
            document.getElementById('hallType').value = hall.type || 'عادية';
            if(document.getElementById('hallCapacity')) document.getElementById('hallCapacity').value = hall.capacity || 20;
            if(document.getElementById('hallStatus')) document.getElementById('hallStatus').value = hall.status || 'متاح';"""
html = re.sub(r"document\.getElementById\('hallId'\)\.value = hall\.id;.*?(?=document\.getElementById\('hallModal'\))", js_edit + "\n            ", html, flags=re.DOTALL)

# Fix Javascript saveHall
js_save = """        const data = {
            id: document.getElementById('hallId').value || null,
            name: document.getElementById('hallName').value,
            floorNumber: document.getElementById('hallFloorId').value,
            type: document.getElementById('hallType').value,
            capacity: document.getElementById('hallCapacity') ? document.getElementById('hallCapacity').value : 20,
            status: document.getElementById('hallStatus') ? document.getElementById('hallStatus').value : 'متاح'
        };"""
html = re.sub(r'const data = \{\s*id: document\.getElementById\(\'hallId\'\)\.value \|\| null,.*?(?=capacity:).*?\},?\}?;', js_save, html, flags=re.DOTALL)

# Fix renderHallsTable
def replace_td(match):
    # match.group(1) is the capacity td
    return match.group(1) + """\n                    <td><span class="badge ${h.status === 'متاح' ? 'badge-success' : 'badge-danger'}">${h.status || 'متاح'}</span></td>"""
html = re.sub(r'(<td>\$\{h\.capacity \|\| 0\}</td>)', replace_td, html)
html = html.replace('colspan="6"', 'colspan="7"')

with open("floors.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated halls module.")
