import re

with open("schedule.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix Multi-Day Checkboxes in Modal
old_day_input = re.search(r'<div class="form-group">\s*<label>.*?</label>\s*<select id="bookingDay">.*?</select>\s*</div>', content, re.DOTALL)
if not old_day_input:
    # Maybe it's already checkboxes? Let's check for "day-cb"
    if 'class="day-cb"' in content:
        print("Checkboxes already exist. We need to check if saveBooking uses them.")
else:
    # If it was a select, replace it. Actually, wait. I see 'document.querySelectorAll('.day-cb').forEach' in the output above. 
    # This means checkboxes might already exist for days! Let's check `bookingData` in `saveBooking`.
    pass

# I'll just rewrite the whole JS saveBooking to make sure it sends days: [...] instead of day: string
# Let's replace the JS saveBooking
old_save_booking = re.search(r'async function saveBooking\(\) \{.*?\}\s*catch\(e\) \{\}\s*showLoading\(false\);\s*\}', content, re.DOTALL)
new_save_booking = """async function saveBooking() {
        const rules = {
            hallId: [{ fn: Validators.required, msg: 'مطلوب إختيار القاعة' }],
            trainerId: [{ fn: Validators.required, msg: 'مطلوب إختيار المدرب' }]
        };
        
        if (!validateForm(rules)) return;
        
        // Gather selected days
        const selectedDays = Array.from(document.querySelectorAll('.day-cb:checked')).map(cb => cb.value);
        if(selectedDays.length === 0) {
            alert('يرجى اختيار يوم واحد على الأقل');
            return;
        }

        const startTime = document.getElementById('startTime').value;
        const endTime = document.getElementById('endTime').value;
        if (!startTime || !endTime) {
            alert('يرجى اختيار وقت البداية والنهاية');
            return;
        }
        
        const bookingData = {
            id: document.getElementById('bookingId').value || null,
            days: selectedDays,
            startTime: startTime,
            endTime: endTime,
            hallId: parseInt(document.getElementById('hallId').value, 10) || 0,
            trainerId: parseInt(document.getElementById('trainerId').value, 10) || 0,
            groupId: document.getElementById('groupId').value ? parseInt(document.getElementById('groupId').value, 10) : null,
            createdBy: currentUser.id
        };
        
        showLoading(true);
        try {
            const res = await apiCall('saveBooking', bookingData);
            if(res.success === false) {
                 alert(res.message || 'يوجد تعارض');
            } else {
                 showToast('تم الحفظ بنجاح', 'success');
                 closeModal();
                 loadData();
            }
        } catch(e) {
             alert('حدث خطأ');
        }
        showLoading(false);
    }"""
if old_save_booking:
    content = content.replace(old_save_booking.group(0), new_save_booking)


# 2. Fix 12-Hour Time Picker
# Find startTime and endTime inputs
def generate_time_options():
    options = ""
    for hour in range(1, 13):
        for minute in ["00", "30"]:
            am_pm = "AM"
            h_24 = hour
            if h_24 == 12:
                h_24 = 0
            time_24 = f"{h_24:02d}:{minute}"
            options += f'<option value="{time_24}">{hour}:{minute} AM</option>\n'
    for hour in range(1, 13):
        for minute in ["00", "30"]:
            am_pm = "PM"
            h_24 = hour
            if h_24 != 12:
                h_24 += 12
            time_24 = f"{h_24:02d}:{minute}"
            options += f'<option value="{time_24}">{hour}:{minute} PM</option>\n'
    return options

time_options_html = generate_time_options()

pattern_time1 = re.compile(r'<input type="time" id="startTime".*?>')
content = pattern_time1.sub(f'<select id="startTime">\n{time_options_html}</select>', content)

pattern_time2 = re.compile(r'<input type="time" id="endTime".*?>')
content = pattern_time2.sub(f'<select id="endTime">\n{time_options_html}</select>', content)

# Also check for type="time" with class or something if it failed
if 'type="time"' in content:
    content = content.replace('<input type="time" id="startTime" required>', f'<select id="startTime" required>\n{time_options_html}</select>')
    content = content.replace('<input type="time" id="endTime" required>', f'<select id="endTime" required>\n{time_options_html}</select>')

# 3. Schedule Cards Redesign
# The user wants: Course Name, Department, Instructor, Hall, Hall Type, Floor, Start/End Time, Days, Student Count, Status
# In renderBoard function, we generate the cards. Let's rewrite the card generation.
old_card_gen = re.search(r'const card = document\.createElement\(\'div\'\);\s*card\.className = \'booking-card\';.*?return card;\s*\}', content, re.DOTALL)

if old_card_gen:
    new_card_gen = """const card = document.createElement('div');
        card.className = 'booking-card';
        card.onclick = () => editBooking(booking.id);
        
        let deptName = 'غير محدد';
        let courseName = 'غير محدد';
        let hallType = hall ? (hall.type || 'عادية') : 'عادية';
        let floorName = 'غير محدد';
        let studentsCount = group ? (group.studentsCount || 0) : 0;
        
        if (group && group.courseId) {
            const course = allCourses.find(c => c.id == group.courseId);
            if (course) {
                courseName = course.name;
                const dept = allDepartments.find(d => d.id == course.deptId);
                if(dept) deptName = dept.name;
            }
        }
        if (hall) {
            const floor = allFloors.find(f => f.id == hall.floorNumber);
            if (floor) floorName = floor.name;
        }
        
        // Convert time to 12hr format
        function to12Hr(time24) {
             if(!time24) return '';
             let [h, m] = time24.split(':');
             h = parseInt(h);
             let ampm = h >= 12 ? 'PM' : 'AM';
             h = h % 12;
             h = h ? h : 12;
             return `${h}:${m} ${ampm}`;
        }
        
        card.innerHTML = `
            <div style="font-weight: bold; color: var(--dark-blue); font-size: 15px; margin-bottom: 5px;">${courseName}</div>
            <div style="font-size: 12px; color: var(--primary-blue); margin-bottom: 5px;">${deptName}</div>
            <hr style="border: 0; border-top: 1px dashed #ccc; margin: 8px 0;">
            <div style="font-size: 13px; color: var(--dark); display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
                <div><i class="fas fa-user-tie"></i> المدرب: <span style="font-weight:600">${trainer ? trainer.name : 'غير محدد'}</span></div>
                <div><i class="fas fa-users"></i> العدد: <span style="font-weight:600">${studentsCount}</span></div>
                <div><i class="fas fa-door-open"></i> القاعة: <span style="font-weight:600">${hall ? hall.name : 'غير محدد'} (${hallType})</span></div>
                <div><i class="fas fa-layer-group"></i> الدور: <span style="font-weight:600">${floorName}</span></div>
            </div>
            <div style="background: #f0f4f8; padding: 6px; border-radius: 6px; margin-top: 8px; text-align: center; font-weight: bold; color: var(--primary-blue); font-size: 13px;">
                <i class="far fa-clock"></i> ${to12Hr(booking.startTime)} - ${to12Hr(booking.endTime)}
            </div>
        `;
        return card;
    }"""
    content = content.replace(old_card_gen.group(0), new_card_gen)


with open("schedule.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated schedule.html frontend")
