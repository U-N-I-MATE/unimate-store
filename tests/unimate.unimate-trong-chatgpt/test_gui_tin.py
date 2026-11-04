"""Gói "UNI MATE trong ChatGPT" 1.2.0: gửi tin vào khung Trò chuyện chính và đọc câu trả lời, chỉ ở mức Toàn quyền.

    UNIMATE_OS_DIR=../UNI-MATE python tests/unimate.unimate-trong-chatgpt/test_gui_tin.py   (KHÔNG mạng)

Canh:
  1. Hai tool gửi tin, đọc kết quả CHỈ hiện ở mức Toàn quyền; Chỉ đọc và Ghi nháp không thấy, gọi thẳng tên cũng bị
     chặn với lời báo đọc được.
  2. Ở Toàn quyền, gói chuyển đúng tham số cho `gate_api` của lõi: hội thoại, brain đang mở, nội dung, và nguồn theo
     địa chỉ quay về của client (Claude.ai -> "Claude"), không theo tên tự khai.
  3. Ranh giới hội thoại là việc của lõi: qua gói, gửi vào hội thoại khách hay hội thoại với Cộng sự đều bị từ chối.
  4. Lõi 0.441.0 đến 0.445.x (có gate_api nhưng chưa có phần gửi): hai tool không hiện, ba tool cũ vẫn có; gọi thẳng
     tên thì báo cần 0.446.0.
Phần chạy thật lượt chat (gửi vào khung Trò chuyện, gõ thêm khi đang bận) do lõi kiểm ở
tests/python/test_gate_send_chat_0446.py của UNI MATE.
"""
import asyncio
import importlib.util
import json
import os
import sys
import tempfile
import types
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STORE = Path(__file__).resolve().parents[2]
ROOT = Path(os.environ.get("UNIMATE_OS_DIR") or (STORE.parent / "UNI-MATE")).resolve()
if not (ROOT / "server" / "mcp_hub.py").is_file():
    raise SystemExit(f"UNI MATE checkout not found at {ROOT} (set UNIMATE_OS_DIR)")
os.environ["UNIMATE_OS_DIR"] = str(ROOT)
os.environ.setdefault("UNIMATE_STATE_DIR", tempfile.mkdtemp(prefix="unimate-test-gui-"))
sys.path.insert(0, str(ROOT / "server"))

fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(them)[:300] + "]") if not cond else ""))
    if not cond:
        fails.append(name)


PLUGIN = STORE / "packs" / "unimate.unimate-trong-chatgpt" / "plugins" / "unimate-trong-chatgpt" / "plugin.py"
spec = importlib.util.spec_from_file_location("cong_chatgpt_gui", PLUGIN)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
P._co_mat_khau = lambda: True


class Ctx:
    def __init__(self):
        self.slug = "unimate-trong-chatgpt"
        self.data_dir = Path(tempfile.mkdtemp(prefix="unimate-gui-data-"))
        self.http, self.tools = {}, []

    def register_http(self, path, fn, methods=("GET",), **kw):
        for m in methods:
            self.http[(path, m)] = fn

    def register_well_known(self, name, fn):
        pass

    def register_tool(self, *a, **kw):
        self.tools.append(a)


class Req:
    def __init__(self, body, token=""):
        self._body = body
        self.headers = {"authorization": f"Bearer {token}"} if token else {}
        self.cookies = {}
        self.url = type("U", (), {"scheme": "https", "netloc": "unimate.example", "path": "/ext/x/mcp"})()

    async def json(self):
        return self._body


def run(c):
    return asyncio.run(c)


c = Ctx()
P.register(c)
check("không có tool nào qua register_tool", c.tools == [], c.tools)

import main  # noqa: E402
import mcp_hub  # noqa: E402
import gate_api  # noqa: E402
from sessions import get_store  # noqa: E402

brain = tempfile.mkdtemp(prefix="unimate-gui-brain-")
mcp_hub.resolve_vault = lambda raw: (Path(brain), "phien", "")
store = get_store()
key = main._brain_key(brain)
s_chu = store.create_session(brain=key, title="Kế hoạch tháng 11", channel="web")
s_khach = store.create_session(brain=key, title="Khách hỏi giá", channel="bot:shop")
s_cong_su = store.create_session(brain=key, title="Cộng sự viết bài", channel="agent:viet-bai")

CLAUDE_CB = "https://claude.ai/api/mcp/auth_callback"
ma, kq = P.dang_ky_client(c, {"redirect_uris": [CLAUDE_CB], "client_name": "ChatGPT"})
d = P._doc(c)
tok = P._cap_token(d, kq["client_id"], "ho1")["access_token"]
P._ghi(c, d)
MCP = c.http[("mcp", "POST")]


def goi(body):
    r = run(MCP(Req(body, tok), c))
    return r.status_code, (json.loads(r.body) if r.body else None)


def ten_tool(muc):
    P.dat_muc_quyen(c, muc)
    st, r = goi({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    return [t["name"] for t in r["result"]["tools"]]


def call(ten, args):
    st, r = goi({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": ten, "arguments": args}})
    res = r["result"]
    return res["isError"], res["content"][0]["text"]


GUI = {P.T_GUI, P.T_KET_QUA}

# ---- 1. chỉ Toàn quyền ----
check("lõi này có phần gửi tin (0.446.0)", P.co_gui(gate_api))
check("Chỉ đọc: không thấy hai tool gửi", not GUI & set(ten_tool("suggest")))
check("Ghi nháp: không thấy hai tool gửi", not GUI & set(ten_tool("auto")))
ds = ten_tool("full")
check("Toàn quyền: thấy đủ hai tool gửi, vẫn có ba tool cũ",
      GUI <= set(ds) and {P.T_DANH_SACH, P.T_DOC, P.T_GHI} <= set(ds), ds[-6:])
P.dat_muc_quyen(c, "auto")
loi, txt = call(P.T_GUI, {"chat_id": s_chu, "message": "x"})
check("Ghi nháp gọi thẳng tool gửi: chặn, nói rõ chỉ Toàn quyền", loi and "Toàn quyền" in txt, txt)
loi, txt = call(P.T_KET_QUA, {"chat_id": s_chu, "after_id": 0})
check("Ghi nháp gọi thẳng tool đọc kết quả: chặn", loi and "Toàn quyền" in txt, txt)
check("không có gì được gửi ở mức thấp", len(store.get_messages(s_chu)) == 0)

# ---- 2. Toàn quyền: gói chuyển đúng tham số cho lõi ----
P.dat_muc_quyen(c, "full")
GOI = []
_that_gui, _that_kq = gate_api.send_chat, gate_api.chat_result


async def _gui(sid, br, text, source):
    GOI.append(("send", sid, br, text, source))
    return {"chat_id": sid, "title": "Kế hoạch tháng 11", "mode": "started", "after_id": 41}


async def _kq(sid, br, after_id=0, wait=25):
    GOI.append(("result", sid, br, after_id, wait))
    return {"status": "done", "answer": "Đã lên danh sách việc tuần này."}
gate_api.send_chat, gate_api.chat_result = _gui, _kq
try:
    loi, txt = call(P.T_GUI, {"chat_id": s_chu, "message": "Lên danh sách việc tuần này."})
    out = json.loads(txt) if not loi else {}
    check("gửi: thành công, trả after_id và lời dặn gọi tool kết quả",
          not loi and out.get("after_id") == 41 and P.T_KET_QUA in out.get("huong_dan", ""), txt)
    check("gửi: đúng hội thoại, brain đang mở, nội dung",
          GOI and GOI[0][1] == s_chu and Path(GOI[0][2]) == Path(brain) and GOI[0][3] == "Lên danh sách việc tuần này.",
          GOI[:1])
    check("gửi: nguồn theo địa chỉ quay về (claude.ai) dù tự khai tên ChatGPT", GOI and GOI[0][4] == "Claude", GOI[:1])
    loi, txt = call(P.T_KET_QUA, {"chat_id": s_chu, "after_id": 41, "wait": 5})
    check("đọc kết quả: trả câu trả lời", not loi and json.loads(txt).get("status") == "done", txt)
    check("đọc kết quả: đúng after_id và thời gian chờ", GOI[-1] == ("result", s_chu, GOI[-1][2], 41, 5), GOI[-1:])
finally:
    gate_api.send_chat, gate_api.chat_result = _that_gui, _that_kq

# ---- 3. ranh giới hội thoại (lõi thật) ----
loi, txt = call(P.T_GUI, {"chat_id": s_khach, "message": "xin chào"})
check("gửi vào hội thoại khách: từ chối", loi and "Không có hội thoại này" in txt, txt)
loi, txt = call(P.T_GUI, {"chat_id": s_cong_su, "message": "xin chào"})
check("gửi vào hội thoại với Cộng sự: từ chối, chỉ khung Trò chuyện chính", loi and "Trò chuyện chính" in txt, txt)
loi, txt = call(P.T_GUI, {"chat_id": s_chu, "message": "   "})
check("tin rỗng: từ chối", loi, txt)
check("các lượt bị từ chối không lưu gì", all(len(store.get_messages(s)) == 0 for s in (s_chu, s_khach, s_cong_su)))

# ---- 4. lõi 0.441.0 đến 0.445.x ----
cu = types.SimpleNamespace(**{k: getattr(gate_api, k) for k in ("GateError", "list_chats", "read_chat", "record_note")})
P._gate = lambda: cu
ds = ten_tool("full")
check("lõi cũ: không có hai tool gửi, vẫn có ba tool cũ",
      not GUI & set(ds) and {P.T_DANH_SACH, P.T_DOC, P.T_GHI} <= set(ds), ds[-5:])
loi, txt = call(P.T_GUI, {"chat_id": s_chu, "message": "x"})
check("lõi cũ gọi thẳng tool gửi: báo cần 0.446.0", loi and "0.446.0" in txt, txt)

check("không có ký tự gạch dài trong gói", "—" not in PLUGIN.read_text(encoding="utf-8"))

print()
if fails:
    print(f"FAIL {len(fails)}: {fails}")
    sys.exit(1)
print("OK - test_gui_tin: all pass")
