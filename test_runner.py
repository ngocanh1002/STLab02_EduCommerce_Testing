
from pathlib import Path
import csv, datetime, html, json
from collections import Counter
import pandas as pd
from decimal import Decimal
from ecommerce_app import Checkout, Customer, Cart, Product, D

ROOT = Path(__file__).resolve().parent

def fixture(subtotal_case='600k'):
    """Test Fixture: Provides isolated environment for each test case. 
       Old def fixture in ecommerce_app.py doesnt have enough cases for 5 new REQ"""
    service = Checkout()
    customer = Customer('U_NEW', authenticated=True)
    cart = Cart(service.catalog)
    if subtotal_case == 'clean_cart':
        pass  # Fresh empty cart for testing Cart operations (REQ-02)
    elif subtotal_case == 'empty_cart':
        pass  # Empty cart
    elif subtotal_case == 'unauth_user':
        customer = Customer('U_GUEST', authenticated=False)
        # User not logged in (REQ-04)
        cart.add('A', 3)
    elif subtotal_case == 'used_voucher':
        customer = Customer('U_USED', authenticated=True, used_codes={'SAVE10'})
        # User has used voucher (REQ-07)
        cart.add('A', 3)
    elif subtotal_case == '500k':
        cart.add('A', 1)
        cart.add('B', 1)
    elif subtotal_case == '499999':
        # Order just under the 500k boundary (REQ-09)
        cart.add('A', 1)
        cart.add('B', 1)
        service.catalog.products['B'].price = D(299999)
    elif subtotal_case == '600k':
        cart.add('A', 3)
    elif subtotal_case == '1000k':
        cart.add('A', 5)
    elif subtotal_case == '1500k':
        cart.add('B', 5)
    elif subtotal_case == '300k':
        cart.add('B', 1)
    else:
        raise ValueError(f"UNKNOWN_FIXTURE: {subtotal_case}")
    return service, customer, cart

def execute_case(row):
    # 1. Initialize the fixture and read data from a CSV row
    app, user, cart = fixture(row['fixture_key'])
    req = row['requirement_id']
    inp = json.loads(row['input_json']) if row.get('input_json') else {}
    exp = json.loads(row['expected_json']) if row.get('expected_json') else {}
    actual_res = {}
    err = ''
    passed = False
    before_stock = {k: p.stock for k, p in app.catalog.products.items()}
    before_orders_count = len(app.orders)
    try:
        # 2. Test Dispatcher: Coordinate the invocation of the correct function based on the Requirement ID.
        if req == 'REQ-02':
            # Cart: Validate addition and line aggregation
            for action in inp.get('actions', []):
                cart.add(action['sku'], action['quantity'])
            actual_res = {
                'total_quantity': sum(line.quantity for line in cart.lines),
                'lines_count': len(cart.lines),
                'subtotal': int(cart.subtotal())
            }
            passed = (actual_res == exp)
        elif req == 'REQ-04':
            # Authentication: Check login enforcement
            order = app.place(user, cart, method=inp.get('method', 'COD'), key=row['test_case_id'])
            actual_res = {
                'status': order.status,
                'orders_count': len(app.orders)
            }
            passed = (actual_res.get('status') == exp.get('status'))

        elif req == 'REQ-07':
            # Promotion: Invalid voucher, reuse, and used_codes updates
            v = inp.get('voucher')
            m = inp.get('method', 'COD')
            appr = inp.get('approved', True)
            order = app.place(user, cart, voucher=v, method=m, approved=appr, key=row['test_case_id'])
            actual_res = {
                'voucher_in_used_codes': (v in user.used_codes),
                'discount': int(order.discount)
            }
            passed = (actual_res == exp)
        elif req == 'REQ-09':
            # Shipping: Calculate shipping fee based on area and subtotal
            subtotal = cart.subtotal()
            area = inp.get('area')
            fee = app.shipping.calculate(subtotal, area)
            actual_res = {'shipping': int(fee)}
            passed = (actual_res == exp)
        elif req == 'REQ-10':
            # Payment: COD status and Online payment approval/decline
            m = inp.get('method')
            appr = inp.get('approved', True)
            order = app.place(user, cart, method=m, approved=appr, key=row['test_case_id'])
            actual_res = {
                'order_status': order.status,
                'orders_count': len(app.orders),
                'charges_count': len(app.payments.charges)
            }
            passed = all(actual_res.get(k) == exp[k] for k in exp)
        else:
            raise ValueError(f"UNKNOWN_REQUIREMENT_TEST: {req}")

    except Exception as e:
        err = str(e)
        after_stock = {k: p.stock for k, p in app.catalog.products.items()}
        stock_restored = (after_stock == before_stock) # Can inventory be returned?
        actual_res = {
            'error': err,
            'orders_count': len(app.orders),
            'voucher_in_used_codes': (inp.get('voucher') in user.used_codes) if inp.get('voucher') else False,
            'stock_restored': stock_restored
        }
        if 'error' in exp:
            passed = (exp['error'] == err)
            if 'orders_count':
                if 'orders_count' in exp:
                    passed = passed and (exp['orders_count'] == len(app.orders))
            if 'voucher_in_used_codes' in exp:
                passed = passed and (exp['voucher_in_used_codes'] == actual_res['voucher_in_used_codes'])
            if 'stock_restored' in exp:
                passed = passed and (exp['stock_restored'] == stock_restored)
        else:
            passed = False
    after_stock = {k: p.stock for k, p in app.catalog.products.items()}
    status = 'PASS' if passed else 'FAIL'
    return {
        **row,
        'execution_status': status,
        'actual_result': json.dumps(actual_res, ensure_ascii=False),
        'error_message': err,
        'stock_before': json.dumps(before_stock),
        'stock_after': json.dumps(after_stock),
        'executed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

def run_suite(csv_path=None, out_dir=None):
    csv_path = Path(csv_path or ROOT / 'STLab02_TestCases.csv')
    output = Path(out_dir or ROOT / 'reports')
    output.mkdir(exist_ok=True, parents=True)

    # 1. Đọc và parse dữ liệu file CSV với chuẩn utf-8-sig
    with csv_path.open(newline='', encoding='utf-8-sig') as f:
        testcases = list(csv.DictReader(f))

    # 2. Cơ chế phòng vệ: Kiểm tra chống trùng lặp Test Case ID
    ids = [x['test_case_id'] for x in testcases]
    if len(ids) != len(set(ids)):
        raise ValueError('DUPLICATE_TEST_IDS detected!')

    # 3. Chạy từng dòng test case qua hàm execute_case
    results = [execute_case(x) for x in testcases]

    df = pd.DataFrame(results)
    counts = Counter(df['execution_status'])
    summary = df.groupby(['requirement_id', 'execution_status']).size().unstack(fill_value=0).reset_index()

    totals = pd.DataFrame([{
        'executed': len(df),
        'passed': counts['PASS'],
        'failed': counts.get('FAIL', 0),
        'blocked': counts.get('BLOCKED', 0),
        'pass_rate': round(100 * counts['PASS'] / len(df), 1)
    }])
    # 1. Export CSV execution log
    df.to_csv(output / 'test_execution.csv', index=False, encoding='utf-8-sig')
    # 2. Export Excel report with 3 sheets
    try:
        with pd.ExcelWriter(output / 'test_report.xlsx', engine='openpyxl') as xls:
            df.to_excel(xls, index=False, sheet_name='Execution')
            summary.to_excel(xls, index=False, sheet_name='Traceability')
            totals.to_excel(xls, index=False, sheet_name='Summary')
    except Exception as exc:
        print(f"Note: Could not export Excel file (.xlsx): {exc}")
    # 3. Export HTML dashboard
    rows = ''.join(
        '<tr>' + ''.join(
            f'<td>{html.escape(str(row.get(key, "")))}</td>'
            for key in ['test_case_id', 'requirement_id', 'condition_id', 'scenario_id', 'expected_json', 'actual_result', 'execution_status']
        ) + '</tr>'
        for row in results
    )
    page = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>STLab02 Test Report</title>
<style>
body{{font:15px Arial;margin:30px;color:#1e293b;background:#f8fafc}}
h1{{color:#0f172a}}
.metric-box{{display:flex;gap:15px;margin-bottom:20px}}
.metric{{background:white;padding:15px 25px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,0.1);font-size:18px}}
.pass{{color:#16a34a;font-weight:bold}}
.fail{{color:#dc2626;font-weight:bold}}
table{{border-collapse:collapse;width:100%;background:white;box-shadow:0 1px 3px rgba(0,0,0,0.1);border-radius:8px;overflow:hidden}}
td,th{{border:1px solid #e2e8f0;padding:10px 12px;text-align:left;font-size:14px}}
th{{background:#1e293b;color:white}}
tr:nth-child(even){{background:#f1f5f9}}
</style></head><body>
<h1>STLab02 – EduCommerce Automated Test Execution</h1>
<div class="metric-box">
  <div class="metric">Total: <b>{len(df)}</b></div>
  <div class="metric pass">PASS: <b>{counts["PASS"]}</b></div>
  <div class="metric fail">FAIL: <b>{counts.get("FAIL", 0)}</b></div>
  <div class="metric">Pass Rate: <b>{totals["pass_rate"].iloc[0]}%</b></div>
</div>
<h2>Traceability & Execution Details</h2>
<table>
  <tr><th>Test Case ID</th><th>Requirement</th><th>Condition</th><th>Scenario</th><th>Expected JSON</th><th>Actual Result</th><th>Status</th></tr>
  {rows}
</table>
</body></html>'''
    (output / 'test_dashboard.html').write_text(page, encoding='utf-8')
    print(f"Executed: {len(df)} | PASS: {counts['PASS']} | FAIL: {counts.get('FAIL', 0)} | Pass Rate: {totals['pass_rate'].iloc[0]}%")
    if counts.get('FAIL', 0) > 0:
        print("\n--- Failed Cases ---")
        print(df.loc[df['execution_status'] == 'FAIL', ['test_case_id', 'expected_json', 'actual_result']].to_string(index=False))
    return df, output


if __name__ == '__main__':
    run_suite()
