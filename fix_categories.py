import re, os

path = r"E:\Cloudbook_git\supermarket\backend\app\api\categories.py"
content = open(path, "r", encoding="utf-8").read()

# Replace the list_categories function
pattern = r'@router\.get\("/", response_model=ApiResponse\)\s+async def list_categories\(.*?return ApiResponse\(data=tree\)'
replacement = (
    '@router.get("/", response_model=ApiResponse)\n'
    'async def list_categories(db: Session = Depends(get_db)):\n'
    '    categories = db.query(Category).order_by(Category.sort_order).all()\n'
    '    data = []\n'
    '    for c in categories:\n'
    '        data.append({"id": c.id, "name": c.name, "parent_id": c.parent_id, "sort_order": c.sort_order})\n'
    '    return ApiResponse(data=data)'
)
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)
print("Categories API fixed")
