import os

lines = open(r"E:\Cloudbook_git\supermarket\frontend\dashboard.html", "r", encoding="utf-8").readlines()

# Find new CSS and body
new_css_start = -1
new_body_start = -1
for i, line in enumerate(lines):
    if "<style>" in line and i > 110:
        if new_css_start == -1:
            new_css_start = i
    if "<body" in line and i > new_css_start and new_css_start != -1:
        new_body_start = i
        break

new_css_lines = lines[new_css_start:new_body_start - 1]
new_body_lines = lines[new_body_start:]

clean = []
clean.append("<!DOCTYPE html>\n")
clean.append('<html lang="zh-CN">\n')
clean.append("<head>\n")
clean.append('    <meta charset="UTF-8">\n')
clean.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
clean.append("    <title>超市管理系统 - 工作台</title>\n")
for line in new_css_lines:
    clean.append(line)
clean.append("</head>\n")
for line in new_body_lines:
    clean.append(line)

with open(r"E:\Cloudbook_git\supermarket\frontend\dashboard.html", "w", encoding="utf-8") as f:
    f.writelines(clean)

print(f"Wrote clean dashboard: {len(clean)} lines")
