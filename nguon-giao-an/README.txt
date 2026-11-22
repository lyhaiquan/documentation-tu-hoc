Nguon sinh ra giao-an-theo-mon.html (giao an 197 ngay, 10 mon (LIN SYS KER NET GOL CON K8S DBS DIS AIS)).

Du lieu: moi mon mot file s_*.py (s_lin, s_sys, s_ker, s_net, s_gol, s_con, s_k8s, s_dbs, s_dis, s_ais).
  Moi ngay la mot dict: t (chu de), why (noi tu bai truoc), r (doc: ma sach, nhan, trang dau, trang cuoi),
  g (nam duoc), lab (thuc hanh), q (tu kiem), tags, x (lien quan).
Muc luc sach: toc.json (tao bang mktoc.py tu cac PDF trong D:\Documentation; xem BOOKS trong mktoc.py).
Lich tuan: ALLOC trong common.py (mon nao, bao nhieu ngay moi tuan).

Chinh sua roi chay lai (Python 3, can PyMuPDF `pip install pymupdf`, Node de kiem JS):
  python validate_data.py     # kiem trang nam trong sach, tai doc moi ngay <= 40, thu tu tien quyet, ho trang
  python build.py             # ghi D:\Documentation\giao-an-theo-mon.html
  python check_html.py        # the, id, lien ket, node --check
  python spot.py / spot2.py   # doi chieu nhan/thuat ngu voi noi dung PDF

Luu y: chay voi `python -I` thi bien PYTHONIOENCODING bi bo qua; dat sys.stdout.reconfigure(encoding='utf-8') (da co san).
