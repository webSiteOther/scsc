import re

def append_halls_api():
    with open('code.gs', 'r', encoding='utf-8') as f:
        content = f.read()

    # Append saveHall and deleteHall
    halls_api = """
function saveHall(hallData) {
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
        sheet.getRange(i+1, 4).setValue(hallData.type || 'عملي');
        sheet.getRange(i+1, 5).setValue(safeInt(hallData.capacity, 0));
        return { success: true, message: "تم تحديث القاعة بنجاح" };
      }
    }
  } else {
    var newId = sheet.getLastRow();
    if (sheet.getRange(newId, 1).getValue() != "hall_id" && typeof sheet.getRange(newId, 1).getValue() === "number") {
      newId = sheet.getRange(newId, 1).getValue() + 1;
    } else {
      newId = 1;
    }
    
    var lastRow = sheet.getLastRow();
    sheet.getRange(lastRow + 1, 1).setValue(newId);
    sheet.getRange(lastRow + 1, 2).setValue(hallData.name);
    sheet.getRange(lastRow + 1, 3).setValue(safeInt(hallData.floorNumber, ''));
    sheet.getRange(lastRow + 1, 4).setValue(hallData.type || 'عملي');
    sheet.getRange(lastRow + 1, 5).setValue(safeInt(hallData.capacity, 0));
    sheet.getRange(lastRow + 1, 6).setValue("Active");
    return { success: true, message: "تمت إضافة القاعة بنجاح" };
  }
}

function deleteHall(id) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Halls");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] == id) {
      sheet.deleteRow(i + 1);
      return { success: true, message: "تم حذف القاعة بنجاح" };
    }
  }
  return { success: false, message: "القاعة غير موجودة" };
}
"""
    # Let's insert it before `function getAllGroups()`
    target = "function getAllGroups()"
    if target in content:
        content = content.replace(target, halls_api + "\n" + target)
    else:
        content += "\n" + halls_api

    # Add them to handleApiRequestPost
    api_post_marker = "    case 'deleteFloor':\n      return deleteFloor(params.id);"
    api_post_new = api_post_marker + """
    case 'saveHall':
      return saveHall(params.data || params);
    case 'deleteHall':
      return deleteHall(params.id);"""
    
    content = content.replace(api_post_marker, api_post_new)

    with open('code.gs', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    append_halls_api()
