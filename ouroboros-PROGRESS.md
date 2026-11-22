# Ouroboros — Tiến độ

> Mở file này mỗi buổi học. Tick xong thì tick. Không tick khống.

**Tổng thể**

```
[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0 / 87 tuần  ·  0%
```

**Tuần hiện tại:** Tuần 0 — chưa bắt đầu
**Bắt đầu:** Thứ Hai 21/09/2026
**Dự kiến xong:** Tháng 5/2028

---

## Bản đồ 8 phase

| # | Phase | Tuần | Từ → Đến | Ngôn ngữ | Trạng thái |
|---|---|---|---|---|---|
| 0 | Biết cái máy của mình | 5 | 21/09/26 → 25/10/26 | C | ⬜ Chưa bắt đầu |
| 1 | Storage engine | 9 | 26/10/26 → 27/12/26 | C | ⬜ |
| 2 | Process & concurrency | 7 | 28/12/26 → 14/02/27 | C | ⬜ |
| — | *Đệm* (Tết, thi) | 2 | linh hoạt | | ⬜ |
| 3 | Mạng | 9 | 01/03/27 → 02/05/27 | C | ⬜ |
| 4 | Go | 6 | 03/05/27 → 13/06/27 | Go | ⬜ |
| — | *Đệm* (thi học kỳ) | 2 | linh hoạt | | ⬜ |
| 5 | Phân tán · Raft | 11 | 28/06/27 → 12/09/27 | Go | ⬜ |
| 6 | Container runtime | 11 | 13/09/27 → 28/11/27 | Go + C | ⬜ |
| — | *Đệm* | 2 | linh hoạt | | ⬜ |
| 7 | Orchestrator · khép vòng | 11 | 13/12/27 → 27/02/28 | Go | ⬜ |
| — | *Đệm* (Tết) | 2 | linh hoạt | | ⬜ |
| 8 | AI Infrastructure | 10 | 13/03/28 → 21/05/28 | Go + Python | ⬜ |

**8 tuần đệm đã tính sẵn.** Trượt tiến độ không phải thất bại — nó nằm trong kế hoạch.
Dời tuần đệm theo lịch thi và Tết thật của bạn.

Ký hiệu: ⬜ chưa · 🟨 đang làm · ✅ xong · ⏸️ tạm dừng

---

# Phase 0 — Biết cái máy của mình

`[░░░░░] 0/5 tuần`

**Mục tiêu:** học C thật sự qua CSAPP, và biết máy tính của mình nhanh chậm ở đâu, bằng số đo của chính mình.
**Môi trường:** WSL2 Ubuntu · gcc · gdb · make · valgrind

### Tuần 1 — Bit và byte (21/09 – 27/09)
- [ ] CSAPP Ch1 — đọc nhanh, coi như bản đồ, không sa đà
- [ ] CSAPP Ch2.1–2.3 — biểu diễn thông tin, integer
- [ ] Bài tập CSAPP 2.5 → 2.30
- [ ] Viết `hexdump.c` — tự viết, không xem bản có sẵn
- [ ] TLPI Ch1–3 — khái niệm nền
- [ ] Viết `util.c`: wrapper syscall có xử lý `errno` và retry `EINTR` đúng chuẩn
- [ ] `git init` repo `D:/Code/ouroboros`, push lên GitHub công khai

> `util.c` bạn viết tuần này sẽ theo bạn suốt 2 năm. Làm cẩn thận.

### Tuần 2 — Số thực và assembly (28/09 – 04/10)
- [ ] CSAPP Ch2.4 — floating point
- [ ] Viết chương trình in bit pattern của `float` và `double`
- [ ] CSAPP Ch3.1–3.7 — machine-level representation
- [ ] Đọc được `objdump -d` của hàm mình viết
- [ ] Bắt đầu **Bomb Lab** (CMU, miễn phí)

### Tuần 3 — Bomb Lab + cache (05/10 – 11/10)
- [ ] Hoàn thành Bomb Lab
- [ ] CSAPP Ch6 — memory hierarchy
- [ ] Viết `mountain.c` — đo memory mountain
- [ ] Vẽ biểu đồ kết quả, giải thích từng vùng trên đồ thị

### Tuần 4 — Tối ưu (12/10 – 18/10)
- [ ] CSAPP Ch5 — optimizing program performance
- [ ] Đo và giải thích: vì sao duyệt mảng 2D theo cột chậm hơn theo hàng ~6 lần
- [ ] Học dùng `perf stat`, đọc cache-miss counter
- [ ] Ghi kết quả vào `docs/bench/phase0.md`

### Tuần 5 — Allocator (19/10 – 25/10)
- [ ] CSAPP Ch9.9 — dynamic memory allocation
- [ ] OSTEP Ch17 — free-space management
- [ ] TLPI Ch7 — memory allocation
- [ ] Viết `myalloc`: implicit free list → explicit → segregated fit
- [ ] Pass CSAPP malloc lab, utilization > 70%
- [ ] Valgrind sạch

### ✅ Cổng ra Phase 0 — không qua thì không sang Phase 1
- [ ] `myalloc` pass test, utilization > 70%
- [ ] Giải thích được hiệu ứng cache **bằng số đo của chính mình**, không phải số trong sách
- [ ] Đọc `objdump -d` không hoảng
- [ ] Repo có ít nhất 25 commit
- [ ] **Viết blog #1:** "Tôi viết lại malloc và học được gì về bộ nhớ"

---

# Phase 1 — Storage engine

`[░░░░░░░░░] 0/9 tuần` · 26/10/2026 → 27/12/2026

**Mục tiêu:** `ouro-store` — engine lưu trữ không mất dữ liệu khi mất điện.

### Tuần 6–7 — File format & page layout
- [ ] DB Internals Ch1–3
- [ ] TLPI Ch4, Ch5, Ch13 (I/O buffering), Ch14 (file systems)
- [ ] CSAPP Ch10 (system-level I/O)
- [ ] Thiết kế page layout, ghi quyết định vào `docs/page-format.md`
- [ ] Cài `page.c` — slotted page, header, checksum
- [ ] Trả lời: page size bao nhiêu, vì sao?

### Tuần 8–10 — B-Tree
- [ ] DB Internals Ch2, Ch4, Ch6
- [ ] `btree.c` — insert, split
- [ ] `btree.c` — delete, merge, rebalance
- [ ] Test trên 10 triệu key, `store_scan` trả đúng thứ tự
- [ ] OSTEP Ch39–41 (files & directories, FS implementation, FFS)

### Tuần 11 — Buffer pool
- [ ] `bufpool.c` — page cache, pin/unpin, thay thế CLOCK
- [ ] **PostgreSQL 14 Internals Part II** — đối chiếu với hàng thật
- [ ] Nhiệm vụ phụ: page-replacement simulator FIFO/LRU/CLOCK, so số liệu (lấp OSTEP Ch21–22)
- [ ] Trả lời: `mmap` hay `pread`/`pwrite`? Ghi lý do.

### Tuần 12–13 — WAL & recovery
- [ ] DB Internals Ch5
- [ ] **PostgreSQL 14 Internals Part I (MVCC) + Part II (WAL)**
- [ ] OSTEP Ch42 (crash consistency & journaling) — chương quan trọng nhất phase này
- [ ] `wal.c` — append-only log, LSN, group commit
- [ ] `recovery.c` — redo, checkpoint, phát hiện torn page
- [ ] TLPI Ch55 (file locking), Ch49 (memory mappings)
- [ ] **Test tra tấn: 1000 lần `kill -9` ngẫu nhiên**

### Tuần 14 — LSM & đối đầu
- [ ] DB Internals Ch7 (log-structured storage)
- [ ] OSTEP Ch43 (LFS), Ch44 (SSD)
- [ ] `lsm.c` — memtable, SSTable, compaction
- [ ] Benchmark B-Tree vs LSM trên 3 workload, vẽ biểu đồ
- [ ] Nhiệm vụ phụ: build system + shared library (lấp CSAPP Ch7, TLPI Ch41–42)

### ✅ Cổng ra Phase 1
- [ ] 1000 lần `kill -9` → không mất dữ liệu đã ack
- [ ] Biểu đồ B-Tree vs LSM trên 3 workload
- [ ] Valgrind sạch, ThreadSanitizer sạch
- [ ] **Viết blog #2:** "Tôi viết một storage engine và nó sống sót qua 1000 lần kill -9"

---

# Phase 2 → 8

Chi tiết từng tuần sẽ được mở rộng **khi sắp tới phase đó**.
Lập kế hoạch chi tiết cho 18 tháng sau là viết tiểu thuyết — nó sẽ sai.

Giờ chỉ giữ cổng ra. Sách đã có sẵn trong `SACH.md`.

### Phase 2 — Process & concurrency · 7 tuần
- [ ] `ouro-store` chạy được dạng daemon, đa luồng
- [ ] Graceful shutdown khi nhận `SIGTERM`
- [ ] Thread pool hoạt động, ThreadSanitizer sạch
- [ ] Nhiệm vụ phụ: viết một shell có job control
- [ ] **Blog #3**

### Phase 3 — Mạng · 9 tuần
- [ ] Bốn bản server (iterative → fork → thread pool → epoll), đo cả bốn
- [ ] Giữ 10.000 kết nối đồng thời
- [ ] Đọc `tcpdump`, giải thích được một gói retransmit cụ thể
- [ ] Xử lý đúng partial read/write, `EINTR`, `EAGAIN`, backpressure
- [ ] **Blog #4** — đây sẽ là bài hay nhất, UNP Ch30 cho bạn nội dung

### Phase 4 — Go · 6 tuần
- [ ] `ouro-net` viết lại bằng Go, cùng bộ test integration, cùng pass
- [ ] Bảng so sánh C vs Go: LOC, throughput, p50/p99/p999, bộ nhớ, giờ công
- [ ] Trả lời được: Go scheduler khác OS scheduler chỗ nào?
- [ ] **Blog #5**
- [ ] ⚠️ **Làn B khởi động** — DS&A 3–5h/tuần từ đây (tháng thứ 8)

### Phase 5 — Phân tán · 11 tuần
- [ ] Gõ hết *Distributed Services with Go* ở `scratch/` — rồi **đóng sách**
- [ ] `ouro-dist` viết lại từ đầu, sách đóng
- [ ] 3 node: giết leader → bầu lại dưới 1 giây, không mất commit
- [ ] Thêm/bớt node khi đang chạy, không downtime
- [ ] Test kiểu Jepsen đơn giản
- [ ] **Blog #6**
- [ ] ⚠️ Chuẩn bị 3 VM Linux thật trước khi vào phase này

### Phase 6 — Container runtime · 11 tuần
- [ ] `ouro-run run alpine /bin/sh` → shell cô lập thật sự
- [ ] Giới hạn 256MB RAM có hiệu lực
- [ ] Container ping ra ngoài và ping được nhau
- [ ] Rootless qua user namespace
- [ ] Kể được từng syscall đã gọi và vì sao thứ tự đó
- [ ] **Blog #7**

### Phase 7 — Orchestrator · 11 tuần
- [ ] `ouroctl apply -f ouro-cluster.yaml` khởi động 3 replica
- [ ] Giết container bằng tay → tự tạo lại trong 10 giây
- [ ] Rolling update không downtime
- [ ] 🐍 **Trạng thái `ouro-ctl` nằm trong chính cluster nó quản lý**
- [ ] Reboot cả cụm → tự phục hồi
- [ ] **Blog #8 + video demo** — đây là thứ đưa vào CV

### Phase 8 — AI Infrastructure · 10 tuần
- [ ] Scheduler nhận diện và xếp theo GPU
- [ ] Train phân tán 3 node, máy chết giữa chừng vẫn resume
- [ ] Inference server có dynamic batching, đạt mục tiêu p99
- [ ] **Blog #9 + bài tổng kết hành trình**

---

# Làn B — DS&A

Khởi động **tháng thứ 8** (đầu Phase 4, khoảng 05/2027). Không sớm hơn.
3–5h/tuần, đều đặn, không cày dồn.

```
[░░░░░░░░░░] 0%   Chưa tới lúc
```

- [ ] Mảng, chuỗi, two pointer, sliding window
- [ ] Hash map, set
- [ ] Stack, queue, monotonic stack
- [ ] Cây nhị phân, BST, traversal
- [ ] Đồ thị: BFS, DFS, topological sort
- [ ] Quy hoạch động
- [ ] Heap, priority queue
- [ ] Binary search và biến thể
- [ ] Mock interview với người thật

---

# Nghi thức hàng tuần

**Mỗi buổi học** — 5 phút đầu:
1. Mở file này, xem tuần này còn gì chưa tick
2. Mở `SACH.md`, xác nhận đọc chương nào

**Cuối mỗi buổi** — 5 phút cuối:
1. Tick những gì thật sự xong
2. Commit, dù chỉ 20 dòng
3. Chỗ nào bí quá 2 tiếng → ghi vào `NHATKY.md`

**Chủ nhật** — 20 phút:
1. Cập nhật thanh tiến độ ở đầu file
2. Đọc lại **Luật đi đường** trong `README.md`
3. Trượt tiến độ 2 tuần liên tiếp → dừng lại, xem lại nhịp 15–20h có thực tế không.
   Điều chỉnh kế hoạch chứ đừng điều chỉnh sự thật.

---

# Nhật ký cột mốc

| Ngày | Cột mốc |
|---|---|
| | *(ghi vào đây mỗi khi qua một cổng ra)* |
