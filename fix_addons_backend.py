import re

with open("code.gs", "r", encoding="utf-8") as f:
    content = f.read()

# Replace getAllAddOns
old_get_addons = re.search(r'function getAllAddOns\(\) \{.*?return addons;\s*\}', content, re.DOTALL)
if old_get_addons:
    new_get_addons = """function getAllAddOns() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("AddOns");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  var addons = [];
  for (var i = 1; i < data.length; i++) {
    addons.push({
      id: data[i][0],
      name: data[i][1],
      price: safeFloat(data[i][2], 0),
      deptId: data[i][3],
      courseId: data[i][4],
      status: data[i][5] || 'نشط'
    });
  }
  return addons;
}"""
    content = content.replace(old_get_addons.group(0), new_get_addons)

# Replace saveAddOn
old_save_addon = re.search(r'function saveAddOn\(addonData\) \{.*?return \{ success: true, message: "تم إضافة الإضافة بنجاح" \};\s*\}', content, re.DOTALL)
if not old_save_addon:
    # try another match
    old_save_addon = re.search(r'function saveAddOn\(addonData\) \{.*?(?=function deleteAddOn)', content, re.DOTALL)

if old_save_addon:
    new_save_addon = """function saveAddOn(addonData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("AddOns");
  if (!sheet) return { success: false, message: "Sheet not found" };
  if (!addonData || !addonData.name) return { success: false, message: "بيانات ناقصة" };
  
  var data = sheet.getDataRange().getValues();
  if (addonData.id) {
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == addonData.id) {
        sheet.getRange(i+1, 2).setValue(addonData.name);
        sheet.getRange(i+1, 3).setValue(safeFloat(addonData.price, 0));
        sheet.getRange(i+1, 4).setValue(addonData.deptId ? safeInt(addonData.deptId) : '');
        sheet.getRange(i+1, 5).setValue(addonData.courseId ? safeInt(addonData.courseId) : '');
        sheet.getRange(i+1, 6).setValue(addonData.status || 'نشط');
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
    sheet.getRange(sheet.getLastRow() + 1, 1).setValue(newId);
    sheet.getRange(sheet.getLastRow(), 2).setValue(addonData.name);
    sheet.getRange(sheet.getLastRow(), 3).setValue(safeFloat(addonData.price, 0));
    sheet.getRange(sheet.getLastRow(), 4).setValue(addonData.deptId ? safeInt(addonData.deptId) : '');
    sheet.getRange(sheet.getLastRow(), 5).setValue(addonData.courseId ? safeInt(addonData.courseId) : '');
    sheet.getRange(sheet.getLastRow(), 6).setValue(addonData.status || 'نشط');
    return { success: true, message: "تم الإضافة بنجاح" };
  }
}
"""
    content = content.replace(old_save_addon.group(0), new_save_addon)

with open("code.gs", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated AddOn logic in code.gs")
