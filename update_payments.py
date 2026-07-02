import sys

def modify_code_gs():
    with open('code.gs', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update schema
    old_schema = 'sheets.Payments.getRange(1,1,1,8).setValues([["payment_id", "student_id", "level_number", "amount_paid", "total_level_fee", "remaining_balance", "payment_date", "created_by"]]);'
    new_schema = 'sheets.Payments.getRange(1,1,1,13).setValues([["payment_id", "student_id", "level_number", "amount_paid", "discount", "addons_paid", "total_level_fee", "remaining_balance", "payment_date", "created_by", "student_name_auto", "group_name_auto", "course_name_auto"]]);'
    content = content.replace(old_schema, new_schema)

    # 2. Update seed data
    old_seed_header = 'sheets.Payments.getRange(2,1,10,8).setValues(['
    new_seed_header = 'sheets.Payments.getRange(2,1,10,13).setValues(['
    content = content.replace(old_seed_header, new_seed_header)

    # Need to update the rows to have 13 elements
    for i in range(1, 11):
        old_row = f'], 2]'
        new_row = f'], 2, "", "", ""]'
        # This naive replace might fail, let's just do a regex or exact string replacement
    
    import re
    # Add 0, 0 for discount and addons_paid before total_level_fee?
    # Wait, old columns: payment_id, student_id, level_number, amount_paid, total_level_fee, remaining_balance, payment_date, created_by
    # New columns: payment_id, student_id, level_number, amount_paid, discount, addons_paid, total_level_fee, remaining_balance, payment_date, created_by, student_name_auto, group_name_auto, course_name_auto
    # So insert 0, 0 after amount_paid (index 3).
    # And add "", "", "" at the end.
    content = re.sub(
        r'(\[\d+,\s*\d+,\s*\d+,\s*\d+),\s*(\d+,\s*\d+,\s*new Date\([^)]+\),\s*2)\]',
        r'\1, 0, 0, \2, "", "", ""]',
        content
    )

    # 3. Replace getAllPayments
    old_get_all_payments = """function getAllPayments() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  
  // Build student name lookup map to avoid N+1 queries
  var studentNames = {};
  var studentsSheet = ss.getSheetByName("Students");
  if (studentsSheet) {
    var sData = studentsSheet.getDataRange().getValues();
    for (var j = 1; j < sData.length; j++) {
      studentNames[sData[j][0]] = sData[j][2];
    }
  }
  
  var payments = [];
  for (var i = 1; i < data.length; i++) {
    payments.push({
      id: data[i][0],
      studentId: data[i][1],
      studentName: studentNames[data[i][1]] || '',
      levelNumber: data[i][2],
      amountPaid: data[i][3],
      totalFee: data[i][4],
      remainingBalance: data[i][5],
      paymentDate: data[i][6],
      createdBy: data[i][7]
    });
  }
  return payments;
}"""
    
    new_get_all_payments = """function getAllPayments() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return [];
  var data = sheet.getDataRange().getValues();
  
  var studentNames = {};
  var studentsSheet = ss.getSheetByName("Students");
  if (studentsSheet) {
    var sData = studentsSheet.getDataRange().getValues();
    for (var j = 1; j < sData.length; j++) {
      studentNames[sData[j][0]] = sData[j][2];
    }
  }
  
  var payments = [];
  for (var i = 1; i < data.length; i++) {
    payments.push({
      id: data[i][0],
      studentId: data[i][1],
      studentName: studentNames[data[i][1]] || data[i][10] || '',
      levelNumber: data[i][2],
      amountPaid: data[i][3],
      discount: data[i][4] || 0,
      addonsPaid: data[i][5] || 0,
      totalFee: data[i][6],
      remainingBalance: data[i][7],
      paymentDate: data[i][8],
      createdBy: data[i][9],
      groupNameAuto: data[i][11] || '',
      courseNameAuto: data[i][12] || ''
    });
  }
  return payments;
}"""

    if old_get_all_payments in content:
        content = content.replace(old_get_all_payments, new_get_all_payments)
    else:
        print("old_get_all_payments not found")

    # 4. Replace savePayment
    old_save_payment = """function savePayment(paymentData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var studentId = safeInt(paymentData.studentId, 0);
  var levelNumber = safeInt(paymentData.levelNumber, 1);
  var amountPaid = safeFloat(paymentData.amountPaid, 0);
  var totalLevelFee = safeFloat(paymentData.totalLevelFee || paymentData.totalFee, 0);
  
  if (!studentId || amountPaid <= 0) {
    return { success: false, message: "بيانات الدفع غير صالحة" };
  }
  
  var remainingBalance = totalLevelFee - amountPaid;
  if (remainingBalance < 0) remainingBalance = 0;
  
  var lastRow = sheet.getLastRow();
  var newId = lastRow;
  
  sheet.getRange(lastRow + 1, 1).setValue(newId);
  sheet.getRange(lastRow + 1, 2).setValue(studentId);
  sheet.getRange(lastRow + 1, 3).setValue(levelNumber);
  sheet.getRange(lastRow + 1, 4).setValue(amountPaid);
  sheet.getRange(lastRow + 1, 5).setValue(totalLevelFee);
  sheet.getRange(lastRow + 1, 6).setValue(remainingBalance);
  sheet.getRange(lastRow + 1, 7).setValue(paymentData.paymentDate || new Date());
  sheet.getRange(lastRow + 1, 8).setValue(safeInt(paymentData.createdBy, 1));
  
  updateLevelsTable(studentId, levelNumber, totalLevelFee, remainingBalance);
  
  return { success: true, message: "تم تسجيل الدفعة بنجاح" };
}"""
    
    new_save_payment = """function savePayment(paymentData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var studentId = safeInt(paymentData.studentId, 0);
  var levelNumber = safeInt(paymentData.levelNumber, 1);
  var amountPaid = safeFloat(paymentData.amountPaid, 0);
  var discount = safeFloat(paymentData.discount, 0);
  var addonsPaid = safeFloat(paymentData.addonsPaid, 0);
  var totalLevelFee = safeFloat(paymentData.totalLevelFee || paymentData.totalFee, 0);
  
  if (!studentId || (amountPaid <= 0 && discount <= 0 && addonsPaid <= 0)) {
    return { success: false, message: "بيانات الدفع غير صالحة" };
  }
  
  // Calculate total previously paid for this student and level
  var data = sheet.getDataRange().getValues();
  var totalPreviouslyPaidAndDiscounted = 0;
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] == studentId && data[i][2] == levelNumber) {
      totalPreviouslyPaidAndDiscounted += safeFloat(data[i][3], 0); // amount paid
      totalPreviouslyPaidAndDiscounted += safeFloat(data[i][4], 0); // discount
    }
  }
  
  var remainingBalance = totalLevelFee - (totalPreviouslyPaidAndDiscounted + amountPaid + discount);
  if (remainingBalance < 0) remainingBalance = 0;
  
  var lastRow = sheet.getLastRow();
  var newId = lastRow;
  if(data.length > 1) {
    newId = safeInt(data[data.length-1][0], 0) + 1;
  } else {
    newId = 1;
  }
  
  sheet.getRange(lastRow + 1, 1).setValue(newId);
  sheet.getRange(lastRow + 1, 2).setValue(studentId);
  sheet.getRange(lastRow + 1, 3).setValue(levelNumber);
  sheet.getRange(lastRow + 1, 4).setValue(amountPaid);
  sheet.getRange(lastRow + 1, 5).setValue(discount);
  sheet.getRange(lastRow + 1, 6).setValue(addonsPaid);
  sheet.getRange(lastRow + 1, 7).setValue(totalLevelFee);
  sheet.getRange(lastRow + 1, 8).setValue(remainingBalance);
  sheet.getRange(lastRow + 1, 9).setValue(paymentData.paymentDate || new Date());
  sheet.getRange(lastRow + 1, 10).setValue(safeInt(paymentData.createdBy, 1));
  
  updateLevelsTable(studentId, levelNumber, totalLevelFee, remainingBalance);
  
  return { success: true, message: "تم تسجيل الدفعة بنجاح" };
}"""

    if old_save_payment in content:
        content = content.replace(old_save_payment, new_save_payment)
    else:
        print("old_save_payment not found")
        
    with open('code.gs', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("code.gs modified successfully")

if __name__ == "__main__":
    modify_code_gs()
