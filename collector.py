#!/usr/bin/env python3
"""시세를 받아 data.json을 만든다. 신호 판정은 하지 않는다(화면에서 계산)."""
import json, sys, time, datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
OUT = ROOT / "data.json"
CFG = json.loads((ROOT / "collector_config.json").read_text(encoding="utf-8"))
KEEP = 260          # 저장할 거래일 수 (52주 + 여유)
DATA_VERSION = 3


def series_from_df(sub):
    """DataFrame(Open/High/Low/Close...) -> {'d','c','h'} 또는 None"""
    if sub is None or len(sub) == 0 or "Close" not in sub:
        return None
    sub = sub.dropna(subset=["Close"]).tail(KEEP)
    if len(sub) < 2:
        return None
    hi = sub["High"] if "High" in sub else sub["Close"]
    return {
        "d": [i.strftime("%Y-%m-%d") for i in sub.index],
        "c": [round(float(x), 4) for x in sub["Close"]],
        "h": [round(float(h if h == h else c), 4) for h, c in zip(hi, sub["Close"])],
    }


def fetch(symbols):
    """{symbol: series or None}. 일괄 다운로드 후 실패분만 개별 재시도."""
    import yfinance as yf
    got = {s: None for s in symbols}
    try:
        df = yf.download(symbols, period="14mo", interval="1d", auto_adjust=False,
                         group_by="ticker", threads=False, progress=False)
        for s in symbols:
            try:
                got[s] = series_from_df(df[s] if len(symbols) > 1 else df)
            except Exception:
                pass
    except Exception as e:
        print("일괄 다운로드 실패:", e, file=sys.stderr)
    for s in [s for s in symbols if got[s] is None]:
        for attempt in range(2):
            time.sleep(2 + attempt * 3)
            try:
                got[s] = series_from_df(yf.Ticker(s).history(period="14mo", interval="1d", auto_adjust=False))
                if got[s]:
                    break
            except Exception as e:
                print(f"{s} 재시도 {attempt+1} 실패:", e, file=sys.stderr)
    return got


def quote_from_series(key, s):
    p, prev = s["c"][-1], s["c"][-2]
    if key == "^TNX" and p > 20:      # 예전 방식(금리x10) 호환
        p, prev = p / 10, prev / 10
    return {"p": round(p, 4), "prev": round(prev, 4),
            "chg": round((p / prev - 1) * 100, 3) if prev else None, "date": s["d"][-1]}


def build(fetch_fn, old=None):
    old = old or {}
    kr = CFG["kr_etfs"]
    ser_map = {s: s for s in CFG["series"]}
    for k, v in kr.items():
        if v.get("yahoo"):
            ser_map["KR_" + k] = v["yahoo"]
    quote_syms = list(CFG["index_quotes"])
    for g in CFG["flow_groups"]:
        quote_syms += [t for t, _ in g["items"]]
    quote_syms = list(dict.fromkeys(quote_syms))
    all_syms = list(dict.fromkeys(list(ser_map.values()) + quote_syms))

    got = fetch_fn(all_syms)
    out = {"v": DATA_VERSION, "series": {}, "quotes": {}, "errors": {}, "stale": {},
           "kr": {k: {"name": v["name"], "code": v.get("yahoo", "").split(".")[0]} for k, v in kr.items()},
           "flow": CFG["flow_groups"]}
    for key, ysym in ser_map.items():
        s = got.get(ysym)
        if s:
            out["series"][key] = s
        elif key in old.get("series", {}):
            out["series"][key] = old["series"][key]; out["stale"][key] = True
            out["errors"][key] = "이번 실행에서 받지 못해 이전 데이터를 표시"
        else:
            out["errors"][key] = "데이터를 받지 못함"
    for ysym in quote_syms:
        s = got.get(ysym)
        if s:
            out["quotes"][ysym] = quote_from_series(ysym, s)
        elif ysym in old.get("quotes", {}):
            q = dict(old["quotes"][ysym]); q["stale"] = True
            out["quotes"][ysym] = q
        else:
            out["errors"][ysym] = "데이터를 받지 못함"
    now = dt.datetime.now(ZoneInfo("Asia/Seoul"))
    out["fetchedAt"] = int(now.timestamp() * 1000)
    out["generated"] = now.strftime("%Y-%m-%d %H:%M KST")
    fresh = sum(1 for s in all_syms if got.get(s))
    return out, fresh, len(all_syms)


def main():
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    out, fresh, total = build(fetch, old)
    print(f"{fresh}/{total}개 새로 받음")
    if fresh == 0:
        print("아무것도 받지 못해 data.json을 바꾸지 않습니다.", file=sys.stderr)
        sys.exit(1)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    tmp.replace(OUT)
    if out["errors"]:
        print("받지 못한 항목:", ", ".join(out["errors"]), file=sys.stderr)


if __name__ == "__main__":
    main()
