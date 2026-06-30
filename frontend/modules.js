/* ===== 超市管理系统 - 前端模块 (modules.js) ===== */

// ===== Common Helpers =====
function $(id) { return document.getElementById(id); }

function renderTable(tbodyId, data, cols) {
    const tbody = $(tbodyId);
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="20" class="empty">暂无数据</td></tr>';
        return;
    }
    tbody.innerHTML = data.map(row => {
        let tr = "<tr>";
        cols.forEach(c => {
            let val = row[c.v] !== undefined && row[c.v] !== null ? row[c.v] : "";
            if (c.fn) val = c.fn(val, row);
            if (c.link) val = `<a href="${c.link(val,row)}">${val}</a>`;
            tr += `<td>${val}</td>`;
        });
        tr += "</tr>";
        return tr;
    }).join("");
}

function showModal(id) { const el = $(id); if(el) el.style.display = "flex"; }
function hideModal(id) { const el = $(id); if(el) el.style.display = "none"; }

function modalForm(fields, submitText, submitFn) {
    let html = fields.map(f => {
        let val = f.value || "";
        if (f.type === "select") {
            let opts = (f.options||[]).map(o => `<option value="${o.value}" ${val==o.value?"selected":""}>${o.label||o.value}</option>`).join("");
            return `<div class="form-group"><label>${f.label}</label><select id="f_${f.key}" class="form-input">${opts}</select></div>`;
        }
        return `<div class="form-group"><label>${f.label}</label><input id="f_${f.key}" class="form-input" type="${f.type||"text"}" value="${val}" ${f.required?"required":""}></div>`;
    }).join("");
    html += `<button class="btn btn-primary" onclick="submitForm(\`${submitFn}\`)">${submitText}</button>`;
    return html;
}

function getFormValue(key) { const el = $("f_"+key); return el ? el.value : ""; }
function setFormValue(key, val) { const el = $("f_"+key); if(el) el.value = val; }

function submitForm(fn) {
    try {
        return eval(fn);
    } catch(e) {
        console.error("submitForm error:", e);
        alert("操作失败");
    }
}

function formatDate(d) { if(!d) return "-"; return d.substring(0,10); }
function formatMoney(v) { return "¥" + parseFloat(v||0).toFixed(2); }
function fmtStatus(v) {
    const m = {"正常":"badge-green","离职":"badge-gray","上架":"badge-green","下架":"badge-red","待支付":"badge-green","待发货":"badge-gray","已发货":"badge-green","已完成":"badge-blue","已取消":"badge-red","库存不足":"badge-red","库存过多":"badge-orange","库存偏高":"badge-orange"};
    return `<span class="badge ${m[v]||"badge-gray"}">${v||"-"}</span>`;
}

// ===== View System =====
let currentView = "dashboard";
function switchView(name) {
    currentView = name;
    document.querySelectorAll(".view-section").forEach(v => v.style.display = "none");
    const sec = $(name+"View");
    if (sec) {
        sec.style.display = "block";
        const mod = window[name+"Module"];
        if (mod && mod.load) mod.load();
    }
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
    const nav = document.querySelector(`[data-view="${name}"]`);
    if (nav) nav.classList.add("active");
    $("pageTitle").textContent = nav ? nav.textContent.trim() : "工作台";
}

// ===== API helpers =====
function apiGet(path) { return fetch(API_BASE + path, { headers: AUTH }).then(r=>r.json()); }
function apiPost(path, body) { return fetch(API_BASE + path, { method:"POST", headers:AUTH, body:JSON.stringify(body) }).then(r=>r.json()); }
function apiPut(path, body) { return fetch(API_BASE + path, { method:"PUT", headers:AUTH, body:JSON.stringify(body) }).then(r=>r.json()); }
function apiDel(path) { return fetch(API_BASE + path, { method:"DELETE", headers:AUTH }).then(r=>r.json()); }
function apiForm(path, fd) { return fetch(API_BASE + path, { method:"POST", headers:{Authorization:AUTH.Authorization}, body:fd }).then(r=>r.json()); }

// ===== Dashboard Module =====
var dashboardModule = {
    load: async function() {
        try {
            const [prod, emp, inv, fin] = await Promise.all([
                apiGet("/api/products/?page=1&page_size=1").catch(()=>({data:{total:0}})),
                apiGet("/api/employees/").catch(()=>({data:{total:0,data:[]}})),
                apiGet("/api/stats/inventory-analysis").catch(()=>({data:{}})),
                apiGet("/api/stats/finance").catch(()=>({data:{sales_revenue:0}}))
            ]);
            $("statProducts").textContent = prod.data?.total ?? "-";
            $("statLowStock").textContent = inv.data?.low_stock_count ?? "-";
            $("statRevenue").textContent = "¥" + (fin.data?.sales_revenue?.toLocaleString() ?? "0");
            $("statEmployees").textContent = emp.data?.total ?? "-";
            const list = emp.data?.data || [];
            renderTable("empBody", list, [
                {v:"name",fn:(v,r)=>`<strong>${v||"-"}</strong>`},
                {v:"position"},{v:"phone"},{v:"hire_date",fn:formatDate},
                {v:"status",fn:fmtStatus}
            ]);
        } catch(e) { console.error(e); }
    }
};

// ===== Products Module =====
var productsModule = {
    load: async function() {
        try {
            const res = await apiGet("/api/products/");
            renderTable("productsBody", res.data?.data||[], [
                {v:"barcode"},{v:"name",fn:v=>`<strong>${v||"-"}</strong>`},
                {v:"category_name"},{v:"selling_price",fn:formatMoney},
                {v:"stock_quantity",fn:v=>`<span style="font-weight:600">${v??0}</span>`},
                {v:"status",fn:fmtStatus},
                {v:"id",fn:(v)=>`<button class="btn-sm" onclick="productsModule.edit(${v})">编辑</button>
                    <button class="btn-sm btn-danger" onclick="productsModule.del(${v})">删除</button>`}
            ]);
        } catch(e) { console.error("productsModule.load error:", e); }
    },
    showForm: function(data) {
        $("prodModalTitle").textContent = data?.id ? "编辑商品" : "添加商品";
        $("prodFormBody").innerHTML = modalForm([
            {key:"name",label:"商品名称",value:data?.name||"",required:true},
            {key:"barcode",label:"条形码",value:data?.barcode||""},
            {key:"category_id",label:"分类ID",type:"number",value:data?.category_id||""},
            {key:"unit",label:"单位",value:data?.unit||"个"},
            {key:"selling_price",label:"售价",type:"number",value:data?.selling_price||0},
            {key:"purchase_price",label:"进价",type:"number",value:data?.purchase_price||0},
            {key:"stock_quantity",label:"初始库存",type:"number",value:data?.stock_quantity||0},
            {key:"description",label:"描述",value:data?.description||""}
        ], data?.id ? "保存" : "添加", data?.id ? `productsModule.save(${data.id})` : "productsModule.save(0)");
        showModal("prodModal");
    },
    edit: async function(id) {
        const res = await apiGet("/api/products/");
        const item = res.data?.data?.find(p=>p.id===id);
        if(item) this.showForm(item);
    },
    save: async function(id) {
        const body = {name:getFormValue("name"),barcode:getFormValue("barcode"),
            category_id:parseInt(getFormValue("category_id"))||null,
            unit:getFormValue("unit")||"个",
            selling_price:parseFloat(getFormValue("selling_price"))||0,
            purchase_price:parseFloat(getFormValue("purchase_price"))||0,
            stock_quantity:parseInt(getFormValue("stock_quantity"))||0,
            description:getFormValue("description")||""};
        const res = id ? await apiPut("/api/products/"+id, body) : await apiPost("/api/products/", body);
        if(res.code===200) { hideModal("prodModal"); this.load(); }
        else alert(res.detail||"操作失败");
    },
    del: async function(id) {
        if(confirm("确认删除该商品？")) {
            const res = await apiDel("/api/products/"+id);
            if(res.code===200) this.load(); else alert(res.detail||"删除失败");
        }
    }
};

// ===== Categories Module =====
var categoriesModule = {
    load: async function() {
        try {
            const res = await apiGet("/api/categories/");
            renderTable("catBody", res.data||[], [
                {v:"id"},{v:"name",fn:v=>`<strong>${v||"-"}</strong>`},
                {v:"parent_id"},{v:"sort_order"},
                {v:"id",fn:(v)=>`<button class="btn-sm" onclick="categoriesModule.edit(${v})">编辑</button>
                    <button class="btn-sm btn-danger" onclick="categoriesModule.del(${v})">删除</button>`}
            ]);
        } catch(e) { console.error("categoriesModule.load error:", e); }
    },
    showForm: function(data) {
        $("catName").value = data?.name||"";
        showModal("catModal");
    },
    add: async function() {
        const name = $("catName")?.value;
        if(!name) return alert("请输入分类名称");
        const res = await apiPost("/api/categories/", {name});
        if(res.code===200) { hideModal("catModal"); this.load(); }
        else alert(res.detail||"添加失败");
    },
    edit: async function(id) {
        const res = await apiGet("/api/categories/");
        const item = (res.data||[]).find(c=>c.id===id);
        if(item) this.showForm(item);
    },
    del: async function(id) {
        if(confirm("确认删除该分类？")) {
            const res = await apiDel("/api/categories/"+id);
            if(res.code===200) this.load(); else alert(res.detail||"删除失败");
        }
    }
};

// ===== Orders Module =====
var ordersModule = {
    load: async function() {
        try {
            const res = await apiGet("/api/orders/?page=1&page_size=20");
            renderTable("orderBody", res.data?.data||[], [
                {v:"order_no",fn:v=>`<strong>${v||"-"}</strong>`},
                {v:"customer_name",fn:v=>v||"-"},{v:"total_amount",fn:formatMoney},
                {v:"status",fn:fmtStatus},{v:"order_time",fn:formatDate}
            ]);
        } catch(e) { console.error("ordersModule.load error:", e); }
    },
    viewDetail: async function(id) {
        alert("订单详情 ID: "+id);
    },
    del: async function(id) {
        if(confirm("确认删除该订单？")) {
            const res = await apiDel("/api/orders/"+id);
            if(res.code===200) this.load(); else alert(res.detail||"删除失败");
        }
    }
};

// ===== Stock Module =====
var stockModule = {
    load: async function() {
        try {
            const res = await apiGet("/api/stock/");
            renderTable("stockBody", res.data?.data||[], [
                {v:"name",fn:v=>`<strong>${v||"-"}</strong>`},{v:"barcode"},
                {v:"stock_quantity",fn:v=>`<span style="font-weight:600;color:${v<=10?"#dc2626":"inherit"}">${v??0}</span>`},
                {v:"status",fn:fmtStatus},
                {v:"id",fn:(v)=>`<button class="btn-sm" onclick="stockModule.edit(${v})">调整</button>`}
            ]);
        } catch(e) { console.error("stockModule.load error:", e); }
    },
    showForm: function(data) {
        const isAdd = !data;
        const title = data?.name ? "库存调整 - " + data.name : "新建库存调整";
        const fields = [];
        if (isAdd) {
            fields.push({key:"product_id",label:"商品ID",type:"number",value:0,required:true});
        }
        fields.push(
            {key:"change_quantity",label:"调整数量",type:"number",value:0},
            {key:"change_type",label:"类型",type:"select",options:[{value:"采购入库",label:"采购入库"},{value:"手动出库",label:"手动出库"},{value:"盘点调整",label:"盘点调整"}],value:"采购入库"},
            {key:"remark",label:"备注",value:""}
        );
        $("stockModalTitle").textContent = title;
        $("stockFormBody").innerHTML = modalForm(fields, "确认", `stockModule.save(${data?.id || 0})`);
        showModal("stockModal");
    },
    edit: async function(id) {
        const res = await apiGet("/api/stock/");
        const item = res.data?.data?.find(p=>p.id===id);
        if(item) this.showForm(item);
    },
    save: async function(id) {
        const pid = id || parseInt(getFormValue("product_id")) || 0;
        const body = {product_id:pid,change_quantity:parseInt(getFormValue("change_quantity"))||0,
            change_type:getFormValue("change_type"),remark:getFormValue("remark"),operator:"管理员"};
        const qty = body.change_quantity;
        if(qty===0) return alert("数量不能为0");
        const res = qty>0 ? await apiPost("/api/stock/inbound", body) : await apiPost("/api/stock/outbound", {...body,change_quantity:Math.abs(qty)});
        if(res.code===200) { hideModal("stockModal"); this.load(); }
        else alert(res.detail||"操作失败");
    }
};

// ===== Suppliers Module =====
var suppliersModule = {
    load: async function() {
        try {
            const res = await apiGet("/api/suppliers/");
            renderTable("suppBody", res.data?.data||[], [
                {v:"name",fn:v=>`<strong>${v||"-"}</strong>`},{v:"contact_person",fn:v=>v||"-"},
                {v:"phone",fn:v=>v||"-"},{v:"rating",fn:v=>"★".repeat(v||0)},
                {v:"id",fn:(v)=>`<button class="btn-sm" onclick="suppliersModule.edit(${v})">编辑</button>
                    <button class="btn-sm btn-danger" onclick="suppliersModule.del(${v})">删除</button>`}
            ]);
        } catch(e) { console.error("suppliersModule.load error:", e); }
    },
    showForm: function(data) {
        $("suppModalTitle").textContent = data?.id ? "编辑供应商" : "添加供应商";
        $("suppFormBody").innerHTML = modalForm([
            {key:"name",label:"名称",value:data?.name||"",required:true},
            {key:"contact_person",label:"联系人",value:data?.contact_person||""},
            {key:"phone",label:"电话",value:data?.phone||""},
            {key:"address",label:"地址",value:data?.address||""}
        ], data?.id ? "保存" : "添加", data?.id ? `suppliersModule.save(${data.id})` : "suppliersModule.save(0)");
        showModal("suppModal");
    },
    save: async function(id) {
        const body = {name:getFormValue("name"),contact_person:getFormValue("contact_person"),
            phone:getFormValue("phone"),address:getFormValue("address")};
        const res = id ? await apiPut("/api/suppliers/"+id, body) : await apiPost("/api/suppliers/", body);
        if(res.code===200) { hideModal("suppModal"); this.load(); }
        else alert(res.detail||"操作失败");
    },
    edit: async function(id) {
        const res = await apiGet("/api/suppliers/");
        const item = res.data?.data?.find(s=>s.id===id);
        if(item) this.showForm(item);
    },
    del: async function(id) {
        if(confirm("确认删除该供应商？")) {
            const res = await apiDel("/api/suppliers/"+id);
            if(res.code===200) this.load(); else alert(res.detail||"删除失败");
        }
    }
};

// ===== Customers Module =====
var customersModule = {
    load: async function() {
        try {
            const res = await apiGet("/api/customers/?page=1&page_size=100");
            renderTable("custBody", res.data?.data||[], [
                {v:"name",fn:v=>`<strong>${v||"-"}</strong>`},{v:"phone",fn:v=>v||"-"},
                {v:"points",fn:v=>v??0},{v:"total_consumption",fn:v=>formatMoney(v||0)},
                {v:"register_time",fn:formatDate},
                {v:"id",fn:(v)=>`<button class="btn-sm btn-danger" onclick="customersModule.del(${v})">删除</button>`}
            ]);
        } catch(e) { console.error("customersModule.load error:", e); }
    },
    showForm: function(data) {
        $("custModalTitle").textContent = "添加顾客";
        $("custFormBody").innerHTML = modalForm([
            {key:"name",label:"姓名",value:data?.name||""},
            {key:"phone",label:"手机号",value:data?.phone||"",required:true},
            {key:"password",label:"密码",type:"password",value:"",required:true},
            {key:"gender",label:"性别",type:"select",options:[{value:"男",label:"男"},{value:"女",label:"女"},{value:"未知",label:"未知"}],value:data?.gender||"未知"}
        ], "添加", "customersModule.save(0)");
        showModal("custModal");
    },
    save: async function(id) {
        const body = {name:getFormValue("name"),phone:getFormValue("phone"),
            password:getFormValue("password"),gender:getFormValue("gender")};
        const res = await apiPost("/api/customers/register", body);
        if(res.code===200) { hideModal("custModal"); this.load(); }
        else alert(res.detail||"操作失败");
    },
    del: async function(id) {
        if(confirm("确认删除该顾客？")) {
            const res = await apiDel("/api/customers/"+id);
            if(res.code===200) this.load(); else alert(res.detail||"删除失败");
        }
    }
};

// ===== Employees Module =====
var employeesModule = {
    load: async function() {
        try {
            const res = await apiGet("/api/employees/");
            renderTable("empListBody", res.data?.data||[], [
                {v:"name",fn:v=>`<strong>${v||"-"}</strong>`},{v:"position"},{v:"phone"},
                {v:"hire_date",fn:formatDate},{v:"salary",fn:formatMoney},
                {v:"status",fn:fmtStatus},
                {v:"id",fn:(v)=>`<button class="btn-sm" onclick="employeesModule.edit(${v})">编辑</button>
                    <button class="btn-sm btn-danger" onclick="employeesModule.del(${v})">删除</button>`}
            ]);
        } catch(e) { console.error("employeesModule.load error:", e); }
    },
    showForm: function(data) {
        $("empModalTitle").textContent = data?.id ? "编辑员工" : "添加员工";
        $("empFormBody").innerHTML = modalForm([
            {key:"name",label:"姓名",value:data?.name||"",required:true},
            {key:"gender",label:"性别",type:"select",options:[{value:"男",label:"男"},{value:"女",label:"女"},{value:"未知",label:"未知"}],value:data?.gender||"男"},
            {key:"phone",label:"手机号",value:data?.phone||""},
            {key:"position",label:"职位",value:data?.position||""},
            {key:"hire_date",label:"入职日期",type:"date",value:data?.hire_date||""},
            {key:"salary",label:"薪资",type:"number",value:data?.salary||0},
            {key:"status",label:"状态",type:"select",options:[{value:"在职",label:"在职"},{value:"离职",label:"离职"}],value:data?.status||"在职"}
        ], data?.id ? "保存修改" : "添加", data?.id ? `employeesModule.save(${data.id})` : "employeesModule.save(0)");
        showModal("empModal");
    },
    save: async function(id) {
        const body = {name:getFormValue("name"),gender:getFormValue("gender"),
            phone:getFormValue("phone"),position:getFormValue("position"),
            hire_date:getFormValue("hire_date"),salary:parseFloat(getFormValue("salary"))||0,
            status:getFormValue("status")};
        const res = id ? await apiPut("/api/employees/"+id, body) : await apiPost("/api/employees/", body);
        if(res.code===200) { hideModal("empModal"); this.load(); }
        else alert(res.detail||"操作失败");
    },
    edit: async function(id) {
        const res = await apiGet("/api/employees/");
        const item = res.data?.data?.find(e=>e.id===id);
        if(item) this.showForm(item);
    },
    del: async function(id) {
        if(confirm("确认删除该员工？")) {
            const res = await apiDel("/api/employees/"+id);
            if(res.code===200) this.load(); else alert(res.detail||"删除失败");
        }
    }
};

// ===== Stats Module =====
var statsModule = {
    load: async function() {
        try {
            const [inv, fin, top] = await Promise.all([
                apiGet("/api/stats/inventory-analysis").catch(()=>({data:{}})),
                apiGet("/api/stats/finance").catch(()=>({data:{}})),
                apiGet("/api/stats/top-products").catch(()=>({data:{}}))
            ]);
            $("statTotalProd").textContent = inv.data?.total_products ?? "-";
            $("statLowCount").textContent = inv.data?.low_stock_count ?? "-";
            $("statLowRatio").textContent = (inv.data?.low_stock_ratio??0) + "%";
            $("statTurnover").textContent = inv.data?.turnover_rate ?? "-";
            $("statRevenue2").textContent = formatMoney(fin.data?.sales_revenue||0);
            $("statProfit").textContent = formatMoney(fin.data?.gross_profit||0);
            $("statMargin").textContent = (fin.data?.gross_margin??0) + "%";
        } catch(e) { console.error(e); }
    }
};
