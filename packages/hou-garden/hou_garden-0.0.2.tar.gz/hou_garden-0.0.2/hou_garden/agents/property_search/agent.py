import os
from textwrap import dedent
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory

from hou_garden.agents.tools.search_hd_data import search_hd_data

load_dotenv()  # allow .env-based secrets

# Simple persistent memory for retaining recent confirmed query conditions
_memory = Memory(
    model=OpenAIChat(id=os.getenv("LLM_MODEL_NAME", "gpt-4.1")),
    db=SqliteMemoryDb(table_name="user_memories__property_search", db_file="tmp/agent.db"),
    delete_memories=True,
    clear_memories=True,
)

property_search_agent = Agent(
    name="PropertySearch",
    description=dedent(
        """
        你是 HouGarden 的房源检索智能体。唯一可用检索工具是 search_hd_data。
        请优先使用用户画像（user_profiling 输出）和当前对话补齐的关键信息（预算、区域/学区、房型用途、通勤、
        时间线、房龄/土地、风险偏好），在条件充分时调用 search_hd_data 获取结果；不要臆造或二次改写工具输出。
        条件不足时仅提出不超过 3 个关键澄清问题，并可给出合理默认值建议。
        """
    ),
    instructions=[
        "仅使用 search_hd_data 作为检索工具；不得调用其他工具或伪造结果",
        "先用画像数据，不足再从当前对话补齐关键信息",
        "参数严格格式：prn 用‘万’为单位，仅支持 'X-Y'；例如 200-300 表示 200万-300万",
        "数量字段（bern/barn/pkn）允许中文或阿拉伯数字：如 ‘3房’ ‘至少三房’ ‘两个车位’；必要时转为 '3' 或 '3+'",
        "房产类型 ptn 允许别名：联排/联排别墅→城市屋，排屋→排房，apartment→公寓，villa/别墅→独立屋",
        "当关键条件足够时再调用工具；返回值 filters/explain/errors 原样呈现，不做二次改写",
        "默认分页 page=1, pageSize=10；除非用户明确要求更多或更少",
        "当必须澄清时，提出 ≤3 个关键问题，并建议默认值；能检索就不追问",
        "如画像与对话冲突，明确标注并提供备选入参",
        "严禁自行构造/臆造数据：若工具无结果或条件不足以检索，直接返回空或明确无结果，绝不生成虚假条目",
    ],
    model=OpenAIChat(id=os.getenv("LLM_MODEL_NAME", "gpt-4.1")),
    tools=[search_hd_data],
    markdown=True,
    memory=_memory,
    enable_user_memories=True,
    enable_agentic_memory=True,
    show_tool_calls=True,
    debug_mode=True,
)
