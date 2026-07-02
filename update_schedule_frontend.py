import re

def modify_schedule():
    with open('schedule.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Department filter UI
    filter_html_old = """<div class="filter-group" style="flex: 1; min-width: 200px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-building"></i> تصفية بالقاعة</label>
                    <select id="hallFilter" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 10px;">
                        <option value="all">كل القاعات</option>
                    </select>
                </div>"""
    filter_html_new = filter_html_old + """
                <div class="filter-group" style="flex: 1; min-width: 200px;">
                    <label style="display: block; margin-bottom: 8px; color: var(--gray); font-size: 13px;"><i class="fas fa-layer-group"></i> تصفية بالقسم</label>
                    <select id="deptFilter" style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 10px;">
                        <option value="all">كل الأقسام</option>
                        <option value="1">تقنية المعلومات (IT)</option>
                        <option value="2">اللغات (LANG)</option>
                        <option value="3">إدارة الأعمال (BUS)</option>
                        <option value="4">التصميم (GD)</option>
                    </select>
                </div>"""
    content = content.replace(filter_html_old, filter_html_new)

    # 2. Update checkboxes for multiple days in form
    day_select_old = """<div class="form-group">
                    <label>اليوم</label>
                    <select id="bookingDay" required>
                        <option value="">اختر اليوم</option>
                        <option value="Saturday">السبت</option>
                        <option value="Sunday">الأحد</option>
                        <option value="Monday">الاثنين</option>
                        <option value="Tuesday">الثلاثاء</option>
                        <option value="Wednesday">الأربعاء</option>
                        <option value="Thursday">الخميس</option>
                    </select>
                </div>"""
    day_select_new = """<div class="form-group">
                    <label>الأيام</label>
                    <div id="bookingDays" style="display: flex; gap: 10px; flex-wrap: wrap; background: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #e9ecef;">
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;"><input type="checkbox" value="Saturday" class="day-cb"> السبت</label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;"><input type="checkbox" value="Sunday" class="day-cb"> الأحد</label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;"><input type="checkbox" value="Monday" class="day-cb"> الاثنين</label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;"><input type="checkbox" value="Tuesday" class="day-cb"> الثلاثاء</label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;"><input type="checkbox" value="Wednesday" class="day-cb"> الأربعاء</label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;"><input type="checkbox" value="Thursday" class="day-cb"> الخميس</label>
                        <label style="cursor: pointer; display: flex; align-items: center; gap: 5px;"><input type="checkbox" value="Friday" class="day-cb"> الجمعة</label>
                    </div>
                </div>"""
    content = content.replace(day_select_old, day_select_new)

    # 3. Add `allCourses` array and load it
    load_old = """let allGroups = [];
    let allFloors = [];"""
    load_new = """let allGroups = [];
    let allFloors = [];
    let allCourses = [];
    const deptNames = {1: 'تقنية المعلومات (IT)', 2: 'اللغات (LANG)', 3: 'إدارة الأعمال (BUS)', 4: 'التصميم (GD)'};"""
    content = content.replace(load_old, load_new)

    api_old = """const [bRes, hRes, tRes, gRes, fRes] = await Promise.all([
                apiCall('getAllBookings'),
                apiCall('getAllHalls'),
                apiCall('getAllTrainers'),
                apiCall('getAllGroups'),
                apiCall('getAllFloors')
            ]);
            allBookings = bRes || [];
            allHalls = hRes || [];
            allTrainers = tRes || [];
            allGroups = gRes || [];
            allFloors = fRes || [];"""
    api_new = """const [bRes, hRes, tRes, gRes, fRes, cRes] = await Promise.all([
                apiCall('getAllBookings'),
                apiCall('getAllHalls'),
                apiCall('getAllTrainers'),
                apiCall('getAllGroups'),
                apiCall('getAllFloors'),
                apiCall('getAllCourses')
            ]);
            allBookings = bRes || [];
            allHalls = hRes || [];
            allTrainers = tRes || [];
            allGroups = gRes || [];
            allFloors = fRes || [];
            allCourses = cRes || [];"""
    content = content.replace(api_old, api_new)

    # 4. Modify filter logic in renderBoard
    filter_logic_old = """if (hallFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.hallId == hallFilter);
        if (trainerFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.trainerId == trainerFilter);"""
    filter_logic_new = """if (hallFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.hallId == hallFilter);
        if (trainerFilter !== 'all') filteredBookings = filteredBookings.filter(b => b.trainerId == trainerFilter);
        const deptFilter = document.getElementById('deptFilter') ? document.getElementById('deptFilter').value : 'all';
        if (deptFilter !== 'all') {
            filteredBookings = filteredBookings.filter(b => {
                const group = allGroups.find(g => g.id == b.groupId);
                const course = group ? allCourses.find(c => c.id == group.courseId) : null;
                return course && course.deptId == deptFilter;
            });
        }"""
    content = content.replace(filter_logic_old, filter_logic_new)

    # Add event listener for deptFilter
    event_old = """document.getElementById('applyFilterBtn').addEventListener('click', () => renderBoard());"""
    event_new = event_old + """\n        if(document.getElementById('deptFilter')) document.getElementById('deptFilter').addEventListener('change', () => renderBoard());"""
    content = content.replace(event_old, event_new)

    # 5. Modify cell content to show all details
    cell_old = """<div style="font-weight: bold;">${conflictAlert}${booking.startTime} - ${booking.endTime}</div>
                                    <div><i class="fas fa-door-open"></i> ${hall?.name || '-'}</div>
                                    <div><i class="fas fa-user-tie"></i> ${trainer?.name || '-'}</div>"""
    cell_new = """<div style="font-weight: bold; color: var(--dark-blue); font-size: 12px; margin-bottom: 3px;">
                                        ${conflictAlert}<i class="far fa-clock"></i> ${booking.startTime} - ${booking.endTime}
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 5px; margin-bottom: 2px;">
                                        <i class="fas fa-door-open" style="color: var(--info);"></i> <span>${hall?.name || '-'}</span> 
                                        <span style="font-size: 9px; background: #e0f2fe; padding: 1px 4px; border-radius: 4px; color: #0284c7;">${hall?.type || 'عملي'}</span>
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 5px; margin-bottom: 2px;">
                                        <i class="fas fa-user-tie" style="color: var(--primary-blue);"></i> <span>${trainer?.name || '-'}</span>
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 5px; margin-bottom: 2px;">
                                        <i class="fas fa-book" style="color: var(--gold);"></i> 
                                        <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100px;">
                                            ${(() => {
                                                const group = allGroups.find(g => g.id == booking.groupId);
                                                const course = group ? allCourses.find(c => c.id == group.courseId) : null;
                                                return course ? course.name : 'بدون كورس';
                                            })()}
                                        </span>
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 5px; font-size: 9px; color: var(--gray);">
                                        <i class="fas fa-layer-group"></i>
                                        <span>
                                            ${(() => {
                                                const group = allGroups.find(g => g.id == booking.groupId);
                                                const course = group ? allCourses.find(c => c.id == group.courseId) : null;
                                                return course ? deptNames[course.deptId] : '-';
                                            })()}
                                        </span>
                                    </div>"""
    content = content.replace(cell_old, cell_new)

    # 6. Adjust step="1800" for time inputs
    time_old_1 = """<input type="time" id="startTime" required>"""
    time_new_1 = """<input type="time" id="startTime" step="1800" required>"""
    content = content.replace(time_old_1, time_new_1)
    
    time_old_2 = """<input type="time" id="endTime" required>"""
    time_new_2 = """<input type="time" id="endTime" step="1800" required>"""
    content = content.replace(time_old_2, time_new_2)

    # 7. Modify openAddModalAtDay to check the correct checkbox
    open_add_old = """document.getElementById('bookingDay').value = day;"""
    open_add_new = """document.querySelectorAll('.day-cb').forEach(cb => { cb.checked = (cb.value === day); });"""
    content = content.replace(open_add_old, open_add_new)

    open_add_modal_old = """document.getElementById('bookingForm').reset();
        document.getElementById('bookingId').value = '';"""
    open_add_modal_new = """document.getElementById('bookingForm').reset();
        document.getElementById('bookingId').value = '';
        document.querySelectorAll('.day-cb').forEach(cb => cb.checked = false);"""
    content = content.replace(open_add_modal_old, open_add_modal_new)

    # 8. Modify editBooking
    edit_old = """document.getElementById('bookingDay').value = booking.day;"""
    edit_new = """document.querySelectorAll('.day-cb').forEach(cb => { cb.checked = (cb.value === booking.day); });"""
    content = content.replace(edit_old, edit_new)

    # 9. Modify saveBooking
    save_old = """const data = {
            id: document.getElementById('bookingId').value || null,
            day: document.getElementById('bookingDay').value,
            startTime: document.getElementById('startTime').value,
            endTime: document.getElementById('endTime').value,
            hallId: document.getElementById('hallId').value,
            trainerId: document.getElementById('trainerId').value,
            groupId: document.getElementById('groupId').value,
            createdBy: currentUser.id
        };"""
    save_new = """const selectedDays = Array.from(document.querySelectorAll('.day-cb:checked')).map(cb => cb.value);
        if (selectedDays.length === 0) {
            showToast('الرجاء اختيار يوم واحد على الأقل', 'error');
            return;
        }
        
        let startT = document.getElementById('startTime').value;
        let endT = document.getElementById('endTime').value;
        if (!startT.endsWith(':00') && !startT.endsWith(':30')) {
            showToast('يجب أن تكون الدقائق 00 أو 30', 'error');
            return;
        }
        if (!endT.endsWith(':00') && !endT.endsWith(':30')) {
            showToast('يجب أن تكون الدقائق 00 أو 30', 'error');
            return;
        }

        const data = {
            id: document.getElementById('bookingId').value || null,
            days: selectedDays,
            day: selectedDays[0], // For backward compatibility if editing one
            startTime: startT,
            endTime: endT,
            hallId: document.getElementById('hallId').value,
            trainerId: document.getElementById('trainerId').value,
            groupId: document.getElementById('groupId').value,
            createdBy: currentUser.id
        };"""
    content = content.replace(save_old, save_new)

    with open('schedule.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    modify_schedule()
