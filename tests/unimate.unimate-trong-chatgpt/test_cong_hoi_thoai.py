"""Gói "UNI MATE trong ChatGPT" 1.1.0: mức mặc định Ghi nháp và ba tool hội thoại chỉ cửa này có.

    UNIMATE_OS_DIR=../UNI-MATE python tests/unimate.unimate-trong-chatgpt/test_cong_hoi_thoai.py   (KHÔNG mạng)

Canh:
  1. Cài mới mặc định Ghi nháp; bản đã từng kết nối (có kho.json) giữ Toàn quyền như 1.0.0; mức đã chọn
     giữ nguyên; kết nối lần đầu SAU khi lên 1.1.0 không bị coi là bản cũ.
  2. tools/list của cửa = danh sách của hub + tool của cửa theo mức (Chỉ đọc không thấy tool ghi).
  3. tools/call: đọc đúng hội thoại của chủ, từ chối hội thoại khách; ghi ở Chỉ đọc bị chặn kể cả gọi
     thẳng tên; ghi ở Ghi nháp tạo hội thoại "Từ ChatGPT: ..." / "Từ Claude: ..." theo tên client.
  4. Tin khác (initialize, ping, thông báo, lô) đi qua hub nguyên vẹn; lõi cũ (không có gate_api) thì gói
     vẫn chạy, chỉ thiếu ba tool.
  5. Ba tool KHÔNG đăng ký qua ctx.register_tool (sẽ lộ ra cho mọi engine).
"""
import asyncio
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
if not (ROOT / "server" / "mcp_hub.py").is_file():
    raise SystemExit(f"UNI MATE checkout not found at {ROOT} (set UNIMATE_OS_DIR)")
os.environ["UNIMATE_OS_DIR"] = str(ROOT)
os.environ.setdefault("UNIMATE_STATE_DIR", tempfile.mkdtemp(prefix="unimate-test-cong-"))
sys.path.insert(0, str(ROOT / "server"))

fails = []


def check(name, cond, them=""):
    print(("ok   " if cond else "FAIL ") + name + (("  [" + str(them)[:300] + "]") if not cond else ""))
    if not cond:
        fails.append(name)


PLUGIN = STORE / "packs" / "unimate.unimate-trong-chatgpt" / "plugins" / "unimate-trong-chatgpt" / "plugin.py"
spec = importlib.util.spec_from_file_location("cong_chatgpt", PLUGIN)
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
P._co_mat_khau = lambda: True


class Ctx:
    def __init__(self):
        self.slug = "unimate-trong-chatgpt"
        self.data_dir = Path(tempfile.mkdtemp(prefix="unimate-cong-data-"))
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
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


def run(c):
    return asyncio.run(c)


# ---- 0. địa chỉ quay về: ChatGPT như cũ, Claude.ai đúng MỘT địa chỉ Anthropic công bố ----
CLAUDE_CB = "https://claude.ai/api/mcp/auth_callback"
for uri, muon in ((CLAUDE_CB, True),
                  ("https://chatgpt.com/connector_platform_oauth_redirect", True),
                  ("https://claude.com/api/mcp/auth_callback", False),     # chưa có trong tài liệu Anthropic
                  ("https://claude.ai/api/mcp/auth_callback/", False),
                  ("https://claude.ai/api/mcp/auth_callback?x=1", False),
                  ("https://claude.ai/khac", False),
                  ("https://evil.claude.ai/api/mcp/auth_callback", False),
                  ("http://claude.ai/api/mcp/auth_callback", False),
                  ("https://claude.ai.evil.com/api/mcp/auth_callback", False),
                  ("https://localhost/callback", False)):
    check(f"redirect {'nhận' if muon else 'chặn'}: {uri}", P.redirect_hop_le(uri) is muon)

# ---- 1. mức mặc định ----
c = Ctx()
P.register(c)
check("cài mới: mặc định Ghi nháp", P.muc_quyen(c) == "auto", P.muc_quyen(c))
check("không có tool nào qua register_tool", c.tools == [], c.tools)
# Kết nối lần đầu sau khi lên 1.1.0: có kho.json rồi, nạp lại plugin vẫn Ghi nháp.
P.dang_ky_client(c, {"redirect_uris": ["https://chatgpt.com/connector_platform_oauth_redirect"]})
P.register(c)
check("kết nối sau khi lên 1.1.0 không bị coi là bản cũ", P.muc_quyen(c) == "auto", P.muc_quyen(c))

cu = Ctx()
(cu.data_dir / "kho.json").write_text(json.dumps({"clients": {"x": {"id": "x"}}}), encoding="utf-8")
P.register(cu)
check("bản 1.0.0 đã kết nối, chưa chọn mức: giữ Toàn quyền", P.muc_quyen(cu) == "full", P.muc_quyen(cu))
P.dat_muc_quyen(cu, "auto")
P.register(cu)
check("chủ hạ xuống rồi nạp lại: không bị nâng lại", P.muc_quyen(cu) == "auto", P.muc_quyen(cu))

chon = Ctx()
(chon.data_dir / "kho.json").write_text("{}", encoding="utf-8")
(chon.data_dir / "cai-dat.json").write_text(json.dumps({"muc_quyen": "suggest"}), encoding="utf-8")
P.register(chon)
check("bản cũ đã chọn Chỉ đọc: giữ nguyên", P.muc_quyen(chon) == "suggest", P.muc_quyen(chon))

# ---- dữ liệu: hội thoại trong một brain ----
import main  # noqa: E402
import mcp_hub  # noqa: E402
from sessions import get_store  # noqa: E402

brain = tempfile.mkdtemp(prefix="unimate-cong-brain-")
mcp_hub.resolve_vault = lambda raw: (Path(brain), "phien", "")
store = get_store()
key = main._brain_key(brain)


def chat(channel, title):
    sid = store.create_session(brain=key, title=title, channel=channel)
    store.append_message(sid, "user", f"hỏi {title}")
    store.append_message(sid, "assistant", f"trả lời {title}")
    return sid


s_chu = chat("web", "Kế hoạch tháng 11")
s_khach = chat("bot:shop", "Khách hỏi giá")

# Token của một client tên ChatGPT, một client tên Claude.
d = P._doc(c)
cid = next(iter(d["clients"]))
tok = P._cap_token(d, cid, "ho1")["access_token"]
P._ghi(c, d)
# Client Claude đăng ký thật qua RFC 7591; tên tự khai "ChatGPT" cũng không đổi được nguồn.
ma, kq = P.dang_ky_client(c, {"redirect_uris": [CLAUDE_CB], "client_name": "ChatGPT"})
check("đăng ký client Claude với đúng địa chỉ quay về", ma == 201, kq)
ma2, kq2 = P.dang_ky_client(c, {"redirect_uris": [CLAUDE_CB]})
check("client Claude không khai tên: tên là Claude", kq2.get("client_name") == "Claude", kq2)
d = P._doc(c)
tok_claude = P._cap_token(d, kq["client_id"], "ho2")["access_token"]
d["clients"][cid]["ten"] = "Claude giả"          # client ChatGPT tự khai tên Claude
P._ghi(c, d)
MCP = c.http[("mcp", "POST")]


def goi(body, token=tok):
    r = run(MCP(Req(body, token), c))
    return r.status_code, (json.loads(r.body) if r.body else None)


def ten_tool(muc):
    P.dat_muc_quyen(c, muc)
    st, r = goi({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    return st, [t["name"] for t in r["result"]["tools"]]


def call(ten, args, token=tok):
    st, r = goi({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": ten, "arguments": args}},
                token)
    res = r["result"]
    return res["isError"], res["content"][0]["text"]


# ---- 2. tools/list ----
st, ds = ten_tool("suggest")
hub_ds = [t["name"] for t in run(mcp_hub._handle_one({"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                                                     "suggest", True, False, Path(brain), "phien", ""))
          ["result"]["tools"]]
check("tools/list giữ nguyên danh sách của hub", ds[:len(hub_ds)] == hub_ds, (ds[:5], hub_ds[:5]))
check("Chỉ đọc: thấy hai tool đọc, không thấy tool ghi",
      P.T_DANH_SACH in ds and P.T_DOC in ds and P.T_GHI not in ds, ds[-4:])
check("Ghi nháp: thấy cả tool ghi", P.T_GHI in ten_tool("auto")[1])
check("Toàn quyền: thấy cả tool ghi", P.T_GHI in ten_tool("full")[1])
check("không có token: 401", goi({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}, "sai")[0] == 401)

# ---- 3. tools/call ----
P.dat_muc_quyen(c, "suggest")
loi, txt = call(P.T_DANH_SACH, {})
ids = [x["id"] for x in json.loads(txt)["chats"]] if not loi else []
check("liệt kê: có hội thoại của chủ, không có hội thoại khách", s_chu in ids and s_khach not in ids, txt)
loi, txt = call(P.T_DOC, {"chat_id": s_chu})
check("đọc: đúng tin của hội thoại", not loi and "trả lời Kế hoạch tháng 11" in txt, txt)
loi, txt = call(P.T_DOC, {"chat_id": s_khach})
check("đọc hội thoại khách: từ chối", loi and "Không có hội thoại này" in txt, txt)
loi, txt = call(P.T_GHI, {"title": "Tết", "note": "Chốt ngân sách 50 triệu."})
check("Chỉ đọc gọi thẳng tool ghi: chặn", loi and "Chỉ đọc" in txt, txt)

P.dat_muc_quyen(c, "auto")
loi, txt = call(P.T_GHI, {"title": "Kế hoạch Tết", "note": "Chốt ngân sách 50 triệu.", "asked": "Lên kế hoạch Tết"})
sid = json.loads(txt).get("session_id") if not loi else None
row = store.get_session(sid) if sid else {}
check("Ghi nháp: ghi thành hội thoại 'Từ ChatGPT: ...'", row.get("title") == "Từ ChatGPT: Kế hoạch Tết", txt)
loi, txt = call(P.T_GHI, {"title": "Họp NCC", "note": "Chốt giá."}, tok_claude)
check("client quay về claude.ai: 'Từ Claude: ...' dù tự khai tên ChatGPT", not loi and "Từ Claude: Họp NCC" in txt, txt)
loi, txt = call(P.T_GHI, {"title": "Giá", "note": "Chốt giá."})
check("client quay về chatgpt.com: 'Từ ChatGPT: ...' dù tự khai tên Claude", not loi and "Từ ChatGPT: Giá" in txt, txt)
loi, txt = call(P.T_GHI, {"title": "", "note": "x"})
check("thiếu tiêu đề: lỗi đọc được", loi and "tiêu đề" in txt, txt)
mcp_hub.resolve_vault = lambda raw: (None, "", "")
loi, txt = call(P.T_DANH_SACH, {})
check("không có brain đang mở: lỗi đọc được", loi and "brain" in txt, txt)
mcp_hub.resolve_vault = lambda raw: (Path(brain), "phien", "")

# ---- 4. tin khác đi qua hub ----
st, r = goi({"jsonrpc": "2.0", "id": 3, "method": "ping"})
check("ping đi qua hub", st == 200 and r.get("id") == 3 and "result" in r, r)
st, r = goi({"jsonrpc": "2.0", "method": "notifications/initialized"})
check("thông báo: 202", st == 202, (st, r))
st, r = goi([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
             {"jsonrpc": "2.0", "method": "notifications/initialized"},
             {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": P.T_DOC, "arguments": {"chat_id": s_chu}}}])
check("lô: hai câu trả lời, đúng thứ tự, có tool của cửa",
      st == 200 and [x["id"] for x in r] == [1, 2] and P.T_DOC in [t["name"] for t in r[0]["result"]["tools"]], r)
st, r = goi(ValueError("hỏng"))
check("thân hỏng: hub trả lỗi parse", st == 400 and r["error"]["code"] == -32700, (st, r))

P._gate = lambda: None
st, ds = ten_tool("full")
check("lõi cũ: không có ba tool, hub vẫn chạy", st == 200 and not set(ds) & set(P._TOOL_CONG) and ds, ds[-3:])
loi, txt = call(P.T_DANH_SACH, {})
check("lõi cũ gọi thẳng tên: lỗi đọc được", loi and "0.441.0" in txt, txt)

check("không có ký tự gạch dài trong gói", "—" not in PLUGIN.read_text(encoding="utf-8"))

print()
if fails:
    print(f"FAIL {len(fails)}: {fails}")
    sys.exit(1)
print("OK - test_cong_hoi_thoai: all pass")
