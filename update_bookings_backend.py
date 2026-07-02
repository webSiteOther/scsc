import re

def modify_bookings():
    with open('code.gs', 'r', encoding='utf-8') as f:
        content = f.read()

    # Define new functions
    new_functions = """function saveBooking(bookingData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Bookings");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!bookingData || (!bookingData.day && (!bookingData.days || bookingData.days.length === 0)) || !bookingData.startTime || !bookingData.endTime) {
    return { success: false, message: "بيانات الحجز غير مكتملة" };
  }
  
  // Format times (subtract 1 minute from end time automatically)
  // Time format expected "HH:MM"
  var startTime = bookingData.startTime;
  var endTime = bookingData.endTime;
  
  // Parse endTime and subtract 1 minute
  try {
    var parts = endTime.split(':');
    var h = parseInt(parts[0], 10);
    var m = parseInt(parts[1], 10);
    var dateObj = new Date();
    dateObj.setHours(h, m, 0);
    dateObj.setMinutes(dateObj.getMinutes() - 1);
    var newH = dateObj.getHours().toString().padStart(2, '0');
    var newM = dateObj.getMinutes().toString().padStart(2, '0');
    endTime = newH + ':' + newM;
  } catch(e) {}
  
  var allBookings = getAllBookings();
  
  if (bookingData.id) {
    // Edit existing booking
    var testBooking = {
      id: bookingData.id,
      day: bookingData.day || (bookingData.days && bookingData.days[0]),
      hallId: bookingData.hallId,
      trainerId: bookingData.trainerId,
      startTime: startTime,
      endTime: endTime
    };
    if (checkBookingConflict(testBooking, allBookings)) {
      return { success: false, message: "يوجد تعارض في المواعيد أو القاعة أو المدرب!" };
    }
    
    var data = sheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == bookingData.id) {
        sheet.getRange(i+1, 2).setValue(safeInt(bookingData.hallId, ''));
        sheet.getRange(i+1, 3).setValue(safeInt(bookingData.trainerId, ''));
        sheet.getRange(i+1, 4).setValue(safeInt(bookingData.groupId, ''));
        sheet.getRange(i+1, 5).setValue(testBooking.day);
        sheet.getRange(i+1, 6).setValue(startTime);
        sheet.getRange(i+1, 7).setValue(endTime);
        sheet.getRange(i+1, 9).setValue("OK");
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    // New bookings (possibly multiple days)
    var days = bookingData.days || [bookingData.day];
    
    // First, check all for conflicts
    for(var d = 0; d < days.length; d++) {
       var testBooking = {
          id: null,
          day: days[d],
          hallId: bookingData.hallId,
          trainerId: bookingData.trainerId,
          startTime: startTime,
          endTime: endTime
       };
       if (checkBookingConflict(testBooking, allBookings)) {
         return { success: false, message: "يوجد تعارض في يوم " + days[d] + "!" };
       }
    }
    
    // If no conflicts, save all
    var lastRow = sheet.getLastRow();
    for(var d = 0; d < days.length; d++) {
       var newId = sheet.getLastRow(); // generate ID based on current last row
       if (sheet.getRange(newId, 1).getValue() != "booking_id" && typeof sheet.getRange(newId, 1).getValue() === "number") {
         newId = sheet.getRange(newId, 1).getValue() + 1;
       } else {
         newId = 1; // fallback if empty
       }
       
       var rowToInsert = sheet.getLastRow() + 1;
       sheet.getRange(rowToInsert, 1).setValue(newId);
       sheet.getRange(rowToInsert, 2).setValue(safeInt(bookingData.hallId, ''));
       sheet.getRange(rowToInsert, 3).setValue(safeInt(bookingData.trainerId, ''));
       sheet.getRange(rowToInsert, 4).setValue(safeInt(bookingData.groupId, ''));
       sheet.getRange(rowToInsert, 5).setValue(days[d]);
       sheet.getRange(rowToInsert, 6).setValue(startTime);
       sheet.getRange(rowToInsert, 7).setValue(endTime);
       sheet.getRange(rowToInsert, 8).setValue(safeInt(bookingData.createdBy, 1));
       sheet.getRange(rowToInsert, 9).setValue("OK");
    }
    
    return { success: true, message: "تمت إضافة المواعيد بنجاح" };
  }
}

function checkBookingConflict(newBooking, existingBookings) {
  for (var b = 0; b < existingBookings.length; b++) {
    var booking = existingBookings[b];
    if (booking.id == newBooking.id) continue;
    if (booking.day === newBooking.day) {
      if (booking.hallId == newBooking.hallId || booking.trainerId == newBooking.trainerId) {
        if ((newBooking.startTime >= booking.startTime && newBooking.startTime <= booking.endTime) ||
            (newBooking.endTime >= booking.startTime && newBooking.endTime <= booking.endTime) ||
            (newBooking.startTime <= booking.startTime && newBooking.endTime >= booking.endTime)) {
          return true;
        }
      }
    }
  }
  return false;
}"""

    # We need to replace `function saveBooking(bookingData) { ... }` and `function checkBookingConflict(...) { ... }`
    # Let's use regex to match these two functions and replace them.
    pattern = re.compile(r'function saveBooking\(bookingData\).*?return false;\s*}', re.DOTALL)
    
    # Check if we can find it
    if not pattern.search(content):
        # Alternative pattern if checkBookingConflict is separated
        pattern1 = re.compile(r'function saveBooking\(bookingData\).*?^}\s*$', re.MULTILINE | re.DOTALL)
        pattern2 = re.compile(r'function checkBookingConflict\(.*?\).*?^}\s*$', re.MULTILINE | re.DOTALL)
        
        content = pattern1.sub('', content)
        content = pattern2.sub('', content)
        content += "\n\n" + new_functions
    else:
        content = pattern.sub(new_functions, content)

    # Let's just do a manual replacement to be extremely safe, as regex might fail.
    # Actually, appending and removing might be safer. Let's just write a more robust approach.
    pass

def precise_modify_bookings():
    with open('code.gs', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('function saveBooking(bookingData)'):
            start_idx = i
        if line.startswith('function deleteBooking'):
            end_idx = i
            break
            
    if start_idx != -1 and end_idx != -1:
        new_content = "".join(lines[:start_idx])
        new_content += """function saveBooking(bookingData) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Bookings");
  if (!sheet) return { success: false, message: "Sheet not found" };
  
  if (!bookingData || (!bookingData.day && (!bookingData.days || bookingData.days.length === 0)) || !bookingData.startTime || !bookingData.endTime) {
    return { success: false, message: "بيانات الحجز غير مكتملة" };
  }
  
  var startTime = bookingData.startTime;
  var endTime = bookingData.endTime;
  
  try {
    var parts = endTime.split(':');
    var h = parseInt(parts[0], 10);
    var m = parseInt(parts[1], 10);
    var dateObj = new Date();
    dateObj.setHours(h, m, 0);
    dateObj.setMinutes(dateObj.getMinutes() - 1);
    var newH = dateObj.getHours().toString().padStart(2, '0');
    var newM = dateObj.getMinutes().toString().padStart(2, '0');
    endTime = newH + ':' + newM;
  } catch(e) {}
  
  var allBookings = getAllBookings();
  
  if (bookingData.id) {
    var testBooking = {
      id: bookingData.id,
      day: bookingData.day || (bookingData.days && bookingData.days[0]),
      hallId: bookingData.hallId,
      trainerId: bookingData.trainerId,
      startTime: startTime,
      endTime: endTime
    };
    if (checkBookingConflict(testBooking, allBookings)) {
      return { success: false, message: "يوجد تعارض في المواعيد أو القاعة أو المدرب!" };
    }
    
    var data = sheet.getDataRange().getValues();
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == bookingData.id) {
        sheet.getRange(i+1, 2).setValue(safeInt(bookingData.hallId, ''));
        sheet.getRange(i+1, 3).setValue(safeInt(bookingData.trainerId, ''));
        sheet.getRange(i+1, 4).setValue(safeInt(bookingData.groupId, ''));
        sheet.getRange(i+1, 5).setValue(testBooking.day);
        sheet.getRange(i+1, 6).setValue(startTime);
        sheet.getRange(i+1, 7).setValue(endTime);
        sheet.getRange(i+1, 9).setValue("OK");
        return { success: true, message: "تم التحديث بنجاح" };
      }
    }
  } else {
    var days = bookingData.days || [bookingData.day];
    
    for(var d = 0; d < days.length; d++) {
       var testBooking = {
          id: null,
          day: days[d],
          hallId: bookingData.hallId,
          trainerId: bookingData.trainerId,
          startTime: startTime,
          endTime: endTime
       };
       if (checkBookingConflict(testBooking, allBookings)) {
         return { success: false, message: "يوجد تعارض في يوم " + days[d] + "!" };
       }
    }
    
    for(var d = 0; d < days.length; d++) {
       var newId = sheet.getLastRow();
       if (sheet.getRange(newId, 1).getValue() != "booking_id" && typeof sheet.getRange(newId, 1).getValue() === "number") {
         newId = sheet.getRange(newId, 1).getValue() + 1;
       } else {
         newId = 1;
       }
       
       var rowToInsert = sheet.getLastRow() + 1;
       sheet.getRange(rowToInsert, 1).setValue(newId);
       sheet.getRange(rowToInsert, 2).setValue(safeInt(bookingData.hallId, ''));
       sheet.getRange(rowToInsert, 3).setValue(safeInt(bookingData.trainerId, ''));
       sheet.getRange(rowToInsert, 4).setValue(safeInt(bookingData.groupId, ''));
       sheet.getRange(rowToInsert, 5).setValue(days[d]);
       sheet.getRange(rowToInsert, 6).setValue(startTime);
       sheet.getRange(rowToInsert, 7).setValue(endTime);
       sheet.getRange(rowToInsert, 8).setValue(safeInt(bookingData.createdBy, 1));
       sheet.getRange(rowToInsert, 9).setValue("OK");
    }
    
    return { success: true, message: "تمت إضافة المواعيد بنجاح" };
  }
}

function checkBookingConflict(newBooking, existingBookings) {
  for (var b = 0; b < existingBookings.length; b++) {
    var booking = existingBookings[b];
    if (booking.id == newBooking.id) continue;
    if (booking.day === newBooking.day) {
      if (booking.hallId == newBooking.hallId || booking.trainerId == newBooking.trainerId) {
        if ((newBooking.startTime >= booking.startTime && newBooking.startTime <= booking.endTime) ||
            (newBooking.endTime >= booking.startTime && newBooking.endTime <= booking.endTime) ||
            (newBooking.startTime <= booking.startTime && newBooking.endTime >= booking.endTime)) {
          return true;
        }
      }
    }
  }
  return false;
}

"""
        new_content += "".join(lines[end_idx:])
        
        with open('code.gs', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Updated code.gs saveBooking successfully")
    else:
        print("Could not find start or end index")

if __name__ == '__main__':
    precise_modify_bookings()
