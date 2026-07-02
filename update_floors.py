import re

def modify_floors():
    with open('floors.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Tabs UI under toolbar
    toolbar_old = """<div class="toolbar">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="بحث بالاسم، الكود، أو رقم الهاتف...">
                    <button id="searchBtn"><i class="fas fa-search"></i> بحث</button>
                </div>
                <button class="btn-add" id="addFloorBtn">
                    <i class="fas fa-plus"></i>
                    <span>إضافة دور جديد</span>
                </button>
            </div>"""
            
    toolbar_new = """<div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <button id="tabFloors" onclick="switchTab('floors')" style="padding: 10px 20px; border-radius: 10px; border: none; background: var(--primary-blue); color: white; cursor: pointer; font-weight: bold;">الأدوار</button>
                <button id="tabHalls" onclick="switchTab('halls')" style="padding: 10px 20px; border-radius: 10px; border: none; background: white; color: var(--dark-blue); cursor: pointer; font-weight: bold; border: 1px solid #e9ecef;">القاعات</button>
            </div>
            <div class="toolbar">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="بحث...">
                    <button id="searchBtn"><i class="fas fa-search"></i> بحث</button>
                </div>
                <button class="btn-add" id="addBtn">
                    <i class="fas fa-plus"></i>
                    <span id="addBtnText">إضافة دور جديد</span>
                </button>
            </div>"""
    content = content.replace(toolbar_old, toolbar_new)
    
    # Also replace id="addFloorBtn" listeners if any
    content = content.replace("document.getElementById('addFloorBtn').addEventListener('click', () => openAddModal());", "document.getElementById('addBtn').addEventListener('click', () => { if (currentTab === 'floors') openAddModal(); else openAddHallModal(); });")

    # 2. Add Halls Table under Floors Table
    floors_table_old = """<!-- users Table -->
            <div class="floors-table-container">
                <table class="floors-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم الدور/القاعة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="floorsTableBody">
                        <tr>
                            <td colspan="3" style="text-align: center;">جاري التحميل...</td>
                        </tr>
                    </tbody>
                </table>
            </div>"""
    
    floors_table_new = """<!-- Floors Table -->
            <div class="floors-table-container" id="floorsSection">
                <table class="floors-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم الدور</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="floorsTableBody">
                        <tr>
                            <td colspan="3" style="text-align: center;">جاري التحميل...</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Halls Table -->
            <div class="floors-table-container" id="hallsSection" style="display: none;">
                <table class="floors-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>اسم القاعة</th>
                            <th>الدور</th>
                            <th>النوع</th>
                            <th>السعة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="hallsTableBody">
                        <tr>
                            <td colspan="6" style="text-align: center;">جاري التحميل...</td>
                        </tr>
                    </tbody>
                </table>
            </div>"""
    content = content.replace(floors_table_old, floors_table_new)

    # 3. Add Hall Modal next to Floor Modal
    floor_modal_end = """<div class="modal-footer">
            <button class="btn-cancel" id="cancelModal">إلغاء</button>
            <button class="btn-save" id="saveFloor">حفظ</button>
        </div>
    </div>
</div>"""
    
    hall_modal = """\n<!-- Add/Edit Hall Modal -->
<div class="modal" id="hallModal">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="modalTitleHall">إضافة قاعة جديدة</h3>
            <button class="close-modal" id="closeModalHall" onclick="closeHallModal()">&times;</button>
        </div>
        <div class="modal-body">
            <form id="hallForm">
                <input type="hidden" id="hallId" value="">
                <div class="form-group">
                    <label>اسم القاعة *</label>
                    <input type="text" id="hallName" required placeholder="مثال: قاعة 101">
                </div>
                <div class="form-group">
                    <label>الدور التابع له *</label>
                    <select id="hallFloorId" required></select>
                </div>
                <div class="form-group">
                    <label>نوع القاعة *</label>
                    <select id="hallType" required>
                        <option value="نظري">نظري</option>
                        <option value="عملي">عملي</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>سعة القاعة (عدد الطلاب) *</label>
                    <input type="number" id="hallCapacity" required placeholder="مثال: 50">
                </div>
            </form>
        </div>
        <div class="modal-footer">
            <button class="btn-cancel" onclick="closeHallModal()">إلغاء</button>
            <button class="btn-save" id="saveHallBtn">حفظ</button>
        </div>
    </div>
</div>"""
    content = content.replace(floor_modal_end, floor_modal_end + hall_modal)

    # 4. Javascript logic for tabs, halls fetching, rendering, saving
    js_vars_old = """let allFloors = [];
    let currentPage = 1;"""
    js_vars_new = """let allFloors = [];
    let allHalls = [];
    let currentTab = 'floors';
    let currentPage = 1;"""
    content = content.replace(js_vars_old, js_vars_new)

    js_load_old = """async function loadData() {
        showLoading(true);
        try {
            allFloors = await apiCall('getAllFloors');
            filterAndRender();
        } catch (error) {
            console.error('Error:', error);
            // Error handled in apiCall
        }
        showLoading(false);
    }"""
    js_load_new = """async function loadData() {
        showLoading(true);
        try {
            const [fRes, hRes] = await Promise.all([
                apiCall('getAllFloors'),
                apiCall('getAllHalls')
            ]);
            allFloors = fRes || [];
            allHalls = hRes || [];
            
            // Populate Floor Select for Halls
            const floorSelect = document.getElementById('hallFloorId');
            if (floorSelect) {
                floorSelect.innerHTML = '<option value="">اختر الدور</option>' + 
                    allFloors.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
            }
            
            filterAndRender();
        } catch (error) {
            console.error('Error:', error);
        }
        showLoading(false);
    }"""
    content = content.replace(js_load_old, js_load_new)

    js_filter_old = """function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        let filtered = [...allFloors];
        
        if (searchTerm) {
            filtered = filtered.filter(s => 
                (s.name && s.name.toLowerCase().includes(searchTerm))
            );
        }
        
        renderTable(filtered);
    }"""
    js_filter_new = """function filterAndRender() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        
        if (currentTab === 'floors') {
            let filtered = [...allFloors];
            if (searchTerm) filtered = filtered.filter(s => (s.name && s.name.toLowerCase().includes(searchTerm)));
            renderTable(filtered);
        } else {
            let filtered = [...allHalls];
            if (searchTerm) filtered = filtered.filter(s => (s.name && s.name.toLowerCase().includes(searchTerm)));
            renderHallsTable(filtered);
        }
    }
    
    function switchTab(tab) {
        currentTab = tab;
        document.getElementById('tabFloors').style.background = tab === 'floors' ? 'var(--primary-blue)' : 'white';
        document.getElementById('tabFloors').style.color = tab === 'floors' ? 'white' : 'var(--dark-blue)';
        document.getElementById('tabHalls').style.background = tab === 'halls' ? 'var(--primary-blue)' : 'white';
        document.getElementById('tabHalls').style.color = tab === 'halls' ? 'white' : 'var(--dark-blue)';
        
        document.getElementById('floorsSection').style.display = tab === 'floors' ? 'block' : 'none';
        document.getElementById('hallsSection').style.display = tab === 'halls' ? 'block' : 'none';
        
        document.getElementById('addBtnText').textContent = tab === 'floors' ? 'إضافة دور جديد' : 'إضافة قاعة جديدة';
        
        currentPage = 1;
        filterAndRender();
    }"""
    content = content.replace(js_filter_old, js_filter_new)

    # 5. Halls JS Logic (renderHallsTable, openAddHallModal, saveHall, editHall, deleteHall)
    js_methods_new = """
    function renderHallsTable(halls) {
        const tbody = document.getElementById('hallsTableBody');
        
        if (!halls || halls.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">لا توجد قاعات</td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }
        
        const totalPages = Math.ceil(halls.length / rowsPerPage);
        const start = (currentPage - 1) * rowsPerPage;
        const paginated = halls.slice(start, start + rowsPerPage);
        
        tbody.innerHTML = paginated.map(h => {
            const floor = allFloors.find(f => f.id == h.floorNumber);
            return `
                <tr>
                    <td><strong>${h.id || '-'}</strong></td>
                    <td>${h.name || '-'}</td>
                    <td>${floor ? floor.name : '-'}</td>
                    <td><span style="background: ${h.type === 'عملي' ? '#e0f2fe' : '#fef3c7'}; color: ${h.type === 'عملي' ? '#0284c7' : '#d97706'}; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">${h.type || 'عملي'}</span></td>
                    <td>${h.capacity || 0}</td>
                    <td class="action-buttons">
                        <button class="btn-icon btn-edit" onclick="editHall(${h.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deleteHall(${h.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        }).join('');
        
        renderPagination(totalPages);
    }

    function openAddHallModal() {
        document.getElementById('modalTitleHall').textContent = 'إضافة قاعة جديدة';
        document.getElementById('hallForm').reset();
        document.getElementById('hallId').value = '';
        document.getElementById('hallModal').classList.add('show');
    }
    
    function closeHallModal() {
        document.getElementById('hallModal').classList.remove('show');
    }
    
    function editHall(id) {
        const hall = allHalls.find(h => h.id == id);
        if (hall) {
            document.getElementById('modalTitleHall').textContent = 'تعديل قاعة';
            document.getElementById('hallId').value = hall.id;
            document.getElementById('hallName').value = hall.name || '';
            document.getElementById('hallFloorId').value = hall.floorNumber || '';
            document.getElementById('hallType').value = hall.type || 'عملي';
            document.getElementById('hallCapacity').value = hall.capacity || '';
            document.getElementById('hallModal').classList.add('show');
        }
    }
    
    async function saveHall() {
        const rules = {
            hallName: [{ fn: Validators.required, msg: 'الاسم مطلوب' }],
            hallFloorId: [{ fn: Validators.required, msg: 'الدور مطلوب' }],
            hallCapacity: [{ fn: Validators.required, msg: 'السعة مطلوبة' }]
        };
        if (!validateForm(rules)) return;
        
        const data = {
            id: document.getElementById('hallId').value || null,
            name: document.getElementById('hallName').value,
            floorNumber: document.getElementById('hallFloorId').value,
            type: document.getElementById('hallType').value,
            capacity: document.getElementById('hallCapacity').value
        };
        
        showLoading(true);
        try {
            await apiCall('saveHall', { data: data });
            showToast('تم الحفظ بنجاح', 'success');
            closeHallModal();
            loadData();
        } catch(e) {}
        showLoading(false);
    }
    
    async function deleteHall(id) {
        if (confirm('هل أنت متأكد من حذف هذه القاعة؟')) {
            showLoading(true);
            try {
                await apiCall('deleteHall', { id: id });
                showToast('تم الحذف بنجاح', 'success');
                loadData();
            } catch(e) {}
            showLoading(false);
        }
    }
    """
    
    # Insert methods before "window.editFloor = editFloor;"
    window_export_old = """window.editFloor = editFloor;"""
    window_export_new = js_methods_new + """\n    window.editFloor = editFloor;
    window.editHall = editHall;
    window.deleteHall = deleteHall;
    window.switchTab = switchTab;
    window.closeHallModal = closeHallModal;"""
    content = content.replace(window_export_old, window_export_new)

    # Listeners for saveHallBtn
    content = content.replace("document.getElementById('saveFloor').addEventListener('click', () => saveFloor());", "document.getElementById('saveFloor').addEventListener('click', () => saveFloor());\n        document.getElementById('saveHallBtn').addEventListener('click', () => saveHall());")

    with open('floors.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    modify_floors()
