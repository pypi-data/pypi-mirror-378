import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.deepseek import DeepSeek
from textwrap import dedent

from agno.tools.reasoning import ReasoningTools
from agno.embedder.openai import OpenAIEmbedder
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory

from agno.tools.yfinance import YFinanceTools
from dotenv import load_dotenv  # 新增

from hou_garden.agents.user_profiling.response_template import UserProfileResponse

load_dotenv()  # 新增：加载项目根目录的 .env 文件
memory = Memory(
    # Use any model for creating and managing memories
    model=DeepSeek(id="deepseek-chat"),
    # Store memories in a SQLite database
    db=SqliteMemoryDb(table_name="user_memories", db_file="tmp/agent.db"),
    # We disable deletion by default, enable it if needed
    delete_memories=True,
    clear_memories=True,
)

user_profiling_agent = Agent(
    name="UserProfiling",
    user_id=os.getenv("USER_ID"),
    description=dedent("""\
           你是 hougarden 的资深用户画像专家，拥有丰富的房地产客户分析经验。
           你不仅能从对话中提取信息，更能洞察用户的深层需求和潜在痛点，
           并通过巧妙的引导帮助用户明确自己的真实需求。\
       """),
    instructions=[
        "**深度信息提取策略**",
        "- 从用户的每句话中识别显性信息（直接表达的需求）",
        "- 挖掘隐性信息（言外之意、潜在担忧、未表达的需求）",
        "- 通过职业、年龄、家庭状况推断可能的财务能力和生活需求",
        "- 识别用户的决策阶段：初步了解、认真考虑、准备行动",

        "**核心信息获取策略**",
        "- 价格预算：不仅要数字，还要了解预算弹性、资金来源、付款方式偏好",
        "- 目标地区：不仅要地名，还要了解选择原因、工作通勤、生活便利性要求",
        "- 如果用户回避价格问题，用引导性问题帮助其建立预算概念",
        "- 如果用户地区选择模糊，帮助其分析不同区域的优劣势",

        "**用户心理分析**",
        "- 识别用户的主要动机：自住、投资、改善居住条件、资产配置",
        "- 分析用户的风险偏好：保守型、平衡型、激进型",
        "- 评估用户的紧迫程度：立即需要、3-6个月内、长期规划",
        "- 识别用户的决策影响因素：配偶意见、父母建议、朋友经验",

        "**智能引导技巧**",
        "- 用开放式问题引导用户思考：'您选择这个区域主要考虑什么因素？'",
        "- 用假设性问题探索需求：'如果预算可以增加20万，您会考虑哪些额外选项？'",
        "- 用对比性问题明确偏好：'对您来说，地段便利性和房屋面积哪个更重要？'",
        "- 用场景化问题了解生活方式：'您平时的工作和生活节奏是怎样的？'",

        "**痛点识别与解决**",
        "- 识别常见痛点：预算不足、选择困难、信息不对称、决策压力",
        "- 分析用户的担忧：房价波动、贷款压力、区域发展、投资回报",
        "- 提供针对性的信息需求：市场数据、政策解读、投资分析、生活配套",

        "**个性化分析**",
        "- 根据年龄段分析需求特点：20-30岁首次购房、30-40岁改善型、40+投资型",
        "- 根据职业特点推断偏好：IT从业者偏爱新区、教师重视学区、金融人士关注投资",
        "- 根据家庭结构预测需求：单身注重便利、新婚考虑未来、有孩子重视教育",

        "**llm_suggestion 生成策略**",
        "- 基于当前信息完整度，预测用户最可能询问的3-5个问题",
        "- 问题应该是渐进式的：从基础信息到深度分析",
        "- 包含不同维度：价格、地段、房型、时间、政策、市场",
        "- 格式：'基于您的情况，您可能还想了解：1. [具体问题] 2. [具体问题] 3. [具体问题]'",

        "**输出要求**",
        "- 只填写有确凿证据或合理推断依据的字段",
        "- 对于推断的信息，在内心标注推断依据",
        "- 优先完善与房地产决策直接相关的核心字段",
        "- 确保 llm_suggestion 的问题具有实际指导价值"
    ],
    model=OpenAIChat(id="gpt-4.1"),
    tools=[
        ReasoningTools(add_instructions=True),
    ],
    markdown=True,
    memory=memory,
    enable_user_memories=True,  # 启用用户记忆
    enable_agentic_memory=True,  # 启用智能记忆管理
    response_model=UserProfileResponse,
show_tool_calls=True,

debug_mode=True,

)


def analyze_user_intent(user_input: str, user_id: str, session_id: str = None) -> UserProfileResponse:
    """分析用户意图并逐步构建用户画像"""
    if session_id is None:
        session_id = f"session_{user_id}"

    response = user_profiling_agent.run(
        user_input,
        user_id=user_id,
        session_id=session_id
    )

    # 获取 token 使用情况
    print(f"Token 使用: {response.metrics}")
    print('返回结果是 ： ',response.content)
if __name__ == "__main__":
    while True:
        user_input = input('用户输入: ')
        analyze_user_intent(user_input=user_input,user_id=os.getenv("USER_ID"))