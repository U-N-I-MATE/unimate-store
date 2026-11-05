"""Gói "Quản lý khách hàng (CRM)" 1.1.0: tên người bình luận Facebook không bao giờ ra khỏi Hộp thư qua tool AI.

    UNIMATE_OS_DIR=../UNI-MATE python tests/unimate.khach-hang-crm/test_che_ten_facebook.py   (KHÔNG mạng)

Anh chốt 05/11/2026: các model đứng sau tool chạy ở máy chủ bên ngoài, nên kết quả tool không mang tên hay id Facebook
của người bình luận. Trong một hội thoại, người bình luận hiện "Khách 1", "Khách 2"... theo thứ tự viết đầu tiên;
bình luận Meta gửi không kèm tác giả hiện "Khách Facebook". Kênh khác (Zalo, Telegram) giữ nguyên tên như cũ.
Dùng kho hội thoại THẬT của lõi UNI MATE (thư mục tạm).
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STORE = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ.get("UNIMATE_OS_DIR") or (STORE.parent / "UNI-MATE")).resolve()
if not (ROOT / "server" / "conversations.py").is_file():
    raise SystemExit(f"UNI MATE checkout not found at {ROOT} (set UNIMATE_OS_DIR)")
os.environ["UNIMATE_STATE_DIR"] = tempfile.mkdtemp(prefix="unimate-test-crm-")
sys.path.insert(0, str(ROOT / "server"))

fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(them)[:300] + "]") if not cond else ""))
    if not cond:
        fails.append(name)


PLUGIN = STORE / "packs" / "unimate.khach-hang-crm" / "plugins" / "khach-hang-crm" / "plugin.py"
spec = importlib.util.spec_from_file_location("crm_che_ten", PLUGIN)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

import conversations as cs  # noqa: E402

PAGE, POST = "111111111111111", "111111111111111_1001"
NAMES = ["Lan Anh", "Huan Nguyen"]
IDS = ["9001", "9002"]


def fb(cid, sid, name, text, ts, who="customer"):
    return cs.ghi_su_kien({"channel": "facebook", "account_id": PAGE, "account_name": "Golf HaNoi",
                           "external_chat_id": POST, "chat_type": "group", "chat_title": "CHUẨN BỊ COMEBACK!",
                           "sender_type": who, "sender_id": sid, "sender_name": name, "text": text,
                           "external_message_id": cid, "created_at": ts})


fb("c1", IDS[0], NAMES[0], "Giá bao nhiêu?", 1000)
fb("c2", "", "", "😍", 1001)
fb("c3", IDS[1], NAMES[1], "Còn size M không?", 1002)
fb("c4", "", "", "Dạ còn ạ", 1003, who="human")
fb("c5", IDS[0], NAMES[0], "Ship Hà Nội không?", 1004)
cs.ghi_su_kien({"channel": "zalo_personal", "account_id": "zl1", "external_chat_id": "u77", "chat_type": "private",
                "sender_type": "customer", "sender_id": "u77", "sender_name": "Chị Hoa", "text": "Giá bao nhiêu?",
                "external_message_id": "z1", "created_at": 1005})


class Ctx:
    vault_root = tempfile.mkdtemp(prefix="unimate-crm-brain-")


ctx = Ctx()


def out(fn, args):
    s = fn(args, ctx)
    return s, (json.loads(s) if s and s[0] in "{[" else s)


def leak(s):
    return [x for x in NAMES + IDS if x in s]


conv = next(v for v in cs.danh_sach(channel="facebook")["items"]) if isinstance(cs.danh_sach(channel="facebook"), dict) \
    else cs.danh_sach(channel="facebook")[0]

s, d = out(P.crm_hoi_thoai, {"hoi_thoai_id": conv["id"]})
check("đọc một hội thoại Facebook: không lộ tên, không lộ id", not leak(s), leak(s))
ten = [m["ten"] for m in d["tin"]]
check("người bình luận thành Khách 1, Khách 2 theo thứ tự viết đầu tiên",
      ten == ["Khách 1", "Khách Facebook", "Khách 2", "", "Khách 1"], ten)
check("chữ bình luận giữ nguyên", [m["text"] for m in d["tin"]][0] == "Giá bao nhiêu?")
check("tên hội thoại là tiêu đề bài, không phải tên khách", d["hoi_thoai"]["ten"] == "CHUẨN BỊ COMEBACK!", d["hoi_thoai"])

s, d = out(P.crm_hoi_thoai, {"kenh": "facebook"})
check("danh sách hội thoại Facebook: không lộ tên", not leak(s), leak(s))

s, d = out(P.crm_khach_hang, {"kenh": "facebook"})
check("danh sách khách Facebook: không tên thật, không id Facebook", d["so_khach"] == 2 and not leak(s), s[:300])
check("khách Facebook hiện 'Khách Facebook <số>'", all(k["ten"].startswith("Khách Facebook ") for k in d["khach"]), d)

s, d = out(P.crm_khach_hang, {"q": "Lan Anh"})
check("tìm theo tên thật không xác nhận người đó đã bình luận", not leak(s) and d["so_khach"] == 0, s[:300])
s, d = out(P.crm_ho_so_khach, {"q": "Huan"})
check("hồ sơ tìm theo tên thật: không thấy", isinstance(d, str) and "Không thấy" in d, d)
kid = next(k["id"] for k in out(P.crm_khach_hang, {"kenh": "facebook"})[1]["khach"])
s, d = out(P.crm_ho_so_khach, {"khach_id": kid})
check("hồ sơ khách Facebook: không lộ tên, tin trong hồ sơ cũng che", not leak(s) and d["hoi_thoai"][0]["tin_gan_nhat"], s[:300])

s, d = out(P.crm_tim_tin, {"q": "Giá"})
check("tìm tin: dòng Facebook ghi tiêu đề bài, dòng Zalo vẫn ghi tên khách",
      not leak(s) and any(m["khach"] == "CHUẨN BỊ COMEBACK!" for m in d["tin"]) and any(m["khach"] == "Chị Hoa" for m in d["tin"]),
      s[:400])

s, d = out(P.crm_cho_tra_loi, {"gio": 0})
check("khách chờ trả lời: không lộ tên", not leak(s), s[:300])

s, d = out(P.crm_xuat_csv, {})
csv_text = (Path(ctx.vault_root) / d["file"]).read_text(encoding="utf-8")
check("file CSV xuất ra brain: không có tên, id Facebook", not leak(csv_text), csv_text[:300])
check("file CSV vẫn giữ tên khách Zalo", "Chị Hoa" in csv_text)

zc = cs.danh_sach(channel="zalo_personal")
zc = zc["items"][0] if isinstance(zc, dict) else zc[0]
s, d = out(P.crm_hoi_thoai, {"hoi_thoai_id": zc["id"]})
check("kênh Zalo giữ nguyên tên như trước", d["tin"][0]["ten"] == "Chị Hoa", d["tin"])

check("không có ký tự gạch dài trong gói", "—" not in PLUGIN.read_text(encoding="utf-8"))
print()
if fails:
    print(f"FAIL {len(fails)}: {fails}")
    sys.exit(1)
print("OK - test_che_ten_facebook: all pass")
