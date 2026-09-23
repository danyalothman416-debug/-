<!DOCTYPE html>
<html lang="ckb" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سیستەمی بەڕێوەبردنی قەرز | دانیال</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {
            --bg-color: #0b0f19;
            --surface: #111827;
            --surface-glass: rgba(17, 24, 39, 0.7);
            --border: rgba(255, 255, 255, 0.08);
            --accent-primary: #3b82f6;
            --accent-danger: #ef4444;
            --accent-success: #10b981;
            --text-primary: #f9fafb;
            --text-secondary: #9ca3af;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Vazirmatn', sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 24px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* بەشی سەرەوە (Header) */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            background: var(--surface-glass);
            padding: 20px 28px;
            border-radius: 20px;
            border: 1px solid var(--border);
            backdrop-filter: blur(12px);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand i {
            font-size: 28px;
            color: var(--accent-primary);
        }

        .brand h1 {
            font-size: 22px;
            font-weight: 800;
        }

        .btn-add {
            background: var(--accent-primary);
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: 0.2s;
        }

        .btn-add:hover {
            opacity: 0.9;
            transform: translateY(-2px);
        }

        /* کارتەکانی ئامار (KPIs) */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 22px;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .stat-info p {
            color: var(--text-secondary);
            font-size: 13px;
            margin-bottom: 6px;
        }

        .stat-info h2 {
            font-size: 24px;
            font-weight: 800;
        }

        .stat-icon {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }

        .stat-icon.debt { background: rgba(239, 68, 68, 0.15); color: var(--accent-danger); }
        .stat-icon.paid { background: rgba(16, 185, 129, 0.15); color: var(--accent-success); }
        .stat-icon.users { background: rgba(59, 130, 246, 0.15); color: var(--accent-primary); }

        /* خشتەی کڕیاران و گەڕان */
        .table-wrapper {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            overflow-x: auto;
        }

        .table-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            gap: 16px;
        }

        .search-box {
            position: relative;
            width: 100%;
            max-width: 340px;
        }

        .search-box input {
            width: 100%;
            padding: 10px 40px 10px 14px;
            background: #1f2937;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: #fff;
            outline: none;
            font-size: 13px;
        }

        .search-box i {
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: right;
            font-size: 14px;
        }

        th {
            padding: 14px;
            color: var(--text-secondary);
            font-weight: 600;
            border-bottom: 1px solid var(--border);
        }

        td {
            padding: 16px 14px;
            border-bottom: 1px solid var(--border);
        }

        .badge-balance {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 8px;
            font-weight: 700;
        }

        .badge-debt {
            background: rgba(239, 68, 68, 0.15);
            color: var(--accent-danger);
        }

        .badge-zero {
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-success);
        }

        .action-btns {
            display: flex;
            gap: 8px;
        }

        .btn-sm {
            padding: 6px 12px;
            border-radius: 8px;
            border: none;
            font-size: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: 0.2s;
        }

        .btn-debt { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        .btn-debt:hover { background: var(--accent-danger); color: #fff; }

        .btn-pay { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .btn-pay:hover { background: var(--accent-success); color: #fff; }

        .btn-history { background: #374151; color: #fff; }
        .btn-history:hover { background: #4b5563; }

        /* مۆداڵەکان */
        .modal {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }

        .modal-content {
            background: var(--surface);
            border: 1px solid var(--border);
            width: 100%;
            max-width: 420px;
            border-radius: 18px;
            padding: 24px;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .input-group {
            margin-bottom: 14px;
        }

        .input-group label {
            display: block;
            margin-bottom: 6px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .input-group input, .input-group textarea {
            width: 100%;
            padding: 10px;
            background: #1f2937;
            border: 1px solid var(--border);
            border-radius: 10px;
            color: #fff;
            outline: none;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- سەرپەڕە -->
        <header>
            <div class="brand">
                <i class="fa-solid fa-file-invoice-dollar"></i>
                <div>
                    <h1>سیستەمی قەرز و حسابات</h1>
                    <p style="font-size: 12px; color: var(--text-secondary);">بەڕێوەبردنی قەرزی کڕیاران و تۆمارە داراییەکان</p>
                </div>
            </div>
            <button class="btn-add" onclick="openCustomerModal()">
                <i class="fa-solid fa-user-plus"></i> کڕیاری نوێ
            </button>
        </header>

        <!-- ئامارەکان -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-info">
                    <p>کۆی گشتی قەرزی ماوە لای خەڵک</p>
                    <h2 style="color: var(--accent-danger);">{{ "{:,.0f}".format(total_debt) }} دینار</h2>
                </div>
                <div class="stat-icon debt"><i class="fa-solid fa-hand-holding-dollar"></i></div>
            </div>

            <div class="stat-card">
                <div class="stat-info">
                    <p>کۆی گشتی پارەی وەرگیراو (دانراوە)</p>
                    <h2 style="color: var(--accent-success);">{{ "{:,.0f}".format(total_paid) }} دینار</h2>
                </div>
                <div class="stat-icon paid"><i class="fa-solid fa-circle-check"></i></div>
            </div>

            <div class="stat-card">
                <div class="stat-info">
                    <p>کۆی ژمارەی کڕیاران</p>
                    <h2>{{ total_customers }}</h2>
                </div>
                <div class="stat-icon users"><i class="fa-solid fa-users"></i></div>
            </div>
        </div>

        <!-- خشتەی زانیارییەکان -->
        <div class="table-wrapper">
            <div class="table-top">
                <h3 style="font-size: 16px;">لیستی کڕیارەکان و دۆخی قەرز</h3>
                <div class="search-box">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="searchInput" placeholder="گەڕان بەپێی ناو یان مۆبایل..." onkeyup="filterTable()">
                </div>
            </div>

            <table id="customersTable">
                <thead>
                    <tr>
                        <th>ناوی کڕیار</th>
                        <th>ژمارەی مۆبایل</th>
                        <th>ناونیشان</th>
                        <th>بڕی ماوە (باڵانس)</th>
                        <th>کردارەکان</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in customers %}
                    <tr>
                        <td style="font-weight: 700;">{{ c.name }}</td>
                        <td>{{ c.phone }}</td>
                        <td>{{ c.address }}</td>
                        <td>
                            <span class="badge-balance {% if c.balance > 0 %}badge-debt{% else %}badge-zero{% endif %}">
                                {{ "{:,.0f}".format(c.balance) }} دینار
                            </span>
                        </td>
                        <td>
                            <div class="action-btns">
                                <button class="btn-sm btn-debt" onclick="openTxModal({{ c.id }}, '{{ c.name }}', 'debt')">+ قەرز</button>
                                <button class="btn-sm btn-pay" onclick="openTxModal({{ c.id }}, '{{ c.name }}', 'payment')">دانەوە</button>
                                <button class="btn-sm btn-history" onclick="viewHistory({{ c.id }})"><i class="fa-solid fa-clock-rotate-left"></i></button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <!-- مۆداڵی کڕیاری نوێ -->
    <div class="modal" id="customerModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>زیادکردنی کڕیاری نوێ</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('customerModal')"></i>
            </div>
            <form id="customerForm">
                <div class="input-group">
                    <label>ناوی تەواو</label>
                    <input type="text" id="custName" required placeholder="ناوی کڕیار...">
                </div>
                <div class="input-group">
                    <label>ژمارەی مۆبایل</label>
                    <input type="text" id="custPhone" placeholder="0750...">
                </div>
                <div class="input-group">
                    <label>ناونیشان</label>
                    <input type="text" id="custAddress" placeholder="گەڕەک / شوێن...">
                </div>
                <button type="submit" class="btn-add" style="width: 100%; justify-content: center; margin-top: 10px;">پاشەکەوتکردن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی زیادکردنی مامەڵە (قەرز / دانەوە) -->
    <div class="modal" id="txModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="txTitle">تۆمارکردنی مامەڵە</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('txModal')"></i>
            </div>
            <form id="txForm">
                <input type="hidden" id="txCustomerId">
                <input type="hidden" id="txType">
                <div class="input-group">
                    <label>بڕی پارە (دینار)</label>
                    <input type="number" id="txAmount" required placeholder="نموونە: 25000">
                </div>
                <div class="input-group">
                    <label>تێبینی / هۆکار</label>
                    <textarea id="txNote" rows="2" placeholder="بۆچی براوە یان چۆن دراوەتەوە..."></textarea>
                </div>
                <button type="submit" class="btn-add" id="txSubmitBtn" style="width: 100%; justify-content: center; margin-top: 10px;">تۆمارکردن</button>
            </form>
        </div>
    </div>

    <!-- مۆداڵی بینینی مێژووی وەسڵەکان -->
    <div class="modal" id="historyModal">
        <div class="modal-content" style="max-width: 550px;">
            <div class="modal-header">
                <h3 id="historyCustName">مێژووی مامەڵەکان</h3>
                <i class="fa-solid fa-xmark" style="cursor: pointer;" onclick="closeModal('historyModal')"></i>
            </div>
            <div id="historyList" style="max-height: 350px; overflow-y: auto;"></div>
        </div>
    </div>

    <script>
        function openCustomerModal() { document.getElementById('customerModal').style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }

        // گەڕان لەناو کڕیارەکاندا
        function filterTable() {
            let input = document.getElementById("searchInput").value.toLowerCase();
            let rows = document.querySelectorAll("#customersTable tbody tr");
            rows.forEach(row => {
                let text = row.innerText.toLowerCase();
                row.style.display = text.includes(input) ? "" : "none";
            });
        }

        // پاشەکەوتکردنی کڕیار
        document.getElementById('customerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                name: document.getElementById('custName').value,
                phone: document.getElementById('custPhone').value,
                address: document.getElementById('custAddress').value
            };
            const res = await fetch('/api/customer/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if (res.ok) location.reload();
        });

        // کردنەوەی مۆداڵی مامەڵە
        function openTxModal(custId, custName, type) {
            document.getElementById('txCustomerId').value = custId;
            document.getElementById('txType').value = type;
            document.getElementById('txTitle').textContent = type === 'debt' ? `قەرزی نوێ بۆ: ${custName}` : `دانەوەی پارە لەلایەن: ${custName}`;
            document.getElementById('txSubmitBtn').style.background = type === 'debt' ? 'var(--accent-danger)' : 'var(--accent-success)';
            document.getElementById('txModal').style.display = 'flex';
        }

        // تۆمارکردنی قەرز یان دانەوە
        document.getElementById('txForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                customer_id: document.getElementById('txCustomerId').value,
                type: document.getElementById('txType').value,
                amount: document.getElementById('txAmount').value,
                note: document.getElementById('txNote').value
            };
            const res = await fetch('/api/transaction/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            if (res.ok) location.reload();
        });

        // هێنانی مێژووی کڕیار
        async function viewHistory(custId) {
            const res = await fetch(`/api/customer/${custId}/statement`);
            const data = await res.json();
            if (res.ok) {
                document.getElementById('historyCustName').textContent = `وەسڵەکانی: ${data.customer.name}`;
                let container = document.getElementById('historyList');
                container.innerHTML = '';
                if(data.history.length === 0) {
                    container.innerHTML = '<p style="text-align:center; color: #888; padding: 20px;">هیچ مامەڵەیەک تۆمار نەکراوە</p>';
                } else {
                    data.history.forEach(tx => {
                        let isDebt = tx.type === 'debt';
                        container.innerHTML += `
                            <div style="background: #1f2937; padding: 12px; border-radius: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="font-weight: 700; color: ${isDebt ? '#ef4444' : '#10b981'}">
                                        ${isDebt ? 'قەرز براوە' : 'پارە دراوەتەوە'}
                                    </span>
                                    <p style="font-size: 12px; color: #9ca3af; margin-top: 4px;">${tx.note}</p>
                                    <span style="font-size: 11px; color: #6b7280;">${tx.date}</span>
                                </div>
                                <div style="font-weight: 800; font-size: 15px;">
                                    ${Number(tx.amount).toLocaleString()} دینار
                                </div>
                            </div>
                        `;
                    });
                }
                document.getElementById('historyModal').style.display = 'flex';
            }
        }
    </script>
</body>
</html>
