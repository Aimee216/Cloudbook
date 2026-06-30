import urllib.request, json, sys, time

API = "http://localhost:8000"
token = None

def api(method, path, data=None):
    url = API + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data, ensure_ascii=False).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode()) if e.code != 404 else {"error": str(e)}

# 1. Login
print("=" * 50)
print("  初始化数据 - 超市管理系统")
print("=" * 50)
r = api("POST", "/api/auth/login", {"username": "admin", "password": "admin123"})
if r.get("code") == 200:
    token = r["data"]["token"]
    print(f"✅ 登录成功: {r['data']['user']['username']}")
else:
    print(f"❌ 登录失败: {r}")
    sys.exit(1)

# 2. Categories
categories = [
    {"name": "饮料", "sort_order": 1},
    {"name": "零食", "sort_order": 2},
    {"name": "日用品", "sort_order": 3},
    {"name": "粮油调味", "sort_order": 4},
    {"name": "生鲜水果", "sort_order": 5},
    {"name": "酒类", "sort_order": 6},
    {"name": "文具办公", "sort_order": 7},
    {"name": "洗护用品", "sort_order": 8},
]
cat_ids = {}
for c in categories:
    r = api("POST", "/api/categories", c)
    if r.get("code") == 200:
        cid = r["data"].get("id", r["data"].get("data",{}).get("id",0))
        cat_ids[c["name"]] = cid
        print(f"  ✅ 分类: {c['name']} (ID:{cid})")
    else:
        print(f"  ❌ 分类失败 {c['name']}: {r.get('detail','')}")

# 3. Suppliers
suppliers = [
    {"name": "农夫山泉股份有限公司", "contact_person": "张经理", "phone": "13800138001", "address": "浙江省杭州市", "supply_category": "饮料", "rating": 5},
    {"name": "统一集团", "contact_person": "李经理", "phone": "13800138002", "address": "上海市", "supply_category": "饮料/零食", "rating": 4},
    {"name": "康师傅控股", "contact_person": "王经理", "phone": "13800138003", "address": "天津市", "supply_category": "饮料/方便面", "rating": 5},
    {"name": "宝洁中国", "contact_person": "赵经理", "phone": "13800138004", "address": "广东省广州市", "supply_category": "日用品/洗护", "rating": 4},
    {"name": "青岛啤酒", "contact_person": "孙经理", "phone": "13800138005", "address": "山东省青岛市", "supply_category": "酒类", "rating": 5},
    {"name": "中粮集团", "contact_person": "周经理", "phone": "13800138006", "address": "北京市", "supply_category": "粮油调味", "rating": 4},
    {"name": "本地果业合作社", "contact_person": "吴经理", "phone": "13800138007", "address": "本地农产品基地", "supply_category": "生鲜水果", "rating": 3},
    {"name": "晨光文具", "contact_person": "郑经理", "phone": "13800138008", "address": "上海市", "supply_category": "文具办公", "rating": 4},
]
sup_ids = []
for s in suppliers:
    r = api("POST", "/api/suppliers", s)
    if r.get("code") == 200:
        sid = r["data"].get("id", r["data"].get("data",{}).get("id",0))
        sup_ids.append(sid)
        print(f"  ✅ 供应商: {s['name']} (ID:{sid})")
    else:
        print(f"  ❌ 供应商失败 {s['name']}: {r.get('detail','')}")

# 4. Products
products = [
    {"name":"农夫山泉矿泉水550ml","barcode":"6901010100011","category_id":cat_ids.get("饮料",1),"unit":"瓶","purchase_price":1.20,"selling_price":2.00,"stock_quantity":500,"stock_lower_limit":50,"supplier_id":1,"status":"上架"},
    {"name":"统一冰红茶500ml","barcode":"6901010100028","category_id":cat_ids.get("饮料",1),"unit":"瓶","purchase_price":2.50,"selling_price":3.50,"stock_quantity":300,"stock_lower_limit":30,"supplier_id":2,"status":"上架"},
    {"name":"康师傅方便面红烧牛肉","barcode":"6901010100035","category_id":cat_ids.get("零食",2),"unit":"桶","purchase_price":3.00,"selling_price":4.50,"stock_quantity":200,"stock_lower_limit":20,"supplier_id":3,"status":"上架"},
    {"name":"乐事薯片原味40g","barcode":"6901010100042","category_id":cat_ids.get("零食",2),"unit":"包","purchase_price":4.00,"selling_price":6.00,"stock_quantity":150,"stock_lower_limit":15,"supplier_id":2,"status":"上架"},
    {"name":"奥利奥饼干原味97g","barcode":"6901010100059","category_id":cat_ids.get("零食",2),"unit":"包","purchase_price":5.00,"selling_price":7.50,"stock_quantity":120,"stock_lower_limit":10,"supplier_id":2,"status":"上架"},
    {"name":"海飞丝去屑洗发露200ml","barcode":"6901010100066","category_id":cat_ids.get("洗护用品",8),"unit":"瓶","purchase_price":18.00,"selling_price":28.00,"stock_quantity":80,"stock_lower_limit":10,"supplier_id":4,"status":"上架"},
    {"name":"舒肤佳香皂纯白清香","barcode":"6901010100073","category_id":cat_ids.get("洗护用品",8),"unit":"块","purchase_price":3.50,"selling_price":5.50,"stock_quantity":200,"stock_lower_limit":20,"supplier_id":4,"status":"上架"},
    {"name":"金龙鱼花生油5L","barcode":"6901010100080","category_id":cat_ids.get("粮油调味",4),"unit":"桶","purchase_price":55.00,"selling_price":79.90,"stock_quantity":50,"stock_lower_limit":5,"supplier_id":6,"status":"上架"},
    {"name":"东北大米10kg","barcode":"6901010100097","category_id":cat_ids.get("粮油调味",4),"unit":"袋","purchase_price":35.00,"selling_price":49.90,"stock_quantity":40,"stock_lower_limit":5,"supplier_id":6,"status":"上架"},
    {"name":"青岛啤酒经典10听装","barcode":"6901010100103","category_id":cat_ids.get("酒类",6),"unit":"听","purchase_price":3.00,"selling_price":5.00,"stock_quantity":300,"stock_lower_limit":30,"supplier_id":5,"status":"上架"},
    {"name":"红富士苹果1kg","barcode":"6901010100110","category_id":cat_ids.get("生鲜水果",5),"unit":"袋","purchase_price":6.00,"selling_price":9.90,"stock_quantity":60,"stock_lower_limit":10,"supplier_id":7,"status":"上架"},
    {"name":"晨光签字笔12支装","barcode":"6901010100127","category_id":cat_ids.get("文具办公",7),"unit":"盒","purchase_price":8.00,"selling_price":12.00,"stock_quantity":100,"stock_lower_limit":10,"supplier_id":8,"status":"上架"},
    {"name":"清风抽纸3层100抽*6包","barcode":"6901010100134","category_id":cat_ids.get("日用品",3),"unit":"提","purchase_price":10.00,"selling_price":15.90,"stock_quantity":90,"stock_lower_limit":10,"supplier_id":4,"status":"上架"},
    {"name":"可口可乐330ml*6罐装","barcode":"6901010100141","category_id":cat_ids.get("饮料",1),"unit":"组","purchase_price":7.00,"selling_price":10.00,"stock_quantity":250,"stock_lower_limit":25,"supplier_id":2,"status":"上架"},
    {"name":"海天上等蚝油510g","barcode":"6901010100158","category_id":cat_ids.get("粮油调味",4),"unit":"瓶","purchase_price":4.50,"selling_price":7.00,"stock_quantity":120,"stock_lower_limit":10,"supplier_id":6,"status":"上架"},
]
prod_ids = []
for p in products:
    r = api("POST", "/api/products", p)
    if r.get("code") == 200:
        pid = r["data"].get("id", r["data"].get("data",{}).get("id",0))
        prod_ids.append(pid)
        print(f"  ✅ 商品: {p['name']} (ID:{pid})")
    else:
        print(f"  ❌ 商品失败 {p['name']}: {r.get('detail','')}")

# 5. Customers
customers = [
    {"name":"张三","phone":"13900000001","password":"123456"},
    {"name":"李四","phone":"13900000002","password":"123456"},
    {"name":"王五","phone":"13900000003","password":"123456"},
    {"name":"赵六","phone":"13900000004","password":"123456"},
    {"name":"钱七","phone":"13900000005","password":"123456"},
]
for c in customers:
    r = api("POST", "/api/customers", c)
    if r.get("code") == 200:
        print(f"  ✅ 顾客: {c['name']} ({c['phone']})")
    else:
        print(f"  ❌ 顾客失败 {c['name']}: {r.get('detail','')}")

# Summary
print()
print("=" * 50)
print("  ✅ 初始化数据完成!")
print(f"  📦 分类: {len(categories)} 个")
print(f"  🏭 供应商: {len(suppliers)} 个")
print(f"  📋 商品: {len(products)} 个")
print(f"  👤 顾客: {len(customers)} 个")
print("=" * 50)
