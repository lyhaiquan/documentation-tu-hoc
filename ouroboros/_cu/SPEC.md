# Ouroboros — Thiết kế kỹ thuật

Mở file này khi bắt đầu một phase mới. Nó nói **xây cái gì** và **xong là thế nào**.

Nguyên tắc chung: mỗi thành phần phải **đứng một mình được** — chạy được, test được,
demo được, kể cả khi mọi thứ phía trên chưa tồn tại.

---

## Bố cục repo

Code nằm ở `D:/Code/ouroboros/`, **không** nằm cùng thư mục sách.

```
ouroboros/
├── store/          Phase 1-2   C
│   ├── src/        page.c btree.c lsm.c wal.c bufpool.c recovery.c
│   ├── include/
│   └── tests/
├── net/            Phase 3     C       (bản C giữ lại để đối chiếu)
├── netgo/          Phase 4     Go      (bản viết lại)
├── dist/           Phase 5     Go      raft/ gossip/ replica/
├── run/            Phase 6     Go + C  ns/ cgroup/ image/ network/
├── ctl/            Phase 7     Go      apiserver/ scheduler/ controller/
├── scope/          xuyên suốt  bench harness, pprof, perf script
├── scratch/        vùng nháp — gõ theo sách ở đây, KHÔNG commit vào dự án chính
└── docs/           ghi chép thiết kế, sơ đồ, kết quả benchmark
```

`scratch/` vào `.gitignore`. Đó là nơi gõ theo *Distributed Services with Go*.
Code trong `dist/` phải được viết lại từ đầu với sách đóng.

---

## Phase 0 — Nền: hiểu cái máy

Chưa phải thành phần của Ouroboros. Đây là phần luyện tay và luyện mắt.

**Xây:**
| Thứ | Mô tả |
|---|---|
| `myalloc` | `malloc`/`free` tự viết: implicit free list → explicit → segregated fit |
| `mountain` | Đo memory mountain — throughput đọc theo stride và working-set size |
| `hexdump` | Tự viết, để quen với việc nhìn byte thô |

**Xong khi:**
- [ ] `myalloc` pass bộ test của CSAPP malloc lab, utilization > 70%
- [ ] Bạn giải thích được **bằng số đo của chính mình** vì sao duyệt mảng 2D theo cột chậm hơn theo hàng ~6 lần
- [ ] Bạn đọc được output `objdump -d` của hàm mình viết mà không hoảng

---

## `ouro-store` — Storage engine (Phase 1–2, C)

Trái tim của cả hệ thống. Nếu cái này sai, mọi thứ trên nó vô nghĩa.

### Giao diện

```c
store_t *store_open(const char *path, store_opts_t *opts);
int      store_put(store_t *s, const slice_t key, const slice_t val);
int      store_get(store_t *s, const slice_t key, slice_t *out);
int      store_del(store_t *s, const slice_t key);
iter_t  *store_scan(store_t *s, const slice_t from, const slice_t to);
int      store_close(store_t *s);
```

Cố ý nhỏ. Mọi độ phức tạp nằm bên dưới, không lộ ra ngoài.

### Các lớp bên trong

| Lớp | Trách nhiệm | Sách |
|---|---|---|
| **Page layout** | Slotted page, header, checksum, free space map | DB Internals Ch3 |
| **B-Tree** | insert / split / delete / merge / rebalance | DB Internals Ch2, 4, 6 |
| **LSM** | memtable, SSTable, compaction (level + size-tiered) | DB Internals Ch7 |
| **Buffer pool** | Page cache, pin/unpin, thay thế CLOCK | OSTEP Ch22, Rogov Part II |
| **WAL** | Append-only log, LSN, group commit, fsync policy | DB Internals Ch5, Rogov Part II |
| **Recovery** | Redo từ WAL, checkpoint, phát hiện torn page | DB Internals Ch5 |

### Quyết định thiết kế cần tự trả lời (ghi vào `docs/`)

1. Page size bao nhiêu? Vì sao không lớn hơn / nhỏ hơn?
2. `mmap` hay `pread`/`pwrite`? Đọc lập luận của cả hai phe rồi chọn, ghi lý do.
3. `fsync` mỗi commit hay group commit? Đánh đổi độ bền ↔ throughput ở đâu?
4. B-Tree và LSM: giữ **cả hai** để benchmark đối đầu. Mỗi cái thắng ở workload nào?

### Xong khi
- [ ] 1000 lần `kill -9` ngẫu nhiên giữa lúc ghi → không mất dữ liệu đã ack, không hỏng file
- [ ] Benchmark B-Tree vs LSM trên 3 workload (ghi tuần tự, ghi ngẫu nhiên, đọc nhiều) — có biểu đồ
- [ ] `store_scan` trả đúng thứ tự trên 10 triệu key
- [ ] Không rò bộ nhớ (valgrind sạch), không race (ThreadSanitizer sạch)
- [ ] Chạy được đa luồng: nhiều reader + một writer, có file locking

---

## `ouro-net` — Lớp mạng (Phase 3 C → Phase 4 Go)

### Wire protocol

Nhị phân, tự thiết kế. Không JSON, không HTTP ở lớp này.

```
┌────────┬────────┬─────────┬──────────┬─────────┬──────────┐
│ magic  │ ver    │ opcode  │ req_id   │ len     │ payload  │
│ 4 byte │ 1 byte │ 1 byte  │ 8 byte   │ 4 byte  │ len byte │
└────────┴────────┴─────────┴──────────┴─────────┴──────────┘
```

Tự trả lời: little hay big endian? Vì sao? (CSAPP Ch2.1 có câu trả lời.)

### Kiến trúc server

Đọc **UNP Ch30** trước, chọn một kiến trúc, ghi lý do vào `docs/`. Gợi ý lộ trình:

1. Bản 1: iterative — một client một lúc. Cố tình làm sai để thấy nó sai.
2. Bản 2: fork mỗi kết nối. Đo xem chết ở bao nhiêu client.
3. Bản 3: thread pool + blocking I/O.
4. Bản 4: **epoll + event loop + thread pool** — bản cuối.

Đo cả bốn bản. Đây là chỗ số liệu dạy nhiều hơn sách.

### Phase 4: viết lại bằng Go

Giữ **cả hai** bản. So sánh và ghi vào `docs/c-vs-go.md`:

| Chỉ số | C | Go |
|---|---|---|
| Số dòng code | | |
| Throughput (req/s) | | |
| Latency p50 / p99 / p999 | | |
| Bộ nhớ khi 10k kết nối | | |
| Thời gian viết (giờ) | | |

Đây là bảng bạn sẽ kể trong phỏng vấn.

### Xong khi
- [ ] Giữ 10.000 kết nối đồng thời, ổn định
- [ ] Đọc được `tcpdump` và giải thích được một gói retransmit cụ thể
- [ ] Xử lý đúng: partial read/write, `EINTR`, `EAGAIN`, backpressure, slow client
- [ ] Graceful shutdown: `SIGTERM` → ngừng nhận mới, xử nốt đang có, thoát sạch
- [ ] Bản Go có cùng bộ test integration với bản C và cùng pass

---

## `ouro-dist` — Lớp phân tán (Phase 5, Go)

### Thành phần

| Thành phần | Nội dung | Nguồn |
|---|---|---|
| **Raft** | Leader election, log replication, snapshot, membership change | Raft paper + DB Int. Ch14 |
| **Gossip** | Failure detector kiểu SWIM, membership | DB Int. Ch9, 12 |
| **Replication** | Bọc `ouro-store` sau Raft log | DB Int. Ch11, DDIA Ch5 |
| **Client** | Tìm leader, retry, load balance đọc sang follower | DSwGo Ch9 |

### Quyết định cần tự trả lời

1. Read từ leader (linearizable) hay từ follower (nhanh, có thể cũ)? Cho client chọn?
2. Snapshot khi nào? Log dài bao nhiêu thì cắt?
3. Mất mạng chia đôi cluster (network partition) — bên thiểu số làm gì?

### Xong khi
- [ ] 3 node. Giết leader → bầu lại trong **dưới 1 giây**, không mất commit đã ack
- [ ] Thêm/bớt node khi đang chạy, không downtime
- [ ] Test kiểu Jepsen đơn giản: chèn lỗi mạng ngẫu nhiên, kiểm tra tính nhất quán
- [ ] Node chết 10 phút rồi sống lại → tự bắt kịp qua snapshot + log

---

## `ouro-run` — Container runtime (Phase 6, Go + C)

### Những gì phải tự làm, không thư viện

| Cơ chế | Syscall / giao diện |
|---|---|
| Namespaces | `clone()` / `unshare()` với `CLONE_NEW{PID,NET,NS,UTS,IPC,USER}` |
| Cgroups v2 | Ghi vào `/sys/fs/cgroup/...` — `memory.max`, `cpu.max`, `pids.max` |
| Filesystem | `overlayfs` mount, `pivot_root()`, gỡ mount cũ |
| Bảo mật | `seccomp` BPF filter, drop capabilities, no-new-privs |
| Mạng | `veth` pair, bridge, `iptables`/`nftables` NAT, cấp IP |
| Image | Layer dạng tar + manifest, tương thích OCI image spec |

### Giao diện

```
ouro-run run <image> <cmd>       chạy container
ouro-run ps                      liệt kê
ouro-run exec <id> <cmd>         vào container đang chạy
ouro-run rm <id>                 xóa
ouro-run pull <ref>              kéo image (OCI registry)
```

### Xong khi
- [ ] `ouro-run run alpine /bin/sh` → shell cô lập: không thấy process host, hostname riêng, mạng riêng
- [ ] Giới hạn 256MB RAM thực sự có hiệu lực (thử cấp phát 512MB → bị kill)
- [ ] Container ping được ra ngoài và ping được container khác
- [ ] Rootless: chạy được với user thường qua user namespace
- [ ] **Bạn kể được từng syscall đã gọi, theo đúng thứ tự, và vì sao thứ tự đó**

Điều cuối cùng quan trọng nhất. Đó là câu hỏi phỏng vấn.

---

## `ouro-ctl` — Orchestrator (Phase 7, Go)

Chỗ con rắn cắn đuôi.

### Mô hình

Khai báo, không mệnh lệnh. Người dùng mô tả **trạng thái mong muốn**;
hệ thống tự làm cho thực tế khớp với mong muốn.

```yaml
kind: Service
name: ouro-db
replicas: 3
image: ouro-store:v1
resources: { memory: 512Mi, cpu: 1.0 }
```

### Thành phần

| Thành phần | Trách nhiệm |
|---|---|
| **API server** | REST/gRPC, validate, ghi trạng thái mong muốn xuống store |
| **State store** | **Cluster `ouro-store` + Raft từ Phase 5** — thay etcd |
| **Scheduler** | Chọn node cho mỗi workload: lọc → chấm điểm → gán |
| **Controller** | Vòng lặp reconcile: đọc mong muốn, đọc thực tế, làm cho khớp |
| **Node agent** | Chạy trên mỗi node, gọi `ouro-run`, báo trạng thái về |

### Vòng reconcile — hiểu cái này là hiểu Kubernetes

```
lặp mãi mãi:
    mong_muốn  = đọc từ store
    thực_tế    = hỏi các node agent
    với mỗi khác biệt:
        hành động để thu hẹp khác biệt
    ngủ một nhịp
```

Đơn giản đến mức khó tin. Toàn bộ Kubernetes là ý tưởng này lặp lại ở 30 chỗ khác nhau.

### Xong khi
- [ ] `ouroctl apply -f ouro-cluster.yaml` khởi động 3 replica `ouro-store`
- [ ] Giết một container bằng tay → controller tự tạo lại trong 10 giây
- [ ] Rolling update: đổi image, không downtime
- [ ] **Trạng thái của `ouro-ctl` nằm trong chính cluster `ouro-store` mà nó quản lý**
- [ ] `ouroctl exec -it` hoạt động (cần pty — TLPI Ch62, 64)
- [ ] Reboot cả cụm → tự phục hồi về đúng trạng thái trước đó

---

## `ouro-scope` — Quan sát (xuyên suốt)

Không phải phase riêng. Làm dần từ Phase 1.

| Thứ | Khi nào thêm |
|---|---|
| Bench harness tái lập được | Phase 1 |
| `perf stat` / cache miss counters | Phase 1 (CSAPP Ch5–6) |
| Structured logging | Phase 3 |
| `pprof` CPU + heap profile | Phase 4 |
| Metrics kiểu Prometheus | Phase 5 |
| Distributed tracing | Phase 7 |

**Luật:** không tối ưu thứ gì chưa đo. Mỗi lần tối ưu phải có số trước và số sau,
ghi vào `docs/bench/`.

---

## Phase 8 — AI Infrastructure

Mở rộng, không viết lại.

| Thêm vào | Xây trên | Sách |
|---|---|---|
| Device plugin phát hiện GPU; scheduler xếp theo GPU | `ouro-ctl` scheduler | MLSys *AI Acceleration* |
| Checkpoint/resume khi train bị đứt | `ouro-store` WAL | MLSys *Training* |
| All-reduce đồng bộ gradient giữa worker | `ouro-net` + `ouro-dist` | MLSys *Training* |
| Inference server: dynamic batching, hàng đợi, giới hạn độ trễ | `ouro-net` | MLSys *Efficient AI* |
| Benchmark harness cho model serving | `ouro-scope` | MLSys *Benchmarking AI* |

### Xong khi
- [ ] Train một model nhỏ phân tán trên 3 node của cụm mình, máy chết giữa chừng vẫn resume được
- [ ] Inference server đạt mục tiêu p99 latency đặt trước, có dynamic batching
- [ ] Scheduler xếp đúng workload cần GPU vào node có GPU

---

## Rủi ro đã biết

| Rủi ro | Mức | Cách chống |
|---|---|---|
| Bỏ cuộc ở Phase 3 hoặc 6 | **Cao** | Mỗi phase có thứ demo được. Bỏ ngang vẫn còn tài sản. |
| Sa lầy tối ưu sớm | Cao | Luật: chạy đúng trước, đo, rồi mới tối ưu |
| Copy code từ sách | Cao | `scratch/` tách riêng, trong `.gitignore` |
| Thiếu DS&A khi phỏng vấn | **Cao** | Làn B bắt đầu tháng thứ 6, 3–5h/tuần, không đàm phán |
| Thi cử, Tết làm trượt tiến độ | Trung bình | 4 tuần đệm mỗi năm đã tính sẵn trong `PROGRESS.md` |
| WSL2 không đủ cho Phase 6 | Chắc chắn xảy ra | Chuẩn bị 3 VM Linux (Multipass/Vagrant) trước Phase 5 |

---

## Môi trường theo phase

| Phase | Cần gì |
|---|---|
| 0–4 | WSL2 Ubuntu · gcc · gdb · make · valgrind · perf |
| 5 | **3 VM Linux thật** (Multipass hoặc Vagrant) · Go toolchain |
| 6–7 | 3 VM có quyền root đầy đủ. WSL2 **không đủ** — namespace và bridge networking bị giới hạn |
| 8 | Ít nhất 1 máy có GPU, hoặc GPU cloud theo giờ |
