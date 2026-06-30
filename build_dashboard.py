import os

html = open(r"E:\Cloudbook_git\supermarket\frontend\dashboard.html", "r", encoding="utf-8").read()

# Find the content div
marker = '<div class="content">'
idx = html.find(marker)
if idx > 0:
    html = html[:idx + len(marker)]

new_content = r"""
    <style>
        .form-input { width:100%%; padding:8px 12px; border:1.5px solid #e0e0e0; border-radius:8px; font-size:13px; outline:none; }
        .form-input:focus { border-color:#667eea; box-shadow:0 0 0 3px rgba(102,126,234,0.15); }
        .form-group { margin-bottom:14px; }
        .form-group label { display:block; font-size:12px; font-weight:600; color:#555; margin-bottom:4px; }
        .form-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
        .page-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; }
        .page-header h3 { font-size:18px; font-weight:600; color:#1a1a2e; }
        .btn { padding:8px 20px; border:none; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; transition:all 0.2s; }
        .btn-primary { background:linear-gradient(135deg,#667eea,#764ba2); color:#fff; }
        .btn-primary:hover { opacity:0.9; }
        .btn-sm { padding:4px 12px; border:none; border-radius:6px; font-size:12px; cursor:pointer; background:#f0f2ff; color:#667eea; transition:all 0.2s; }
        .btn-sm:hover { background:#e0e4ff; }
        .btn-danger { background:#fef2f2; color:#dc2626; }
        .btn-danger:hover { background:#fecaca; }
        .card { background:#fff; border-radius:12px; padding:0; box-shadow:0 1px 3px rgba(0,0,0,0.06); overflow:hidden; }
        .table { width:100%%; border-collapse:collapse; }
        .table th { text-align:left; padding:12px 16px; font-size:12px; font-weight:600; color:#888; text-transform:uppercase; letter-spacing:0.5px; background:#f9fafb; border-bottom:1px solid #f0f0f0; }
        .table td { padding:11px 16px; font-size:13px; border-bottom:1px solid #f5f5f5; }
        .table tr:last-child td { border-bottom:none; }
        .table .empty { text-align:center; padding:40px; color:#bbb; }
        .badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:12px; font-weight:500; }
        .badge-green { background:#dcfce7; color:#16a34a; }
        .badge-red { background:#fef2f2; color:#dc2626; }
        .badge-gray { background:#f3f4f6; color:#6b7280; }
        .badge-blue { background:#eef2ff; color:#6366f1; }
        .badge-orange { background:#fff7ed; color:#ea580c; }
        .modal-overlay { display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.4); z-index:1000; align-items:center; justify-content:center; }
        .modal-overlay.show { display:flex; }
        .modal { background:#fff; border-radius:16px; padding:28px; width:90%%; max-width:560px; max-height:80vh; overflow-y:auto; animation:fadeIn 0.2s ease; }
        .modal-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; padding-bottom:12px; border-bottom:1px solid #f0f0f0; }
        .modal-header h3 { font-size:16px; font-weight:600; color:#1a1a2e; }
        .modal-close { font-size:24px; cursor:pointer; color:#aaa; line-height:1; }
        .modal-close:hover { color:#333; }
        .view-section { display:none; }
        #dashboardView { display:block; }
        .stats-grid2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:20px; }
        .stat-box { background:#fff; border-radius:10px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,0.06); text-align:center; }
        .stat-box .val { font-size:24px; font-weight:700; color:#1a1a2e; }
        .stat-box .lbl { font-size:12px; color:#888; margin-top:4px; }
        @media (max-width:768px) { .form-row { grid-template-columns:1fr; } }
    </style>
</head>
<body>
<aside class="sidebar">
    <div class="logo"><div class="icon"><svg viewBox="0 0 24 24"><path d="M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z"/></svg></div><span>超市管理系统</span></div>
    <div class="nav-label">导航</div>
    <a class="nav-item active" href="#" data-view="dashboard" onclick="switchView('dashboard')"><svg viewBox="0 0 24 24"><path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/></svg><span>工作台</span></a>
    <div class="nav-label">管理</div>
    <a class="nav-item" href="#" data-view="products" onclick="switchView('products')"><svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8h16v10z"/></svg><span>商品管理</span></a>
    <a class="nav-item" href="#" data-view="categories" onclick="switchView('categories')"><svg viewBox="0 0 24 24"><path d="M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z"/></svg><span>分类管理</span></a>
    <a class="nav-item" href="#" data-view="orders" onclick="switchView('orders')"><svg viewBox="0 0 24 24"><path d="M21 5V3H3v2l8 9v5H6v2h12v-2h-5v-5l8-9z"/></svg><span>订单管理</span></a>
    <a class="nav-item" href="#" data-view="stock" onclick="switchView('stock')"><svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 18H4V4h16v16zM6 6h12v2H6zm0 4h12v2H6zm0 8h8v-2H6z"/></svg><span>库存管理</span></a>
    <a class="nav-item" href="#" data-view="suppliers" onclick="switchView('suppliers')"><svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg><span>供应商管理</span></a>
    <a class="nav-item" href="#" data-view="customers" onclick="switchView('customers')"><svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg><span>顾客管理</span></a>
    <a class="nav-item" href="#" data-view="employees" onclick="switchView('employees')"><svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg><span>员工管理</span></a>
    <a class="nav-item" href="#" data-view="stats" onclick="switchView('stats')"><svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg><span>数据报表</span></a>
</aside>
<div class="main">
    <div class="topbar">
        <h2 id="pageTitle">工作台</h2>
        <div class="user-info">
            <span id="userNameDisplay"></span>
            <div class="avatar" id="userAvatar"></div>
            <button class="logout" onclick="logout()">退出登录</button>
        </div>
    </div>
    <div class="content">
        <!-- Dashboard -->
        <div class="view-section" id="dashboardView">
            <div class="stats-grid">
                <div class="stat-card"><div class="label">商品总数</div><div class="value" id="statProducts">-</div><div class="sub">全部商品</div></div>
                <div class="stat-card"><div class="label">低库存预警</div><div class="value" id="statLowStock">-</div><div class="sub" style="color:#dc2626;">需及时补货</div></div>
                <div class="stat-card"><div class="label">本月营收</div><div class="value" id="statRevenue">-</div><div class="sub">当月销售额</div></div>
                <div class="stat-card"><div class="label">员工人数</div><div class="value" id="statEmployees">-</div><div class="sub">在职员工</div></div>
            </div>
            <div class="section-header"><h3>员工列表</h3><span class="badge badge-blue">最新数据</span></div>
            <div class="card"><table class="table"><thead><tr><th>姓名</th><th>职位</th><th>手机号</th><th>入职日期</th><th>状态</th></tr></thead><tbody id="empBody"><tr><td colspan="5" class="empty">加载中...</td></tr></tbody></table></div>
        </div>

        <!-- Products View -->
        <div class="view-section" id="productsView"></div>
        <!-- Categories View -->
        <div class="view-section" id="categoriesView"><div class="page-header"><h3>分类管理</h3><button class="btn btn-primary" id="btnAddCat">+ 添加分类</button></div>
            <div class="card"><table class="table"><thead><tr><th>ID</th><th>名称</th><th>父分类</th><th>排序</th><th>操作</th></tr></thead><tbody id="catBody"><tr><td colspan="5" class="empty">加载中...</td></tr></tbody></table></div></div>
        <!-- Orders View -->
        <div class="view-section" id="ordersView"></div>
        <!-- Stock View -->
        <div class="view-section" id="stockView"></div>
        <!-- Suppliers View -->
        <div class="view-section" id="suppliersView"></div>
        <!-- Customers View -->
        <div class="view-section" id="customersView"><div class="page-header"><h3>顾客管理</h3></div>
            <div class="card"><table class="table"><thead><tr><th>姓名</th><th>手机号</th><th>积分</th><th>总消费</th><th>注册时间</th><th>操作</th></tr></thead><tbody id="custBody"><tr><td colspan="6" class="empty">加载中...</td></tr></tbody></table></div></div>
        <!-- Employees View -->
        <div class="view-section" id="employeesView"></div>
        <!-- Stats View -->
        <div class="view-section" id="statsView"><div class="page-header"><h3>数据报表</h3></div>
            <div class="stats-grid2">
                <div class="stat-box"><div class="val" id="statTotalProd">-</div><div class="lbl">商品总数</div></div>
                <div class="stat-box"><div class="val" id="statLowCount">-</div><div class="lbl">低库存数量</div></div>
                <div class="stat-box"><div class="val" id="statLowRatio">-</div><div class="lbl">低库存占比</div></div>
                <div class="stat-box"><div class="val" id="statTurnover">-</div><div class="lbl">库存周转率</div></div>
                <div class="stat-box"><div class="val" id="statRevenue2">-</div><div class="lbl">销售额</div></div>
                <div class="stat-box"><div class="val" id="statProfit">-</div><div class="lbl">毛利</div></div>
                <div class="stat-box"><div class="val" id="statMargin">-</div><div class="lbl">毛利率</div></div>
            </div></div>
    </div>
</div>

<!-- Modals -->
<div class="modal-overlay" id="productModal"><div class="modal">
    <div class="modal-header"><h3 id="productModalTitle">添加商品</h3><span class="modal-close" onclick="hideModal(productModal)">&times;</span></div>
    <div class="modal-body" id="productFormBody"></div></div></div>
<div class="modal-overlay" id="catModal"><div class="modal" style="max-width:400px">
    <div class="modal-header"><h3>添加分类</h3><span class="modal-close" onclick="hideModal(catModal)">&times;</span></div>
    <div class="modal-body"><div class="form-group"><label>分类名称</label><input id="catName" class="form-input"></div>
    <button class="btn btn-primary" id="btnAddCatSubmit">添加</button></div></div></div>
<div class="modal-overlay" id="orderDetailModal"><div class="modal" style="max-width:480px">
    <div class="modal-header"><h3>订单详情</h3><span class="modal-close" onclick="hideModal(orderDetailModal)">&times;</span></div>
    <div class="modal-body" id="orderDetail"></div></div></div>
<div class="modal-overlay" id="supModal"><div class="modal">
    <div class="modal-header"><h3 id="supModalTitle">添加供应商</h3><span class="modal-close" onclick="hideModal(supModal)">&times;</span></div>
    <div class="modal-body" id="supFormBody"></div></div></div>
<div class="modal-overlay" id="empModal"><div class="modal">
    <div class="modal-header"><h3 id="empModalTitle">添加员工</h3><span class="modal-close" onclick="hideModal(empModal)">&times;</span></div>
    <div class="modal-body" id="empFormBody"></div></div></div>

<script>
const API_BASE = window.location.port === '3000' ? 'http://localhost:8000' : '';
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user') || '{}');
if (!token) { window.location.href = 'login'; }
const AUTH = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token };
document.getElementById('userNameDisplay').textContent = user.username || '';
document.getElementById('userAvatar').textContent = (user.username || '?')[0];
function logout() { localStorage.removeItem('token'); localStorage.removeItem('user'); window.location.href = 'login'; }

// Generate view sections
var mods = {products:'商品管理',orders:'订单管理',stock:'库存管理',suppliers:'供应商管理',employees:'员工管理'};
var headers = {products:'<th>名称</th><th>条形码</th><th>分类</th><th>进价</th><th>售价</th><th>库存</th><th>状态</th><th>操作</th>',
    orders:'<th>订单号</th><th>顾客</th><th>金额</th><th>状态</th><th>时间</th><th>操作</th>',
    stock:'<th>商品</th><th>变动数量</th><th>类型</th><th>变动前</th><th>变动后</th><th>操作人</th><th>时间</th>',
    suppliers:'<th>名称</th><th>联系人</th><th>电话</th><th>评分</th><th>操作</th>',
    employees:'<th>姓名</th><th>职位</th><th>手机号</th><th>入职日期</th><th>薪资</th><th>状态</th><th>操作</th>'};
Object.keys(mods).forEach(function(m) {
    var v = document.getElementById(m+'View');
    if (!v) return;
    var btn = (m=='stock'||m=='orders') ? '' : '<button class="btn btn-primary" id="btnAdd'+m+'">+ 添加</button>';
    v.innerHTML = '<div class="page-header"><h3>'+mods[m]+'</h3>'+btn+'</div><div class="card"><table class="table"><thead><tr>'+headers[m]+'</tr></thead><tbody id="'+m+'Body"><tr><td colspan="10" class="empty">加载中...</td></tr></tbody></table></div>';
});

// Bind dynamic buttons
setTimeout(function() {
    document.getElementById('btnAddCat') && (document.getElementById('btnAddCat').onclick = function() { categoriesModule.showForm(); });
    document.getElementById('btnAddCatSubmit') && (document.getElementById('btnAddCatSubmit').onclick = function() { categoriesModule.add(); });
    Object.keys(mods).forEach(function(m) {
        var btn = document.getElementById('btnAdd'+m);
        if (btn) btn.onclick = function() { window[m+'Module'].showForm(); };
    });
}, 100);
</script>
<script src="modules.js"></script>
<script>dashboardModule.load();</script>
</body>
</html>
"""

html += new_content

with open(r"E:\Cloudbook_git\supermarket\frontend\dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard updated successfully")
