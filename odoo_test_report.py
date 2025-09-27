import re
from datetime import datetime

# Đường dẫn file log Odoo
LOG_FILE = "./log/odoo.log"
# Tên file HTML report
HTML_FILE = "odoo_test_report.html"

# Đọc log
with open(LOG_FILE, "r", encoding="utf-8") as f:
    log_lines = f.readlines()

# Patterns
test_start_pattern = re.compile(
    r"Starting (\S+\.\S+) \.\.\.")  # Bắt TestClass.test_method
error_pattern = re.compile(
    r"ERROR odoo-user3 odoo.addons.\S+: FAIL: (\S+\.\S+)")  # Để bắt lỗi trong một test cụ thể

tests = []
current_test = None

for line in log_lines:
    line = line.strip()

    # Bắt đầu test
    start_match = test_start_pattern.search(line)

    # Bắt lỗi trong test (FAIL)
    error_match = error_pattern.search(line)

    if start_match:
        # Bắt tên test
        test_name = start_match.group(1)
        current_test = {"name": test_name, "status": "RUNNING", "log": []}
        tests.append(current_test)
        current_test["log"].append(line)

    elif current_test:
        # Ghi log vào test hiện tại
        current_test["log"].append(line)

    # Kiểm tra nếu có lỗi trong test
    if error_match:
        failed_test_name = error_match.group(1)
        for test in tests:
            if test["name"] == failed_test_name:
                test["status"] = "ERROR"  # Đánh dấu test đó là ERROR
                # Thêm thông tin lỗi vào log
                test["log"].append(f"ERROR: {failed_test_name} failed.")

# Cập nhật trạng thái 'RUNNING' thành 'PASSED'
for test in tests:
    if test["status"] == "RUNNING":
        # Đánh dấu trạng thái 'RUNNING' thành 'PASSED'
        test["status"] = "PASSED"

# Tạo HTML report
html_content = f"""
<html>
<head>
    <title>Odoo Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .passed {{ color: green; }}
        .error {{ color: red; }}
        pre {{
            background: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 5px;
        }}
    </style>
</head>
<body>
    <h1>Odoo Test Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <table>
        <tr><th>Test Name</th><th>Status</th><th>Log</th></tr>
"""

# Xây dựng nội dung HTML cho báo cáo
for test in tests:
    status_class = "passed" if test["status"] == "PASSED" else "error"
    log_text = "<br>".join(test["log"])
    html_content += f"""
    <tr>
        <td>{test['name']}</td>
        <td class="{status_class}">{test['status']}</td>
        <td><pre>{log_text}</pre></td>
    </tr>
    """

html_content += """
    </table>
</body>
</html>
"""

# Ghi ra file HTML
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Report generated: {HTML_FILE}")
