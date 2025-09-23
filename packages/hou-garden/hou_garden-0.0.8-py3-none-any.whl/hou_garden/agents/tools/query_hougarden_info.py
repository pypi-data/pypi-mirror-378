# -*- coding: utf-8 -*-
"""
HouGarden 对话式检索 · Agno Tool 版本

- 读取 .env（OPENAI_API_KEY、HG_API_BASE、HG_AUTH_TOKEN、HG_LANG、HG_COUNTRY）
- 通过 LLM 将中文查询解析为结构化检索参数
- 解析地区 → 构造 URL → 请求 /api/v1/ai/houses
- 作为 Agno Tool 暴露：`query_hougarden_info(query, page=1, page_size=10, sort=0)`

依赖:
    pip install python-dotenv requests openai agno
"""

from typing import Any, Dict, Optional
import os
import json
import time
import datetime as dt
import urllib.parse
from pathlib import Path
import requests
from dotenv import load_dotenv
from agno.tools import tool
from openai import OpenAI
from omegaconf import OmegaConf

# =========================
# 环境与常量
# =========================

CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "tools" / "query_hougarden_info.yaml"

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
MODEL = os.getenv("MODEL", "gpt-5-mini").strip()
HG_API_BASE = os.getenv("HG_API_BASE", "https://api4.hougarden.com").rstrip("/")
HG_AUTH_TOKEN = os.getenv("HG_AUTH_TOKEN", "").strip()  # 形如 "Public xxx"
HG_LANG = os.getenv("HG_LANG", "zh-CN").strip()
HG_COUNTRY = os.getenv("HG_COUNTRY", "nz").strip()


def _apply_settings_from_config() -> None:
    global MODEL, HG_API_BASE, HG_AUTH_TOKEN, HG_LANG, HG_COUNTRY, COMBINE_PATH, HOUSES_PATH
    if not CONFIG_PATH.exists():
        return
    try:
        cfg = OmegaConf.load(CONFIG_PATH)
    except Exception:
        return
    data = cfg.get("query_hougarden_info") or cfg
    model = data.get("model")
    if model:
        MODEL = str(model).strip()
    api_base = data.get("hg_api_base")
    if api_base:
        HG_API_BASE = str(api_base).rstrip("/")
    auth_token = data.get("hg_auth_token")
    if auth_token is not None:
        HG_AUTH_TOKEN = str(auth_token).strip()
    accept_language = data.get("accept_language")
    if accept_language:
        HG_LANG = str(accept_language).strip()
    country_iso = data.get("country_iso")
    if country_iso:
        HG_COUNTRY = str(country_iso).strip()
    combine_path = data.get("combine_path")
    if combine_path:
        globals()["COMBINE_PATH"] = str(combine_path)
    houses_path = data.get("houses_path")
    if houses_path:
        globals()["HOUSES_PATH"] = str(houses_path)


COMBINE_PATH = "/api/v5.1.8/property-search-combine"
HOUSES_PATH = "/api/v1/ai/houses"
_apply_settings_from_config()

BASE_HEADERS = {
    "Authorization": HG_AUTH_TOKEN,
    "client": "web",
    "Countryiso": HG_COUNTRY,
    "Accept-Language": HG_LANG,
    "Accept": "application/json, text/plain, */*",
}

# 可选：常见地名兜底（当接口解析失败时使用）
KNOWN_LOCATIONS = {
    "flat bush": ("suburbId", "69"),
    "remuera": ("suburbId", "1962"),
}

# OpenAI 客户端（惰性初始化，避免在无 Key 环境下直接退出）
_openai_client: Optional[OpenAI] = None

def _get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("missing_openai_api_key")
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


# =========================
# 工具函数
# =========================

def now_ts():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _pick_param_name_by_level(level: str) -> str:
    l = (level or "").strip().lower()
    if l == "suburb":
        return "suburbId"
    if l == "district":
        return "districtId"
    if l == "region":
        return "regionId"
    # 极端兜底
    return "suburbId"

def resolve_location_ids(keyword: str):
    """
    解析地区：
    1) 若 filters[].paramsMeta.suburb 只有 1 个 → 直接用；
    2) 若顶层 locations 只有 1 条 → 直接用；
    3) 否则按 suburb > district > region 的顺序取第一个；
    4) 两轮语言尝试：先用 .env 的 Accept-Language，再用 en；
    5) 最后兜底 KNOWN_LOCATIONS。
    返回: (param_name, id_str) 或 (None, None)
    """
    if not keyword:
        return None, None

    def try_once(accept_lang: str):
        url = f"{HG_API_BASE}{COMBINE_PATH}"
        headers = dict(BASE_HEADERS, **{"Accept-Language": accept_lang})
        r = requests.get(url, headers=headers, params={"keyword": keyword}, timeout=10)
        r.raise_for_status()
        return r.json() if r.text else {}

    def from_filters_one_suburb(data):
        for item in (data.get("filters") or []):
            try:
                if (item.get("type") == "suburb"
                    and isinstance(item.get("paramsMeta"), dict)):
                    subs = item["paramsMeta"].get("suburb") or []
                    if isinstance(subs, list) and len(subs) == 1:
                        sid = str(subs[0].get("id") or subs[0].get("value"))
                        if sid and sid != "0":
                            return "suburbId", sid
            except Exception:
                continue
        return None, None

    def from_locations(data):
        locs = data.get("locations") or []
        # 只有一个地区 → 直接用它
        if isinstance(locs, list) and len(locs) == 1:
            one = locs[0] or {}
            level = one.get("level") or ""
            pid = str(one.get("id", "") or "")
            if pid:
                return _pick_param_name_by_level(level), pid

        # 多个 → suburb/district/region 优先
        def first_with_level(target):
            for it in locs:
                if (it or {}).get("level", "").lower() == target:
                    pid = str(it.get("id", "") or "")
                    if pid:
                        return _pick_param_name_by_level(target), pid
            return None, None

        for pri in ("suburb", "district", "region"):
            p, i = first_with_level(pri)
            if p and i:
                return p, i

        # 多个但没有标准 level，取第一个的 id，当作 suburbId 兜底
        if locs:
            pid = str((locs[0] or {}).get("id", "") or "")
            if pid:
                return "suburbId", pid
        return None, None

    # 1) 当前语言
    try:
        data = try_once(HG_LANG)
        p, i = from_filters_one_suburb(data)
        if p and i:
            return p, i
        p, i = from_locations(data)
        if p and i:
            return p, i
    except Exception:
        pass

    # 2) 英文重试
    try:
        data = try_once("en")
        p, i = from_filters_one_suburb(data)
        if p and i:
            return p, i
        p, i = from_locations(data)
        if p and i:
            return p, i
    except Exception:
        pass

    # 3) 兜底
    k = (keyword or "").strip().lower().replace("-", " ")
    if k in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[k]

    return None, None


def build_filters_param(filters: dict) -> str:
    """
    将形如:
        {"ptn": ["1","2"], "bern": "3", "prn": ["10-100","100+"]}
    转为:
        "ptn_1,2_bern_3_prn_10-100,100%2B"
    注意：整体再交给 urlencode 处理，这里只拼语义。
    """
    if not filters:
        return ""
    parts = []
    for alias, val in filters.items():
        if val is None:
            continue
        if isinstance(val, (list, tuple)):
            vals = [str(v) for v in val if str(v)]
            if not vals:
                continue
            parts.append(f"{alias}_{','.join(vals)}")
        else:
            sval = str(val)
            if not sval:
                continue
            parts.append(f"{alias}_{sval}")
    return "_".join(parts)


# =========================
# LLM 解析
# =========================

SYSTEM_PROMPT = """你是房源检索助手。将用户中文问题解析为 HouGarden 检索参数的 JSON，不要多余文字。
仅返回一行 JSON，字段如下：
- location_keywords: string 地区关键字（如 "Remuera"、"Flat Bush"）
- typeId: number 房源大类（住宅=1，商业=2，租房=3，建地=9 等；不确定就用 1）
- filters: object，键为 alias（字符串），值为字符串或字符串数组；允许多选
- page: number，默认 1
- pageSize: number，默认 10（1~100）
- sort: number，默认 0

filters 的 alias 及取值（均为字符串，允许多选）：
- prn: 价格，如 "10-100", "0-100", "100+" 等
- ptn: 房产类型 1独立屋 2公寓 3单元房 4城市屋 5排房 6自住投资 7乡村别墅 8乡村住宅建地 9建地
- stl: 建筑风格 "1"…"6"（1当代、2豪华现代、3传统、4乡村、5海滩热带、6维多利亚/地中海）
- bern: 卧室数 "1"…"5"（1:1房 ... 5:5+）
- barn: 浴室数 "1"…"5"（1:1卫 ... 5:5+）
- pkn: 车位数 "1"…"5"（1:1车 ... 5:5+）
- sm: 价格方式 "1","2","3","4","5","6","7","9","17"
- lt: 上市时间 "1","3","7","30","90"
- fa: 建筑面积 "1"…"7"（<50, 50-100, 100-150, 150-200, 200-250, 250-300, 300+）
- la: 土地面积 "1"…"4"（<200, 200-500, 500-1000, 1000+）
- yb: 建筑年代 "1"…"7"（60s=1, 70s=2, 80s=3, 90s=4, 2000s=5, 2010s=6, 新房(12个月内)=7）
- tt: 产权类型 "1"…"9"
- cr: 政府估价 "1"…"5"（1:<50万；2:50-100万；3:100-200万；4:200-500万；5:>500万）
- utz: Zoning "19","18","60","8","20","23","999"
- sz: 学校评分 "1"…"5" （1:10分 ... 5:6-）
- oh: 开放日，值格式 "YYYYMMDD"

注意：
- 尽量从问题中识别出 ptn/bern/barn/pkn/yb 等，没给就别乱填。
- 只返回 JSON，不要解释。
- 示例：
  输入：Remuera60年代建造的独立别墅有哪些？
  输出：{"location_keywords":"Remuera","typeId":1,"filters":{"ptn":["1"],"yb":["1"]},"page":1,"pageSize":10,"sort":0}

  输入：flat-bush浴室数量在 2-5个的，车位数量在 2-4个的？
  输出：{"location_keywords":"Flat Bush","typeId":1,"filters":{"barn":["2","3","4","5"],"pkn":["2","3","4"]},"page":1,"pageSize":10,"sort":0}
"""

def llm_parse_query(user_text: str) -> dict:
    """
    用 LLM 将中文问题解析为结构化检索 JSON。
    仅使用 system+user 两条消息，避免不必要的 tool 结构。
    """
    client = _get_openai_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text.strip()},
        ],
        # 不显式设置 temperature，避免某些模型不支持自定义温度的报错
    )
    content = (resp.choices[0].message.content or "").strip()
    # 只取第一行（防守）
    first_line = content.splitlines()[0]
    try:
        data = json.loads(first_line)
        # 基础字段兜底
        data.setdefault("page", 1)
        data.setdefault("pageSize", 10)
        data.setdefault("sort", 0)
        data.setdefault("typeId", 1)
        data.setdefault("filters", {})
        return data
    except Exception:
        # 返回给上层决定如何报错
        return {"_raw": content, "_error": "parse_json_failed"}


# =========================
# 检索主流程
# =========================

def _query_hougarden_info_core(
    query: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    sort: Optional[int] = None,
    surrounding: Optional[int] = None,
) -> Dict[str, Any]:
    """核心实现：根据自然语言查询 HouGarden 房源，返回结构化结果。"""
    t0 = time.time()

    # 1) LLM 解析
    try:
        parsed = llm_parse_query(query)
    except RuntimeError as e:
        # OpenAI Key 缺失等初始化错误
        return {"ok": False, "error": str(e), "stage": "llm_init"}

    if "_error" in parsed:
        return {"ok": False, "error": "llm_parse_json_failed", "raw": parsed.get("_raw")}

    # 允许外部 page/page_size 覆盖 LLM 结果
    location_keywords = parsed.get("location_keywords") or ""
    type_id = int(parsed.get("typeId") or 1)
    filters = parsed.get("filters") or {}
    def _pick_int(override: Optional[int], parsed_value: Any, fallback: int) -> int:
        for candidate in (override, parsed_value, fallback):
            try:
                if candidate is None or candidate == "":
                    continue
                return int(candidate)
            except (TypeError, ValueError):
                continue
        return fallback

    def _pick_surrounding(override: Optional[int], parsed_value: Any) -> Optional[int]:
        for candidate in (override, parsed_value):
            try:
                if candidate is None or candidate == "":
                    continue
                value = int(candidate)
                if value in (0, 1):
                    return value
            except (TypeError, ValueError):
                continue
        return None

    pg = max(1, _pick_int(page, parsed.get("page"), 1))
    ps = max(1, _pick_int(page_size, parsed.get("pageSize"), 10))
    srt = _pick_int(sort, parsed.get("sort"), 0)
    surrounding_value = _pick_surrounding(surrounding, parsed.get("surrounding"))

    if surrounding_value is None:
        normalized_query = query or ""
        lower_query = normalized_query.lower()
        positive_tokens = [
            "周边",
            "附近",
            "周围",
            "邻近",
            "nearby",
            "surrounding",
        ]
        negative_tokens = [
            "不含周边",
            "不要周边",
            "只要本区域",
            "仅查本区域",
            "exclude nearby",
            "exclude surrounding",
            "surrounding=0",
        ]
        has_positive = any(token in normalized_query for token in positive_tokens)
        has_positive = has_positive or any(token in lower_query for token in ("nearby", "surrounding"))
        has_negative = any(token in normalized_query for token in negative_tokens)
        has_negative = has_negative or any(token in lower_query for token in ("exclude nearby", "exclude surrounding"))
        if has_positive and not has_negative:
            surrounding_value = 1

    # 2) 地区解析
    loc_param, loc_id = resolve_location_ids(location_keywords)
    if not (loc_param and loc_id):
        return {
            "ok": False,
            "error": "location_resolve_failed",
            "parsed": parsed,
            "location_keywords": location_keywords,
        }

    # 3) 构造 filters 字符串
    filters_str = build_filters_param(filters)

    # 4) 发起检索
    params = {
        "typeId": type_id,
        "page": pg,
        "pageSize": ps,
        "sort": srt,
        "filters": filters_str,
        loc_param: loc_id,
    }
    if surrounding_value == 1:
        params["surrounding"] = 1
    qs = urllib.parse.urlencode(params, doseq=False, safe=",+-")
    url = f"{HG_API_BASE}{HOUSES_PATH}?{qs}"

    try:
        r = requests.get(url, headers=BASE_HEADERS, timeout=15)
        status = r.status_code
        if status != 200:
            return {
                "ok": False,
                "error": f"http_{status}",
                "final_url": url,
                "body": r.text[:1000],
            }
        data = r.json() if r.text else {}
    except Exception as e:
        return {"ok": False, "error": f"request_exception: {e}", "final_url": url}

    meta = data.get("meta") or {}
    items = data.get("items") or []
    t1 = time.time()

    return {
        "ok": True,
        "final_url": url,
        "meta": meta,
        "items": items,
        "location": {"param": loc_param, "id": loc_id, "keyword": location_keywords},
        "filters_str": filters_str,
        "parsed": parsed,
        "surrounding": surrounding_value,
        "duration_ms": int((t1 - t0) * 1000),
    }


@tool(name="query_hougarden_info", description="根据中文/英文自然语言查询 HouGarden 房源，支持分页与常见筛选条件（建筑面积、上市时间、卧室数等）。")
def query_hougarden_info(
    query: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    sort: Optional[int] = None,
    surrounding: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Agno Tool 包装：转调核心实现。
    """
    return _query_hougarden_info_core(
        query=query,
        page=page,
        page_size=page_size,
        sort=sort,
        surrounding=surrounding,
    )


# =========================
# 入口 · 默认查询 + 交互循环
# =========================

if __name__ == "__main__":
    # 简易本地调试入口
    print(f"[{now_ts()}] 已加载 .env，MODEL={MODEL}，Country={HG_COUNTRY}，Lang={HG_LANG}")
    demo_q = "Epsom 建筑面积 100到200 平，上市时间 2000 年以后的房子"
    print('example : ', demo_q)
    while True:
        user_input = input('请输入你要查询的条件  : ',)
        t1 = time.time()
        out = _query_hougarden_info_core(user_input, page=1, page_size=5)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        print('花费时间 : ',time.time()-t1)
