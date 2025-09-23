import requests, json
import datetime as dt
import time
BASE_URL = "http://3.106.195.98/v1"
API_KEY  = "app-lZAHzfrNYCdLa3IsU5UCRbRK"
USER_ID  = "wt-04"
HEADERS  = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
LOG_FILE = f"{USER_ID}.jsonl"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

def now_str():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(obj: dict):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def chat_stream(query: str, conversation_id: str | None) -> tuple[str, str | None]:
    """
    发起一次流式对话：边流式打印、边记录时间。
    返回 (完整回答, conversation_id)
    """
    url = f"{BASE_URL}/chat-messages"
    payload = {
        "query": query,
        "inputs": {
            # 你的 App 如果把 user_id 设为必填，这里必须传
            "user_id": USER_ID
        },
        "response_mode": "streaming",
        "user": USER_ID,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    # ===== 打印 & 记录：用户消息 =====
    user_ts = now_str()
    print(f"\n你 [{user_ts}]: {query}")
    log_event({"role": "user", "text": query, "ts": user_ts})

    with requests.post(url, headers=HEADERS, json=payload, stream=True) as r:
        if not r.ok:
            print("\n== Request Error ==")
            print("Status:", r.status_code)
            print("Body:", r.text)
            r.raise_for_status()

        full_answer = []
        got_first_chunk = False
        as_start_ts_str = None
        as_end_ts_str = None
        new_conversation_id = conversation_id
        last_task_id = None
        t0 = None  # 用于计算耗时

        # 先把“助手 [时间]：”打印出来，等第一块文本到时补时间
        # 为了视觉好看，第一块到来时再补时间
        printed_header = False

        for raw in r.iter_lines(decode_unicode=True):
            if not raw:
                continue
            if not raw.startswith("data: "):
                continue
            data_str = raw[6:]
            try:
                data = json.loads(data_str)
            except Exception:
                continue

            event = data.get("event")
            if "task_id" in data:
                last_task_id = data["task_id"]

            if event == "message":
                if not got_first_chunk:
                    got_first_chunk = True
                    t0 = time.perf_counter()
                    as_start_ts_str = now_str()
                    if not printed_header:
                        print(f"助手 [{as_start_ts_str}]: ", end="", flush=True)
                        printed_header = True
                token = data.get("answer", "")
                if token:
                    print(token, end="", flush=True)
                    full_answer.append(token)
                if not new_conversation_id:
                    new_conversation_id = data.get("conversation_id", new_conversation_id)

            elif event == "message_end":
                as_end_ts_str = now_str()
                break

            elif event == "error":
                msg = data.get("message", "stream error")
                print(f"\n[Error] {msg}")
                as_end_ts_str = now_str()
                break
            # 其他 workflow/node 事件不打印

        # 收尾打印：换行 + 摘要（结束时间 / 耗时 / 会话ID）
        print()  # 换行
        if as_end_ts_str is None:
            as_end_ts_str = now_str()
        elapsed = (time.perf_counter() - t0) if t0 else 0.0
        ans_text = "".join(full_answer) if full_answer else ""

        print(f"—— 结束 [{as_end_ts_str}] | 耗时 {elapsed:.2f}s"
              + (f" | conversation_id: {new_conversation_id}" if new_conversation_id else ""))

        # 记录助手消息
        log_event({
            "role": "assistant",
            "text": ans_text,
            "ts_start": as_start_ts_str or as_end_ts_str,
            "ts_end": as_end_ts_str,
            "elapsed_sec": round(elapsed, 3),
            "conversation_id": new_conversation_id,
            "task_id": last_task_id
        })

        # 告知写到哪：当前目录下 chat_log.jsonl
        print(f"(已记录到 ./{LOG_FILE})")

        return ans_text, new_conversation_id

def main():
    if not API_KEY or API_KEY == "YOUR_API_KEY":
        print("请先设置环境变量 DIFY_API_KEY 或在代码里填入 API_KEY。")
    print("已连接。输入内容后回车发送。/exit 退出。\n")
    conversation_id = None

    while True:
        try:
            user_input = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见～")
            break

        if not user_input:
            continue
        if user_input.lower() in ("/exit", "exit", "quit", "/quit"):
            print("已退出。")
            break

        try:
            _, conversation_id = chat_stream(user_input, conversation_id)
        except requests.HTTPError:
            pass
        except Exception as e:
            print(f"[本地异常] {e}")

if __name__ == "__main__":
    main()