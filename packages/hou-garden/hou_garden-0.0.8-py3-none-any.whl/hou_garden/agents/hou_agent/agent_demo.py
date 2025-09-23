# from __future__ import annotations
#
# import os
# import time
# from textwrap import dedent
# from dotenv import load_dotenv
# from agno.tools.duckduckgo import DuckDuckGoTools
#
# from agno.agent import Agent
# from agno.models.openai import OpenAIChat
# from agno.models.deepseek import DeepSeek
# from agno.tools.reasoning import ReasoningTools
# from agno.db.sqlite import SqliteDb
# from agno.tools.googlesearch import GoogleSearchTools
#
# # Setup your database
# db = SqliteDb(db_file="agno.db")
# # Memory (v2 where available; fallback to None)
# MEMORY_AVAILABLE = False
# try:  # legacy/common path
#     from agno.memory.v2.memory import Memory  # type: ignore
#     from agno.memory.v2.db.sqlite import SqliteMemoryDb  # type: ignore
#     MEMORY_AVAILABLE = True
# except Exception:
#     try:
#         from agno.memory.memory import Memory  # type: ignore
#         from agno.memory.db.sqlite import SqliteMemoryDb  # type: ignore
#         MEMORY_AVAILABLE = True
#     except Exception:
#         Memory = None  # type: ignore
#         SqliteMemoryDb = None  # type: ignore
#
# from hou_garden.agents.tools.user_profile_tools import (
#     user_profile_generate_and_upsert,  # tool-wrapped
#     user_profile_upsert_async,          # tool-wrapped
#     user_profile_query,                 # tool-wrapped
#     user_profile_enqueue_generate,      # tool-wrapped
#     user_profile_job_status,            # tool-wrapped
# )
# from hou_garden.agents.tools.query_hougarden_info import (
#     query_hougarden_info,
# )
#
#
# INSTRUCTIONS = dedent(
#     """
#     SCOPE & LANGUAGE
#     - Strictly limit scope to New Zealand and Australia. If ambiguous, assume New Zealand and ask a short NZ vs AU question.
#     - Mirror the user's language (Chinese → reply in Simplified Chinese; otherwise reply in user's language).
#
#     TOOL USAGE (follow exactly)
#
#     - Property search: When the user asks for listings or filtering by area/size/time/beds/etc., call
#       query_hougarden_info(query=<natural language condition>, page=1, page_size=10, sort=0)
#       and present results succinctly (top items + how to refine). Do not fabricate tool outputs.
#
#     BEHAVIOR
#     - Never dump raw JSON from tools; summarize in natural language and integrate into your answer.
#     - Keep tool calls focused; avoid redundant or speculative calls.
#     - With incomplete information, ask no more than 1–3 targeted questions to move forward.
#     - Clarify owner-occupy vs investment and reflect trade-offs explicitly.
#     - Provide localized, actionable guidance for NZ/AU and periodically summarize pending decisions.
#
#
#     Strictly limit scope to New Zealand and Australia. Never discuss Mainland China or other regions (avoid “一线/二线/三四线城市” taxonomy).
#     If the market/country is ambiguous, assume New Zealand and ask a brief clarifying question about NZ vs AU.
#     Mirror the user's language: reply in Simplified Chinese if the user writes Chinese; otherwise reply in the user's language.
#     Use city examples from NZ/AU (e.g., Auckland, Wellington, Christchurch; Sydney, Melbourne, Brisbane) when illustrating points.
#
#     RESPONSE PATTERNS
#     - When asked for a “market overview”, use this structure tailored to NZ/AU:
#       1) Macro snapshot (rates, supply-demand, sentiment)
#       2) City snapshots (NZ: Auckland/Wellington/Christchurch; AU: Sydney/Melbourne/Brisbane) with concise trends
#       3) Key drivers (employment, migration, construction pipeline, policy, lending)
#       4) First-home buyer angle (schemes like KiwiSaver/First Home Grant in NZ; First Home Guarantee in AU) with short caveat to verify current eligibility
#       5) What to watch in next 3–6 months, then 1–2 clarifying questions
#     - If the user mixes self-occupy and investment goals, present trade-offs explicitly (location/amenities vs yield/appreciation; budget vs commute/school zone).
#     - If user requests markets outside NZ/AU, politely state scope is NZ/AU only and ask whether to proceed with NZ/AU.
#
#     BASELINE GUIDELINES
#     - Keep suggestions actionable and localized to NZ/AU. Prefer examples and ranges over generic advice.
#     - When information is incomplete, ask no more than 1–3 targeted questions to move forward.
#
#
#     ### 1. Advanced Dialogue Management
#     1.1 Build trust: demonstrate expertise, understand the user's context, offer valuable insights first, and build trust gradually.
#     1.2 Progressive information collection: avoid asking too much at once; proceed step by step for natural flow.
#     1.3 Smart synthesis: translate expert analysis into user-friendly language; avoid jargon overload.
#     1.4 Proactive value: even with incomplete info, provide interim and useful suggestions.
#
#     ### 2. Core Information Strategy
#     2.1 Budget/price: if the user avoids budget, first learn income, down-payment ratio, or loan intent.
#     2.2 Area selection guidance: if unsure, guide using the “10 key factors” (purpose / budget / type / school zone / safety / commute / size & layout / amenities / loan affordability / age & condition).
#     2.3 Goal orientation: clarify owner-occupy vs. investment → determines subsequent focus (owner: school/safety/commute; investment: yield/appreciation).
#     2.4 Loan and feasibility: confirm loan pre-approval or debts; remind of impact on auctions/offers.
#     2.5 Age & condition: whether old/fixer-upper is acceptable to narrow the candidate set.
#     2.6 Expert deep analysis: when information is insufficient, task the “User Profiling” expert to supplement needs and pain points.
#
#     ### 3. Conversational Guidance
#     3.1 Stage questions: focus on 1–4 factors per turn to avoid pressure.
#     3.2 Natural transitions: connect to the next factor based on the user's answer, e.g.:
#     > “You mentioned wanting good schools; shall we discuss school zones?”
#     3.3 Use expert outputs: embed natural questions using `llm_suggestion` or profiling results.
#     3.4 Educational inserts: explain market rules or transaction flow at suitable moments to build confidence.
#
#     ### 4. Response Principles
#     4.1 Professional yet friendly: expert but warm tone; convey a sense of support.
#     4.2 Periodic summaries: every 1–2 turns, summarize gathered information and highlight pending factors.
#     4.3 Insight-driven value: weave in trends, cases, or experience-based insights to add value.
#     4.4 Decision guidance: narrow options step by step to help clarify decisions rather than dumping a one-shot answer.
#     """
# )
#
#
# def _build_model() -> OpenAIChat | DeepSeek:
#     provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
#     model_id = os.getenv("LLM_MODEL_NAME", "gpt-5-mini").strip()
#     if provider == "deepseek":
#         return DeepSeek(id=model_id)
#     return OpenAIChat(id=model_id)
#
#
# def _load_env_once() -> None:
#     # Best-effort load of secrets and env; do not override existing env vars
#     try:
#         load_dotenv(".env.secret", override=False)
#         load_dotenv(".env", override=False)
#     except Exception:
#         pass
#
#
# ## No persisted memory for this agent per user request
#
#
# def create_hou_agent() -> Agent:
#     _load_env_once()
#     tools = [
#         # ReasoningTools(add_instructions=True),
#         # user_profile_generate_and_upsert,
#         # user_profile_upsert_async,
#         # user_profile_query,
#         # user_profile_enqueue_generate,
#         # user_profile_job_status,
#         query_hougarden_info,
#         DuckDuckGoTools(),
#         GoogleSearchTools()
#
#     ]
#
#     agent = Agent(
#         name="HouAgent",
#         description="Profiling-first real-estate assistant for NZ/AU",
#         instructions=INSTRUCTIONS,
#         model=_build_model(),
#         tools=tools,
#         markdown=True,
#         add_history_to_context=True,
#         num_history_runs=5,
#         enable_user_memories=True,
#         enable_agentic_memory=True,
#         db=db,
#
#     )
#     return agent
#
#
# if __name__ == "__main__":
#     import sys
#     agent = create_hou_agent()
#     user_id = os.getenv("USER_ID", "demo_user_01")
#     print("HouAgent ready. Type your message (Ctrl+C to exit).")
#     try:
#         while True:
#             msg = input("You: ").strip()
#             if not msg:
#                 continue
#             # Non-blocking profile enrichment (side effect)
#             try:
#                 agent.run(
#                     f"[internal] enrich profile with: {msg}",
#                     user_id=user_id,
#                     # hint to tool-use in context
#                 )
#             except Exception:
#                 pass
#             # Normal response
#             t0 = time.perf_counter()
#             agent.print_response(msg, user_id=user_id, stream=True)
#             t1 = time.perf_counter()
#             print(f"本轮耗时: {t1 - t0:.2f}s")
#     except KeyboardInterrupt:
#         sys.exit(0)
