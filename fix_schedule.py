import os

filepath = "c:/Users/shahd/Downloads/ss/schedule.html"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add allFloors to variables
content = content.replace('let allGroups = [];', 'let allGroups = [];\n    let allFloors = [];')

# Update loadData
old_loadData = """    async function loadData() {
        showLoading(true);
        try {
            allBookings = await apiCall('getAllBookings');
            allHalls = await apiCall('getAllHalls');
            allTrainers = await apiCall('getAllTrainers');
            allGroups = await apiCall('getAllGroups');
            
            updateFilters();
            renderCurrentView();
        } catch(e) { 
            console.error(e); 
            // Error handled in apiCall
        }
        showLoading(false);
    }"""
new_loadData = """    async function loadData() {
        showLoading(true);
        try {
            const [bRes, hRes, tRes, gRes, fRes] = await Promise.all([
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
            allFloors = fRes || [];
            
            updateFilters();
            renderCurrentView();
        } catch(e) {}
        showLoading(false);
    }"""
content = content.replace(old_loadData, new_loadData)

# Update renderWeeklyView
old_renderWeekly = """    function renderWeeklyView() {
        const hallFilter = document.getElementById('hallFilter').value;
        const trainerFilter = document.getElementById('trainerFilter').value;
        
        let filtered = [...allBookings];
        if (hallFilter !== 'all') filtered = filtered.filter(b => b.hallId == hallFilter);
        if (trainerFilter !== 'all') filtered = filtered.filter(b => b.trainerId == trainerFilter);
        
        const header = document.getElementById('weeklyHeader');
        const body = document.getElementById('weeklyBody');
        
        header.innerHTML = '<th>اليوم / الوقت</th>' + timeSlots.map(slot => `<th>${slot}</th>`).join('');
        
        let rows = '';
        for (let day of daysOfWeek) {
            let cells = `<td style="background: var(--light-gray); font-weight: 600;">${daysNames[day]}</td>`;
            for (let time of timeSlots) {
                const booking = filtered.find(b => b.day === day && b.startTime <= time && b.endTime > time);
                if (booking) {
                    const trainer = allTrainers.find(t => t.id === booking.trainerId);
                    const hall = allHalls.find(h => h.id === booking.hallId);
                    const group = allGroups.find(g => g.id === booking.groupId);
                    const conflictClass = booking.conflict === 'CONFLICT' ? 'conflict' : '';
                    cells += `
                        <td>
                            <div class="booking-slot ${conflictClass}" onclick="editBooking(${booking.id})">
                                <div class="booking-time">${booking.startTime} - ${booking.endTime}</div>
                                <div class="booking-trainer">${trainer?.name || 'مدرب'}</div>
                                <div class="booking-group">${group?.name || 'جروب'}</div>
                                <div class="booking-hall">${hall?.name || 'قاعة'}</div>
                            </div>
                        </td>
                    `;
                } else {
                    cells += `<td onclick="openAddModalAtSlot('${day}', '${time}')" style="cursor: pointer; background: rgba(0,0,0,0.02);"></td>`;
                }
            }
            rows += `<tr>${cells}</tr>`;
        }
        body.innerHTML = rows;
    }"""
new_renderWeekly = """    function getVisibleFloors() {
        let allowed = currentUser.allowedFloors || '*';
        if (allowed === '*') return allFloors;
        let allowedIds = allowed.toString().split(',').map(id => parseInt(id));
        return allFloors.filter(f => allowedIds.includes(f.id));
    }

    function renderWeeklyView() {
        const hallFilter = document.getElementById('hallFilter').value;
        const trainerFilter = document.getElementById('trainerFilter').value;
        
        const visibleFloors = getVisibleFloors();
        
        let filtered = [...allBookings];
        // Filter based on allowed floors
        filtered = filtered.filter(b => {
            const hall = allHalls.find(h => h.id == b.hallId);
            return hall && visibleFloors.some(f => f.id == hall.floorNumber);
        });
        
        if (hallFilter !== 'all') filtered = filtered.filter(b => b.hallId == hallFilter);
        if (trainerFilter !== 'all') filtered = filtered.filter(b => b.trainerId == trainerFilter);
        
        const header = document.getElementById('weeklyHeader');
        const body = document.getElementById('weeklyBody');
        
        header.innerHTML = '<th>الوقت / اليوم</th>' + daysOfWeek.map(day => `<th>${daysNames[day]}</th>`).join('');
        
        let rows = '';
        for (let time of timeSlots) {
            let cells = `<td style="background: var(--light-gray); font-weight: 600; text-align: center; vertical-align: middle;">${time}</td>`;
            for (let day of daysOfWeek) {
                let cellContent = '';
                
                // Group bookings by floor
                for (let floor of visibleFloors) {
                    const floorBookings = filtered.filter(b => {
                        const hall = allHalls.find(h => h.id == b.hallId);
                        return b.day === day && b.startTime <= time && b.endTime > time && hall && hall.floorNumber == floor.id;
                    });
                    
                    if (floorBookings.length > 0) {
                        const bookingsHtml = floorBookings.map(booking => {
                            const trainer = allTrainers.find(t => t.id === booking.trainerId);
                            const hall = allHalls.find(h => h.id === booking.hallId);
                            const group = allGroups.find(g => g.id === booking.groupId);
                            const conflictClass = booking.conflict === 'CONFLICT' ? 'conflict' : '';
                            return `
                                <div class="booking-slot ${conflictClass}" onclick="editBooking(${booking.id})" style="margin-bottom: 4px; padding: 4px; font-size: 11px;">
                                    <div style="font-weight: bold;">${hall?.name || ''}</div>
                                    <div class="booking-trainer">${trainer?.name || 'مدرب'}</div>
                                    <div class="booking-group">${group?.name || 'جروب'}</div>
                                </div>
                            `;
                        }).join('');
                        
                        cellContent += `
                            <div style="border-bottom: 1px solid #dee2e6; padding-bottom: 5px; margin-bottom: 5px;">
                                <div style="font-size: 10px; color: var(--gray); text-align: right; margin-bottom: 3px;">${floor.name}</div>
                                ${bookingsHtml}
                            </div>
                        `;
                    }
                }
                
                if (!cellContent) {
                    cells += `<td onclick="openAddModalAtSlot('${day}', '${time}')" style="cursor: pointer; background: rgba(0,0,0,0.02);"></td>`;
                } else {
                    cells += `<td style="vertical-align: top;">${cellContent}<div style="text-align: center; margin-top: 5px;"><button class="btn-icon" style="background: #f8f9fa; color: #6c757d; padding: 2px 5px;" onclick="openAddModalAtSlot('${day}', '${time}')"><i class="fas fa-plus"></i></button></div></td>`;
                }
            }
            rows += `<tr>${cells}</tr>`;
        }
        body.innerHTML = rows;
    }"""
content = content.replace(old_renderWeekly, new_renderWeekly)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated schedule.html layout")
