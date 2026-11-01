# STLab02 — Requirement-Based Automated Test Execution

[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Test Suite Status](https://img.shields.io/badge/tests-18%20PASS%20%7C%201%20FAIL-success)](reports/test_dashboard.html)
[![Requirements Coverage](https://img.shields.io/badge/coverage-100%25%20(5%2F5%20REQs)-brightgreen)](reports/test_report.xlsx)
[![Defect Found](https://img.shields.io/badge/defect-DEF--PAY--01%20(Critical)-critical)](reports/test_execution.csv)

Dự án thực hành kiểm thử tự động hướng yêu cầu (Requirement-Based Automated Testing) cho hệ thống thương mại điện tử **EduCommerce Checkout** trong khuôn khổ môn học **Kiểm thử Phần mềm (Software Testing - STLab02)**.  

---

## 1. Thông tin Sinh viên & Dự án
* **Sinh viên thực hiện:** Lê Thị Ngọc Anh
* **Mã số sinh viên (MSSV):** 23110131
* **Hệ thống kiểm thử (SUT):** EduCommerce In-Memory Checkout Engine (`ecommerce_app.py`)
* **Báo cáo PDF chính thức:** `23110131_LeThiNgocAnh_STLab02.pdf`

---

## 2. Danh sách 5 Requirements mới được Chọn
Dự án lựa chọn 5 Requirements hoàn toàn mới, độc lập, không trùng lặp với các Requirement đã làm mẫu trong hướng dẫn (REQ-06, REQ-08, REQ-11):

| Req ID | Module nghiệp vụ | Tóm tắt Quy tắc Nghiệp vụ (Business Rules) | Số Test Cases |
| :---: | :--- | :--- | :---: |
| **REQ-02** | **Cart Management** | Số lượng thêm vào giỏ phải là số nguyên dương ($qty > 0$); cộng dồn khi thêm trùng SKU; ném lỗi `INVALID_QUANTITY` nếu $qty \le 0$. | 4 |
| **REQ-04** | **Authentication** | Chỉ khách hàng đã đăng nhập (`authenticated=True`) mới được checkout. Khách chưa đăng nhập bị chặn với lỗi `LOGIN_REQUIRED` và không phát sinh đơn hàng. | 3 |
| **REQ-07** | **Promotion / Voucher** | Voucher sai ném `INVALID_VOUCHER`; voucher đã dùng ném `VOUCHER_USED`. Chỉ đánh dấu voucher vào `used_codes` khi đơn hàng thành công; rollback nếu thanh toán thất bại. | 4 |
| **REQ-09** | **Shipping Calculation** | Nội thành (`inner`): Miễn phí nếu Subtotal $\ge 500.000$đ; dưới $500$k phí $30.000$đ. Ngoại thành (`outer`): Cố định $50.000$đ. Khu vực lạ ném `INVALID_AREA`. | 5 |
| **REQ-10** | **Payment Processing** | COD tạo đơn trạng thái `PENDING_COD`. ONLINE approved tạo đơn `PAID` & lưu giao dịch. ONLINE declined ném lỗi `PAYMENT_DECLINED`, không tạo đơn và hoàn tồn kho. | 3 |
| **TỔNG** | **5 Requirements** | **12 Test Conditions $\rightarrow$ 12 Test Scenarios** | **19 Cases** |

---

## 3. Cấu trúc Thư mục Dự án (Project Directory Structure)

```text
Lab02/
├── 📁 images/                            # Ảnh chụp minh chứng thực thi (Screenshots E01 -> E10)
│   ├── E01.jpg                
│   ├── E02.jpg                
│   ├── E03.jpg                        
│   ├── E04.jpg                          
│   ├── E05_01.jpg
│   ├── E05_02.jpg 
│   ├── E06.jpg                          
│   ├── E07.jpg                         
│   ├── E08.jpg                        
│   ├── E09.jpg                        
│   └── E10.jpg                        
├── 📁 reports/                        
│   ├── test_dashboard.html              
│   ├── test_execution.csv             
│   └── test_report.xlsx                 
├── 📄 ecommerce_app.py                 
├── 📄 test_runner.py                   
├── 📄 STLab02_TestCases.csv             
├── 📄 STLab02_EduCommerce.ipynb        
├── 📄 23110131_LeThiNgocAnh_STLab02.pdf   # Báo cáo PDF chính thức nộp bài
└── 📄 README.md                           # Hướng dẫn cài đặt, thực thi & phân tích lỗi
```

---

## 4. Hướng dẫn Cài đặt & Thực thi từ Môi trường Sạch

### 4.1. Yêu cầu hệ thống
* Python 3.9 trở lên
* Git 

### 4.2. Cài đặt thư viện phụ thuộc
Mở Terminal / PowerShell tại thư mục dự án và chạy:
```bash
pip install pandas openpyxl matplotlib gradio
```

### 4.3. Thực thi bộ kiểm thử tự động (Command Line)
Chạy trực tiếp module Test Runner:
```bash
python test_runner.py
# hoặc trên Windows:
py test_runner.py
```

### 4.4. Chạy trên Jupyter Notebook / Google Colab
Mở file `STLab02_EduCommerce.ipynb` và bấm **Run All** để:
1. Sinh file dữ liệu kiểm thử `STLab02_TestCases.csv`.
2. Thực thi toàn bộ test suite và in bảng truy vết.
3. Khởi chạy giao diện tương tác **Gradio Dashboard** tại cổng `http://127.0.0.1:7866`.

---

## 5. Kết quả Thực thi Kiểm thử Tự động (Execution Results)

Khi chạy `test_runner.py`, kết quả hiển thị trên Terminal:

```text
========================================================================
            STLab02 - EDUCOMMERCE AUTOMATED TEST EXECUTION
========================================================================
  Executed: 19  |  PASS: 18  |  FAIL: 1  |  Pass Rate: 94.7%
------------------------------------------------------------------------
  [FAILED TEST CASES / DEFECTS DETECTED]:
  * Case ID     : TC-PAY-003
    Traceability: REQ-10 -> COND-PAY-03 -> TS-PAY-ONLINE-FAIL
    Expected    : {"error": "PAYMENT_DECLINED", "orders_count": 0, "stock_restored": true}
    Actual      : {"error": "PAYMENT_DECLINED", "orders_count": 0, "voucher_in_used_codes": false, "stock_restored": false}
    Defect ID   : DEF-PAY-01 (Missing inventory rollback on declined payment)
  --------------------------------------------------------------------
  Reports output directory: G:\Download\testSoftware\Lab02\reports
========================================================================
```

### Bảng Thống kê Traceability Matrix theo Requirement:

| Requirement ID | Số Cases | PASS | FAIL | BLOCKED | Pass Rate (%) | Đánh giá Trạng thái |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **REQ-02** (Cart) | 4 | 4 | 0 | 0 | 100.0% | Đạt yêu cầu thêm và cộng dồn SKU |
| **REQ-04** (Auth) | 3 | 3 | 0 | 0 | 100.0% | Chặn hoàn toàn khách chưa đăng nhập |
| **REQ-07** (Promotion) | 4 | 4 | 0 | 0 | 100.0% | Quản lý voucher & rollback used_codes chính xác |
| **REQ-09** (Shipping) | 5 | 5 | 0 | 0 | 100.0% | Đạt chuẩn 3 điểm biên $500$k ($499.999$đ, $500$k, $600$k) |
| **REQ-10** (Payment) | 3 | 2 | 1 | 0 | 66.7% | **Bắt chính xác 01 Defect Critical DEF-PAY-01** |
| **TỔNG CỘNG** | **19** | **18** | **1** | **0** | **94.7%** | **Đạt chỉ tiêu: Bắt lỗi thật & phân tích nguyên nhân gốc rễ** |

---

## 6. Báo cáo Lỗi Chi tiết (Defect Report — DEF-PAY-01)

Quá trình kiểm thử tự động đã phát hiện **01 Defect mức độ Critical** trong mã nguồn ứng dụng `ecommerce_app.py`:

| Thuộc tính | Nội dung chi tiết |
| :--- | :--- |
| **Defect ID** | `DEF-PAY-01` (Severity: **Critical** \| Priority: **P0**) |
| **Ca kiểm thử phát hiện** | `TC-PAY-003` (`REQ-10` $\rightarrow$ `COND-PAY-03` $\rightarrow$ `TS-PAY-ONLINE-FAIL`) |
| **Vị trí trong mã nguồn** | File `ecommerce_app.py`, Class `Checkout`, hàm `place()` (Dòng 94–97) |
| **Hành vi lỗi** | Cổng Online bị từ chối (`PAYMENT_DECLINED`), nhưng hàm `place()` **không hoàn trả hàng tồn kho** |
| **Hậu quả nghiệp vụ** | Đơn hàng không tạo (`orders_count = 0`), nhưng tồn kho bị mất vĩnh viễn (Ví dụ SKU A giảm 20 $\rightarrow$ 17) |

### So sánh Mã nguồn Trước & Sau khi sửa:

```python
# ❌ TRƯỚC (Code hiện tại trong ecommerce_app.py - Rò rỉ tồn kho):
self.inventory.reserve(cart.lines)                           # Trừ kho thành công
if method == "ONLINE":
    self.payments.collect(customer, total, approved=approved) # Ném lỗi PAYMENT_DECLINED -> Bị ngắt, không hoàn kho!

#  SAU (Giải pháp khắc phục - Transaction Rollback):
self.inventory.reserve(cart.lines)                           # Trừ kho
if method == "ONLINE":
    try:
        self.payments.collect(customer, total, approved=approved)
    except Exception as e:
        self.inventory.release(cart.lines)                   # Tự động hoàn tác tồn kho khi thanh toán thất bại
        raise e
```

---

## 7. Danh mục Bằng chứng Thực thi (Test Execution Evidences E01 – E10)

Báo cáo chính thức kèm đầy đủ 10 bằng chứng thực nghiệm trong thư mục `images/`:
* **`E01` - Project Directory Structure:** Cây thư mục dự án chuẩn hóa, phân tách mã nguồn và báo cáo.
* **`E02` - Traceability Matrix:** Ma trận truy vết xuyên suốt $REQ \rightarrow COND \rightarrow TS \rightarrow TC \rightarrow RUN$.
* **`E03` - Fixture Code:** Đoạn mã hàm `fixture()` cô lập dữ liệu cho 5 requirements (`clean_cart`, `unauth_user`, `used_voucher`, `499999`).
* **`E04` - CSV Reader & Integrity Check:** Đoạn mã đọc file CSV và thuật toán kiểm tra chống trùng lặp Test Case ID.
* **`E05` - Test Dispatcher:** Khối lệnh điều phối tự động phân luồng kiểm thử theo `requirement_id`.
* **`E06` - Exception Handling & Assertions:** Đoạn mã khối `try...except` xác thực ngoại lệ và kiểm tra side-effects.
* **`E07` - Terminal Execution Log:** Ảnh chụp màn hình console hiển thị kết quả 18 PASS / 1 FAIL (94.7%).
* **`E08` - Gradio Interactive Dashboard:** Giao diện trực quan hóa kết quả kiểm thử trên trình duyệt web.
* **`E09` - Execution Summary & Risk Analysis:** Báo cáo HTML và phân tích 2 rủi ro kỹ thuật (Concurrency & Financial Rounding).
* **`E10` - Public GitHub Repository & README:** Minh chứng repository mã nguồn mở hoàn chỉnh và tài liệu hướng dẫn.

