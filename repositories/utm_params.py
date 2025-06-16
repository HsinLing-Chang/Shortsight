from sqlalchemy.orm import Session
from sqlalchemy import select, func, case, distinct, cast, Float, or_, and_
from database.model import UrlMapping, EventLog, UTMParams, EventTrafficSource
from datetime import datetime, timedelta, date


async def get_source_medium(db: Session, user_id, start_date, end_date, event_type):
    """ALL scanS or clickS source/medium"""
    first_seen_subq = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

    # Step 2: 條件
    conditions = [
        EventTrafficSource.visitor_id.isnot(None),
        EventTrafficSource.event_type == event_type,
        UrlMapping.user_id == user_id,
    ]
    if start_date:
        conditions.append(EventTrafficSource.created_at >= start_date)
    if end_date:
        conditions.append(EventTrafficSource.created_at <
                          end_date + timedelta(days=1))

    # Step 3: 處理日期條件（避免 None 比較錯誤）
    end_adj = end_date + timedelta(days=1) if end_date else None
    if start_date and end_adj:
        new_user_cond = (first_seen_subq.c.first_seen >= start_date) & (
            first_seen_subq.c.first_seen < end_adj)
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_adj:
        new_user_cond = first_seen_subq.c.first_seen < end_adj
    else:
        new_user_cond = True

    # Step 4: 查詢語句
    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventTrafficSource.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_cond, EventTrafficSource.visitor_id))
                )
            ).label("new_users")
        )
        .select_from(UTMParams)
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventTrafficSource,
            and_(
                EventTrafficSource.mapping_id == UrlMapping.id,
                EventTrafficSource.event_type == event_type if event_type else True,
                *conditions  # created_at 篩選條件
            )
        )
        .outerjoin(
            first_seen_subq,
            EventTrafficSource.visitor_id == first_seen_subq.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_source.isnot(None),  # 可省略，視你是否接受空值分群
            UTMParams.utm_medium.isnot(None)
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventTrafficSource.id).desc())
    )
    result = db.execute(stmt).mappings().all()
    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)
    final_data = []

    for row in result:
        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)
        final_data.append({
            "source": row["source"],
            "medium": row["medium"],
            "total_interactions": total,
            "new_users": new,
            "new_user_ratio": ratio,  # e.g., 33.3
            "new_user_level": level
        })
    print(final_data)
    return {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data": final_data
    }


async def get_canpaign_source_medium(campaign, db, user_id, start_date, end_date, event_type):
    if end_date:
        end_date += timedelta(days=1)

    first_seen_subq = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

    # ✅ 時間條件 for join filter
    event_conditions = []
    if event_type:
        event_conditions.append(EventTrafficSource.event_type == event_type)
    if start_date:
        event_conditions.append(EventTrafficSource.created_at >= start_date)
    if end_date:
        event_conditions.append(EventTrafficSource.created_at < end_date)

    # ✅ 新用戶條件（套用 first_seen_subq）
    if start_date and end_date:
        new_user_cond = (first_seen_subq.c.first_seen >= start_date) & (
            first_seen_subq.c.first_seen < end_date)
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_subq.c.first_seen < end_date
    else:
        new_user_cond = True

    # ✅ 主查詢：從使用者的 UTMParams 出發
    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventTrafficSource.id).label("total_interactions"),
            func.count(
                distinct(case((new_user_cond, EventTrafficSource.visitor_id)))
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventTrafficSource,
            and_(
                EventTrafficSource.mapping_id == UrlMapping.id,
                *event_conditions
            )
        )
        .outerjoin(
            first_seen_subq,
            EventTrafficSource.visitor_id == first_seen_subq.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign == campaign  # ✅ 特定 campaign 條件
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)
    final_data = []
    for row in result:
        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)
        final_data.append({
            **row,
            "new_user_ratio": ratio,  # 百分比
            "new_user_level": level
        })
    print(final_data)
    return {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data": final_data
    }


async def get_all_source_interactions(db, start_date, end_date, user_id):
    if end_date:
        end_adj = end_date + timedelta(days=1)
    else:
        end_adj = None
    # ✅ 找出每個 visitor 的首次出現時間
    first_seen_subq = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

    # ✅ event 時間範圍條件
    event_filters = [EventTrafficSource.event_type.in_(["click", "scan"])]
    if start_date:
        event_filters.append(EventTrafficSource.created_at >= start_date)
    if end_adj:
        event_filters.append(EventTrafficSource.created_at < end_adj)

    # ✅ new_user 條件
    if start_date and end_adj:
        new_user_cond = (first_seen_subq.c.first_seen >= start_date) & (
            first_seen_subq.c.first_seen < end_adj)
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_adj:
        new_user_cond = first_seen_subq.c.first_seen < end_adj
    else:
        new_user_cond = True

# ✅ 主查詢從 UTMParams 出發
    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventTrafficSource.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_cond, EventTrafficSource.visitor_id))
                )
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventTrafficSource,
            and_(
                EventTrafficSource.mapping_id == UrlMapping.id,
                *event_filters
            )
        )
        .outerjoin(
            first_seen_subq,
            EventTrafficSource.visitor_id == first_seen_subq.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_source.isnot(None),
            UTMParams.utm_medium.isnot(None)
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)
    final_data = []
    for row in result:
        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)
        final_data.append({
            **row,
            "new_user_ratio": ratio,
            "new_user_level": level
        })
    print(final_data)
    return {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data": final_data
    }


async def get_campaign_source_interactions(db, campaign, start_date, end_date, user_id):
    if end_date:
        end_adj = end_date + timedelta(days=1)
    else:
        end_adj = None

    # 🔹 新用戶基準表
    first_seen_subq = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

    # 🔹 事件條件（只作用於 join 條件）
    event_filters = [EventTrafficSource.event_type.in_(["click", "scan"])]
    if start_date:
        event_filters.append(EventTrafficSource.created_at >= start_date)
    if end_adj:
        event_filters.append(EventTrafficSource.created_at < end_adj)

    # 🔹 新用戶判斷條件
    if start_date and end_adj:
        new_user_cond = (first_seen_subq.c.first_seen >= start_date) & (
            first_seen_subq.c.first_seen < end_adj)
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_adj:
        new_user_cond = first_seen_subq.c.first_seen < end_adj
    else:
        new_user_cond = True

    # 🔹 主查詢
    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventTrafficSource.id).label("total_interactions"),
            func.count(
                distinct(case((new_user_cond, EventTrafficSource.visitor_id)))
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventTrafficSource,
            and_(
                EventTrafficSource.mapping_id == UrlMapping.id,
                *event_filters
            )
        )
        .outerjoin(
            first_seen_subq,
            EventTrafficSource.visitor_id == first_seen_subq.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign == campaign,
            UTMParams.utm_source.isnot(None),
            UTMParams.utm_medium.isnot(None)
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventTrafficSource.id).desc())
    )
    result = db.execute(stmt).mappings().all()

    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)
  # 🔹 添加 new_user_ratio 欄位
    final_data = []
    for row in result:
        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)
        final_data.append(
            {**row, "new_user_ratio": ratio, "new_user_level": level})
    print(final_data)

    return {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data": final_data
    }


def classify_new_user_ratio(ratio: float, total) -> str:
    if total < 5:
        return "Unstable"
    elif ratio >= 70:
        return "Very High"
    elif ratio >= 50:
        return "High"
    elif ratio >= 30:
        return "Moderate"
    elif ratio >= 10:
        return "Low"
    else:
        return "Very Low"


async def get_all_campaign_data(db, user_id, start_date, end_date):
    first_seen_subq = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
        .subquery()
    )

    # 新用戶條件
    if start_date and end_date:
        new_user_cond = and_(
            first_seen_subq.c.first_seen >= start_date,
            first_seen_subq.c.first_seen < end_date + timedelta(days=1)
        )
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_subq.c.first_seen < end_date + \
            timedelta(days=1)
    else:
        new_user_cond = True

# 時間條件
    traffic_filters = []
    if start_date:
        traffic_filters.append(EventTrafficSource.created_at >= start_date)
    if end_date:
        traffic_filters.append(
            EventTrafficSource.created_at < end_date + timedelta(days=1))

# 主查詢
    stmt = (
        select(
            UTMParams.utm_campaign.label("campaign"),
            func.count(EventTrafficSource.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_cond, EventTrafficSource.visitor_id))
                )
            ).label("new_users")
        )
        .select_from(UrlMapping)
        .outerjoin(
            UTMParams,
            UrlMapping.id == UTMParams.mapping_id  # 所有該用戶設定過的 UTM
        )
        .outerjoin(
            EventTrafficSource,
            and_(
                EventTrafficSource.mapping_id == UrlMapping.id,
                EventTrafficSource.event_type.in_(["click", "scan"]),
                *traffic_filters
            )
        )
        .outerjoin(
            first_seen_subq,
            EventTrafficSource.visitor_id == first_seen_subq.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.isnot(None)
        )
        .group_by(UTMParams.utm_campaign)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()

    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)

    data = []
    for row in result:
        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)
        data.append({
            "campaign": row["campaign"] or "(none)",
            "total_interactions": total,
            "new_users": new,
            "new_user_ratio": ratio,
            "new_user_level": level
        })

    return {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data": data
    }


async def get_campaign_with_type(db, user_id, event_type, start_date, end_date):

    first_seen_subq = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
        .subquery()
    )

    # 🔹 判斷新用戶的條件
    if start_date and end_date:
        new_user_cond = (first_seen_subq.c.first_seen >= start_date) & (
            first_seen_subq.c.first_seen < end_date + timedelta(days=1))
    elif start_date:
        new_user_cond = first_seen_subq.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_subq.c.first_seen < end_date + \
            timedelta(days=1)
    else:
        new_user_cond = True

    # 🔹 對 EventTrafficSource 的篩選條件（時間）
    traffic_conditions = []
    if start_date:
        traffic_conditions.append(EventTrafficSource.created_at >= start_date)
    if end_date:
        traffic_conditions.append(
            EventTrafficSource.created_at < end_date + timedelta(days=1))

    # 🔹 主查詢：從使用者的 utm_campaign 出發
    stmt = (
        select(
            UTMParams.utm_campaign.label("campaign"),
            func.count(EventTrafficSource.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_cond, EventTrafficSource.visitor_id))
                )
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventTrafficSource,
            and_(
                EventTrafficSource.mapping_id == UrlMapping.id,
                EventTrafficSource.event_type == event_type if event_type else True,
                *traffic_conditions
            )
        )
        .outerjoin(first_seen_subq, EventTrafficSource.visitor_id == first_seen_subq.c.visitor_id)
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.isnot(None)
        )
        .group_by(UTMParams.utm_campaign)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()

    # 🔹 總體統計
    total_users = sum(row["total_interactions"] for row in result)
    total_new_users = sum(row["new_users"] for row in result)
    overall_ratio = round(total_new_users * 100 /
                          total_users, 1) if total_users else 0.0
    total_level = classify_new_user_ratio(overall_ratio, total_users)

    # 🔹 每筆 campaign 資料
    final_data = []
    for row in result:
        total = row["total_interactions"]
        new = row["new_users"]
        ratio = round(new * 100 / total, 1) if total else 0.0
        level = classify_new_user_ratio(ratio, total)
        final_data.append({
            "campaign": row["campaign"] or "(none)",
            "total_interactions": total,
            "new_users": new,
            "new_user_ratio": ratio,
            "new_user_level": level
        })

    return {
        "summary": {
            "total_users": total_users,
            "total_new_users": total_new_users,
            "overall_ratio": overall_ratio,
            "new_user_level": total_level
        },
        "data": final_data
    }
