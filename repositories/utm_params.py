from sqlalchemy.orm import Session
from sqlalchemy import select, func, case, distinct,  and_
from database.model import UrlMapping, UTMParams, EventTrafficSource
from datetime import timedelta


def summarize_utm_user_stats(result):
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


def summarize_campaign_stats(result):
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


async def get_source_medium(db: Session, user_id, start_date, end_date, event_type):
    """ALL scanS or clickS source/medium"""
    first_seen_visitors = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

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

    end_adj = end_date + timedelta(days=1) if end_date else None
    if start_date and end_adj:
        new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
            first_seen_visitors.c.first_seen < end_adj)
    elif start_date:
        new_user_cond = first_seen_visitors.c.first_seen >= start_date
    elif end_adj:
        new_user_cond = first_seen_visitors.c.first_seen < end_adj
    else:
        new_user_cond = True

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
            first_seen_visitors,
            EventTrafficSource.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_source.isnot(None),
            UTMParams.utm_medium.isnot(None),
            UTMParams.utm_campaign.is_not(None),
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventTrafficSource.id).desc())
    )
    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)


async def get_canpaign_source_medium(campaign, db, user_id, start_date, end_date, event_type):
    if end_date:
        end_date += timedelta(days=1)

    first_seen_visitors = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

    event_conditions = []
    if event_type:
        event_conditions.append(EventTrafficSource.event_type == event_type)
    if start_date:
        event_conditions.append(EventTrafficSource.created_at >= start_date)
    if end_date:
        event_conditions.append(EventTrafficSource.created_at < end_date)

    if start_date and end_date:
        new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
            first_seen_visitors.c.first_seen < end_date)
    elif start_date:
        new_user_cond = first_seen_visitors.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_visitors.c.first_seen < end_date
    else:
        new_user_cond = True

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
            first_seen_visitors,
            EventTrafficSource.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign == campaign
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)


async def get_all_source_interactions(db, start_date, end_date, user_id):
    if end_date:
        end_adj = end_date + timedelta(days=1)
    else:
        end_adj = None

    first_seen_visitors = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

    event_filters = [EventTrafficSource.event_type.in_(["click", "scan"])]
    if start_date:
        event_filters.append(EventTrafficSource.created_at >= start_date)
    if end_adj:
        event_filters.append(EventTrafficSource.created_at < end_adj)

    if start_date and end_adj:
        new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
            first_seen_visitors.c.first_seen < end_adj)
    elif start_date:
        new_user_cond = first_seen_visitors.c.first_seen >= start_date
    elif end_adj:
        new_user_cond = first_seen_visitors.c.first_seen < end_adj
    else:
        new_user_cond = True

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
            first_seen_visitors,
            EventTrafficSource.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_source.isnot(None),
            UTMParams.utm_medium.isnot(None),
            UTMParams.utm_campaign.is_not(None),
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)


async def get_campaign_source_interactions(db, campaign, start_date, end_date, user_id):
    if end_date:
        end_adj = end_date + timedelta(days=1)
    else:
        end_adj = None

    first_seen_visitors = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
    ).subquery()

    event_filters = [EventTrafficSource.event_type.in_(["click", "scan"])]
    if start_date:
        event_filters.append(EventTrafficSource.created_at >= start_date)
    if end_adj:
        event_filters.append(EventTrafficSource.created_at < end_adj)

    if start_date and end_adj:
        new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
            first_seen_visitors.c.first_seen < end_adj)
    elif start_date:
        new_user_cond = first_seen_visitors.c.first_seen >= start_date
    elif end_adj:
        new_user_cond = first_seen_visitors.c.first_seen < end_adj
    else:
        new_user_cond = True

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
            first_seen_visitors,
            EventTrafficSource.visitor_id == first_seen_visitors.c.visitor_id
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
    return summarize_utm_user_stats(result)


async def get_all_campaign_data(db, user_id, start_date, end_date):
    first_seen_visitors = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
        .subquery()
    )

    if start_date and end_date:
        new_user_cond = and_(
            first_seen_visitors.c.first_seen >= start_date,
            first_seen_visitors.c.first_seen < end_date + timedelta(days=1)
        )
    elif start_date:
        new_user_cond = first_seen_visitors.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_visitors.c.first_seen < end_date + \
            timedelta(days=1)
    else:
        new_user_cond = True

    traffic_filters = []
    if start_date:
        traffic_filters.append(EventTrafficSource.created_at >= start_date)
    if end_date:
        traffic_filters.append(
            EventTrafficSource.created_at < end_date + timedelta(days=1))

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
            UrlMapping.id == UTMParams.mapping_id
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
            first_seen_visitors,
            EventTrafficSource.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.isnot(None)
        )
        .group_by(UTMParams.utm_campaign)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_campaign_stats(result)


async def get_campaign_with_type(db, user_id, event_type, start_date, end_date):

    first_seen_visitors = (
        select(
            EventTrafficSource.visitor_id,
            func.min(EventTrafficSource.created_at).label("first_seen")
        )
        .where(EventTrafficSource.visitor_id.isnot(None))
        .group_by(EventTrafficSource.visitor_id)
        .subquery()
    )

    if start_date and end_date:
        new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
            first_seen_visitors.c.first_seen < end_date + timedelta(days=1))
    elif start_date:
        new_user_cond = first_seen_visitors.c.first_seen >= start_date
    elif end_date:
        new_user_cond = first_seen_visitors.c.first_seen < end_date + \
            timedelta(days=1)
    else:
        new_user_cond = True

    traffic_conditions = []
    if start_date:
        traffic_conditions.append(EventTrafficSource.created_at >= start_date)
    if end_date:
        traffic_conditions.append(
            EventTrafficSource.created_at < end_date + timedelta(days=1))

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
        .outerjoin(first_seen_visitors, EventTrafficSource.visitor_id == first_seen_visitors.c.visitor_id)
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.isnot(None)
        )
        .group_by(UTMParams.utm_campaign)
        .order_by(func.count(EventTrafficSource.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_campaign_stats(result)


# 尋找所有source/medium 組合
# SELECT utm_source, utm_medium, COUNT(CASE WHEN ETS.event_type in ('scan', 'click') THEN 1 ELSE NULL END) AS total_interaction from utm_params
# join url_mapping ON utm_params.mapping_id = url_mapping.id
# left join event_traffic_source as ETS ON url_mapping.id =  ETS.mapping_id
# where url_mapping.user_id = 4 AND  utm_campaign is not null
# GROUP BY 1, 2
