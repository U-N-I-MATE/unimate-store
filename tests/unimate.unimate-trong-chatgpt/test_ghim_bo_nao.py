"""Gói "UNI MATE trong ChatGPT" 1.3.0: ghim bộ não cho cổng, và gửi tin không kèm chat_id thì tạo hội thoại mới.

    UNIMATE_OS_DIR=../UNI-MATE python tests/unimate.unimate-trong-chatgpt/test_ghim_bo_nao.py   (KHÔNG mạng)

Chủ chốt 04/11/2026: "brain đang mở" của lõi là brain của hội thoại cập nhật gần nhất trên cả máy, nên cổng từng nhảy
sang Brain Default sau một lần khởi động lại. Canh:
  1. CHƯA chọn bộ não: cả 05 tool hội thoại báo lỗi kèm địa chỉ trang gói; không tự dùng Brain mặc định hay brain
     đang mở. Trang gói có ô chọn ở đầu, kèm lựa chọn phụ "Theo hội thoại gần nhất".
  2. Đã ghim: luôn làm trên bộ não đó dù hội thoại mới nhất ở bộ não khác; mọi kết quả ghi tên bộ não; các tool
     thường của hub cũng nhận bộ não đã ghim.
  3. Gửi không kèm chat_id: tạo hội thoại mới ở bộ não đã ghim; chỉ ở Toàn quyền.
  4. Bộ não đã ghim mất: báo lỗi, không rơi sang bộ não khác.
  5. "Theo hội thoại gần nhất" và lõi cũ hơn 0.447.0: theo hội thoại gần nhất như 1.2.0.
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
os.environ.setdefault("UNIMATE_STATE_DIR", tempfile.mkdtemp(prefix="unimate-test-ghim-"))
_BRAINS = tempfile.mkdtemp(prefix="unimate-test-ghim-brains-")
os.environ["BRAINS_DIR"] = _BRAINS          # test này tạo thư mục brain: không bao giờ ở brains/ thật
sys.path.insert(0, str(ROOT / "server"))

fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(them)[:300] + "]") if not cond else ""))
    if not cond:
        fails.append(name)


PLUGIN = STORE / "packs" / "unimate.unimate-trong-chatgpt" / "plugins" / "unimate-trong-chatgpt" / "plugin.py"
spec = importlib.util.spec_from_file_location("cong_chatgpt_ghim", PLUGIN)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
P._co_mat_khau = lambda: True


class Ctx:
    def __init__(self):
        self.slug = "unimate-trong-chatgpt"
        self.data_dir = Path(tempfile.mkdtemp(prefix="unimate-ghim-data-"))
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


import main  # noqa: E402
import mcp_hub  # noqa: E402
import gate_api  # noqa: E402
from sessions import get_store  # noqa: E402

BASE = Path(main.BRAINS_DIR)
if BASE.resolve() != Path(_BRAINS).resolve():
    print(f"FAIL BRAINS_DIR không phải thư mục tạm: {BASE}. DỪNG để không ghi vào brains/ thật.")
    sys.exit(1)
A = BASE / "Bonao_AI"
B = BASE / "Brain Default"
A.mkdir(parents=True)
B.mkdir(parents=True)
store = get_store()


def chat(brain_dir, channel, title):
    sid = store.create_session(brain=main._brain_key(str(brain_dir)), title=title, channel=channel)
    store.append_message(sid, "user", f"hỏi {title}")
    store.append_message(sid, "assistant", f"trả lời {title}")
    return sid


s_a = chat(A, "web", "Từ Claude: Thử cổng Claude.ai")
s_b = chat(B, "web", "Chào Uni")
# Hội thoại mới nhất ở Brain Default (như UNI MATE Core sau khi khởi động lại): hub tự suy ra B.
mcp_hub.resolve_vault = lambda raw: ((str(raw), "header", "") if raw else (str(B), "phien", ""))

c = Ctx()
P.register(c)
CLAUDE_CB = "https://claude.ai/api/mcp/auth_callback"
ma, kq = P.dang_ky_client(c, {"redirect_uris": [CLAUDE_CB]})
d = P._doc(c)
tok = P._cap_token(d, kq["client_id"], "ho1")["access_token"]
P._ghi(c, d)
MCP = c.http[("mcp", "POST")]
P.dat_muc_quyen(c, "full")


def goi(body):
    r = run(MCP(Req(body, tok), c))
    return r.status_code, (json.loads(r.body) if r.body else None)


def call(ten, args):
    st, r = goi({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": ten, "arguments": args}})
    res = r["result"]
    return res["isError"], res["content"][0]["text"]


def trang():
    r = c.http[("", "GET")](Req({}), c)
    return r.body.decode("utf-8")


NAM = [(P.T_DANH_SACH, {}), (P.T_DOC, {"chat_id": s_a}), (P.T_GHI, {"title": "x", "note": "y"}),
       (P.T_GUI, {"chat_id": s_a, "message": "x"}), (P.T_KET_QUA, {"chat_id": s_a, "after_id": 0})]
TRANG = "https://unimate.example/ext/unimate-trong-chatgpt/"

# ---- 1. chưa chọn bộ não ----
check("cài mới: chưa có bộ não ghim", P.bo_nao_ghim(c) == "")
for ten, args in NAM:
    loi, txt = call(ten, args)
    check(f"chưa chọn: {ten} báo lỗi kèm địa chỉ trang gói",
          loi and "chưa chọn bộ não" in txt and TRANG in txt, txt)
check("chưa chọn: không ghi gì vào bộ não nào", len(store.get_messages(s_a)) == 2 and len(store.get_messages(s_b)) == 2)
st, r = goi({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
check("chưa chọn: danh sách tool vẫn trả (để AI gọi và nhận lời nhắc)", st == 200 and r["result"]["tools"])
h = trang()
check("trang gói: ô chọn bộ não nằm trước mục dán địa chỉ", 0 <= h.find('id="bo_nao"') < h.find("1. Dán địa chỉ"))
check("trang gói: có ô giữ chỗ 'Chọn bộ não...' đang được chọn",
      '<option value="" selected disabled>Chọn bộ não...</option>' in h)
check("trang gói: liệt kê đủ hai bộ não", "Bonao_AI" in h and "Brain Default" in h)
check("trang gói: có lựa chọn phụ 'Theo hội thoại gần nhất' kèm ghi chú",
      f'value="{P.GAN_NHAT}"' in h and "dễ nhảy bộ não" in h)
check("trang gói: nhắc rõ là chưa chọn", "Chưa chọn bộ não" in h)

# ---- lưu lựa chọn ----
check("không nhận đường dẫn lạ", P.dat_bo_nao(c, "/etc") is False and P.bo_nao_ghim(c) == "")
check("không nhận chuỗi rỗng", P.dat_bo_nao(c, "") is False)
check("nhận đúng một bộ não lõi đang liệt kê", P.dat_bo_nao(c, str(A)) and P.bo_nao_ghim(c) == str(A))

# ---- 2. đã ghim Bonao_AI dù hội thoại mới nhất ở Brain Default ----
loi, txt = call(P.T_DANH_SACH, {})
out = json.loads(txt) if not loi else {}
ids = [x["id"] for x in out.get("chats", [])]
check("đã ghim: liệt kê hội thoại của bộ não đã ghim", s_a in ids and s_b not in ids, txt)
check("đã ghim: kết quả ghi tên bộ não", out.get("bo_nao") == "Bonao_AI", out.get("bo_nao"))
loi, txt = call(P.T_DOC, {"chat_id": s_a})
check("đã ghim: đọc được hội thoại của bộ não đó, có tên bộ não",
      not loi and json.loads(txt).get("bo_nao") == "Bonao_AI", txt)
loi, txt = call(P.T_DOC, {"chat_id": s_b})
check("đã ghim: hội thoại của bộ não khác bị từ chối, lỗi cũng ghi tên bộ não",
      loi and "Không có hội thoại này" in txt and "Bonao_AI" in txt, txt)
loi, txt = call(P.T_GHI, {"title": "Kế hoạch Tết", "note": "Chốt ngân sách."})
sid = json.loads(txt).get("session_id") if not loi else ""
check("đã ghim: ghi chép vào đúng bộ não đã ghim",
      sid and (store.get_session(sid) or {}).get("brain") == main._brain_key(str(A)), txt)
h = trang()
check("trang gói: hiện bộ não đang ghim, không còn lời nhắc",
      f'<option value="{A}" selected>' in h and "Chưa chọn bộ não" not in h)

# Các tool thường của hub qua cửa này cũng nhận bộ não đã ghim.
seen = []
_that_tl = mcp_hub.tra_loi_jsonrpc


async def _ghi_lai(req, mode, **kw):
    seen.append(kw.get("raw_vault"))
    return await _that_tl(req, mode, **kw)
mcp_hub.tra_loi_jsonrpc = _ghi_lai
try:
    goi({"jsonrpc": "2.0", "id": 9, "method": "ping"})
    check("đã ghim: tool thường của hub nhận đúng bộ não đã ghim", seen and seen[-1] == str(A), seen)
    P.dat_bo_nao(c, P.GAN_NHAT)
    goi({"jsonrpc": "2.0", "id": 9, "method": "ping"})
    check("theo hội thoại gần nhất: hub tự suy như cũ (không truyền bộ não)", seen[-1] is None, seen)
finally:
    mcp_hub.tra_loi_jsonrpc = _that_tl
P.dat_bo_nao(c, str(A))

# ---- 3. gửi không kèm chat_id: tạo hội thoại mới ở bộ não đã ghim ----
GOI = []
_that_gui, _that_kq = gate_api.send_chat, gate_api.chat_result


async def _gui(sid, br, text, source, title=""):
    GOI.append((sid, br, text, source, title))
    return {"chat_id": "moi-1", "title": f"Từ {source}: {title}", "mode": "started", "after_id": 0, "created": not sid}
gate_api.send_chat = _gui
try:
    loi, txt = call(P.T_GUI, {"message": "Lên việc tuần này.", "title": "Việc tuần 45"})
    out = json.loads(txt) if not loi else {}
    check("không có chat_id: gửi thành công, created, ghi tên bộ não",
          not loi and out.get("created") is True and out.get("bo_nao") == "Bonao_AI", txt)
    check("không có chat_id: lõi nhận id rỗng, đúng bộ não đã ghim, tiêu đề, nguồn Claude",
          GOI and GOI[-1][0] == "" and GOI[-1][1] == str(A) and GOI[-1][4] == "Việc tuần 45" and GOI[-1][3] == "Claude",
          GOI[-1:])
    n = len(GOI)
    P.dat_muc_quyen(c, "auto")
    loi, txt = call(P.T_GUI, {"message": "Lên việc tuần này."})
    check("Ghi nháp: tạo hội thoại mới bị chặn, nói rõ chỉ Toàn quyền", loi and "Toàn quyền" in txt and len(GOI) == n, txt)
    P.dat_muc_quyen(c, "suggest")
    loi, txt = call(P.T_GUI, {"message": "Lên việc tuần này."})
    check("Chỉ đọc: tạo hội thoại mới bị chặn", loi and len(GOI) == n, txt)
    P.dat_muc_quyen(c, "full")
finally:
    gate_api.send_chat, gate_api.chat_result = _that_gui, _that_kq
n_a = len(store.list_sessions(limit=500, brain=[main._brain_key(str(A))], channel="*"))
loi, txt = call(P.T_GUI, {"message": "   "})
check("lõi thật: không có chat_id + tin rỗng thì từ chối, không tạo hội thoại",
      loi and len(store.list_sessions(limit=500, brain=[main._brain_key(str(A))], channel="*")) == n_a, txt)

# ---- 4. bộ não đã ghim mất: báo lỗi, không rơi sang bộ não khác ----
A.rename(BASE / "Bonao_AI_cu")
for ten, args in NAM:
    loi, txt = call(ten, args)
    check(f"bộ não ghim mất: {ten} báo lỗi, chỉ trang gói", loi and "không còn" in txt and TRANG in txt, txt)
check("bộ não ghim mất: không tự rơi sang Brain Default", len(store.get_messages(s_b)) == 2)
check("trang gói: báo bộ não đã ghim không còn", "không còn. Chọn lại" in trang())
(BASE / "Bonao_AI_cu").rename(A)

# ---- 5. theo hội thoại gần nhất, và lõi cũ ----
P.dat_bo_nao(c, P.GAN_NHAT)
loi, txt = call(P.T_DANH_SACH, {})
out = json.loads(txt) if not loi else {}
check("theo hội thoại gần nhất: làm trên bộ não hub suy ra (Brain Default)",
      s_b in [x["id"] for x in out.get("chats", [])] and out.get("bo_nao") == "Brain Default", txt)

c2 = Ctx()
P.register(c2)
_, kq2 = P.dang_ky_client(c2, {"redirect_uris": [CLAUDE_CB]})
d2 = P._doc(c2)
tok2 = P._cap_token(d2, kq2["client_id"], "ho2")["access_token"]
P._ghi(c2, d2)
P.dat_muc_quyen(c2, "full")
MCP2 = c2.http[("mcp", "POST")]


def call2(ten, args):
    r = run(MCP2(Req({"jsonrpc": "2.0", "id": 8, "method": "tools/call",
                      "params": {"name": ten, "arguments": args}}, tok2), c2))
    res = json.loads(r.body)["result"]
    return res["isError"], res["content"][0]["text"]


cu = types.SimpleNamespace(**{k: getattr(gate_api, k) for k in
                              ("GateError", "list_chats", "read_chat", "record_note", "send_chat", "chat_result")})
_that_gate = P._gate
P._gate = lambda: cu
try:
    check("lõi cũ: bản gói chưa chọn bộ não", P.bo_nao_ghim(c2) == "")
    loi, txt = call2(P.T_DANH_SACH, {})
    check("lõi cũ: chưa chọn vẫn chạy theo hội thoại gần nhất như 1.2.0",
          not loi and s_b in [x["id"] for x in json.loads(txt).get("chats", [])], txt)
    h2 = c2.http[("", "GET")](Req({}), c2).body.decode("utf-8")
    check("lõi cũ: trang gói nói cần 0.447.0 để chọn bộ não", "0.447.0" in h2 and 'id="bo_nao"' not in h2)
    loi, txt = call2(P.T_GUI, {"message": "x"})
    check("lõi cũ: gửi không kèm chat_id báo cần 0.447.0", loi and "0.447.0" in txt, txt)
    check("lõi cũ: không ghim được", P.dat_bo_nao(c2, str(A)) is False)
finally:
    P._gate = _that_gate

check("không có ký tự gạch dài trong gói", "—" not in PLUGIN.read_text(encoding="utf-8"))

print()
if fails:
    print(f"FAIL {len(fails)}: {fails}")
    sys.exit(1)
print("OK - test_ghim_bo_nao: all pass")
