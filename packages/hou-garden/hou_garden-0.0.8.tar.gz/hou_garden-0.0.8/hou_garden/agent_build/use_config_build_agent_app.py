# build_team.py
import os
from pathlib import Path

from agno.db.sqlite import SqliteDb
from dotenv import load_dotenv
from importlib import import_module
from hydra import initialize, compose
from hydra import initialize_config_dir
import asyncio
from agno.tools.reasoning import ReasoningTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.duckduckgo import DuckDuckGoTools

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.deepseek import DeepSeek
from sympy.testing.pytest import tooslow

# Memory API varies across agno versions; support multiple layouts or disable gracefully
MEMORY_AVAILABLE = False
try:
    # Legacy v2 path (commonly used in this repo)
    from agno.memory.v2.memory import Memory  # type: ignore
    from agno.memory.v2.db.sqlite import SqliteMemoryDb  # type: ignore
    MEMORY_AVAILABLE = True
except Exception:
    try:
        # Alternate newer-style modules
        from agno.memory.memory import Memory  # type: ignore
        from agno.memory.db.sqlite import SqliteMemoryDb  # type: ignore
        MEMORY_AVAILABLE = True
    except Exception:
        # Memory not available; we will run without persisted memory
        Memory = None  # type: ignore
        SqliteMemoryDb = None  # type: ignore

# Tools
from hou_garden.agents.tools.search_hd_data import search_hd_data

def _build_model(conf):
    # Provider-specific kwargs (avoid sending unsupported keys)
    base_kwargs = {}
    for key in ("api_key", "base_url", "temperature", "top_p"):
        if hasattr(conf, key):
            val = getattr(conf, key)
            if val is not None:
                base_kwargs[key] = val

    # Determine a tokens value from any of the common config fields
    tokens_val = None
    for key in ("max_completion_tokens", "max_output_tokens", "max_tokens"):
        if hasattr(conf, key) and getattr(conf, key) is not None:
            tokens_val = getattr(conf, key)
            break

    if conf.provider == "openai":
        # Newer OpenAI models (gpt-4.1/gpt-5/4o family) do not support temperature/top_p overrides.
        openai_kwargs = {k: v for k, v in base_kwargs.items() if k not in ("temperature", "top_p")}
        # Newer OpenAI models (gpt-4.1/gpt-4o/gpt-5) require max_completion_tokens instead of max_tokens
        if tokens_val is not None:
            openai_kwargs["max_completion_tokens"] = tokens_val
        return OpenAIChat(id=conf.id, **openai_kwargs)
    elif conf.provider == "deepseek":
        ds_kwargs = dict(base_kwargs)
        if tokens_val is not None:
            ds_kwargs["max_tokens"] = tokens_val
        return DeepSeek(id=conf.id, **ds_kwargs)
    else:
        raise ValueError(f"Unknown provider: {conf.provider}")

def _build_memory(mem_model_conf, backend_conf):
    if not MEMORY_AVAILABLE:
        return None
    model = _build_model(mem_model_conf)
    db_file = backend_conf.db_file
    db_dir = os.path.dirname(db_file)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    db = SqliteMemoryDb(table_name=getattr(backend_conf, "table_name", "user_memories"), db_file=db_file)
    return Memory(
        model=model,
        db=db,
        delete_memories=getattr(backend_conf, "delete_memories", True),
        clear_memories=getattr(backend_conf, "clear_memories", True),
    )
#sasas
def build_user_profiling_agent(cfg) -> Agent:
    base = cfg.agents.user_profiling
    up = cfg.app.agents.user_profiling
    chat = _build_model(up.chat)
    memory = _build_memory(up.memory, up.memory_backend)

    # 如需工具，可从配置里实例化；此处略
    tools = [ReasoningTools(add_instructions=True)]

    # Build with a minimal, broadly-compatible signature
    agent_kwargs = dict(
        name=str(base.name),
        model=chat,
        tools=tools,
        add_name_to_context=True,

    )
    # Attach optional fields only if commonly supported
    if getattr(base, "description", None):
        agent_kwargs["description"] = str(base.description)
    if hasattr(base, "instructions") and base.instructions is not None:
        instr = base.instructions
        agent_kwargs["instructions"] = (
            instr if isinstance(instr, (list, tuple)) else [str(instr)]
        )

    # Only set response_model if it is not a plain string path
    resp_model = getattr(base, "response_model", None)
    if resp_model is not None and not isinstance(resp_model, str):
        agent_kwargs["response_model"] = resp_model

    return Agent(**agent_kwargs)

def build_planner_team(cfg, members: list[Agent]) -> Team:
    p = cfg.app.team.planner
    base = p.base  # agents.planner 静态定义
    chat = _build_model(p.chat)
    memory = _build_memory(p.memory, p.memory_backend)

    # 将配置里“逻辑名”映射到真实成员（这里我们只演示 user_profiling）
    # 你也可以按 p.members 列表遍历并动态匹配
    # Build Team with minimal, broadly-compatible signature
    db = SqliteDb(db_file="hou_garden_team.db")

    team_kwargs = dict(
        name=str(base.name),
        model=chat,
        members=members,
        debug_mode=True,
        db=db,
        determine_input_for_members=False,
        show_members_responses=True,
        enable_user_memories=True,
        enable_session_summaries=True,
        add_history_to_context=True,
        num_history_runs=3,
        delegate_task_to_all_members=True,
        respond_directly=False,
        tools = [GoogleSearchTools(),DuckDuckGoTools()]
    )

    # Optional fields from base planner config
    if getattr(base, "description", None):
        team_kwargs["description"] = str(base.description)
    if hasattr(base, "instructions") and base.instructions is not None:
        tinstr = base.instructions
        team_kwargs["instructions"] = (
            tinstr if isinstance(tinstr, (list, tuple)) else [str(tinstr)]
        )
    if memory is not None:
        team_kwargs["memory"] = memory

    return Team(**team_kwargs)


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    # Use absolute path to configs to avoid CWD issues
    config_dir = str(Path(__file__).resolve().parents[2] / "configs")
    with initialize_config_dir(version_base="1.3", config_dir=config_dir):
        cfg = compose(config_name="apps/ask-hougarden.yaml")

    # Build members and team
    user_profiling_agent = build_user_profiling_agent(cfg)
    # property_search_agent = build_property_search_agent(cfg)
    hougarden_team = build_planner_team(cfg, members=[user_profiling_agent])

    # Non-interactive validation path for automation
    if os.getenv("HG_VALIDATE_CONFIG") == "1":
        print("validate_ok:", {
            "user_profiling": user_profiling_agent.name,
            "team": hougarden_team.name,
        })
        raise SystemExit(0)

    # Interactive loop
    while True:
        user_id = f"test_user_{os.getenv('USER_ID', 'demo')}"
        try:
            question = input("用户输入问题  : ")
        except EOFError:
            break
        hougarden_team.print_response(question, stream=True)

# 你好，我刚开始工作不久，想要买人生中第一套房子，主要是自住，但也想未来房价能涨点。你能先给我简单介绍一下现在的市场情况吗？

        # # Asynchronous execution
        # async for chunk in hougarden_team.arun("What is the weather in Tokyo?", stream=True, stream_intermediate_steps=True):
        #     print(chunk.content, end="", flush=True)
