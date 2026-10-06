# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

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

Dựa trên kết quả chạy 3 tác vụ học ở điều kiện `baseline`, tổng hợp phân loại các check thất bại:

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|:---:|---|
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

- **Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):**
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

- **Số lần chạy curator, số skill bị xóa và lý do:** Chạy curator 1 lần (`python -m lab.curator`), sinh thành công 3/3 skill hợp lệ qua bộ lọc `validate_skill`. Không có skill nào bị xóa vì cả 3 skill đều ngắn gọn, đúng định dạng và không bị rò rỉ dữ liệu đánh giá.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `organizational-conventions-check` | **Tổng quát**: Nêu quy chuẩn áp dụng chung cho coding (type annotations, `CHANGELOG.md`, `test_regressions.py`, cấu trúc `meta`, tiền tệ cent). Không chứa tên bài toán hay con số cụ thể. | **Đúng**: Khớp chính xác với các quy ước bắt buộc của bot đánh giá Acme được trích xuất từ phản hồi `detail`. | Độ dài 12 dòng. `description`: *"Use when ensuring compliance with organizational coding and documentation standards."* (rõ ràng). `skills_read`: 0. |
| `csv-formatting-guidelines` | **Tổng quát**: Hướng dẫn chuẩn hóa dữ liệu bảng và file CSV (chuẩn hóa tên vùng, UTC timestamp, loại bỏ dòng trùng lặp, chuẩn RFC 4180 về escape dấu ngoặc kép). | **Đúng**: Đúng chuẩn RFC 4180 và giải quyết chính xác lỗi bỏ sót escape dấu nháy kép trong docstring. | Độ dài 12 dòng. `description`: *"Use when creating or modifying CSV files to meet organizational standards."*. `skills_read`: 0. |
| `error-logging-standards` | **Tổng quát**: Hướng dẫn chuẩn hóa tệp đầu ra của tác vụ xử lý log (cấu trúc `schema_version: 2`, `generated_by: log-triage`, sắp xếp tăng dần theo service và timestamp, tên service gạch dưới). | **Đúng**: Đúng 100% các quy ước của bot kiểm tra log Acme. | Độ dài 12 dòng. `description`: *"Use when processing and logging error data to ensure compliance with organizational standards."*. `skills_read`: 0. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
