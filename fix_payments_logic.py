import re

with open("code.gs", "r", encoding="utf-8") as f:
    content = f.read()

# I will replace getAllPayments completely
old_get_all_payments = re.search(r'function getAllPayments\(\) \{.*?(?=function savePayment)', content, re.DOTALL)
if old_get_all_payments:
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
  
  // To calculate remaining balances dynamically, we track accumulated payments per student/level
  var accumulated = {};
  
  var payments = [];
  for (var i = 1; i < data.length; i++) {
    var stId = data[i][1];
    var lvl = data[i][2];
    var key = stId + "_" + lvl;
    if (!accumulated[key]) {
       accumulated[key] = {
         paidCourse: 0,
         paidAddons: 0,
         discount: 0
       };
    }
    
    var amtPaid = safeFloat(data[i][3], 0);
    var disc = safeFloat(data[i][4], 0);
    var addPaid = safeFloat(data[i][5], 0);
    var totalFee = safeFloat(data[i][6], 0); // This is course price
    var addonsTotal = safeFloat(data[i][13], 0); // We will use col 14 for addons total if available, else 0
    var notes = data[i][14] || '';
    
    accumulated[key].paidCourse += amtPaid;
    accumulated[key].paidAddons += addPaid;
    accumulated[key].discount += disc;
    
    var remCourse = totalFee - accumulated[key].paidCourse - accumulated[key].discount;
    if(remCourse < 0) remCourse = 0;
    var remAddons = addonsTotal - accumulated[key].paidAddons;
    if(remAddons < 0) remAddons = 0;
    
    payments.push({
      id: data[i][0],
      studentId: stId,
      studentName: studentNames[stId] || data[i][10] || '',
      levelNumber: lvl,
      amountPaid: amtPaid,
      discount: disc,
      addonsPaid: addPaid,
      totalFee: totalFee,
      addonsTotal: addonsTotal,
      remainingCourse: remCourse,
      remainingAddons: remAddons,
      paymentDate: data[i][8],
      createdBy: data[i][9],
      groupNameAuto: data[i][11] || '',
      courseNameAuto: data[i][12] || '',
      notes: notes
    });
  }
  return payments;
}

"""
    content = content.replace(old_get_all_payments.group(0), new_get_all_payments)

old_save_payment = re.search(r'function savePayment\(paymentData\) \{.*?(?=function deletePayment)', content, re.DOTALL)
if old_save_payment:
    new_save_payment = """function savePayment(paymentData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Payments");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  var studentId = safeInt(paymentData.studentId, 0);
  var levelNumber = safeInt(paymentData.levelNumber, 1);
  var amountPaid = safeFloat(paymentData.amountPaid, 0); // Course amount paid
  var discount = safeFloat(paymentData.discount, 0);
  var addonsPaid = safeFloat(paymentData.addonsPaid, 0); // Addons amount paid
  var totalLevelFee = safeFloat(paymentData.totalLevelFee || paymentData.totalFee, 0); // Course total
  var addonsTotal = safeFloat(paymentData.addonsTotal, 0); // Addons total
  var notes = paymentData.notes || '';
  
  if (!studentId || (amountPaid <= 0 && discount <= 0 && addonsPaid <= 0)) {
    return { success: false, message: "يجب إدخال مبلغ صحيح" };
  }
  
  // Calculate remaining dynamically
  var data = sheet.getDataRange().getValues();
  var totalCoursePaid = 0;
  var totalAddonsPaid = 0;
  var totalDiscount = 0;
  
  for (var i = 1; i < data.length; i++) {
    if (data[i][1] == studentId && data[i][2] == levelNumber) {
      totalCoursePaid += safeFloat(data[i][3], 0);
      totalDiscount += safeFloat(data[i][4], 0);
      totalAddonsPaid += safeFloat(data[i][5], 0);
    }
  }
  
  var newCoursePaid = totalCoursePaid + amountPaid;
  var newDiscount = totalDiscount + discount;
  var newAddonsPaid = totalAddonsPaid + addonsPaid;
  
  var remainingCourse = totalLevelFee - newCoursePaid - newDiscount;
  if (remainingCourse < 0) remainingCourse = 0;
  
  var remainingAddons = addonsTotal - newAddonsPaid;
  if (remainingAddons < 0) remainingAddons = 0;
  
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
  sheet.getRange(lastRow + 1, 8).setValue(remainingCourse + remainingAddons); // Legacy remaining col
  sheet.getRange(lastRow + 1, 9).setValue(paymentData.paymentDate || new Date());
  sheet.getRange(lastRow + 1, 10).setValue(safeInt(paymentData.createdBy, 1));
  sheet.getRange(lastRow + 1, 11).setValue(paymentData.studentNameAuto || '');
  sheet.getRange(lastRow + 1, 12).setValue(paymentData.groupNameAuto || '');
  sheet.getRange(lastRow + 1, 13).setValue(paymentData.courseNameAuto || '');
  sheet.getRange(lastRow + 1, 14).setValue(addonsTotal);
  sheet.getRange(lastRow + 1, 15).setValue(notes);
  
  updateLevelsTable(studentId, levelNumber, totalLevelFee + addonsTotal, remainingCourse + remainingAddons);
  
  return { success: true, message: "تم تسجيل الدفعة بنجاح" };
}

"""
    content = content.replace(old_save_payment.group(0), new_save_payment)

with open("code.gs", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated code.gs payments logic")
