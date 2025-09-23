import os

from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from textwrap import dedent

from hou_garden.agents.user_profiling.agent import user_profiling_agent

memory = Memory(
    # Use any model for creating and managing memories
    model=DeepSeek(id="deepseek-chat"),
    # Store memories in a SQLite database
    db=SqliteMemoryDb(table_name="user_memories", db_file="tmp/team.db"),
    # We disable deletion by default, enable it if needed
    delete_memories=True,
    clear_memories=True,
)

# 用户画像专家智能体（团队成员）

# HouGarden 团队（Team 本身就是 Planner）
hougarden_team = Team(
    name="HouGarden_Team",
    mode="coordinate",  # 协调模式
    model=OpenAIChat(id="gpt-4.1"),
    user_id=os.getenv("USER_ID"),
    # 只添加专家智能体作为成员
    members=[user_profiling_agent],
    memory=memory,
    # Team 的描述（这就是 Planner 的角色定义）
    description=dedent("""\
        你是 HouGarden 房地产智能客服系统的首席编排智能体。
        你是用户唯一的对话接口，负责理解用户意图、制定执行计划并协调专家团队。\
    """),

    # Team 的指令（这就是 Planner 的工作流程）
    instructions=[
        "**高级对话管理**",
        "1. 建立信任关系：展现专业性，理解用户处境，提供有价值的见解",
        "2. 渐进式信息收集：不要一次性询问太多，让对话自然流畅",
        "3. 智能信息整合：将专家分析转化为用户易懂的建议",
        "4. 主动价值提供：即使信息不完整，也要给出阶段性的有用建议",

        "**核心信息获取策略**",
        "- 价格预算获取：如果用户回避，先了解其收入情况或现有资产",
        "- 地区选择引导：如果用户不确定，则根据下面这些信息,分析用户的需求重点: ",
        """
        根据房地产市场的特性，以及购房者常考虑的因素，以下是我认为除了“价格”和“位置”之外，可能影响购房决策的前十个关键因素：
        
        1. **目的** (Purpose)
        
           * 自住还是投资将极大影响购房者的选择。自住的购房者通常更加看重生活质量、学区和安全性；而投资者则更加注重增值潜力、租金回报等。
        
        2. **预算/价格区间** (Budget/Price Range)
        
           * 除了位置外，预算是购房决策中最核心的因素，决定了购房者的选择范围。
        
        3. **房产类型** (Property Type)
        
           * 是选择独立屋、公寓、联排别墅，还是其他类型的房产，直接影响购房者的舒适度、使用功能以及未来增值空间。
        
        4. **学区资源** (Education Resources)
        
           * 特别是对于有子女的家庭，学区优劣直接影响到购房的决策。好的学校是很多家庭选择住宅区域的首要条件。
        
        5. **社区安全性** (Community Safety)
        
           * 社区的治安状况对许多购房者来说是一个决定性因素，尤其是对于有子女的家庭。一个安全的社区意味着更高的生活质量和长期居住的稳定性。
        
        6. **交通和通勤** (Commute & Transportation)
        
           * 便利的交通和适中的通勤时间对于购房者的决策非常重要。特别是在大城市中，通勤时间长会极大影响生活质量，因此通勤条件对购房者至关重要。
        
        7. **房屋面积及布局** (Property Size & Layout)
        
           * 房屋的面积、卧室数量、客厅功能等布局设计会直接影响购房者的居住舒适度。不同的家庭需求对于房屋空间的要求有所不同。
        
        8. **周边设施** (Amenities)
        
           * 附近是否有医院、商店、公园等设施，能大大提高购房者的生活便利性。尤其是在一些大型社区，周边设施完善的房产通常更具吸引力。
        
        9. **贷款条件和可负担性** (Loan & Affordability)
        
           * 是否能够获得贷款及贷款额度，首付比例，贷款利率等也是购房决策中的关键因素，特别是对于首次购房者而言。
        
        10. **房屋年龄和状况** (Property Age & Condition)
        
        * 房屋的建造年代以及是否需要翻新，也是影响购房决策的重要因素。较新的房产可能意味着较少的维修成本，而老房子则可能需要更多的翻修和维护。


        """
        "- 通过用户画像专家的深度分析，识别用户真实需求和潜在痛点",

        "**对话引导技巧**",
        "- 当用户信息不足时，委托用户画像专家进行深度分析",
        "- 基于专家的 llm_suggestion，自然地引导下一轮对话",
        "- 用专业见解和市场洞察增加对话价值",
        "- 适时提供教育性内容，帮助用户做出更好的决策",


        "**回复生成原则**",
        "- 将专业分析转化为用户友好的语言",
        "- 保持专业但不失亲和力的沟通风格"
        
    ],

    # 团队配置
    enable_agentic_context=True,
    share_member_interactions=True,
    show_members_responses=True,  # 用户只看到最终回复

    markdown=True,
    show_tool_calls=True,
)

def main():
    while True:
        user_id = f"test_user_{os.getenv('USER_ID')}"
        response = hougarden_team.run(
            input('用户输入问题  : '),
            user_id=user_id,
            session_id='session_id_'+user_id,
            # stream=True,
            # stream_intermediate_steps=True
        )
        print(f"团队回复: {response.content}")


if __name__ == "__main__":
    main()