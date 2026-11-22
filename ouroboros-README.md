# Ouroboros

> Tự xây một đám mây thu nhỏ — từ mặt đĩa cứng lên tới API — rồi bắt nó tự host chính nó.

**Người học:** Lý Hải Quân
**Bắt đầu:** 21/09/2026
**Dự kiến xong:** Quý 2/2028
**Nhịp:** 15–20 giờ/tuần
**Mục tiêu nghề:** Cloud / Infrastructure Engineer đi sâu vào lõi → AI Infrastructure

---

## Nôm na dự án này là gì

Bóc trần AWS ra thì nó chỉ có 5 thứ:

1. Một chỗ **cất dữ liệu** xuống đĩa mà không mất khi mất điện.
2. Một cách để **nhiều máy đồng ý với nhau** ngay cả khi có máy chết.
3. Một cách **nhốt phần mềm vào hộp** để chạy cô lập.
4. Một **thằng quản đốc** tự động đặt hộp nào lên máy nào.
5. Một cách **nhìn xuyên vào** xem cả đống đó đang làm gì.

Dự án này là viết lại đúng 5 thứ đó, từ số 0, bằng tay. Không Docker. Không Kubernetes. Không etcd. Không thư viện làm hộ phần khó.

| Bạn viết | Ngoài đời tên là |
|---|---|
| `ouro-store` | DynamoDB · RocksDB · storage engine của PostgreSQL |
| `ouro-net` | lớp server/RPC của mọi dịch vụ |
| `ouro-dist` | Raft trong etcd · replication của Spanner |
| `ouro-run` | Docker · containerd · runc |
| `ouro-ctl` | Kubernetes · Amazon ECS |
| `ouro-scope` | CloudWatch · Prometheus |

## Cú kết: con rắn cắn đuôi

Quản đốc (`ouro-ctl`) lưu trạng thái của chính nó trong database (`ouro-store`).
Database đó lại đang chạy trong container (`ouro-run`) do quản đốc đặt xuống.

```bash
ouroctl apply -f ouro-cluster.yaml
```

Một lệnh. Orchestrator đọc YAML, lên lịch 3 replica database, đóng gói trong
container, nối mạng bằng veth/bridge, đồng thuận bằng Raft. Rút điện một node —
cluster bầu leader mới, không mất một commit nào đã ack.

Không một dòng code của người khác ở những chỗ khó.

---

## Kiến trúc

```
┌──────────────────────────────────────────────────────────┐
│  ouroctl  →  ouro-ctl   (Go)                             │  Phase 7
│  API khai báo · scheduler · reconcile loop · rolling update│
├──────────────────────┬───────────────────────────────────┤
│  ouro-run (Go + C)   │  ouro-dist (Go)                   │  Phase 5-6
│  namespaces, cgroups │  Raft · replication · gossip      │
│  overlayfs, seccomp  │  2PC · failure detection          │
│  veth/bridge         │                                   │
├──────────────────────┴───────────────────────────────────┤
│  ouro-net  (C → Go)                                       │  Phase 3-4
│  epoll server · wire protocol nhị phân · client lib       │
├───────────────────────────────────────────────────────────┤
│  ouro-store  (C)                                          │  Phase 1-2
│  B-Tree + LSM · WAL · buffer pool · crash recovery         │
└───────────────────────────────────────────────────────────┘
   ouro-scope: perf counters · pprof · bench harness          Xuyên suốt
   + Phase 8: GPU scheduling · distributed training · serving
```

---

## Luật đi đường

Sáu điều này quan trọng hơn bất kỳ chương sách nào. Đọc lại mỗi khi thấy mình chệch hướng.

**1. Không đọc hết sách rồi mới code.**
Đọc 3–5 chương → code ngay cái vừa đọc → đọc tiếp. Sách là tài liệu tra cứu
theo nhu cầu, không phải hàng rào phải vượt qua trước khi được phép gõ phím.

**2. Mỗi phase kết thúc bằng một thứ chạy được và demo được.**
Không có "code dở dang chờ phase sau". Nếu bỏ ngang giữa chừng, thứ đã làm
vẫn phải chạy.

**3. Không copy code từ sách vào dự án.**
Đặc biệt là *Distributed Services with Go*. Gõ theo sách ở thư mục nháp để
học, rồi **đóng sách lại** và tự viết từ đầu trong dự án. Copy = mất sạch giá trị.

**4. Commit mỗi ngày có học, dù chỉ 20 dòng.**
Commit history 2 năm là tài sản recruiter đọc được. Chứng chỉ thì không.

**5. Xong mỗi phase → viết một bài blog kỹ thuật.**
Kể cả chỗ làm sai và phải sửa. Đặc biệt là chỗ làm sai.

**6. Bí quá 2 tiếng → ghi vào `NHATKY.md` rồi mới đi hỏi.**
Viết ra câu hỏi thường tự giải được nó. Nếu không, bạn đã có câu hỏi tử tế để hỏi.

---

## Hai làn song song

Ouroboros dạy bạn chiều sâu, nhưng **không** đưa bạn qua vòng coding interview.
Đây là rủi ro lớn nhất của kế hoạch này.

| Làn | Nội dung | Thời lượng | Bắt đầu |
|---|---|---|---|
| **A** | Ouroboros | 80% | Tuần 1 |
| **B** | DS&A / thuật toán phỏng vấn | 20% (3–5h/tuần) | **Tháng thứ 6** |

Làn B bắt đầu muộn là cố ý: sáu tháng đầu cần C và tư duy hệ thống vững đã,
lúc đó học thuật toán vào nhanh hơn nhiều.

---

## Tài liệu trong thư mục này

| File | Dùng khi nào |
|---|---|
| `README.md` | Bạn đang đọc. Mở lại khi mất phương hướng. |
| **`KIEN-TRUC.md`** | **Đọc TRƯỚC khi gõ dòng đầu tiên.** Dự án có hình gì, một byte đi qua những đâu, chương sách nào phục vụ dòng code nào. Đọc lại ở đầu mỗi phase. |
| `SPEC.md` | Thiết kế kỹ thuật từng thành phần. Mở khi bắt đầu một phase. |
| `SACH.md` | Bản đồ sách: chương nào, phase nào, cuốn nào bỏ. Mở hàng tuần. |
| `PROGRESS.md` | Checklist từng tuần + thanh tiến độ. Mở mỗi buổi học. |
| `NHATKY.md` | Nhật ký chỗ bí. Tự tạo khi cần. |

**Bản web** (mở bằng Chrome/Edge, không mở trong editor):

| Trang | Nội dung |
|---|---|
| **`so-do.html`** | **17 sơ đồ:** 7 kiến trúc (triển khai, thành phần, bên trong từng mảnh) + 10 tuần tự (PUT, GET, recovery, split, epoll, Raft, bầu leader, khởi động container, apply, tự lành). Mở khi ngồi xuống viết code. |
| `kien-truc.html` | Bản web của `KIEN-TRUC.md` — 11 nấc tiến hoá, sơ đồ vẽ lại bằng SVG. |
| `lo-trinh.html` | Tracker tiến độ bấm tick được, lưu trong trình duyệt. |

**Code không nằm ở đây.** Tạo repo riêng: `D:/Code/ouroboros/`, git init, push lên GitHub công khai từ ngày đầu.
