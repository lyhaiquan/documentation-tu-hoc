# Bản đồ sách Ouroboros

Mở file này mỗi đầu tuần. Nó trả lời đúng một câu: **tuần này đọc chương nào, cuốn nào.**

Tất cả đường dẫn tính từ `D:/Documentation/`.

---

## Nguyên tắc số một

Bốn cuốn nền (CSAPP, OSTEP, TLPI, DB Internals) **chồng lấn nhau tới 40%**.
Virtual memory nằm trong cả ba. Concurrency nằm trong cả ba.

**Đọc tuần tự từng cuốn = đọc lại cùng một thứ ba lần = mất 3 năm.**

Đọc theo chủ đề, cắt ngang cả bốn cuốn. Bảng dưới đã cắt sẵn cho bạn.

Công thức nhớ vai trò:

> **OSTEP** = tại sao thiết kế như vậy
> **TLPI** = gọi hàm nào, tham số gì
> **CSAPP** = chuyện gì thực sự xảy ra dưới lớp gỗ
> **DB Internals / Stevens** = dùng mấy thứ đó xây cái gì có ích

---

## Đính chính: bạn đang hiểu sai 3 trong 4 cuốn

| Cuốn | Nhãn sai | Thực tế |
|---|---|---|
| CSAPP | "kiến trúc máy tính" | Kiến trúc chỉ là Ch3–4. Còn lại là hệ thống nhìn từ mắt lập trình viên. Đây là cuốn **nền** cho cả TLPI lẫn OSTEP. |
| TLPI | "Linux kernel" | Là **userspace system programming** — API gọi *vào* kernel. Không dạy kernel bên trong. |
| OSTEP | "OS" | Đúng, nhưng nó dạy **tại sao**, không dạy gõ code. |
| DB Internals | "core DB" | Part I là storage engine. **Part II thực chất là sách hệ phân tán**, không dính gì DB. |

---

## Kho sách: giữ gì, bỏ gì

### Xương sống — đọc kỹ

| Sách | Đường dẫn | Phase |
|---|---|---|
| CSAPP 3rd ed | `OS-Linux-Networking/CSAPP_2016.pdf` | 0–3 |
| OSTEP | `OS-Linux-Networking/Operating Systems - Three Easy Pieces.pdf` | 0–3 |
| TLPI (Kerrisk) | `OS-Linux-Networking/The Linux Programming Interface (Kerrisk).pdf` | 1–6 |
| UNIX Network Programming Vol.1 3e | `_repo-technical-books/UNIX Network Programming(Volume1,3rd).pdf` | 3 |
| TCP/IP Illustrated Vol.1 | `OS-Linux-Networking/Stevens W.R. - TCP IP Illustrated, Vol.1, The Protocols.pdf` | 3 |
| Database Internals (Petrov) | `Database/Database Internals - A Deep Dive (Alex Petrov).pdf` | 1, 5 |
| PostgreSQL 14 Internals (Rogov) | `Database/PostgreSQL 14 Internals (Egor Rogov).pdf` | 1 |
| Learning Go (Bodner) | `Go/Learning Go 1st Ed 2021 (Jon Bodner).pdf` | 4 |
| Mastering Go 3e | `Go/Mastering Go 3rd Ed (Mihalis Tsoukalos).pdf` | 4 |
| Network Programming with Go | `Go/Network Programming with Go (Adam Woodbeck).pdf` | 4 |
| Distributed Services with Go | `Go/Distributed Services with Go (Travis Jeffery).pdf` | 5 |
| DDIA (Kleppmann) | `System-Design-Architecture/Designing Data-Intensive Applications*.pdf` | 5 |
| Container Security 2e (Liz Rice) | `Kubernetes/Container Security 2nd Ed (Liz Rice).pdf` | 6 |
| Kubernetes Up & Running 3e | `Kubernetes/Kubernetes Up and Running - 3rd Ed 2022*.pdf` | 7 |
| Cloud Native Go (Titmus) | `Go/Cloud Native Go 1st Ed 2021 (Matthew Titmus).pdf` | 7 |
| Machine Learning Systems Vol 1–2 | `AI-ML/Machine Learning Systems Vol 1.pdf`, `Vol 2.pdf` | 8 |

### Tra cứu — không đọc tuần tự

| Sách | Dùng khi |
|---|---|
| APUE 3e (Stevens) | Chỉ khi cần biết BSD/macOS khác Linux chỗ nào. Trùng ~85% với TLPI. |
| System Design Interview Vol 2 (Alex Xu) | Ba tháng trước khi nộp hồ sơ. Không phải để xây. |
| Designing Event-Driven Systems | Nếu Phase 5 rẽ sang hướng streaming. Tùy chọn. |

### Bỏ hẳn — tiết kiệm nhiều tháng

| Sách | Lý do |
|---|---|
| OS Concepts (Silberschatz) | Trùng ~90% OSTEP, dài gấp đôi, khô hơn. **Bỏ.** |
| CSAPP 2e (`_repo-technical-books`) | Bản cũ. Bạn đã có 3e. Xóa cho khỏi nhầm. |
| C++ Primer | Không dính gì dự án này. |
| Deep Learning with Python · Python ML · ML cơ bản · ML Yearning | Sách dạy **làm model**. Bạn xây **cái máy chạy model**. Cất 2 năm. |
| 6 cuốn Go còn lại (Pro Go, Practical Go, Everyday Go, Essentials, Little Go Book) | Bạn có 10 cuốn Go, cần 3. Đừng mở cho tới khi gặp vấn đề cụ thể. |

> **Bẫy lớn nhất:** sưu tầm sách là cách trì hoãn dễ chịu nhất trên đời.
> Kho của bạn đã thừa. Đừng tải thêm, trừ hai thứ dưới đây.

### Còn thiếu — tải hai thứ này, rồi dừng

1. **Modern C (Jens Gustedt)** — miễn phí hợp pháp, C17/C23. Bạn không có cuốn C nào tử tế (`C-Cpp/` chỉ có C++ Primer). CSAPP dạy đủ C để sống sót nhưng cần quyển tra cứu.
2. **Raft paper (extended)** — *In Search of an Understandable Consensus Algorithm*, Ongaro & Ousterhout. 18 trang, miễn phí, bắt buộc cho Phase 5.

---

## Bảng đọc theo phase

### Phase 0 — Biết cái máy của mình (5 tuần)

| Sách | Chương |
|---|---|
| CSAPP | Ch1 (đọc nhanh, coi như bản đồ) · **Ch2 toàn bộ** (bits, integer, float) · Ch5 (tối ưu) · Ch6 (memory hierarchy) · Ch9.9 (dynamic memory allocation) |
| OSTEP | Ch17 (Free-Space Management) |
| TLPI | Ch1–3 (khái niệm nền) · Ch7 (Memory Allocation) |
| Modern C | Tra cứu khi vướng cú pháp |

**Đây là phase học C thật sự.** Không học C qua sách C — học C qua CSAPP.

---

### Phase 1 — Storage engine bằng C (9 tuần)

| Sách | Chương |
|---|---|
| **Database Internals** | **Ch1–7 (toàn bộ Part I)** — B-Tree, file format, transaction & recovery, B-Tree variants, log-structured storage |
| **PostgreSQL 14 Internals** | **Part I (Isolation & MVCC)** · **Part II (Buffer Cache & WAL)** |
| CSAPP | Ch10 (System-Level I/O) |
| TLPI | Ch4, Ch5 (File I/O) · Ch13 (I/O buffering) · Ch14 (File Systems) · Ch49 (Memory Mappings) · Ch55 (File Locking) |
| OSTEP | Ch36–44 (I/O devices, HDD, RAID, files & directories, FS implementation, FFS, crash consistency & journaling, LFS, SSD) |

> **Cách dùng Rogov:** viết B-Tree + WAL + buffer pool đồ chơi của mình trước,
> rồi mở Rogov xem một engine sản xuất thật làm y hệt thứ đó thế nào.
> Không sách nào khác cho bạn đối chiếu đồ chơi ↔ hàng thật kiểu này.

---

### Phase 2 — Process & concurrency bằng C (7 tuần)

| Sách | Chương |
|---|---|
| CSAPP | Ch8 (Exceptional Control Flow) · Ch12 (Concurrent Programming) |
| OSTEP | Ch4–10 (process, API, direct execution, scheduling, MLFQ, lottery, multiprocessor) · **Ch26–33 (toàn bộ concurrency)** |
| TLPI | Ch6 (Processes) · Ch20–25 (signals, process creation & termination) · Ch29–33 (threads) · Ch34 (job control) · Ch35 (scheduling) · Ch37 (daemons) · Ch43–54 (toàn bộ IPC) |

---

### Phase 3 — Mạng bằng C (9 tuần)

| Sách | Chương |
|---|---|
| **UNP Vol.1** | Ch3–8 (sockets, TCP client/server, **Ch6 I/O Multiplexing**, socket options, UDP) · Ch14 (Advanced I/O) · Ch16 (Nonblocking I/O) · Ch26 (Threads) · **Ch30 (Client/Server Design Alternatives)** |
| TLPI | Ch56–61 (sockets) · **Ch63 (Alternative I/O Models — select/poll/epoll)** |
| CSAPP | Ch11 (Network Programming) |
| TCP/IP Illustrated | Ch1–3 (nền) · Ch17–24 (TCP: connection, timeout & retransmission, flow control, congestion) |

> **UNP Ch30** so sánh 9 kiến trúc server khác nhau kèm số đo thật.
> Đây là chương bạn dựa vào để thiết kế `ouro-net`. Đọc kỹ nhất trong cả lộ trình.

---

### Phase 4 — Go (6 tuần)

| Sách | Chương |
|---|---|
| Learning Go (Bodner) | Ch1–13 (bỏ Ch14 reflect/unsafe/cgo, để sau) |
| Mastering Go 3e | Chỉ chương **Go Concurrency** + phần runtime/GC/unsafe |
| Network Programming with Go | Ch3–7 (TCP, gửi dữ liệu, UDP, độ tin cậy UDP, Unix domain socket) |

**Câu hỏi phải trả lời được khi xong phase:**
Go runtime scheduler khác OS scheduler (OSTEP Ch7–10) ở chỗ nào,
và tại sao goroutine rẻ hơn thread (TLPI Ch29)?

---

### Phase 5 — Phân tán (11 tuần)

| Sách | Chương |
|---|---|
| **Distributed Services with Go** | **Cả cuốn, gõ theo ở thư mục nháp** — protobuf → gRPC → TLS → observability → Serf discovery → **Raft** → client load balancing |
| Database Internals | Ch8–14 (toàn bộ Part II) — failure detection, leader election, replication & consistency, anti-entropy, distributed transactions, consensus |
| DDIA | **Ch5–9** (replication, partitioning, transactions, trouble with distributed systems, consistency & consensus). Dùng bản tiếng Việt cho nhanh, tra bản Anh khi thuật ngữ gợn. |
| Raft paper | Bản extended, 18 trang |

> ⚠️ **Luật quan trọng nhất của phase này:** gõ theo Jeffery ở `~/scratch/dsgo/`,
> rồi **đóng sách** và viết `ouro-dist` từ đầu. Copy code vào dự án = Phase 5 vô nghĩa.

---

### Phase 6 — Container runtime (11 tuần)

| Sách | Chương |
|---|---|
| **Container Security 2e** | Ch2 (syscalls, permissions, capabilities) · Ch3 (**cgroups**) · Ch4 (**container isolation — namespaces, pivot_root**) · Ch6 (container images) · Ch8 (seccomp, AppArmor, SELinux) · Ch10 (container network security) |
| TLPI | Ch38 (secure privileged programs) · Ch39 (Capabilities) · Ch18 (Directories & Links) · Ch14 (File Systems — đọc lại) |
| man pages | `man 7 namespaces` · `man 7 cgroups` · `man 7 capabilities` · `man 2 unshare` · `man 2 pivot_root` |

> **Lỗ hổng đã biết:** TLPI viết 2010 nên **không** dạy namespace/cgroup đầy đủ.
> Lấp bằng Liz Rice + man pages. Nói trước để bạn không hoang mang khi tra không thấy.

---

### Phase 7 — Orchestrator (11 tuần)

| Sách | Chương |
|---|---|
| Kubernetes Up & Running 3e | Ch5–13 (pods, labels, service discovery, ingress, ReplicaSet, Deployment, DaemonSet, Job, ConfigMap & Secret) — đọc để **lấy mô hình khái niệm**, không phải học kubectl · **Ch17 (Extending Kubernetes — CRD, operator)** |
| Cloud Native Go | Ch4 (Cloud Native Patterns: circuit breaker, retry, throttle, timeout, fan-in/fan-out) |
| Distributed Services with Go | Ch10–11 (deploy với Kubernetes) |

---

### Phase 8 — AI Infrastructure (10 tuần)

| Sách | Phần |
|---|---|
| **Machine Learning Systems Vol 1–2** | *Training* · *Efficient AI* · *Model Optimizations* · *AI Acceleration* · *Benchmarking AI* · *ML Operations* |

Đây là cuốn đúng cho bạn: nó viết cho **kỹ sư hệ thống**, không phải data scientist.

Ba thứ AI infra thêm vào so với cloud infra thường, và mảnh nào của Ouroboros gánh:

| Thêm vào | Dùng lại |
|---|---|
| Device plugin nhận diện GPU, scheduler xếp theo GPU | `ouro-ctl` |
| Checkpoint khi train, resume khi máy chết | `ouro-store` + WAL |
| Đồng bộ gradient giữa worker (all-reduce) | `ouro-net` + `ouro-dist` |
| Inference server có dynamic batching | `ouro-net` |

---

## Độ phủ cuối cùng

| Sách | Phủ |
|---|---|
| Database Internals | ~100% |
| CSAPP | ~95% |
| OSTEP | ~90% |
| UNP Vol.1 | ~85% |
| TLPI | ~85% |

### Những chương dự án KHÔNG tự phủ — nhiệm vụ phụ để lấp

| Thiếu | Cách lấp | Xen vào |
|---|---|---|
| CSAPP Ch3–4 (assembly, Y86) | **Bomb Lab + Attack Lab + Architecture Lab** của CMU (miễn phí) | Phase 0–1, 3 tuần |
| CSAPP Ch7 (Linking) | Tự viết build system + shared library cho `ouro-store`; đọc kèm TLPI Ch41–42 | Phase 1 |
| OSTEP Ch13–23 (paging, TLB chi tiết) | Viết page-replacement simulator (FIFO/LRU/CLOCK) và so số liệu | Phase 1, 1 tuần |
| TLPI Ch62, 64 (terminals, pty) | `ouroctl exec -it` cần pty thật | Phase 7, tự nhiên rơi vào |
| TLPI Ch8–9, 40 (users, credentials) | User namespace + rootless container | Phase 6, bắt buộc |
| TLPI Ch19 (inotify) | Config hot-reload | Phase 7 |

**Phần TLPI còn lại** (Ch11–12, Ch40, Ch45–48 System V IPC cũ) là thứ ngay cả kỹ sư
Linux lâu năm cũng chỉ tra khi cần. **Không cày.**
