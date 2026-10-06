# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin sinh viên và cấu hình thực nghiệm

| Họ tên sinh viên | Mã sinh viên | Tỷ lệ đóng góp |
|---|---|---|
| Phùng Quốc Việt | 2A202602456 | 100% (cá nhân) |

- Mô hình: `gpt-4o-mini`, nhiệt độ: `0.0`, `recursion_limit`: `60`
- Phiên bản Deep Agents: `0.7.21`, hệ điều hành: `Windows 11`, chạy trực tiếp với `WindowsShellBackend` (tích hợp môi trường POSIX Git Bash)
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / 30 lượt chạy (18 lượt chính thức + 3 lượt dev)
- Commit của tag `freeze`: `13b7ad4bb4357490cae9956145d63c93201c4757`

## 2. Giả thuyết nghiên cứu (commit trước tag `freeze`)

- H1 (subagents so với baseline): Điều kiện `subagents` dự kiến không cải thiện đáng kể điểm số so với `baseline` trên tác vụ eval (điểm tương đương hoặc chênh lệch không quá 1 điểm), trong khi chi phí token tăng cao hơn (~10-20%). Căn cứ: Ở các bài toán kỹ thuật đơn lẻ, tác tử thường tự giải quyết mà không phân rã qua công cụ `task` (`subagent_calls = 0`), và việc chia nhỏ tác tử không thể tự khắc phục các lỗi thiếu thông tin quy ước nội bộ (Nhóm E).
- H2 (skills-auto so với baseline): Điều kiện `skills-auto` dự kiến cải thiện điểm số mạnh trên tác vụ học (đặc biệt là các check quy ước nhóm E đã được đúc kết), nhưng trên tác vụ đánh giá (`eval`), mức độ cải thiện sẽ khiêm tốn hơn nhiều và chỉ phát huy tác dụng ở các quy ước dùng chung; nó không thể vượt qua các quy ước mới chưa từng xuất hiện trong tập học (phù hợp với hiện tượng context-level overfitting / generalization gap trong SkillsBench và SkillEvolBench).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ học (`learn`) sẽ cao hơn đáng kể so với tác vụ đánh giá (`eval`) trên cả ba điều kiện, đặc biệt ở `skills-auto`. Căn cứ: Tác vụ đánh giá chứa các trường hợp biên mới và các quy ước ẩn mới (chưa có trong vết chạy để curator học), tạo ra khoảng cách tổng quát hóa tự nhiên.

## 3. Làm quen Deep Agents (Phần 0.3)

1. **Các công cụ của tác tử mặc định:** Bao gồm 7 công cụ tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), 1 công cụ shell (`execute`) và 1 công cụ gọi subagent (`task`). Công cụ cho phép chạy lệnh hệ thống là `execute`.
2. **Subagent `general-purpose`:** Là tác tử đa năng dùng để nghiên cứu câu hỏi phức tạp, tìm kiếm file/nội dung và thực thi các tác vụ nhiều bước; nó có quyền truy cập đầy đủ tất cả công cụ như tác tử chính. Về ngữ cảnh: subagent hoạt động phi trạng thái (stateless) theo mặc định, nó **chỉ nhìn thấy nội dung prompt** mà tác tử chính gửi sang, không nhìn thấy lịch sử cuộc hội thoại trước đó của tác tử chính và chỉ trả về một báo cáo cuối duy nhất.
3. **Trích dẫn hướng dẫn hành vi:**
   - Từ mô tả công cụ `task`: *"Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead."*
   - Từ mô tả công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Dựa trên kết quả chạy thực nghiệm 3 tác vụ học ở điều kiện `baseline`, tôi tổng hợp phân loại các check thất bại như sau:

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
| --- | --- | :---: | --- |
| `data-learn` | `rule_money_in_cents` | E | `RULE: money values in answer.json are integer cents (1606.67 USD is written 160667).` |
| `data-learn` | `rule_meta_block` | E | `RULE: answer.json has an object meta = {"source": <input file name>, "rows_in": ..., "rows_used": ...}` |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv containing the cleaned rows, with no duplicate rows and no missing amount rows.` |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| `code-learn` | `parse_price_all_formats` | D | `wrong for: ['$1,299.50', '$1,000,000.00']` (tác tử không xử lý trường hợp dấu phẩy ngăn cách hàng nghìn). |
| `code-learn` | `csv_quoting_follows_docstring` | A | `to_csv_row returned 'Desk, large "oak",10.00,2'` (bỏ qua mô tả trong docstring yêu cầu escape dấu ngoặc kép theo chuẩn CSV). |
| `logs-learn` | `rule_service_names` | E | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |
| `logs-learn` | `timestamps_utc` | D | `4/25 timestamps match` (bỏ sót việc chuyển đổi đồng nhất các múi giờ ISO/RFC sang chuẩn UTC). |

**Nhận xét:**

- **Nhóm lỗi chiếm đa số:** Nhóm **E (Vi phạm quy ước tổ chức Acme)** chiếm tuyệt đối 9/9 check quy ước thất bại (tỷ lệ 100% theo thống kê `scripts/check_breakdown.py`). Nguyên nhân gốc rễ là các quy ước nội bộ này hoàn toàn không có trong đề bài (`instruction.md`) mà chỉ có trong quy chuẩn ngầm của tổ chức chấm điểm (`check.py`).
- **Khả năng phòng ngừa của Skill:** Một `SKILL.md` được sinh từ Curator hoàn toàn có thể phòng ngừa hiệu quả 100% nhóm lỗi E bằng cách tóm tắt rõ ràng các quy ước Acme bắt buộc (cấu trúc `meta`, `clean.csv`, `test_regressions.py`, `CHANGELOG.md`, `schema_version`) thành danh sách kiểm tra checklist trước khi hoàn thành tác vụ.
- **Bằng chứng phủ định cho các nhóm A-D:** Đối với các check kỹ thuật cơ bản (như logic giảm giá `discount_rounds_half_up`, cảnh báo tồn kho `low_stock_follows_docstring`, cấu trúc log hợp lệ `valid_structure`), mô hình `gpt-4o-mini` đều xử lý đạt được mà không mắc lỗi nghiêm trọng.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent do tôi định nghĩa và tích hợp (tên, vai trò, lý do thiết kế):**
  1. `explorer`: Chuyên đọc tài liệu, kiểm tra cấu trúc workspace, schema và log mà không chỉnh sửa file.
  2. `implementer`: Chuyên chỉnh sửa code, dữ liệu và thực thi các script/lệnh shell.
  3. `reviewer`: Độc lập kiểm tra, chạy lại test suite và đối chiếu kết quả đầu ra với yêu cầu đề bài.
- **`subagent_calls` ở từng tác vụ và nhận xét:**
  - `code-learn`: 0 lần gọi.
  - `data-learn`: 0 lần gọi.
  - `logs-learn`: 0 lần gọi.
  - **Nhận xét:** Việc `subagent_calls = 0` trên cả 3 tác vụ là hoàn toàn bình thường và hợp lý. Do tác tử chính bản thân đã có đầy đủ toàn bộ công cụ thực thi (`read_file`, `write_file`, `execute`), mô hình LLM khi lập kế hoạch nhận thấy các tác vụ chỉ gồm 1 workspace nhỏ nên tự giải quyết trực tiếp để tối ưu số bước thay vì mất thêm chi phí khởi tạo phiên subagent mới.
- **Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):** Do tác tử chính không thực hiện ủy quyền nên không phát sinh truyền tải thông tin giữa các agent.
- **Ảnh hưởng đến token và thời gian:**
  - Token trung bình: `baseline` tiêu tốn **22,550 tokens**, trong khi `subagents` tiêu tốn **27,559 tokens** (tăng ~22.2%).
  - Nguyên nhân tăng token dù không gọi subagent: System prompt của chế độ `subagents` dài hơn (do có thêm mô tả chi tiết của 3 subagents trong công cụ `task` và chỉ dẫn `SUBAGENTS_NOTE`), dẫn đến chi phí input tokens tăng lên ở mỗi vòng lặp tương tác.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator, số skill bị xóa và lý do:** Tôi đã chạy curator 1 lần (`python -m lab.curator`), sinh thành công 3/3 skill hợp lệ qua bộ lọc `validate_skill`. Không có skill nào bị xóa vì cả 3 skill đều ngắn gọn, đúng định dạng và không bị rò rỉ dữ liệu đánh giá.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
| --- | --- | --- | --- |
| `organizational-conventions-check` | **Tổng quát**: Nêu quy chuẩn áp dụng chung cho coding (type annotations, `CHANGELOG.md`, `test_regressions.py`, cấu trúc `meta`, tiền tệ cent). Không chứa tên bài toán hay con số cụ thể. | **Đúng**: Khớp chính xác với các quy ước bắt buộc của bot đánh giá Acme được trích xuất từ phản hồi `detail`. | Độ dài 12 dòng. `description`: *"Use when ensuring compliance with organizational coding and documentation standards."* (rõ ràng). `skills_read`: 0. |
| `csv-formatting-guidelines` | **Tổng quát**: Hướng dẫn chuẩn hóa dữ liệu bảng và file CSV (chuẩn hóa tên vùng, UTC timestamp, loại bỏ dòng trùng lặp, chuẩn RFC 4180 về escape dấu ngoặc kép). | **Đúng**: Đúng chuẩn RFC 4180 và giải quyết chính xác lỗi bỏ sót escape dấu nháy kép trong docstring. | Độ dài 12 dòng. `description`: *"Use when creating or modifying CSV files to meet organizational standards."*. `skills_read`: 0. |
| `error-logging-standards` | **Tổng quát**: Hướng dẫn chuẩn hóa tệp đầu ra của tác vụ xử lý log (cấu trúc `schema_version: 2`, `generated_by: log-triage`, sắp xếp tăng dần theo service và timestamp, tên service gạch dưới). | **Đúng**: Đúng 100% các quy ước của bot kiểm tra log Acme. | Độ dài 12 dòng. `description`: *"Use when processing and logging error data to ensure compliance with organizational standards."*. `skills_read`: 0. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng tổng hợp đối đầu giữa 3 điều kiện thực nghiệm (từ `report/table.md`):

| Task | baseline | subagents | skills-auto |
| --- | --- | --- | --- |
| code-learn | 2/10 | 1/10 | 4/10 |
| data-learn | 0/8 | 2/8 | 0/8 |
| logs-learn | 1/9 | 0/9 | 1/9 |
| code-eval | 1/11 | 0/11 | 3/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 1/10 | 1/10 | 1/10 |
| **Mean score - learning tasks** | 0.10 | 0.12 | 0.17 |
| **Mean score - evaluation tasks** | 0.06 | 0.03 | 0.12 |
| **Mean tokens per run** | 67,135 | 746,027 | 175,130 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

Thống kê phân tách theo check kỹ thuật và check quy ước (từ `scripts/check_breakdown.py`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      2/18         0/12         111,720      0/3     
baseline      learn     3/18         0/9           22,550      0/3     
subagents     eval      1/18         0/12       1,464,495      0/3     
subagents     learn     3/18         0/9           27,559      0/3     
skills-auto   eval      4/18         0/12         199,695      0/3     
skills-auto   learn     5/18         0/9          150,566      0/3     
```

- **Các lần chạy có `error` và cách xử lý:**
  - `GraphRecursionError`: Xuất hiện ở một số lần chạy (`baseline code-eval`, `subagents code-eval`, `skills-auto code-eval`, `skills-auto data-learn`, `skills-auto data-eval`) khi tác tử chạm ngưỡng `recursion_limit = 60` do thử nghiệm code nhiều lần không hội tụ. Nhờ cơ chế `stream_mode="values"` trong `runner.py`, toàn bộ vết thực thi `trace.md` và artifact sinh ra trước thời điểm đạt giới hạn đều được bảo tồn nguyên vẹn để chấm điểm chính xác.
  - `OpenAIRateLimitError` (HTTP 429 TPM): Xảy ra ở `subagents data-eval` do subagent bị lặp ngữ cảnh lớn đẩy lượng token lên tới 4,138,662 tokens, làm cạn ngân sách 200,000 TPM của tài khoản. Lần chạy này được ghi nhận đúng thực tế lỗi, và sau 1 phút hạ nhiệt, tác vụ kế tiếp (`subagents logs-eval`) được chạy độc lập và hoàn tất đạt 1/10 điểm.
  - **Kiểm tra sửa đổi kỹ năng:** `skills_modified = false` ở 100% tất cả 18 lượt chạy, đảm bảo tính toàn vẹn tuyệt đối của giao thức đóng băng.

## 8. Phân tích

1. **So sánh cải thiện giữa tác vụ học và tác vụ đánh giá:**
   - So với `baseline` (học: 0.10, eval: 0.06), điều kiện `skills-auto` cải thiện điểm số mạnh nhất trên cả hai tập: đạt **0.17** trên tập học (+70%) và **0.12** trên tập đánh giá (+100%).
   - Điều kiện `subagents` có cải thiện nhẹ trên tập học (0.12 so với 0.10) nhưng lại bị **giảm điểm** trên tập đánh giá (0.03 so với 0.06 của baseline).
   - Hiện tượng: Điểm đánh giá ở mọi điều kiện đều thấp hơn tập học. Riêng ở `subagents`, việc tăng điểm ở tập học nhưng suy giảm rõ rệt ở tập eval là dấu hiệu của sự mất ổn định hệ thống đa tác tử (multi-agent instability): khi gặp dữ liệu đánh giá phức tạp hơn, sự phối hợp giữa tác tử chính và subagent bị quá tải ngữ cảnh (context overhead) và dễ rơi vào vòng lặp cạn kiệt ngân sách.

2. **Phân tách check kỹ thuật và check quy ước (`rule_`):**
   - Tỷ lệ check quy ước Acme (`house rules`): Cả 3 điều kiện đều đạt **0/9** ở tập học và **0/12** ở tập đánh giá.
   - Nguyên nhân: Các tác tử LLM chưa chủ động thực hiện hành vi đọc nội dung file kỹ năng (`skills_read = 0/6`). Vì không đọc phần thân (body) của `SKILL.md`, tác tử không tiếp cận được các chỉ dẫn chi tiết về cấu trúc `meta block`, định dạng `integer cents` hay quy ước `CHANGELOG.md`.
   - Tuy nhiên, sự xuất hiện của danh sách tên và mô tả skill trong system prompt đã tạo ra hiệu ứng mồi ngữ cảnh (context priming), giúp `skills-auto` nâng tỷ lệ giải quyết các check kỹ thuật (`technical checks`) lên **5/18** ở tập học và **4/18** ở tập eval (vượt trội so với 3/18 và 2/18 của `baseline`).
   - Các check quy ước mới của tập đánh giá hoàn toàn không được giải quyết (0/12), vì (1) tác tử không đọc skill, và (2) curator được thiết kế tuân thủ nghiêm ngặt nguyên tắc chống rò rỉ dữ liệu (chỉ học từ `role == "learn"`), do đó không thể biết trước quy ước mới của tập eval.

3. **Phân tích cơ chế từ vết (`trace.md`) và `skills_read`:**
   - **Check được cải thiện thành công:** Trong `skills-auto/code-eval` (đạt 3/11 điểm), tác tử giải quyết thành công các hàm logic cốt lõi như `parse_price` và `apply_discount` trong `inventory.pricing`. Vết thực thi cho thấy sau khi chạy `pytest` và thấy lỗi, tác tử đã đọc kỹ docstring và sửa đổi hàm tương thích với các ca kiểm thử phức tạp thay vì chỉ sửa qua loa như ở `baseline`.
   - **Check không được cải thiện:** `rule_money_in_cents` trong `data-learn` và `data-eval`. Mặc dù curator đã tự động tạo skill `csv-formatting-guidelines` với hướng dẫn rất cụ thể: *"Ensure all monetary amounts are represented in integer cents (e.g., $1,606.67 should be 160667)"*, nhưng tác tử chỉ đọc mô tả ở system prompt mà không dùng công cụ `read_file` để mở file skill (`skills_read = 0`). Do đó, tác tử vẫn xuất số tiền dạng số thực (float) và bị bot kiểm tra đánh trượt.

4. **Phân tích chi phí và hiệu quả của Đa tác tử (Subagents):**
   - Chi phí token trung bình / lần chạy:
     - `baseline`: **67,135 tokens** (chi phí thấp nhất, hiệu quả cơ sở).
     - `skills-auto`: **175,130 tokens** (gấp ~2.6 lần baseline, mang lại điểm số cao nhất).
     - `subagents`: **746,027 tokens** (gấp ~11.1 lần baseline!). Riêng lần chạy `data-eval` đã bùng nổ lên 4,138,662 tokens do subagent lặp truyền dữ liệu lớn.
   - **Đánh giá hiệu quả:** Trong thí nghiệm này, kiến trúc đa tác tử **hoàn toàn không đáng chi phí**. Với chi phí token gấp 11 lần nhưng điểm số ở tập đánh giá lại giảm xuống một nửa so với baseline (0.03 vs 0.06), kiến trúc subagent bộc lộ nhược điểm nghiêm trọng về kiểm soát ngữ cảnh và chi phí trên các tác vụ kỹ thuật quy mô vừa.

5. **Hiện tượng rò rỉ dữ liệu (Data Leakage) và quá khớp (Overfitting):**
   - **Rò rỉ dữ liệu:** Hoàn toàn không xảy ra. Hàm `curate_skills()` lọc cứng điều kiện `if record.get("role") != "learn": continue`, ngăn chặn tuyệt đối việc curator đọc kết quả của các bài eval. Điều này đã được chứng minh qua unit test `tests/test_04_curator.py` và script `verify_freeze.py` đạt chuẩn OK.
   - **Quá khớp (Overfitting):** Nhờ cơ chế prompt yêu cầu quy tắc chung, các skill được tạo ra đều có tính khái quát cao (`organizational-conventions-check`, `csv-formatting-guidelines`, `error-logging-standards`), không chứa các định danh cụ thể của bài toán học. Tuy nhiên, sự phụ thuộc vào các quy ước cũ khiến skill không thể hỗ trợ các quy ước hoàn toàn mới trên tập đánh giá.

6. **Ước lượng độ nhiễu thực nghiệm (Noise Estimation):**
   - So sánh điểm tập học của cùng một bộ kỹ năng `skills-auto`:
     - Lần chạy thử nghiệm (dev run trong `results/skills-auto-dev`): điểm trung bình **0.00** (code-learn: 0.0, data-learn: 0.0, logs-learn: 0.0).
     - Lần chạy chính thức (official run sau freeze): điểm trung bình **0.17** (code-learn: 0.4, data-learn: 0.0, logs-learn: 0.11).
   - Độ chênh lệch điểm (biên độ nhiễu): **0.17 điểm**.
   - **Ý nghĩa khoa học:** Độ ngẫu nhiên của mô hình ngôn ngữ lớn (stochasticity) trong việc lập kế hoạch công cụ tạo ra phương sai đáng kể giữa các lần chạy lặp lại. Sự chênh lệch 0.17 điểm này cho thấy các khác biệt nhỏ giữa các điều kiện (dưới 0.10) có thể rơi vào vùng nhiễu thống kê; do đó để khẳng định chắc chắn tính ưu việt của một phương pháp, cần thực hiện nhiều lần chạy lặp lại (multi-trial) với các hạt ngẫu nhiên (random seeds) khác nhau.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập tác vụ nhỏ (Sample Size Limitation):** Thí nghiệm chỉ kiểm thử trên 6 tác vụ (3 tác vụ học, 3 tác vụ đánh giá), khiến phương sai thống kê còn lớn và kết quả dễ bị ảnh hưởng bởi độ khó đặc thù của từng đề bài cụ thể.
2. **Mỗi cấu hình chỉ chạy một lần (Single-run Variance):** Do hạn chế về ngân sách token và hạn mức tốc độ (TPM) của API, mỗi tác vụ chỉ được thực thi một lần duy nhất. Với biên độ nhiễu quan sát được lên tới 0.17, việc thiếu các lần chạy lặp lại làm giảm mức độ tin cậy của các suy diễn so sánh biên.
3. **Mô hình thử nghiệm đơn lẻ (Model Specificity):** Toàn bộ nghiên cứu chỉ thực hiện trên mô hình `gpt-4o-mini`. Các đặc tính như sự ngập ngừng không chủ động đọc file kỹ năng (`skills_read = 0`) hoặc việc bùng nổ token khi ủy quyền subagent có thể là đặc thù riêng của mô hình cỡ nhỏ này, và kết quả có thể khác biệt lớn trên các mô hình lý luận mạnh hơn (như Claude 3.5 Sonnet, GPT-4o, hoặc DeepSeek-R1).

## 10. Kết luận

1. Cơ chế tác tử tự tiến hóa (`skills-auto`) đạt hiệu quả tổng thể cao nhất, nâng điểm trung bình trên tập học lên 0.17 và tập đánh giá lên 0.12.
2. Kiến trúc đa tác tử (`subagents`) kém hiệu quả rõ rệt trên các tác vụ kỹ thuật đơn lẻ, tiêu tốn lượng token gấp 11 lần (746K tokens/run) nhưng làm giảm điểm đánh giá xuống 0.03.
3. Tác tử chưa tự giác khai thác cơ chế nạp dần kỹ năng (`skills_read = 0/6`), chỉ tận dụng được phần mồi gợi ý từ system prompt.
4. Khoảng cách khái quát hóa (generalization gap) xuất hiện nhất quán ở mọi điều kiện khi điểm số tập đánh giá luôn thấp hơn tập học.
5. Đề xuất cải tiến tiếp theo là cài đặt cơ chế tiền kiểm soát hành vi (pre-execution hook) bắt buộc tác tử phải đọc nội dung `SKILL.md` trước khi cấp quyền truy cập vào công cụ thực thi shell.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự thực hiện):**
  1. `python -m venv .venv` và `.venv\Scripts\pip install -e .` (Khởi tạo môi trường ảo)
  2. `pytest tests/test_01_provided.py` (Kiểm thử chức năng có sẵn)
  3. Cài đặt harness: `pytest tests/test_02_agent.py` và `pytest tests/test_03_runner.py`
  4. Chạy CP2: `python -m lab.runner --condition baseline --tasks learn`, `python -m lab.runner --condition subagents --tasks learn`, `python scripts/check_breakdown.py`
  5. Cài đặt curator CP3: `pytest tests/test_04_curator.py`, `python -m lab.curator`, `python -m lab.runner --condition skills-auto --tasks learn`, sao lưu `results/skills-auto-dev`
  6. Giao thức đóng băng CP4: `git commit -m "hypotheses: ..."` -> `git tag freeze`
  7. Chạy đánh giá chính thức CP4:
     - `python -m lab.runner --condition baseline --tasks eval`
     - `python -m lab.runner --condition subagents --tasks eval`
     - `python -m lab.runner --condition skills-auto --tasks all`
     - `python scripts/verify_freeze.py` (Xác thực OK)
  8. Tổng hợp CP5: `python -m lab.compare > report/table.md`, `python scripts/check_breakdown.py`
- **Ghi chú kỹ thuật:**
  - Để khắc phục vấn đề `cmd.exe` trên Windows ngắt lệnh khi gặp ký tự `&` trong câu lệnh Python một dòng của agent, tôi đã cài đặt lớp `WindowsShellBackend` trong `src/lab/agent.py` để định tuyến lệnh thực thi qua Git Bash (`C:\Program Files\Git\bin\sh.exe`), mang lại tính tương thích POSIX chuẩn xác cho môi trường Windows.
