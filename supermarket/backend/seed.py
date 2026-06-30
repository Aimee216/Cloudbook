import os, sys
sys.path.insert(0, r"E:\Cloudbook_git\supermarket\backend")
os.chdir(r"E:\Cloudbook_git\supermarket\backend")

from app.database import SessionLocal, engine, Base
from app.models import User, Employee
from app.utils.auth import hash_password
from datetime import date

Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing = db.query(User).filter(User.username == "admin").first()
if not existing:
    emp = Employee(name="系统管理员", gender="未知", position="超级管理员", hire_date=date.today(), salary=0, status="在职")
    db.add(emp)
    db.flush()
    
    admin = User(username="admin", password=hash_password("admin123"), role="超级管理员", status="正常", employee_id=emp.id)
    db.add(admin)
    db.commit()
    print("Admin user seeded: admin / admin123")
else:
    print("Admin user already exists")

# Also seed a test employee user
existing2 = db.query(User).filter(User.username == "员工").first()
if not existing2:
    emp2 = Employee(name="张三", gender="男", phone="13800138000", position="收银员", hire_date=date.today(), salary=5000, status="在职")
    db.add(emp2)
    db.flush()
    user2 = User(username="员工", password=hash_password("123456"), role="普通员工", status="正常", employee_id=emp2.id)
    db.add(user2)
    db.commit()
    print("Employee user seeded: 员工 / 123456")
else:
    print("Employee user already exists")

db.close()
