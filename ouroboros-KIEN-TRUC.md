# Kiến trúc Ouroboros — bản chi tiết

> Đọc file này **trước** khi gõ dòng code đầu tiên. Rồi đọc lại ở đầu mỗi phase.
> Nó trả lời ba câu: dự án có hình gì · một byte đi qua những đâu · chương sách đó phục vụ dòng code nào.

**Viết cho:** người đã học qua kiến trúc máy tính, mạng máy tính, hệ điều hành ở mức khái niệm —
nhưng chưa build gì ở tầng hệ thống, chưa rành Linux, C mới dùng để code thuật toán, chưa từng viết Go.

---

## Mục lục

- [Phần 0 — Vì sao bạn chưa biết bắt đầu từ đâu](#phần-0)
- [Phần I — Bức tranh lớn](#phần-i)
- [Phần II — Đi theo một byte](#phần-ii) ← **phần quan trọng nhất**
- [Phần III — Giải phẫu từng thành phần](#phần-iii)
- [Phần IV — Mỗi chương sách phục vụ dòng code nào](#phần-iv)
- [Phần V — Những thứ bạn chưa biết mà bắt buộc phải biết](#phần-v)
- [Phần VI — Dòng code đầu tiên](#phần-vi)

---

<a name="phần-0"></a>
# Phần 0 — Vì sao bạn chưa biết bắt đầu từ đâu

Cảm giác của bạn đúng, và nó không phải do bạn kém. Nó do hai hiểu lầm mà gần như ai cũng mắc.

## Hiểu lầm 1: "Phải hiểu hết rồi mới code được"

Sai. Ngược lại mới đúng: **bạn hiểu được là nhờ đã code.**

Bạn có thể đọc chương B-Tree của Petrov ba lần và vẫn mơ hồ. Nhưng chỉ cần
tự viết hàm `split()` một lần — chỉ một lần thôi — là hiểu mãi mãi. Vì lúc viết,
bạn buộc phải trả lời những câu sách không nói: node đầy thì đẩy key nào lên cha?
Con trỏ trỏ đi đâu? Nếu cha cũng đầy thì sao?

Sách cho bạn **bản đồ**. Code cho bạn **ký ức cơ bắp**. Không thay thế nhau được.

## Hiểu lầm 2: "Phải xây theo bản vẽ kiến trúc"

Cũng sai, và đây mới là thứ đang chặn bạn.

Sơ đồ kiến trúc bạn sắp thấy ở Phần I là **đích đến sau 20 tháng**. Không ai
ngồi xuống và gõ ra kiến trúc đó. Nếu bạn cố bắt đầu từ nó, bạn sẽ tê liệt —
đúng như bây giờ.

Cách thật sự người ta xây phần mềm hệ thống:

> **Bộ xương biết đi (walking skeleton).**
> Viết thứ nhỏ nhất mà *chạy được từ đầu đến cuối*. Rồi phình nó ra từng chút một.
> Mỗi bước phình, hệ thống vẫn phải chạy.

Cụ thể với Ouroboros: tuần thứ 6, bạn sẽ viết một cơ sở dữ liệu **60 dòng C**.
Nó xấu, nó chậm, nó mất dữ liệu khi cúp điện. **Nhưng nó chạy.** Bạn `put` được,
`get` được.

Rồi tuần 7 bạn hỏi: *"sao đọc chậm thế?"* → thêm chỉ mục trong RAM.
Tuần 8: *"sao file phình mãi?"* → thêm nén gộp.
Tuần 9: *"sao cúp điện là mất?"* → thêm WAL.

**Mỗi lần thêm, bạn giải một bài toán bạn tự cảm nhận được**, chứ không phải
bài toán sách bảo có. Đó là lý do bạn sẽ nhớ.

Sau 9 tuần, thứ 60 dòng đó trở thành 6000 dòng và có hình dạng đúng như sơ đồ
kiến trúc. Nhưng bạn đến đó bằng cách bò, không phải bằng cách nhảy.

## Vậy sơ đồ kiến trúc để làm gì?

Để bạn biết **mình đang bò về hướng nào**, và để khi thêm một mảnh, bạn biết nó
gắn vào đâu. Chỉ vậy thôi. Nó là la bàn, không phải bản vẽ thi công.

---

<a name="phần-i"></a>
# Phần I — Bức tranh lớn

## Mọi đám mây đều trả lời 5 câu hỏi

Bóc AWS, Google Cloud, Azure ra thì phần lõi đều đang trả lời đúng 5 câu:

| # | Câu hỏi | Thành phần của bạn |
|---|---|---|
| 1 | Cất dữ liệu xuống đĩa sao cho **mất điện không mất dữ liệu**? | `ouro-store` |
| 2 | Cho **máy khác ở xa** dùng được dữ liệu đó? | `ouro-net` |
| 3 | **Nhiều máy** cùng giữ dữ liệu, máy chết vẫn đúng? | `ouro-dist` |
| 4 | **Nhốt phần mềm vào hộp** để chạy cô lập trên máy chung? | `ouro-run` |
| 5 | **Tự động** quyết định hộp nào chạy ở máy nào? | `ouro-ctl` |

Cộng thêm một câu thứ sáu chạy xuyên suốt: *làm sao nhìn thấy cả đống đó đang làm gì?* → `ouro-scope`.

## Sơ đồ tổng thể

```
                        NGƯỜI DÙNG
                            │
                            │  ouroctl apply -f cluster.yaml
                            ▼
╔═══════════════════════════════════════════════════════════════════╗
║  ouro-ctl                                           [Go · Phase 7] ║
║  ┌─────────────┐  ┌────────────┐  ┌──────────────┐               ║
║  │ API server  │─▶│ Scheduler  │─▶│ Controller   │               ║
║  │ nhận YAML   │  │ chọn máy   │  │ vòng lặp     │               ║
║  │ validate    │  │ lọc+chấm   │  │ reconcile    │               ║
║  └──────┬──────┘  └────────────┘  └──────┬───────┘               ║
║         │ lưu "trạng thái mong muốn"      │ ra lệnh               ║
╚═════════╪═══════════════════════════════╪═════════════════════════╝
          │                                │
          │        ┌───────────────────────┘
          │        │
          │        ▼   (trên MỖI máy trong cụm)
          │   ╔══════════════════════════════════════════════════╗
          │   ║  node-agent  ──▶  ouro-run       [Go+C·Phase 6]  ║
          │   ║                   ┌──────────────────────────┐   ║
          │   ║                   │ namespaces  (cô lập)     │   ║
          │   ║                   │ cgroups     (giới hạn)   │   ║
          │   ║                   │ overlayfs   (hệ tệp)     │   ║
          │   ║                   │ veth/bridge (mạng)       │   ║
          │   ║                   │ seccomp     (bảo mật)    │   ║
          │   ║                   └───────────┬──────────────┘   ║
          │   ╚═══════════════════════════════╪══════════════════╝
          │                                   │ chạy bên trong
          │                                   ▼
          │   ╔══════════════════════════════════════════════════╗
          │   ║  ouro-dist                       [Go · Phase 5]  ║
          │   ║  ┌──────────┐ ┌──────────┐ ┌─────────────────┐  ║
          │   ║  │  Raft    │ │  Gossip  │ │  Replication    │  ║
          │   ║  │ đồng     │ │ ai còn   │ │ bọc store sau   │  ║
          │   ║  │ thuận    │ │ sống?    │ │ Raft log        │  ║
          │   ║  └──────────┘ └──────────┘ └────────┬────────┘  ║
          │   ╚════════════════════════════════════╪════════════╝
          │                                        │
          │   ╔════════════════════════════════════╪════════════╗
          │   ║  ouro-net              [C Phase 3 → Go Phase 4] ║
          │   ║  ┌───────────┐ ┌────────────┐ ┌──────────────┐ ║
          │   ║  │ epoll     │ │ wire       │ │ thread pool  │ ║
          │   ║  │ event loop│ │ protocol   │ │              │ ║
          │   ║  └───────────┘ └────────────┘ └──────┬───────┘ ║
          │   ╚═══════════════════════════════════════╪═════════╝
          │                                           │
          │   ╔═══════════════════════════════════════╪═════════╗
          │   ║  ouro-store                     [C · Phase 1-2]  ║
          │   ║  ┌─────────┐ ┌─────────┐ ┌─────┐ ┌───────────┐ ║
          │   ║  │ B-Tree  │ │ LSM     │ │ WAL │ │ bufferpool│ ║
          │   ║  └─────────┘ └─────────┘ └─────┘ └───────────┘ ║
          │   ║           ▼ ▼ ▼  hệ tệp Linux  ▼ ▼ ▼           ║
          │   ╚═══════════════════════════════════════════════════╝
          │                       │
          └───────────────────────┘
              🐍 ouro-ctl lưu state của chính nó
                 vào cluster ouro-store phía dưới
```

Mũi tên cuối cùng, cái vòng quay ngược lên, chính là **Ouroboros** — con rắn cắn đuôi.

## Luật vàng của kiến trúc

> **Mỗi lớp chỉ được biết lớp ngay dưới nó. Không được nhảy cóc.**

`ouro-ctl` không biết B-Tree tồn tại. Nó chỉ biết gọi `Put(key, value)`.
`ouro-store` không biết mạng tồn tại. Nó chỉ biết ghi file.

Vì sao luật này quan trọng đến thế: **nó cho phép bạn xây từng lớp một và test
được từng lớp một.** Nếu `ouro-store` phải biết về Raft, bạn không thể test nó
một mình, và Phase 1 sẽ không bao giờ kết thúc.

Đây cũng là lý do thứ tự phase là như vậy: từ dưới lên. Mỗi phase xây một tầng
trên nền tầng đã vững.

## Sáu thành phần, mỗi cái một câu

| Thành phần | Một câu | Dòng code ước tính |
|---|---|---|
| `ouro-store` | Biến RAM tạm bợ thành đĩa bền vững, không mất khi cúp điện | ~8.000 C |
| `ouro-net` | Cho máy khác nói chuyện được với store, 10.000 máy cùng lúc | ~2.500 C + ~1.500 Go |
| `ouro-dist` | Ba bản sao của store cùng đồng ý một sự thật, dù máy chết | ~6.000 Go |
| `ouro-run` | Nhốt một tiến trình vào hộp: không thấy, không đụng, không ăn quá phần | ~5.000 Go+C |
| `ouro-ctl` | Đọc ý muốn của người dùng, tự làm thực tế khớp ý muốn đó | ~8.000 Go |
| `ouro-scope` | Đo, đếm, vẽ — để không bao giờ tối ưu mù | ~2.000 |

---

<a name="phần-ii"></a>
# Phần II — Đi theo một byte

Đây là phần cho bạn **cái nhìn tổng quan thống nhất** mà bạn đang thiếu.

Ta sẽ đi theo đúng **một thao tác**:

```
PUT  user:1  =  "Quan"
```

từ lúc bạn gõ, tới lúc nó nằm yên trên mặt đĩa. Mỗi tầng dưới đây là một nấc
tiến hóa. **Mỗi nấc bạn thật sự sẽ gõ, theo đúng thứ tự này.**

Chú ý cách mỗi nấc sinh ra từ một câu hỏi bực bội về nấc trước. Đó là toàn bộ
bí quyết của việc học qua dự án.

---

## Nấc 0 — Một file, 60 dòng · *Tuần 6*

**Câu hỏi:** Cơ sở dữ liệu ít nhất phải làm được gì?
**Trả lời:** Ghi được, đọc lại được. Hết.

```c
// PUT: nối vào cuối file. Không bao giờ sửa thứ đã ghi.
void put(const char *key, const char *val) {
    FILE *f = fopen("data.db", "a");        // "a" = append
    fprintf(f, "%s\t%s\n", key, val);
    fclose(f);
}

// GET: quét cả file từ đầu, nhớ giá trị CUỐI CÙNG khớp key.
int get(const char *key, char *out) {
    FILE *f = fopen("data.db", "r");
    if (!f) return -1;
    char line[1024];
    int found = -1;
    while (fgets(line, sizeof line, f)) {
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab = '\0';                         // cắt đôi: trước tab là key
        if (strcmp(line, key) == 0) {
            char *v = tab + 1;
            v[strcspn(v, "\n")] = '\0';
            strcpy(out, v);
            found = 0;                       // bản ghi sau đè bản ghi trước
        }
    }
    fclose(f);
    return found;
}
```

**Đó là một cơ sở dữ liệu thật.** Không đùa. Nó có hai tính chất mà các engine
thật cũng có:

- **Append-only** — chỉ nối thêm, không bao giờ sửa chỗ cũ. Ghi tuần tự nhanh hơn ghi ngẫu nhiên rất nhiều, trên cả HDD lẫn SSD.
- **Last write wins** — muốn sửa thì ghi đè bản mới ở cuối. Muốn xoá thì ghi một "bia mộ" (tombstone).

Cả LSM Tree của RocksDB lẫn WAL của PostgreSQL đều đứng trên đúng hai ý này.

> 🎯 **Đây là dòng code đầu tiên của dự án.** Không phải kiến trúc. Không phải
> thiết kế. Là 60 dòng này, và nó chạy được ngay hôm bạn gõ xong.

**Nó tệ ở đâu:** đọc là O(n) — 1 triệu bản ghi thì mỗi lần `get` phải quét 1 triệu dòng.

---

## Nấc 1 — Chỉ mục trong RAM · *Tuần 6–7*

**Câu hỏi:** Đọc chậm quá, làm sao nhanh?
**Ý tưởng:** Giữ trong RAM một bảng băm `key → vị trí byte trong file`.
`get` thành: tra bảng băm → `lseek` tới đúng chỗ → đọc một dòng.

```
RAM:  { "user:1" → byte 0,  "user:2" → byte 14, ... }
                                    │
ĐĨA:  ┌──────────────┬──────────────┬──────────────┐
      │user:1\tQuan\n│user:2\tNam\n │user:1\tHai\n │
      └──────────────┴──────────────┴──────────────┘
       byte 0         byte 14        byte 27
                                     ↑ ghi đè: bảng băm trỏ tới đây
```

**Bạn vừa tự phát minh ra Bitcask** — engine lưu trữ thật của Riak. Nghiêm túc.

**Nó tệ ở đâu:** toàn bộ key phải vừa trong RAM. Và file phình vô hạn vì bản cũ
không bao giờ bị xoá.

📖 *Kiến thức cần:* TLPI Ch4–5 (`open`, `read`, `write`, `lseek`), CSAPP Ch10.
Đây là lúc bạn học **file descriptor là gì** — xem Phần V.

---

## Nấc 2 — Trang có cấu trúc · *Tuần 6–7*

**Câu hỏi:** File dạng dòng text thì lôi thôi. Muốn nhảy tới bản ghi thứ 500 thì sao?
**Ý tưởng:** Chia file thành **trang (page)** cố định — thường 4KB — mỗi trang tự mô tả nội dung của nó.

```
Một trang 4KB (slotted page):

 0        16                                         4096
 ┌────────┬──────┬──────┬─────────┬────────┬─────────┐
 │ HEADER │slot0 │slot1 │  trống  │ data1  │  data0  │
 │ n=2    │→3800 │→3900 │ ←────→  │        │         │
 │checksum│      │      │         │        │         │
 └────────┴──────┴──────┴─────────┴────────┴─────────┘
            │      │                  ▲         ▲
            └──────┼──────────────────┼─────────┘
                   └──────────────────┘
       slot mọc từ trái sang · data mọc từ phải sang
       gặp nhau ở giữa = trang đầy
```

Vì sao 4KB: vì đó là kích thước **page** của kernel Linux và thường là kích
thước khối của hệ tệp. Ghi đúng một page = kernel làm đúng một thao tác. Ghi
4KB+1 byte = kernel phải đụng hai page. Đây là ví dụ đầu tiên về việc **kiến
trúc máy tính rò rỉ lên tận thiết kế phần mềm** — thứ CSAPP dạy suốt.

`checksum` trong header để phát hiện **torn page**: máy chết giữa lúc ghi, nửa
trang mới nửa trang cũ. Không có checksum thì bạn đọc phải rác mà không biết.

📖 *Kiến thức cần:* DB Internals Ch3 (File Formats), CSAPP Ch6 (vì sao 4KB).

---

## Nấc 3 — B-Tree · *Tuần 8–10*

**Câu hỏi:** Bảng băm trong RAM không chứa nổi 1 tỷ key. Và tôi muốn hỏi
*"cho tôi mọi key từ `user:100` đến `user:200`"* — bảng băm chịu.
**Ý tưởng:** Cây giữ key **có thứ tự**, và cây nằm **trên đĩa**, không trong RAM.

```
                    ┌─────────────────┐
         gốc        │  [ user:500 ]   │        ← 1 page
                    └────┬───────┬────┘
              ┌──────────┘       └──────────┐
              ▼                             ▼
     ┌────────────────┐            ┌────────────────┐
nhánh│ [user:200 |    │            │ [user:800 |    │   ← mỗi cái 1 page
     │  user:350]     │            │  user:900]     │
     └──┬────┬────┬───┘            └──┬────┬────┬───┘
        ▼    ▼    ▼                   ▼    ▼    ▼
      ┌───┐┌───┐┌───┐               ┌───┐┌───┐┌───┐
   lá │dữ ││dữ ││dữ │               │dữ ││dữ ││dữ │      ← dữ liệu thật ở lá
      │liệu││liệu││liệu│             │liệu││liệu││liệu│
      └───┘└───┘└───┘               └───┘└───┘└───┘
```

Điểm mấu chốt mà sách hay nói lướt: **mỗi node là đúng một page 4KB.**

Vì sao? Vì đọc đĩa tính theo page. Một page 4KB chứa được ~200 key. Cây 3 tầng
chứa 200³ = **8 triệu** key và tìm bất kỳ key nào chỉ tốn **3 lần đọc đĩa**.
Cây 4 tầng: 1,6 tỷ key, 4 lần đọc đĩa.

Đó là toàn bộ lý do B-Tree thống trị cơ sở dữ liệu suốt 50 năm. Nó tối ưu cho
thứ đắt nhất: **số lần chạm đĩa**, không phải số phép so sánh.

**Phần khó nhất bạn sẽ vật lộn:** `split`. Node đầy, thêm key nữa thì sao?
Cắt đôi, đẩy key giữa lên cha. Nhưng cha cũng đầy thì sao? Cắt cha, đẩy lên ông.
Tới gốc mà gốc đầy? Tạo gốc mới — **cây cao thêm một tầng, và đó là cách duy
nhất B-Tree cao lên.**

Viết được `split` và `merge` đúng là lúc bạn thật sự hiểu B-Tree. Không phải lúc đọc xong chương.

📖 *Kiến thức cần:* DB Internals Ch2, Ch4, Ch6.

---

## Nấc 4 — Buffer pool · *Tuần 11*

**Câu hỏi:** Cây nằm trên đĩa, nhưng mỗi lần tra lại đọc đĩa thì chậm chết.
Mà giữ cả cây trong RAM thì không đủ chỗ.
**Ý tưởng:** Giữ **những page nóng nhất** trong RAM. Page nguội thì đá ra.

```
       RAM (có hạn, ví dụ 256MB)
       ┌────────────────────────────────┐
       │  BUFFER POOL                    │
       │  ┌────┐┌────┐┌────┐┌────┐      │
       │  │pg 7││pg 2││pg 9││pg 4│      │   mỗi ô = 1 page 4KB
       │  │pin1││pin0││pin0││pin3│      │   pin = đang có ai dùng?
       │  │ ★  ││    ││ ★  ││    │      │   ★ = bẩn, cần ghi xuống
       │  └────┘└────┘└────┘└────┘      │
       └──────────┬─────────────────────┘
                  │ hết chỗ → chọn nạn nhân (CLOCK)
                  │ nếu bẩn thì ghi xuống trước
                  ▼
       ĐĨA ┌──────────────────────────────┐
           │ page 0 1 2 3 4 5 6 7 8 9 ... │
           └──────────────────────────────┘
```

Bạn có nhận ra không — **đây chính xác là bài toán page replacement trong hệ
điều hành** mà bạn đã học ở môn OS. FIFO, LRU, CLOCK. Cùng bài toán, cùng thuật
toán, chỉ khác là lần này **bạn là kernel**.

Đó là lý do OSTEP Ch21–22 nằm trong tuần này. Bạn đã học khái niệm rồi; giờ bạn
cài nó, và nó sẽ dính vào đầu theo cách bài giảng không làm được.

`pin` là thứ sách hay bỏ qua: một page đang được luồng khác đọc thì **không
được đá ra**. Đây là mầm mống của Phase 2 (đa luồng).

📖 *Kiến thức cần:* OSTEP Ch21–22, PostgreSQL 14 Internals Part II.
🔍 *Đối chiếu:* đọc Rogov xem PostgreSQL làm y hệt thứ bạn vừa viết, ở quy mô thật.

---

## Nấc 5 — WAL: sống sót qua cúp điện · *Tuần 12–13*

Đây là **nấc quan trọng nhất của cả Phase 1.** Đọc kỹ.

**Câu hỏi:** Máy mất điện giữa lúc `split` một node B-Tree. Nửa cây đã ghi, nửa chưa.
Bật lại máy thì cây hỏng. Làm sao?

**Trước hết phải biết một sự thật phũ phàng:** khi bạn gọi `write()`, dữ liệu
**không** xuống đĩa. Nó nằm trong RAM của kernel (page cache). `write()` trả về
"thành công" khi dữ liệu mới chỉ nằm trong RAM. Kernel sẽ ghi xuống đĩa sau,
lúc nào nó thích — có thể 30 giây sau.

Cúp điện trong 30 giây đó: **mất sạch, mà chương trình của bạn tưởng đã ghi xong.**

Muốn chắc chắn xuống đĩa phải gọi `fsync()`. Nhưng `fsync()` tốn 0,1–10 mili
giây — chậm hơn `write()` khoảng **mười nghìn lần**.

**Ý tưởng WAL:** đừng `fsync` cả cây. Chỉ `fsync` một dòng nhật ký nhỏ, ghi
tuần tự, *trước khi* đụng vào cây.

```
Trình tự bắt buộc của một lần PUT:

  1. Ghi vào WAL:  "LSN 42: đặt user:1 = Quan"   ← nối vào cuối, tuần tự
  2. fsync(WAL)                                   ← ĐẮT, nhưng chỉ 1 lần, 1 file
  3. ✓ Giờ mới báo cho client "xong rồi"
  4. Sửa B-Tree trong buffer pool (chỉ trong RAM)
  5. Lúc nào rảnh thì ghi page bẩn xuống đĩa

Cúp điện ở bước 4 hay 5?  Không sao.
Bật máy lại → đọc WAL từ checkpoint gần nhất → làm lại (redo) mọi thao tác.
```

Quy tắc bất di bất dịch: **nhật ký phải xuống đĩa trước dữ liệu.**
Write-Ahead Logging — "ghi trước" là ghi trước dữ liệu.

**Group commit:** `fsync` đắt, nên nếu 100 client cùng ghi trong 1ms, gom cả 100
vào một lần `fsync`. Trả giá một lần, phục vụ 100 người. Đây là kỹ thuật cho
PostgreSQL và MySQL đạt hàng chục nghìn giao dịch mỗi giây trên phần cứng thường.

> 🎯 Test tra tấn của Phase 1 — `kill -9` 1000 lần ngẫu nhiên — là để kiểm chứng
> đúng cơ chế này. Không qua được test đó thì `ouro-store` chưa phải cơ sở dữ liệu,
> nó chỉ là một cái file.

📖 *Kiến thức cần:* DB Internals Ch5, **OSTEP Ch42 (Crash Consistency)** — chương
quan trọng nhất phase này, PostgreSQL 14 Internals Part II.

---

## Nấc 6 — Nhiều luồng · *Phase 2, tuần 15–21*

**Câu hỏi:** Một lúc chỉ phục vụ một người thì phí cả CPU 8 nhân.
**Ý tưởng:** Nhiều luồng cùng dùng chung buffer pool và B-Tree.

Và lập tức bạn rơi vào địa ngục:

| Vấn đề | Hiện tượng |
|---|---|
| Hai luồng cùng `split` một node | Cây hỏng, mất dữ liệu |
| Một luồng đá page mà luồng khác đang đọc | Đọc phải rác |
| Hai luồng khoá hai page theo thứ tự ngược nhau | **Deadlock** — treo vĩnh viễn |

Đây là lúc concurrency ngừng là lý thuyết. Bạn sẽ gặp một con bug xuất hiện
1 lần trong 10.000 lần chạy, và bạn sẽ học được rằng **`printf` không giúp được gì** —
phải dùng ThreadSanitizer.

Kỹ thuật bạn sẽ học: **latch crabbing** (bò như cua trên cây — khoá con rồi mới
thả cha), lock-free reader, đọc-ghi tách biệt.

📖 *Kiến thức cần:* OSTEP Ch26–33 (toàn bộ concurrency), CSAPP Ch12, TLPI Ch29–33.

---

## Nấc 7 — Qua mạng · *Phase 3, tuần 24–32*

**Câu hỏi:** Giờ cho máy khác dùng được `ouro-store`.

Máy A gửi `PUT user:1 = Quan` qua dây mạng tới máy B. Nhưng TCP không gửi
"tin nhắn" — nó gửi **một dòng byte không có ranh giới**. Bạn gửi 3 tin nhắn,
bên kia có thể nhận được thành 1 cục, hoặc 5 mảnh.

Nên phải tự đóng gói:

```
┌────────┬─────┬────────┬──────────┬───────┬───────────┐
│ magic  │ ver │ opcode │  req_id  │  len  │  payload  │
│ 4 byte │  1  │   1    │  8 byte  │ 4 byte│  len byte │
└────────┴─────┴────────┴──────────┴───────┴───────────┘
  "OURO"        PUT=1     để ghép     độ dài   dữ liệu
                          hồi đáp     phần sau
```

Đọc: đọc đúng 18 byte header → biết `len` → đọc tiếp đúng `len` byte. Luôn luôn.

**Rồi tới bài toán thật sự của Phase 3:** 10.000 client cùng kết nối.

| Cách làm | Vấn đề |
|---|---|
| Mỗi client một luồng | Mỗi luồng ngốn ~8MB stack. 10.000 luồng = 80GB. Chết. |
| `select()` | Mỗi vòng lặp phải quét cả 10.000 socket để hỏi "có gì mới không?" — O(n). |
| **`epoll`** | Kernel giữ sẵn danh sách, **chỉ trả về những socket đã sẵn sàng** — O(1). |

```
        ┌─────────────────────────────────────┐
        │   MỘT luồng chạy vòng lặp sự kiện   │
        │                                     │
        │   ready = epoll_wait(...)           │  ← ngủ cho tới khi có việc
        │   với mỗi fd trong ready:           │
        │       đọc / xử lý / ghi             │
        └──────────────┬──────────────────────┘
                       │ kernel theo dõi giúp
        ┌──────────────┴──────────────────────┐
        │  10.000 socket, chỉ 12 cái có dữ liệu│
        │  → epoll_wait trả về đúng 12 cái     │
        └─────────────────────────────────────┘
```

Bạn sẽ viết **bốn bản** server và đo cả bốn: tuần tự → fork mỗi client → thread
pool → epoll. Cố ý làm sai trước, để thấy nó sai bằng số đo của chính mình.

📖 *Kiến thức cần:* **UNP Ch6 và Ch30** (Ch30 so sánh 9 kiến trúc server kèm số
đo thật — chương đọc kỹ nhất cả lộ trình), TLPI Ch63, CSAPP Ch11.

---

## Nấc 8 — Viết lại bằng Go · *Phase 4, tuần 33–38*

Bạn nói bạn chưa từng viết Go và không biết runtime là gì. Đây là chỗ giải thích.

**Runtime là gì.** Khi bạn viết C, `main()` gần như là thứ đầu tiên chạy, và
chương trình của bạn nói chuyện thẳng với hệ điều hành. Khi bạn viết Go, trước
khi `main()` của bạn chạy, có **một bộ máy viết sẵn khởi động trước** — đó là
runtime. Nó gồm hai thứ chính: một bộ thu gom rác (GC) và **một bộ lập lịch**.

**Vì sao Phase 4 phải nằm SAU Phase 3.** Vì bạn vừa tự tay viết epoll bằng C.
Giờ trong Go bạn viết:

```go
conn, _ := listener.Accept()
go handleConn(conn)              // một dòng
```

Hai dòng đó xử lý được 100.000 kết nối. Trông như phép màu — trừ khi bạn vừa
viết epoll bằng tay xong, lúc đó bạn biết chính xác Go đang giấu gì:

| Bạn viết trong Go | Runtime thật sự làm gì |
|---|---|
| `go f()` | Tạo goroutine — **không** phải OS thread. ~2KB stack, co giãn được |
| `conn.Read(buf)` | Trông như blocking, nhưng runtime đăng ký fd vào **epoll** rồi cho goroutine khác chạy |
| 100.000 goroutine | Chạy trên ~8 OS thread. Runtime tự xoay vòng |

Bộ lập lịch của Go làm **đúng công việc** mà OSTEP Ch7–10 mô tả cho kernel —
nhưng ở userspace. Đổi goroutine tốn ~100 nano giây; đổi OS thread tốn ~1–2 micro
giây, **chậm hơn 10–20 lần**.

Đó là toàn bộ lý do Go thống trị hạ tầng đám mây: Docker, Kubernetes, etcd,
Prometheus đều viết bằng Go. Nó cho bạn hiệu năng gần C ở I/O mạng với code
đơn giản như viết blocking.

**Bạn giữ cả hai bản** và lập bảng:

| | C | Go |
|---|---|---|
| Số dòng | ~2.500 | ~1.500 |
| Throughput | ? | ? |
| p99 latency | ? | ? |
| RAM khi 10k kết nối | ? | ? |
| Giờ công để viết | ? | ? |

Bảng này là thứ bạn kể trong phỏng vấn. Người phỏng vấn nghe xong sẽ biết bạn
không học vẹt.

📖 *Kiến thức cần:* Learning Go Ch1–13, Mastering Go (chương Concurrency + runtime).

---

## Nấc 9 — Ba máy, Raft · *Phase 5, tuần 41–51*

**Câu hỏi:** Một máy chết là mất hết. Cần 3 máy cùng giữ dữ liệu.
**Vấn đề:** Ba máy làm sao **đồng ý** với nhau thứ tự các thao tác, khi mạng có
thể chậm, gói tin có thể mất, và máy có thể chết giữa chừng?

Đó là bài toán **đồng thuận (consensus)**, và Raft là lời giải.

```
          ┌──────────────┐
client ──▶│  Node A      │  LEADER
          │  (leader)    │
          └──┬────────┬──┘
   ①ghi vào  │        │  ②gửi bản sao log đi
   log của mình        │
             ▼        ▼
      ┌──────────┐ ┌──────────┐
      │ Node B   │ │ Node C   │  FOLLOWER
      │(follower)│ │(follower)│
      └────┬─────┘ └────┬─────┘
           │ ③"đã ghi"  │
           └──────┬─────┘
                  ▼
        ④ ĐA SỐ (2/3) đã ghi → leader "commit"
        ⑤ Lúc này mới báo client: xong
```

Chữ **đa số** là chìa khoá. 2 trên 3 là đủ. Nghĩa là một máy chết, hệ thống vẫn
chạy. Và vì mọi đa số đều phải giao nhau ở ít nhất một node, không thể có hai
leader cùng tin mình đúng.

Ba phần của Raft bạn sẽ viết:

1. **Leader election** — leader im lặng quá lâu, follower tự ứng cử, ai được đa số phiếu thì thắng
2. **Log replication** — leader đẩy log sang follower, đảm bảo mọi log giống hệt nhau
3. **Safety** — không bao giờ commit thứ có thể bị mất

**Chú ý cấu trúc:** `ouro-dist` **không viết lại** `ouro-store`. Nó **bọc** ra
ngoài. Mọi thao tác ghi đi qua Raft log trước, rồi mới được "áp dụng" vào
`ouro-store` bên dưới. `ouro-store` hoàn toàn không biết mình đang được nhân bản.

Đó là luật vàng ở Phần I đang phát huy tác dụng.

> ⚠️ Cuốn *Distributed Services with Go* dựng gần đúng thứ này. Gõ theo nó ở
> `scratch/` để học, rồi **đóng sách lại** và viết `ouro-dist` từ đầu. Copy code
> vào dự án = Phase 5 mất sạch ý nghĩa.

📖 *Kiến thức cần:* Raft paper, DB Internals Ch8–14, DDIA Ch5–9.

---

## Nấc 10 — Nhốt vào hộp · *Phase 6, tuần 52–62*

**Câu hỏi:** Ba bản `ouro-store` chạy chung một máy thì đạp lên chân nhau: cùng
tên file, cùng cổng mạng, một thằng ăn hết RAM.
**Ý tưởng:** Cho mỗi cái một "thế giới riêng".

Và đây là chỗ bạn sẽ ngạc nhiên nhất trong cả dự án:

> **Container không phải máy ảo. Nó là một tiến trình Linux bình thường —
> chỉ khác vài con trỏ trong struct của kernel.**

Kernel giữ cho mỗi tiến trình một struct `task_struct`. Trong đó có con trỏ tới
bảng PID, tới bảng mount, tới ngăn xếp mạng. **Namespace chỉ là: cho tiến trình
này trỏ tới một bảng khác.**

```
Tiến trình thường:          Tiến trình trong container:
 task_struct                 task_struct
  ├─ pid_ns  ──▶ bảng PID     ├─ pid_ns  ──▶ bảng PID RIÊNG (nó là PID 1!)
  ├─ mnt_ns  ──▶ / của host   ├─ mnt_ns  ──▶ / RIÊNG (overlayfs)
  ├─ net_ns  ──▶ eth0 thật    ├─ net_ns  ──▶ card mạng ẢO (veth)
  └─ uts_ns  ──▶ hostname     └─ uts_ns  ──▶ hostname RIÊNG
```

Sáu namespace bạn sẽ dùng: PID, MNT, NET, UTS, IPC, USER.
Gọi bằng `clone()` hoặc `unshare()` với cờ tương ứng. Thế thôi.

**Cgroups còn đơn giản hơn nữa** — nó là một hệ thống tệp. Giới hạn RAM 256MB:

```bash
mkdir /sys/fs/cgroup/ouro-1
echo 268435456 > /sys/fs/cgroup/ouro-1/memory.max
echo $PID     > /sys/fs/cgroup/ouro-1/cgroup.procs
```

Xong. Kernel tự lo. Toàn bộ "resource limit" của Docker là ghi số vào file.

**Overlayfs** cho image nhiều lớp: chồng nhiều thư mục chỉ-đọc lên nhau, thêm
một lớp ghi-được ở trên cùng. Sửa file ở lớp dưới → kernel chép nó lên lớp trên
rồi sửa (copy-on-write). Đó là lý do 50 container chạy cùng image chỉ tốn dung
lượng của một image.

**Mạng:** tạo cặp `veth` — như một sợi dây ảo hai đầu. Một đầu cắm vào namespace
mạng của container, đầu kia cắm vào bridge trên host. Thêm NAT để ra Internet.

📖 *Kiến thức cần:* Container Security Ch2–4, Ch6, Ch8, Ch10 · TLPI Ch38–39 ·
`man 7 namespaces`, `man 7 cgroups`.

---

## Nấc 11 — Quản đốc · *Phase 7, tuần 65–75*

**Câu hỏi:** Có 10 máy, cần chạy 30 container. Ai quyết định cái nào ở đâu?
Container chết thì ai bật lại?

**Ý tưởng — và đây là toàn bộ bí mật của Kubernetes:**

> Người dùng không ra lệnh *"chạy container ở máy 3"*.
> Người dùng khai báo *"tôi muốn luôn có 3 bản chạy"*.
> Hệ thống tự lo cho thực tế khớp với mong muốn.

```
                    ┌──────────────────────┐
                    │  VÒNG LẶP RECONCILE  │
                    │   (lặp mãi mãi)      │
                    └──────────┬───────────┘
                               │
     ┌─────────────────────────┼─────────────────────────┐
     ▼                         ▼                         ▼
┌─────────────┐        ┌──────────────┐        ┌─────────────────┐
│ MONG MUỐN   │        │  THỰC TẾ     │        │  KHÁC BIỆT?     │
│ replicas: 3 │  vs    │ đang chạy: 2 │  ───▶  │ thiếu 1         │
│ (đọc từ     │        │ (hỏi node    │        │ → bảo node nào  │
│  ouro-store)│        │  agent)      │        │   đó chạy thêm  │
└─────────────┘        └──────────────┘        └─────────────────┘
                               │
                               └──▶ ngủ 1 giây ──▶ lặp lại
```

Chỉ có thế. Toàn bộ Kubernetes là ý tưởng này lặp lại ở 30 chỗ khác nhau —
Deployment, ReplicaSet, Service, Ingress, mỗi cái một vòng reconcile.

Hiểu vòng lặp này là hiểu Kubernetes. Không phải thuộc lệnh `kubectl`.

**Và đây là chỗ con rắn cắn đuôi:** "mong muốn" lưu ở đâu? Ở `ouro-store` —
cụm 3 node có Raft từ Phase 5. Mà cụm đó lại đang chạy trong container do
`ouro-run` tạo, được chính `ouro-ctl` này đặt xuống.

Thật sự Kubernetes cũng vậy: nó lưu state vào **etcd**, mà etcd thường chạy như
một pod trong chính cụm đó. Bạn không làm trò lạ — bạn làm đúng thứ công nghiệp làm.

📖 *Kiến thức cần:* Kubernetes Up & Running Ch5–13, **Ch17 (Extending Kubernetes)**,
Cloud Native Go Ch4.

---

## Toàn cảnh 11 nấc

| Nấc | Thêm gì | Giải bài toán | Phase | Dòng cộng dồn |
|---|---|---|---|---|
| 0 | File append-only | Ghi/đọc được | 1 | 60 |
| 1 | Chỉ mục RAM | Đọc chậm | 1 | 200 |
| 2 | Page 4KB | Không có cấu trúc | 1 | 700 |
| 3 | B-Tree | Key không vừa RAM, cần quét dải | 1 | 2.500 |
| 4 | Buffer pool | RAM có hạn | 1 | 3.500 |
| 5 | WAL + recovery | **Cúp điện mất dữ liệu** | 1 | 5.000 |
| 6 | Đa luồng | Phí CPU | 2 | 8.000 |
| 7 | epoll + protocol | Máy khác không dùng được | 3 | 10.500 |
| 8 | Viết lại bằng Go | Học Go, so sánh | 4 | 12.000 |
| 9 | Raft | Một máy chết là mất hết | 5 | 18.000 |
| 10 | Namespace + cgroup | Các bản đạp chân nhau | 6 | 23.000 |
| 11 | Reconcile loop | Ai quyết định cái gì ở đâu | 7 | 31.000 |

**Không nấc nào nhảy quá xa nấc trước.** Đó là lý do lộ trình này khả thi dù
nhìn tổng thể thì khổng lồ.

---

<a name="phần-iii"></a>
# Phần III — Giải phẫu từng thành phần

## `ouro-store`

```
store/
├── include/store.h        API công khai — CHỈ 6 hàm
├── src/
│   ├── page.c             đọc/ghi/parse page 4KB, checksum
│   ├── btree.c            search, insert, split, delete, merge
│   ├── lsm.c              memtable, SSTable, compaction
│   ├── bufpool.c          page cache, pin/unpin, CLOCK
│   ├── wal.c              append log, LSN, group commit
│   ├── recovery.c         redo từ WAL, checkpoint
│   └── util.c             wrapper syscall (viết tuần 1!)
└── tests/
    ├── test_btree.c
    ├── test_recovery.c
    └── torture.sh         kill -9 ngẫu nhiên 1000 lần
```

**API công khai cố ý chỉ có 6 hàm.** Mọi độ phức tạp nằm bên trong, không lộ ra:

```c
store_t *store_open (const char *path, store_opts_t *opts);
int      store_put  (store_t *s, slice_t key, slice_t val);
int      store_get  (store_t *s, slice_t key, slice_t *out);
int      store_del  (store_t *s, slice_t key);
iter_t  *store_scan (store_t *s, slice_t from, slice_t to);
int      store_close(store_t *s);
```

**Phần khó nhất:** `btree.c` hàm `split()` và `recovery.c`. Dự trù mỗi cái một tuần
riêng, và dự trù sẽ viết sai vài lần.

## `ouro-net`

```
net/                        netgo/
├── proto.c  đóng/mở gói    ├── proto.go
├── server.c epoll loop     ├── server.go
├── conn.c   trạng thái     ├── conn.go
└── client.c               └── client.go
```

**Phần khó nhất:** đọc **một phần**. TCP có thể trả về 3 byte trong khi bạn cần
18. Phải nhớ trạng thái đọc dở của từng kết nối và quay lại sau. Đây là nguồn
bug số một của server tự viết.

## `ouro-dist`

```
dist/
├── raft/
│   ├── raft.go        vòng đời: follower → candidate → leader
│   ├── log.go         log có LSN, so khớp, cắt bớt
│   ├── election.go    timeout, bỏ phiếu
│   ├── replicate.go   AppendEntries
│   └── snapshot.go    nén log
├── gossip/            ai còn sống (kiểu SWIM)
├── fsm/               áp Raft log vào ouro-store
└── client/            tìm leader, retry, cân bằng đọc
```

**Phần khó nhất:** test. Bug phân tán chỉ hiện khi mạng lỗi đúng lúc. Phải viết
được bộ mô phỏng mạng biết làm chậm, làm mất, chia đôi mạng.

## `ouro-run`

```
run/
├── ns/         unshare/clone với 6 cờ namespace
├── cgroup/     ghi số vào /sys/fs/cgroup
├── image/      tải, giải nén layer, dựng overlayfs
├── network/    veth, bridge, NAT
├── security/   seccomp filter, drop capability
└── shim/       tiến trình cha giám sát container
```

**Phần khó nhất:** thứ tự. Phải `pivot_root` **sau** khi dựng mount namespace
nhưng **trước** khi `exec`. Sai thứ tự thì hoặc rò rỉ ra host, hoặc container
không chạy nổi. Đây đúng là câu hỏi phỏng vấn.

## `ouro-ctl`

```
ctl/
├── api/           REST/gRPC, validate, versioning
├── store/         dùng ouro-dist làm nơi lưu state 🐍
├── scheduler/     lọc node → chấm điểm → gán
├── controller/    vòng reconcile cho từng loại tài nguyên
├── agent/         chạy trên mỗi node, gọi ouro-run
└── cmd/ouroctl/   CLI
```

**Phần khó nhất:** làm cho vòng reconcile **idempotent** — chạy lại 100 lần phải
ra cùng kết quả như chạy 1 lần. Vì nó sẽ chạy lại, liên tục, mãi mãi.

---

<a name="phần-iv"></a>
# Phần IV — Mỗi chương sách phục vụ dòng code nào

Bảng này trả lời thẳng câu bạn hỏi: *chương đó nhằm mục đích gì, đóng góp thế nào.*

## Phase 0

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| CSAPP Ch2 (bits, integer) | Byte, bù hai, tràn số, endianness | Wire protocol (Phase 3), page header |
| CSAPP Ch2.4 (float) | Vì sao `0.1+0.2 != 0.3` | Tính toán benchmark, timestamp |
| CSAPP Ch6 (cache) | Vì sao truy cập tuần tự nhanh hơn ngẫu nhiên | **Toàn bộ thiết kế page và B-Tree** |
| CSAPP Ch5 (tối ưu) | Đo trước, tối ưu sau | `ouro-scope`, mọi benchmark |
| CSAPP Ch9.9 + OSTEP Ch17 | Cấp phát bộ nhớ hoạt động ra sao | Buffer pool (nấc 4) là **cùng bài toán** |
| TLPI Ch1–3 | Syscall là gì, `errno`, quy ước Linux | `util.c` — mọi dòng code sau này |

> Viết `myalloc` không phải bài tập vô ích. Buffer pool ở nấc 4 **chính là**
> allocator: cấp phát khối cố định, theo dõi cái nào rảnh, quyết định đá cái nào.
> Bạn làm bài tập đó để 5 tuần sau viết buffer pool trong hai ngày thay vì hai tuần.

## Phase 1

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| DB Internals Ch1–3 | Page layout, slotted page, file format | `page.c` |
| DB Internals Ch2, 4, 6 | B-Tree, split/merge, biến thể | `btree.c` |
| DB Internals Ch5 | WAL, recovery, checkpoint | `wal.c`, `recovery.c` |
| DB Internals Ch7 | LSM, SSTable, compaction | `lsm.c` |
| **OSTEP Ch42** | **Cúp điện thì hệ tệp làm gì** | Thiết kế crash-safety — nấc 5 |
| OSTEP Ch36–38 | Đĩa quay thế nào, vì sao seek đắt | Vì sao append-only thắng |
| OSTEP Ch21–22 | Page replacement: FIFO/LRU/CLOCK | `bufpool.c` |
| OSTEP Ch44 | SSD khác HDD chỗ nào | Chọn tham số cho engine |
| TLPI Ch4–5, 13 | `open/read/write/lseek`, đệm | `util.c`, mọi thao tác I/O |
| TLPI Ch49 | `mmap` | Quyết định mmap hay pread |
| TLPI Ch55 | File locking | Nhiều tiến trình cùng mở store |
| CSAPP Ch10 | I/O ở tầng Unix | Nền cho tất cả trên |
| PG14 Internals I–II | **Engine thật làm y hệt thế nào** | Đối chiếu sau khi tự viết |

## Phase 2

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| OSTEP Ch26–31 | Lock, condition variable, semaphore | Khoá B-Tree, bảo vệ buffer pool |
| **OSTEP Ch32** | **Các kiểu bug concurrency phổ biến** | Con bug 1/10.000 lần bạn sắp gặp |
| CSAPP Ch12 | Lập trình đồng thời thực hành | Thread pool |
| CSAPP Ch8 | Signal, tiến trình, ngắt luồng điều khiển | Graceful shutdown |
| TLPI Ch29–33 | pthread đầy đủ | Mọi dòng đa luồng |
| TLPI Ch20–22 | Signal chi tiết | Xử lý `SIGTERM` đúng cách |
| TLPI Ch37 | Daemon | Biến store thành dịch vụ nền |
| TLPI Ch43–54 | IPC | Giao tiếp giữa các tiến trình |

## Phase 3

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| **UNP Ch30** | **9 kiến trúc server, có số đo** | Chọn kiến trúc cho `ouro-net` |
| UNP Ch6 | select/poll/epoll | `server.c` vòng lặp sự kiện |
| UNP Ch3–5 | API socket nền | Mọi dòng mạng |
| UNP Ch16 | Non-blocking I/O | Bắt buộc cho epoll |
| TLPI Ch63 | epoll chi tiết, edge vs level trigger | `server.c` |
| TLPI Ch56–61 | Socket trên Linux | `conn.c` |
| TCP/IP Illust. Ch17–21 | TCP: cửa sổ, retransmit, Nagle | Vì sao p99 latency xấu |
| TCP/IP Illust. Ch1–3 | Gói tin đi qua các tầng | Đọc `tcpdump` |
| CSAPP Ch11 | Lập trình mạng cho người mới | Ôn nhẹ trước UNP |

## Phase 4

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| Learning Go Ch1–9 | Cú pháp, type, interface, lỗi | Toàn bộ code Go |
| Learning Go Ch10, 12 | Goroutine, channel, context | `server.go` |
| Learning Go Ch13 | Testing trong Go | Bộ test |
| Mastering Go — Concurrency | sync, race, mẫu hình | Thread pool bản Go |
| Mastering Go — runtime/GC | **Runtime làm gì cho bạn** | Hiểu vì sao Go nhanh ở I/O |
| Net Prog with Go Ch3–7 | net package | `server.go`, `conn.go` |

## Phase 5

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| Raft paper | Thuật toán đồng thuận | `raft/` — tài liệu chính |
| DB Internals Ch14 | Consensus, Paxos vs Raft | Hiểu vì sao Raft thắng |
| DB Internals Ch9 | Phát hiện máy chết | `gossip/` |
| DB Internals Ch10–11 | Bầu leader, nhân bản, nhất quán | `raft/`, `fsm/` |
| DB Internals Ch13 | Giao dịch phân tán, 2PC | Ghi nhiều key nguyên tử |
| **DDIA Ch8–9** | **Vì sao phân tán khó đến vậy** | Tư duy nền — đọc trước khi code |
| DDIA Ch5 | Các kiểu nhân bản | Chọn mô hình |
| DSwGo cả cuốn | Mẫu hình Go cho dịch vụ phân tán | Học ở `scratch/`, không copy |

## Phase 6

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| Container Security Ch4 | **Namespace hoạt động ra sao** | `ns/` |
| Container Security Ch3 | Cgroups v2 | `cgroup/` |
| Container Security Ch2 | Syscall, capability, quyền | `security/` |
| Container Security Ch6 | Định dạng image, layer | `image/` |
| Container Security Ch8 | seccomp, AppArmor | `security/` |
| Container Security Ch10 | Mạng container | `network/` |
| TLPI Ch38–39 | Viết chương trình đặc quyền an toàn | Toàn bộ `run/` — chạy bằng root |
| TLPI Ch14, 18 | Hệ tệp, mount, hard/symlink | `overlayfs`, `pivot_root` |
| `man 7 namespaces` | Tham chiếu chính xác | Tra hàng ngày |

## Phase 7

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| K8s U&R Ch5–7 | Pod, label, service discovery | Mô hình tài nguyên |
| K8s U&R Ch9–10 | ReplicaSet, Deployment | Vòng reconcile, rolling update |
| **K8s U&R Ch17** | **CRD, operator — cách mở rộng K8s** | Thiết kế API server |
| Cloud Native Go Ch4 | Circuit breaker, retry, timeout | Chống lỗi lan truyền |
| TLPI Ch62, 64 | Terminal, pty | `ouroctl exec -it` |
| TLPI Ch19 | inotify | Nạp lại config nóng |

## Phase 8

| Đọc | Để hiểu | Dùng ở |
|---|---|---|
| MLSys — Training | Huấn luyện phân tán vận hành thế nào | All-reduce, checkpoint |
| MLSys — AI Acceleration | GPU/TPU khác CPU chỗ nào | Device plugin |
| MLSys — Efficient AI | Batching, lượng tử hoá, độ trễ | Inference server |
| MLSys — ML Operations | Vòng đời hệ ML trong sản xuất | Thiết kế tổng thể |
| MLSys — Benchmarking | Đo hệ ML thế nào cho đúng | `ouro-scope` mở rộng |

---

<a name="phần-v"></a>
# Phần V — Những thứ bạn chưa biết mà bắt buộc phải biết

Bạn đã học khái niệm ở trường. Đây là lớp kiến thức nằm giữa "khái niệm" và
"gõ được code" — thứ không ai dạy vì ai cũng tưởng bạn biết rồi.

## 1. Syscall thật ra là gì

Bạn đã nghe "lời gọi hệ thống" ở môn OS. Cụ thể:

```c
write(fd, "hello", 5);
```

Trông như gọi hàm thường, nhưng nó **không phải**. Nó chạy lệnh máy `syscall`,
CPU chuyển từ **user mode** sang **kernel mode**, kernel làm việc, rồi quay về.

Cái giá:

| Loại | Thời gian |
|---|---|
| Gọi hàm C bình thường | ~1 nano giây |
| Syscall | ~100–1.000 nano giây |
| `fsync()` trên SSD | ~100.000–1.000.000 nano giây |

**Chậm hơn 100–1000 lần.** Đó là toàn bộ lý do tồn tại của:
- đệm I/O (TLPI Ch13) — gom nhiều lần ghi nhỏ thành một syscall
- buffer pool — tránh đọc đĩa
- group commit — gom nhiều `fsync` thành một

Mỗi khi bạn thấy một kỹ thuật tối ưu trong sách cơ sở dữ liệu, hỏi: *"nó đang
tránh syscall nào?"* Chín trên mười lần, đó là câu trả lời.

## 2. File descriptor chỉ là một số nguyên

`open()` trả về `3`. Con số đó **không** là địa chỉ, không là handle bí ẩn.
Nó là **chỉ số trong một mảng** mà kernel giữ riêng cho tiến trình của bạn.

```
Tiến trình của bạn        Kernel
   fd 0 ─────────────▶ [ stdin  ]
   fd 1 ─────────────▶ [ stdout ]
   fd 2 ─────────────▶ [ stderr ]
   fd 3 ─────────────▶ [ data.db, đang ở byte 4096 ]
   fd 4 ─────────────▶ [ socket tới 10.0.0.5:7000 ]
```

`open()` = kernel tìm ô trống nhỏ nhất, gắn con trỏ vào, trả về chỉ số. Hết.

Vì sao quan trọng: ở Phase 3 bạn giữ 10.000 fd cùng lúc. Biết nó chỉ là mảng
thì `epoll` hết bí ẩn — bạn đang đưa cho kernel một danh sách chỉ số và bảo
"cái nào sẵn sàng thì gọi tôi".

Và trong Linux **mọi thứ đều là file**: file thật, socket, pipe, thiết bị, thậm
chí cgroup. Cùng `read`/`write`. Đó là triết lý Unix, và nó làm code của bạn
ngắn đi rất nhiều.

## 3. `write()` KHÔNG ghi xuống đĩa

Sự thật quan trọng nhất trong Phần V.

```
     write(fd, data, n)
            │
            ▼
   ┌──────────────────┐
   │ Page cache (RAM) │  ← dữ liệu dừng ở ĐÂY. write() trả về ngay.
   │  của kernel      │
   └────────┬─────────┘
            │  kernel ghi xuống lúc nào nó thích (có thể 30 giây sau)
            ▼
   ┌──────────────────┐
   │       ĐĨA        │
   └──────────────────┘
```

Cúp điện trước khi kernel ghi xuống → **mất sạch**, dù `write()` đã báo thành công.

`fsync(fd)` = "ghi xuống đĩa thật, đừng trả về cho tới khi xong".

Toàn bộ chương WAL, toàn bộ khái niệm "độ bền" (durability), toàn bộ chữ D trong
ACID — đều sinh ra từ sự thật này. Nếu `write()` ghi thẳng xuống đĩa thì cơ sở
dữ liệu đã đơn giản hơn nhiều (và chậm hơn 1000 lần).

## 4. Trên đĩa không có "sửa", chỉ có "ghi đè cả khối"

Đĩa không cho bạn sửa 1 byte. Đơn vị nhỏ nhất là một **sector** (512B hoặc 4KB).
Sửa 1 byte = đọc cả khối vào RAM, sửa, ghi cả khối xuống.

Hệ quả trực tiếp: nếu cấu trúc dữ liệu của bạn không thẳng hàng với biên page,
mỗi lần ghi nhỏ biến thành hai lần đọc-sửa-ghi. Đó là lý do page 4KB, và là lý
do cả B-Tree lẫn LSM đều tổ chức theo khối.

## 5. Hai loại "chạy song song"

| | Tiến trình (process) | Luồng (thread) |
|---|---|---|
| Bộ nhớ | Riêng hoàn toàn | **Dùng chung** |
| Tạo ra bằng | `fork()` | `pthread_create()` |
| Giá tạo | đắt (~100µs) | rẻ (~10µs) |
| Một thằng crash | Thằng kia sống | **Chết cả đám** |
| Chia sẻ dữ liệu | Phải qua IPC | Đọc thẳng — và đó là nguồn mọi bug |

Container cô lập **tiến trình**. Server đa luồng dùng **luồng**. Goroutine của Go
là loại thứ ba — nhẹ hơn cả hai, do runtime của Go quản lý chứ không phải kernel.

## 6. Vì sao ghi tuần tự nhanh hơn ghi ngẫu nhiên

| | HDD | SSD |
|---|---|---|
| Đọc tuần tự | ~150 MB/s | ~3.000 MB/s |
| Đọc ngẫu nhiên 4KB | ~0,7 MB/s | ~400 MB/s |
| **Chênh lệch** | **~200 lần** | **~7 lần** |

HDD: đầu đọc phải bay tới đúng rãnh (~5ms). SSD không có bộ phận chuyển động
nhưng vẫn có wear leveling và write amplification.

Đây là lý do LSM Tree tồn tại: nó biến mọi lần ghi ngẫu nhiên thành ghi tuần tự,
trả giá bằng việc đọc phải xem nhiều chỗ hơn. **Mọi thiết kế lưu trữ đều là một
lựa chọn trên đường cân bằng ghi-nhanh ↔ đọc-nhanh.**

## 7. Runtime là gì (cho người chưa từng viết Go)

Chương trình C: `main()` chạy, nói chuyện thẳng với kernel. Không có ai ở giữa.

Chương trình Go: trước `main()` của bạn, runtime khởi động. Nó gồm:

- **Bộ thu gom rác** — bạn không `free()` nữa, nó tự dọn
- **Bộ lập lịch** — xoay vòng goroutine trên vài OS thread
- **Netpoller** — epoll được gói lại, bạn không thấy

```
 C:   main() ──▶ kernel
 Go:  main() ──▶ [ runtime: GC + scheduler + netpoller ] ──▶ kernel
```

Cái giá: bạn mất quyền kiểm soát chi tiết, GC có thể gây khựng.
Cái được: 1.500 dòng Go làm bằng 2.500 dòng C, và ít bug hơn nhiều.

Đó là lý do Ouroboros dùng **cả hai**: C ở tầng dưới nơi cần kiểm soát từng byte,
Go ở tầng trên nơi cần đi nhanh và an toàn. Đúng như ngành công nghiệp thật làm.

---

<a name="phần-vi"></a>
# Phần VI — Dòng code đầu tiên

Đọc xong Phần II bạn đã biết mình đang bò về đâu. Giờ là lúc bò.

## Thứ Hai 21/09 — buổi đầu tiên

**Không** mở B-Tree. **Không** vẽ kiến trúc. Làm đúng bốn việc:

**1. Dựng môi trường (30 phút)**
```bash
wsl --install -d Ubuntu
sudo apt update && sudo apt install -y build-essential gdb valgrind linux-tools-generic git
```

**2. Tạo repo (10 phút)**
```bash
mkdir -p /mnt/d/Code/ouroboros && cd /mnt/d/Code/ouroboros
git init && mkdir -p store/src store/include store/tests docs scratch
echo "scratch/" > .gitignore
```

**3. Viết `util.c` (2 giờ)**

File này sẽ theo bạn suốt hai năm. Nó giải quyết một vấn đề C không lo hộ:
**mọi syscall đều có thể lỗi, và bạn phải xử lý.**

Hai hàm để bắt đầu:

```c
// Đọc cho ĐỦ n byte. read() có thể trả về ít hơn yêu cầu — đó
// không phải lỗi, đó là bình thường. Phải gọi lại cho tới khi đủ.
ssize_t read_full(int fd, void *buf, size_t n);

// Ghi cho ĐỦ n byte. write() cũng vậy.
ssize_t write_full(int fd, const void *buf, size_t n);
```

Ba thứ phải xử lý đúng, không được bỏ qua cái nào:
- Trả về ít hơn yêu cầu → gọi lại phần còn thiếu
- Trả về `-1` với `errno == EINTR` → bị signal ngắt, **thử lại**, không phải lỗi
- Trả về `0` khi đọc → hết file / đầu kia đóng kết nối

Hai hàm này nhìn tầm thường. Chúng là nguồn bug số một của code hệ thống do
người mới viết. Viết đúng một lần, dùng hai năm.

**4. Đọc CSAPP Ch1 (1 giờ)** — đọc như xem bản đồ trước chuyến đi. Không sa đà,
không làm bài tập. Chỉ để biết vùng đất có những gì.

## Tuần 6 — dòng code đầu tiên của `ouro-store`

Gõ đúng 60 dòng ở **Nấc 0** trong Phần II. Chạy cho được. Ăn mừng.

Rồi đo: bỏ vào 100.000 bản ghi, đo `get` mất bao lâu. Thấy nó chậm.
**Sự chậm đó là giáo viên của bạn** — nó đẩy bạn sang Nấc 1, và bạn sẽ hiểu
chỉ mục để làm gì theo cách không bài giảng nào dạy được.

## Câu hỏi tự kiểm mỗi cuối tuần

Nếu trả lời được cả ba, tuần đó thành công:

1. Tuần này tôi thêm **năng lực** gì mà hệ thống tuần trước không có?
2. Nó giải bài toán nào mà tôi **tự cảm nhận được**, không phải sách bảo có?
3. Tôi giải thích được cho người khác **trong 2 phút** không?

Nếu câu 2 trả lời không được — bạn đang code theo sách chứ không theo nhu cầu.
Dừng lại, lùi một bước, đo lại hệ thống hiện tại để tìm ra chỗ đau thật.

---

## Lời cuối

Thứ khiến dự án này khó **không** phải là B-Tree hay Raft. Sách có hết.

Thứ khó là **đi đủ lâu** — 87 tuần.

Và cách duy nhất đi đủ lâu là luôn luôn có một thứ đang chạy. Nấc 0 chạy được ở
tuần 6. Nấc 5 chạy được ở tuần 13. Không bao giờ có giai đoạn ba tháng liền
"đang xây, chưa chạy được". Đó là lý do lộ trình chia theo nấc chứ không chia
theo mô-đun.

Mở [PROGRESS.md](ouroboros-PROGRESS.md), tick ô đầu tiên, bắt đầu.
