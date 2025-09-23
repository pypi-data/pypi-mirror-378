"""
This module defines a Pydantic model for capturing a real estate user's
profile.  All field descriptions and examples have been translated
from Chinese to English.  Each field is optional and includes a
description and one or more example values to illustrate typical
inputs.

The model is designed to be comprehensive, covering demographic
details, financial capacity, property preferences, and other factors
that may influence a user's housing search.  You can import this
model and use it to validate or serialize user profiles in your
applications.
"""

from typing import Optional
from pydantic import BaseModel, Field
from typing import Optional
from pydantic import BaseModel, Field

class UserProfileResponse(BaseModel):
    """Pydantic model representing a user's housing profile (NZ/AU)."""

    # 4.1 交易 & 区域
    transaction_type: Optional[str] = Field(
        None, description="Transaction type: purchase or rent",
        examples=["Purchase", "Rent"]
    )
    address: Optional[str] = Field(
        None, description="Target city or region",
        examples=["Sydney CBD", "Auckland North Shore"]
    )
    sale_method: Optional[str] = Field(
        None, description="Sale method: asking price, negotiable, auction, tender, POA, limited-time sale, etc.",
        examples=["Auction", "Tender", "POA"]
    )
    listing_time: Optional[str] = Field(
        None, description="Listing time filter: today, past 3/7/30/90 days, etc.",
        examples=["Past 7 days", "Past 30 days"]
    )

    # 4.2 财务能力（预算/贷款）
    price_range: Optional[str] = Field(
        None, description="General budget/rent range placeholder",
        examples=["500000-600000", "Monthly rent 2000-3000"]
    )
    budget_range: Optional[str] = Field(
        None, description="Overall purchase budget range",
        examples=["800,000-1,000,000"]
    )
    monthly_payment_range: Optional[str] = Field(
        None, description="Acceptable monthly mortgage/rent range",
        examples=["Monthly payment 3000-4000"]
    )
    down_payment_percentage: Optional[str] = Field(
        None, description="Available down payment percentage",
        examples=["20%"]
    )
    loan_preference: Optional[str] = Field(
        None, description="Loan preference/status: pre-approved, limit, full cash, etc.",
        examples=["Loan pre-approved", "Plan to pay in full"]
    )
    has_existing_loans: Optional[str] = Field(
        None, description="Existing liabilities (e.g., mortgage, car loan) or none",
        examples=["Car loan", "No loans"]
    )

    # 4.3 人口学与家庭结构
    age_group: Optional[str] = Field(
        None, description="Age range",
        examples=["25-30 years"]
    )
    marital_status: Optional[str] = Field(
        None, description="Marital status",
        examples=["Married, no children", "Single"]
    )
    children_count: Optional[str] = Field(
        None, description="Number of children",
        examples=["0", "2"]
    )
    occupation: Optional[str] = Field(
        None, description="Occupation or industry",
        examples=["IT engineer", "Teacher"]
    )
    employment_status: Optional[str] = Field(
        None, description="Employment status",
        examples=["Full-time", "Self-employed"]
    )
    education_level: Optional[str] = Field(
        None, description="Highest education level",
        examples=["Master's degree", "Bachelor's degree"]
    )
    household_structure: Optional[str] = Field(
        None, description="Household composition",
        examples=["Couple with one child", "Single"]
    )
    residency_status: Optional[str] = Field(
        None, description="Residency/immigration status",
        examples=["Permanent resident", "Foreign work visa"]
    )
    family_income_range: Optional[str] = Field(
        None, description="Household income range",
        examples=["200,000-300,000 per year"]
    )
    salary_range: Optional[str] = Field(
        None, description="Personal salary income range",
        examples=["50k-80k per year"]
    )

    # 4.4 需求目的 & 投资偏好
    purpose: Optional[str] = Field(
        None, description="Overall purpose: owner-occupied or investment",
        examples=["Owner-occupied", "Investment"]
    )
    home_purchase_purpose: Optional[str] = Field(
        None, description="Purchase purpose detail: owner-occupied, investment, vacation, etc.",
        examples=["Investment rental", "Owner-occupied"]
    )
    rent_purpose: Optional[str] = Field(
        None, description="Rent purpose: transitional, long-term, etc.",
        examples=["Long-term rental", "Temporary living"]
    )
    investment_type: Optional[str] = Field(
        None, description="Investment strategy: long-term appreciation, fix-and-flip, rental",
        examples=["Long-term appreciation", "Fix and flip"]
    )
    risk_preference: Optional[str] = Field(
        None, description="Risk preference: conservative, moderate, aggressive",
        examples=["Moderate", "Conservative"]
    )
    investment_horizon: Optional[str] = Field(
        None, description="Planned holding period",
        examples=["More than 5 years", "1-2 years"]
    )

    # 4.5 工作/通勤 & 安全/教育/配套
    work_or_school_location: Optional[str] = Field(
        None, description="Work or school location (for commute evaluation)",
        examples=["Downtown"]
    )
    commute_time: Optional[str] = Field(
        None, description="Acceptable commute time or distance",
        examples=["30 minutes", "Within one hour"]
    )
    community_safety: Optional[str] = Field(
        None, description="Community safety requirement",
        examples=["Safe area", "Near police station"]
    )
    education_resource: Optional[str] = Field(
        None, description="Concern level for school/education resources",
        examples=["Highly concerned", "Moderate"]
    )
    amenities_preference: Optional[str] = Field(
        None, description="Preference for nearby amenities (parks, shops, hospitals, etc.)",
        examples=["Close to shopping center", "Park nearby"]
    )

    # 4.6 物业类型 & 细节偏好
    property_type: Optional[str] = Field(
        None, description="Property type: detached, apartment, unit, townhouse, land, etc.",
        examples=["Apartment", "Detached house"]
    )
    building_style: Optional[str] = Field(
        None, description="Architectural style (modern, traditional, coastal, etc.)",
        examples=["Contemporary", "Country style"]
    )
    bedroom_number: Optional[str] = Field(
        None, description="Number of bedrooms",
        examples=["3", "4"]
    )
    bathroom_number: Optional[str] = Field(
        None, description="Number of bathrooms",
        examples=["2", "3"]
    )
    parking_number: Optional[str] = Field(
        None, description="Number of parking spaces",
        examples=["1", "2"]
    )
    car_ownership: Optional[str] = Field(
        None, description="Car ownership (parking needs)",
        examples=["Own a car", "No car"]
    )
    pet_ownership: Optional[str] = Field(
        None, description="Pet ownership (pet-friendly requirements)",
        examples=["Own a dog", "No pets"]
    )
    garden_or_balcony: Optional[str] = Field(
        None, description="Need for garden or balcony",
        examples=["Need a garden", "Not required"]
    )
    elevator: Optional[str] = Field(
        None, description="Need for elevator (for high floors)",
        examples=["Yes", "No"]
    )
    floor_level: Optional[str] = Field(
        None, description="Preferred floor level (low/middle/high)",
        examples=["High floor", "Low floor"]
    )
    orientation: Optional[str] = Field(
        None, description="Preferred orientation (e.g., south-facing, east-facing)",
        examples=["South-facing", "East-facing"]
    )
    renovation_condition: Optional[str] = Field(
        None, description="Renovation status",
        examples=["Newly renovated", "Needs renovation"]
    )
    sustainability_requirements: Optional[str] = Field(
        None, description="Sustainability/energy-saving requirements",
        examples=["Need solar panels", "No special requirements"]
    )
    mobility_needs: Optional[str] = Field(
        None, description="Accessibility/mobility needs",
        examples=["Need wheelchair access", "No special requirements"]
    )

    # 4.7 时间计划 & 决策流程
    purchase_or_move_time: Optional[str] = Field(
        None, description="Planned purchase or move time",
        examples=["Within 3 months", "After one year"]
    )
    urgency_level: Optional[str] = Field(
        None, description="Decision urgency level",
        examples=["Immediate", "Within 6 months"]
    )
    lease_term: Optional[str] = Field(
        None, description="Lease term (renting scenario)",
        examples=["12 months", "6 months"]
    )
    sale_move_plan: Optional[str] = Field(
        None, description="Plan for selling/moving and its timing",
        examples=["Consider selling in two years", "No current plan"]
    )
    decision_makers: Optional[str] = Field(
        None, description="Decision makers/influencers",
        examples=["Decide with spouse", "Decide by yourself"]
    )
    service_needs: Optional[str] = Field(
        None, description="Additional service needs (loan, renovation, moving, etc.)",
        examples=["Need loan advice", "Need renovation advice"]
    )
    information_sources: Optional[str] = Field(
        None, description="Information sources (friends, websites, agents, etc.)",
        examples=["Real estate website", "Real estate agent"]
    )
    other_preferences: Optional[str] = Field(
        None, description="Other personal preferences (smart home, non-smoking floor, etc.)",
        examples=["Smart home", "Non-smoking floor"]
    )

    # 4.8 资产属性 & 监管/估值
    building_area: Optional[str] = Field(
        None, description="Building area range",
        examples=["100-150 m²", "150-200 m²"]
    )
    land_area: Optional[str] = Field(
        None, description="Land area range",
        examples=["200-500 m²", "500-1000 m²"]
    )
    build_year: Optional[str] = Field(
        None, description="Build decade / property age",
        examples=["2010s", "New build"]
    )
    tenure_type: Optional[str] = Field(
        None, description="Tenure type: Freehold, Leasehold, Unit, Timeshare, etc.",
        examples=["Freehold", "Leasehold"]
    )
    government_valuation_range: Optional[str] = Field(
        None, description="Government valuation range",
        examples=["1M-2M", "Below 500k"]
    )
    zoning: Optional[str] = Field(
        None, description="Zoning (single house, mixed housing suburban/urban, terrace/apartment, rural/coastal, large lot, etc.)",
        examples=["Terrace/apartment zone", "Mixed urban residential zone"]
    )

    # 4.9 学校与看房
    school_decile: Optional[str] = Field(
        None, description="School decile rating (historical NZ indicator, placeholder)",
        examples=["9", "10"]
    )
    open_home_date: Optional[str] = Field(
        None, description="Open home dates (comma-separated for multiple)",
        examples=["2025-09-08, 2025-09-10"]
    )
    property_tenure: Optional[str] = Field(
        None, description="Additional tenure/record types (e.g., apartment/unit, supplementary record sheet)",
        examples=["Supplementary record", "Apartment"]
    )

    # 4.10 心理/引导
    decision_anxiety_level: Optional[str] = Field(
        None, description="User anxiety level or blockers in decision-making",
        examples=["I must find a house within two months, feeling very stressed"]
    )
    llm_suggestion: Optional[str] = Field(
        None, description="LLM-generated suggestions/prompts for next questions or guidance",
        examples=[
            "What factors should I consider when buying a home for investment purposes?",
            "Do you have suggestions on affordable houses near schools in central Sydney?"
        ]
    )


data = {
  "transaction_type": {
    "desc": "交易类型：购买或租赁",
    "value": "",
    "examples": [
      "购买",
      "租赁"
    ]
  },
  "address": {
    "desc": "目标城市或区域",
    "value": "",
    "examples": [
      "悉尼CBD",
      "奥克兰北岸"
    ]
  },
  "price_range": {
    "desc": "预算/价格区间（购房或租房）",
    "value": "",
    "examples": [
      "500000-600000",
      "月租2000-3000"
    ]
  },
  "age_group": {
    "desc": "年龄段，例如20-30岁、30-40岁等",
    "value": "",
    "examples": [
      "25-30岁",
      "35-40岁"
    ]
  },
  "marital_status": {
    "desc": "婚姻状况：未婚、已婚、有无子女等",
    "value": "",
    "examples": [
      "已婚无子",
      "未婚"
    ]
  },
  "children_count": {
    "desc": "子女数量，用于判断住房需求",
    "value": "",
    "examples": [
      "0",
      "2"
    ]
  },
  "occupation": {
    "desc": "职业或行业",
    "value": "",
    "examples": [
      "教师",
      "IT工程师"
    ]
  },
  "employment_status": {
    "desc": "就业状况：全职、兼职、自雇、退休、学生等",
    "value": "",
    "examples": [
      "全职",
      "自雇"
    ]
  },
  "education_level": {
    "desc": "教育水平，如高中、本科、研究生",
    "value": "",
    "examples": [
      "本科",
      "研究生"
    ]
  },
  "household_structure": {
    "desc": "家庭结构：单身、夫妻、有无子女等",
    "value": "",
    "examples": [
      "夫妻+1孩",
      "单身"
    ]
  },
  "residency_status": {
    "desc": "居住/移民身份，如公民、永久居民、外籍",
    "value": "",
    "examples": [
      "永久居民",
      "外籍工作签证"
    ]
  },
  "family_income_range": {
    "desc": "家庭收入区间，用于评估经济能力",
    "value": "",
    "examples": [
      "20万-30万/年",
      "50万+/年"
    ]
  },
  "salary_range": {
    "desc": "个人工资收入范围",
    "value": "",
    "examples": [
      "5万-8万/年",
      "12万+/年"
    ]
  },
  "budget_range": {
    "desc": "总体预算区间，用于评估经济实力",
    "value": "",
    "examples": [
      "80万-100万",
      "100万-120万"
    ]
  },
  "monthly_payment_range": {
    "desc": "可接受的月供或租金范围",
    "value": "",
    "examples": [
      "月供3000-4000",
      "月租1500-2000"
    ]
  },
  "down_payment_percentage": {
    "desc": "可用首付比例",
    "value": "",
    "examples": [
      "20%",
      "30%"
    ]
  },
  "loan_preference": {
    "desc": "贷款需求或偏好，是否有预批、贷款上限等",
    "value": "",
    "examples": [
      "已有贷款预批",
      "计划全款支付"
    ]
  },
  "has_existing_loans": {
    "desc": "是否存在正在偿还的贷款（如房贷、车贷）",
    "value": "",
    "examples": [
      "有车贷",
      "无贷款"
    ]
  },
  "existing_properties": {
    "desc": "现有房产数量或是否首套房",
    "value": "",
    "examples": [
      "首套房",
      "已有两套房"
    ]
  },
  "purpose": {
    "desc": "总体目的：自住或投资",
    "value": "",
    "examples": [
      "自住",
      "投资"
    ]
  },
  "home_purchase_purpose": {
    "desc": "购房目的：自住、投资、度假等",
    "value": "",
    "examples": [
      "自住",
      "投资出租"
    ]
  },
  "rent_purpose": {
    "desc": "租房目的：自住、短租、过渡居住等",
    "value": "",
    "examples": [
      "过渡居住",
      "长租自住"
    ]
  },
  "investment_type": {
    "desc": "投资类型：长期增值、短期翻修、出租等",
    "value": "",
    "examples": [
      "长期增值",
      "短期翻修"
    ]
  },
  "risk_preference": {
    "desc": "风险偏好：保守、中等或激进",
    "value": "",
    "examples": [
      "保守",
      "中等"
    ]
  },
  "investment_horizon": {
    "desc": "投资期限或计划持有时间",
    "value": "",
    "examples": [
      "5年以上",
      "1-2年"
    ]
  },
  "work_or_school_location": {
    "desc": "工作或学校位置，便于评估通勤",
    "value": "",
    "examples": [
      "市中心",
      "郊区学校"
    ]
  },
  "commute_time": {
    "desc": "可接受的通勤时间或距离",
    "value": "",
    "examples": [
      "30分钟",
      "一小时内"
    ]
  },
  "community_safety": {
    "desc": "对社区安全性的要求",
    "value": "",
    "examples": [
      "治安良好",
      "靠近警察局"
    ]
  },
  "education_resource": {
    "desc": "对学区或教育资源的关注度",
    "value": "",
    "examples": [
      "重点关注",
      "一般"
    ]
  },
  "amenities_preference": {
    "desc": "对周边设施（公园、商店、医院等）的偏好",
    "value": "",
    "examples": [
      "靠近购物中心",
      "附近有公园"
    ]
  },
  "property_type": {
    "desc": "房产类型：独立屋、公寓、单元房、城市房、排房、自住投资房、乡村别墅、乡村住宅用地、建地等",
    "value": "",
    "examples": [
      "独立屋",
      "公寓"
    ]
  },
  "building_style": {
    "desc": "建筑风格：当代、豪华现代、传统、乡村、海滩风格、维多利亚/地中海等",
    "value": "",
    "examples": [
      "当代",
      "乡村"
    ]
  },
  "bedroom_number": {
    "desc": "卧室数量，如1、2、3、4或5+",
    "value": "",
    "examples": [
      "3",
      "4"
    ]
  },
  "bathroom_number": {
    "desc": "浴室数量，如1、2、3、4或5+",
    "value": "",
    "examples": [
      "2",
      "3"
    ]
  },
  "parking_number": {
    "desc": "车位数量，如1、2、3、4或5+",
    "value": "",
    "examples": [
      "1",
      "2"
    ]
  },
  "car_ownership": {
    "desc": "家庭是否拥有汽车，用于评估车位需求",
    "value": "",
    "examples": [
      "有车",
      "无车"
    ]
  },
  "pet_ownership": {
    "desc": "是否有宠物，用于评估宠物友好需求",
    "value": "",
    "examples": [
      "有狗",
      "无宠物"
    ]
  },
  "garden_or_balcony": {
    "desc": "是否需要花园或阳台",
    "value": "",
    "examples": [
      "需要花园",
      "不需要"
    ]
  },
  "elevator": {
    "desc": "是否需要电梯（针对高层）",
    "value": "",
    "examples": [
      "需要",
      "不需要"
    ]
  },
  "floor_level": {
    "desc": "楼层偏好（低层/中层/高层）",
    "value": "",
    "examples": [
      "高层",
      "低层"
    ]
  },
  "orientation": {
    "desc": "房屋朝向偏好",
    "value": "",
    "examples": [
      "朝南",
      "朝东"
    ]
  },
  "renovation_condition": {
    "desc": "装修新旧或是否需要翻新",
    "value": "",
    "examples": [
      "全新装修",
      "需要翻新"
    ]
  },
  "sustainability_requirements": {
    "desc": "节能和可持续性要求（如节能设备、环保材料）",
    "value": "",
    "examples": [
      "需要太阳能",
      "普通即可"
    ]
  },
  "mobility_needs": {
    "desc": "特殊通行需求：无障碍设施、轮椅通道等",
    "value": "",
    "examples": [
      "需要无障碍通道",
      "无特殊要求"
    ]
  },
  "purchase_or_move_time": {
    "desc": "计划购房或搬迁的时间",
    "value": "",
    "examples": [
      "3个月内",
      "一年后"
    ]
  },
  "urgency_level": {
    "desc": "决策紧迫度（立即、3个月内、6个月内等）",
    "value": "",
    "examples": [
      "立即",
      "6个月内"
    ]
  },
  "lease_term": {
    "desc": "租期长短（针对租房用户）",
    "value": "",
    "examples": [
      "12个月",
      "6个月"
    ]
  },
  "sale_move_plan": {
    "desc": "是否有出售或搬出计划及其时间",
    "value": "",
    "examples": [
      "两年后考虑出售",
      "暂无计划"
    ]
  },
  "decision_makers": {
    "desc": "决策影响者，如配偶、父母、理财顾问等",
    "value": "",
    "examples": [
      "与配偶共同决定",
      "自己决定"
    ]
  },
  "service_needs": {
    "desc": "额外服务需求，如学区信息、贷款咨询、装修/搬家服务等",
    "value": "",
    "examples": [
      "需要贷款咨询",
      "需要装修建议"
    ]
  },
  "information_sources": {
    "desc": "信息获取渠道，如朋友推荐、网络、经纪人等",
    "value": "",
    "examples": [
      "房产中介",
      "房产网站"
    ]
  },
  "other_preferences": {
    "desc": "其他个人偏好，如智能家居、无烟环境等",
    "value": "",
    "examples": [
      "智能家居",
      "无烟楼层"
    ]
  },
  "sale_method": {
    "desc": "售价方式：要价、议价、拍卖、投标、POA、出价、限期出售等",
    "value": "",
    "examples": [
      "要价",
      "拍卖"
    ]
  },
  "listing_time": {
    "desc": "房源上市时间范围，如今日、过去3天、过去7天、过去1个月、过去3个月等",
    "value": "",
    "examples": [
      "过去7天",
      "过去1个月"
    ]
  },
  "building_area": {
    "desc": "建筑面积范围，如<50㎡、50-100㎡、100-150㎡、150-200㎡、200-250㎡、250-300㎡、300㎡+",
    "value": "",
    "examples": [
      "100-150㎡",
      "150-200㎡"
    ]
  },
  "land_area": {
    "desc": "土地面积范围，如<200㎡、200-500㎡、500-1000㎡、1000㎡+",
    "value": "",
    "examples": [
      "200-500㎡",
      "500-1000㎡"
    ]
  },
  "build_year": {
    "desc": "建造年代或房龄，例如60s、70s、80s、90s、2000s、2010s或新建",
    "value": "",
    "examples": [
      "2010s",
      "新建"
    ]
  },
  "tenure_type": {
    "desc": "产权类型，如全幅地永久产权、半幅地永久产权、租赁产权、公寓/单元房、分时度假物业等",
    "value": "",
    "examples": [
      "全幅地永久产权",
      "租赁产权"
    ]
  },
  "government_valuation_range": {
    "desc": "政府估价区间，例如50万以下、50万-100万、100万-200万、200万-500万、500万以上",
    "value": "",
    "examples": [
      "50万以下",
      "100万-200万"
    ]
  },
  "zoning": {
    "desc": "城市规划分区，如单体住宅区、混合郊区住宅区、混合城市住宅区、排屋/公寓区、农村及沿海区、大地块区等",
    "value": "",
    "examples": [
      "混合城市住宅区",
      "排屋/公寓区"
    ]
  },
  "school_decile": {
    "desc": "学校评分 Decile，帮助衡量学区质量",
    "value": "",
    "examples": [
      "9",
      "10"
    ]
  },
  "open_home_date": {
    "desc": "开放日日期（可多选），表示用户希望参加看房的时间",
    "value": "",
    "examples": [
      "2025-09-08",
      "2025-09-10"
    ]
  },
  "property_tenure": {
    "desc": "更多产权细分类型，如公寓/单元房、Supplementary record sheet 等（若适用）",
    "value": "",
    "examples": [
      "公寓/单元房",
      "Supplementary record"
    ]
  },
  "decision_anxiety_level": {
    "desc": "用户在购房/租房决策过程中的焦虑程度或面临的挑战",
    "value": "",
    "examples": [
      "我必须在两个月内找到房子，感觉压力很大",
      "担心贷款审批时间影响购买进度"
    ]
  }
}

'''
目的 (Purpose)

自住还是投资将极大影响购房者的选择。自住的购房者通常更加看重生活质量、学区和安全性；而投资者则更加注重增值潜力、租金回报等。

预算/价格区间 (Budget/Price Range)

除了位置外，预算是购房决策中最核心的因素，决定了购房者的选择范围。

房产类型 (Property Type)

是选择独立屋、公寓、联排别墅，还是其他类型的房产，直接影响购房者的舒适度、使用功能以及未来增值空间。

学区资源 (Education Resources)

特别是对于有子女的家庭，学区优劣直接影响到购房的决策。好的学校是很多家庭选择住宅区域的首要条件。

社区安全性 (Community Safety)

社区的治安状况对许多购房者来说是一个决定性因素，尤其是对于有子女的家庭。一个安全的社区意味着更高的生活质量和长期居住的稳定性。

交通和通勤 (Commute & Transportation)

便利的交通和适中的通勤时间对于购房者的决策非常重要。特别是在大城市中，通勤时间长会极大影响生活质量，因此通勤条件对购房者至关重要。

房屋面积及布局 (Property Size & Layout)

房屋的面积、卧室数量、客厅功能等布局设计会直接影响购房者的居住舒适度。不同的家庭需求对于房屋空间的要求有所不同。

周边设施 (Amenities)

附近是否有医院、商店、公园等设施，能大大提高购房者的生活便利性。尤其是在一些大型社区，周边设施完善的房产通常更具吸引力。

贷款条件和可负担性 (Loan & Affordability)

是否能够获得贷款及贷款额度，首付比例，贷款利率等也是购房决策中的关键因素，特别是对于首次购房者而言。

房屋年龄和状况 (Property Age & Condition)

房屋的建造年代以及是否需要翻新，也是影响购房决策的重要因素。较新的房产可能意味着较少的维修成本，而老房子则可能需要更多的翻修和维护。
'''