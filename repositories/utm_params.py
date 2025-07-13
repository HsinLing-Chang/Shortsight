from sqlalchemy.orm import Session
from sqlalchemy import select, func, case, distinct,  and_, or_
from database.model import UrlMapping, UTMParams, EventLog
from datetime import timedelta
from services.utm_services import summarize_campaign_stats, summarize_utm_user_stats


def get_first_seen_visitors_subquery():
    """回傳每位visitor最初來的時間的子查詢"""
    first_seen_visitors = (
        select(
            EventLog.visitor_id,
            func.min(EventLog.created_at).label("first_seen")
        )
        .group_by(EventLog.visitor_id)
    ).subquery()

    return first_seen_visitors


def build_eventlog_filter_conditions(event_type,  start_date, end_date):

    conditions = [
        EventLog.mapping_id == UrlMapping.id,
    ]
    if event_type != None:
        # if isinstance(event_type, list):
        #     conditions.append(EventLog.event_type.in_(event_type))
        conditions.append(EventLog.event_type == event_type)
    if start_date:
        conditions.append(EventLog.created_at >= start_date)
    if end_date:
        conditions.append(EventLog.created_at <
                          end_date + timedelta(days=1))
    return conditions


def build_new_user_condition(start_date, end_date, first_seen_visitors):
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
    return new_user_cond


async def fetch_sources_medium_by_eventlog_types(db: Session, user_id, start_date, end_date, event_type=None):

    first_seen_visitors = get_first_seen_visitors_subquery()

    eventlog_filter_conditions = build_eventlog_filter_conditions(
        event_type,  start_date, end_date)

    new_user_conditions = build_new_user_condition(
        start_date, end_date, first_seen_visitors)

    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_conditions, EventLog.visitor_id))
                )
            ).label("new_users")
        )
        .select_from(UTMParams)
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventLog,
            and_(
                *eventlog_filter_conditions
            )
        )
        .outerjoin(
            first_seen_visitors,
            EventLog.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.is_not(None),
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventLog.id).desc())
    )
    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)


async def fetch_campaign_sources_by_eventlog_types(campaign, db, user_id, start_date, end_date, event_type=None):

    first_seen_visitors = get_first_seen_visitors_subquery()

    eventlog_filter_conditions = build_eventlog_filter_conditions(
        event_type,  start_date, end_date)

    new_user_conditions = build_new_user_condition(
        start_date, end_date, first_seen_visitors)

    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(case((new_user_conditions, EventLog.visitor_id)))
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventLog,
            and_(
                *eventlog_filter_conditions
            )
        )
        .outerjoin(
            first_seen_visitors,
            EventLog.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign == campaign
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventLog.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)


async def fetch_campaign_by_eventlog_types(db, user_id,  start_date, end_date, event_type=None):

    first_seen_visitors = get_first_seen_visitors_subquery()

    eventlog_filter_conditions = build_eventlog_filter_conditions(
        event_type,  start_date, end_date)

    new_user_conditions = build_new_user_condition(
        start_date, end_date, first_seen_visitors)

    stmt = (
        select(
            UTMParams.utm_campaign.label("campaign"),
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_conditions, EventLog.visitor_id))
                )
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventLog,
            and_(
                *eventlog_filter_conditions
            )
        )
        .outerjoin(first_seen_visitors, EventLog.visitor_id == first_seen_visitors.c.visitor_id)
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.isnot(None)
        )
        .group_by(UTMParams.utm_campaign)
        .order_by(func.count(EventLog.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_campaign_stats(result)


async def fetch_other_traffic_by_eventlog_types(db, user_id,  start_date, end_date, event_type=None):

    first_seen_visitors = get_first_seen_visitors_subquery()
    new_user_condition = build_new_user_condition(
        start_date, end_date, first_seen_visitors)

    eventlog_filter_conditions = build_eventlog_filter_conditions(
        event_type,  start_date, end_date)

    stmt = (select(
        EventLog.source,
        EventLog.medium,
        func.count(EventLog.id).label("total_interactions"),
        func.count(
            distinct(
                case((new_user_condition,  EventLog.visitor_id))
            )
        ).label("new_users")
    )
        .select_from(EventLog)
        .join(UrlMapping,
              UrlMapping.id == EventLog.mapping_id
              )
        .outerjoin(first_seen_visitors,  EventLog.visitor_id == first_seen_visitors.c.visitor_id)
        .where(
        UrlMapping.user_id == user_id,
        or_(
            EventLog.campaign.is_(None),
            EventLog.campaign == "",
        ),
        *eventlog_filter_conditions
    )
        .group_by(EventLog.source,  EventLog.medium))

    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)

# async def fetch_sources_by_event_type(db: Session, user_id, start_date, end_date, event_type):
#     """ALL scanS or clickS source/medium"""

#     first_seen_visitors = get_first_seen_visitors_subquery()

#     # conditions = [
#     #     EventLog.event_type == event_type,
#     #     UrlMapping.user_id == user_id,
#     # ]
#     # if start_date:
#     #     conditions.append(EventLog.created_at >= start_date)
#     # if end_date:
#     #     conditions.append(EventLog.created_at <
#     #                       end_date + timedelta(days=1))
#     eventlog_filter_conditions = build_eventlog_filter_conditions(
#         event_type,  start_date, end_date)

#     # end_adj = end_date + timedelta(days=1) if end_date else None
#     # if start_date and end_adj:
#     #     new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
#     #         first_seen_visitors.c.first_seen < end_adj)
#     # elif start_date:
#     #     new_user_cond = first_seen_visitors.c.first_seen >= start_date
#     # elif end_adj:
#     #     new_user_cond = first_seen_visitors.c.first_seen < end_adj
#     # else:
#     #     new_user_cond = True

#     new_user_cond = build_new_user_condition(
#         start_date, end_date, first_seen_visitors)

#     stmt = (
#         select(
#             UTMParams.utm_source.label("source"),
#             UTMParams.utm_medium.label("medium"),
#             func.count(EventLog.id).label("total_interactions"),
#             func.count(
#                 distinct(
#                     case((new_user_cond, EventLog.visitor_id))
#                 )
#             ).label("new_users")
#         )
#         .select_from(UTMParams)
#         .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
#         .outerjoin(
#             EventLog,
#             and_(
#                 *eventlog_filter_conditions
#             )
#         )
#         .outerjoin(
#             first_seen_visitors,
#             EventLog.visitor_id == first_seen_visitors.c.visitor_id
#         )
#         .where(
#             UrlMapping.user_id == user_id,
#             # UTMParams.utm_source.isnot(None),
#             # UTMParams.utm_medium.isnot(None),
#             UTMParams.utm_campaign.is_not(None),
#         )
#         .group_by(UTMParams.utm_source, UTMParams.utm_medium)
#         .order_by(func.count(EventLog.id).desc())
#     )
#     result = db.execute(stmt).mappings().all()
#     print(result)
#     return summarize_utm_user_stats(result)

# async def fetch_sources_by_all_interactions(db, start_date, end_date, user_id):
#     # if end_date:
#     #     end_adj = end_date + timedelta(days=1)
#     # else:
#     #     end_adj = None
#     first_seen_visitors = get_first_seen_visitors_subquery()

#     # event_filters = [EventLog.event_type.in_(["click", "scan"])]
#     # if start_date:
#     #     event_filters.append(EventLog.created_at >= start_date)
#     # if end_adj:
#     #     event_filters.append(EventLog.created_at < end_adj)
#     eventlog_filter_conditions = build_eventlog_filter_conditions(
#         ["click", "scan"],  start_date, end_date)
#     new_user_cond = build_new_user_condition(
#         start_date, end_date, first_seen_visitors)
#     # if start_date and end_adj:
#     #     new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
#     #         first_seen_visitors.c.first_seen < end_adj)
#     # elif start_date:
#     #     new_user_cond = first_seen_visitors.c.first_seen >= start_date
#     # elif end_adj:
#     #     new_user_cond = first_seen_visitors.c.first_seen < end_adj
#     # else:
#     #     new_user_cond = True

#     stmt = (
#         select(
#             UTMParams.utm_source.label("source"),
#             UTMParams.utm_medium.label("medium"),
#             func.count(EventLog.id).label("total_interactions"),
#             func.count(
#                 distinct(
#                     case((new_user_cond, EventLog.visitor_id))
#                 )
#             ).label("new_users")
#         )
#         .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
#         .outerjoin(
#             EventLog,
#             and_(
#                 *eventlog_filter_conditions
#             )
#         )
#         .outerjoin(
#             first_seen_visitors,
#             EventLog.visitor_id == first_seen_visitors.c.visitor_id
#         )
#         .where(
#             UrlMapping.user_id == user_id,
#             # UTMParams.utm_source.isnot(None),
#             # UTMParams.utm_medium.isnot(None),
#             UTMParams.utm_campaign.is_not(None),
#         )
#         .group_by(UTMParams.utm_source, UTMParams.utm_medium)
#         .order_by(func.count(EventLog.id).desc())
#     )

#     result = db.execute(stmt).mappings().all()
#     return summarize_utm_user_stats(result)


# async def fetch_campaign_sources_by_event_type(campaign, db, user_id, start_date, end_date, event_type):

    first_seen_visitors = get_first_seen_visitors_subquery()

    eventlog_filter_conditions = build_eventlog_filter_conditions(
        event_type,  start_date, end_date)

    new_user_cond = build_new_user_condition(
        start_date, end_date, first_seen_visitors)
    # if start_date and end_date:
    #     new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
    #         first_seen_visitors.c.first_seen < end_date)
    # elif start_date:
    #     new_user_cond = first_seen_visitors.c.first_seen >= start_date
    # elif end_date:
    #     new_user_cond = first_seen_visitors.c.first_seen < end_date
    # else:
    #     new_user_cond = True

    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(case((new_user_cond, EventLog.visitor_id)))
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventLog,
            and_(
                *eventlog_filter_conditions
            )
        )
        .outerjoin(
            first_seen_visitors,
            EventLog.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign == campaign
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventLog.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)


# async def fetch_campaign_sources_by_all_interactions(db, campaign, start_date, end_date, user_id):
    # if end_date:
    #     end_adj = end_date + timedelta(days=1)
    # else:
    #     end_adj = None
    first_seen_visitors = get_first_seen_visitors_subquery()
    eventlog_filter_conditions = build_eventlog_filter_conditions(
        ["click", "scan"],  start_date, end_date)
    # event_filters = [EventLog.event_type.in_(["click", "scan"])]
    # if start_date:
    #     event_filters.append(EventLog.created_at >= start_date)
    # if end_adj:
    #     event_filters.append(EventLog.created_at < end_adj)
    new_user_cond = build_new_user_condition(
        start_date, end_date, first_seen_visitors)
    # if start_date and end_adj:
    #     new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
    #         first_seen_visitors.c.first_seen < end_adj)
    # elif start_date:
    #     new_user_cond = first_seen_visitors.c.first_seen >= start_date
    # elif end_adj:
    #     new_user_cond = first_seen_visitors.c.first_seen < end_adj
    # else:
    #     new_user_cond = True

    stmt = (
        select(
            UTMParams.utm_source.label("source"),
            UTMParams.utm_medium.label("medium"),
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(case((new_user_cond, EventLog.visitor_id)))
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventLog,
            and_(
                *eventlog_filter_conditions
            )
        )
        .outerjoin(
            first_seen_visitors,
            EventLog.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign == campaign,
        )
        .group_by(UTMParams.utm_source, UTMParams.utm_medium)
        .order_by(func.count(EventLog.id).desc())
    )
    result = db.execute(stmt).mappings().all()
    return summarize_utm_user_stats(result)


# async def get_all_campaign_data(db, user_id, start_date, end_date):
    # first_seen_visitors = (
    #     select(
    #         EventLog.visitor_id,
    #         func.min(EventLog.created_at).label("first_seen")
    #     )
    #     .where(EventLog.visitor_id.isnot(None))
    #     .group_by(EventLog.visitor_id)
    #     .subquery()
    # )
    first_seen_visitors = get_first_seen_visitors_subquery()

    eventlog_filter_conditions = build_eventlog_filter_conditions(
        ["click", "scan"],  start_date, end_date)
    new_user_conditions = build_new_user_condition(
        start_date, end_date, first_seen_visitors)
    # if start_date and end_date:
    #     new_user_cond = and_(
    #         first_seen_visitors.c.first_seen >= start_date,
    #         first_seen_visitors.c.first_seen < end_date + timedelta(days=1)
    #     )
    # elif start_date:
    #     new_user_cond = first_seen_visitors.c.first_seen >= start_date
    # elif end_date:
    #     new_user_cond = first_seen_visitors.c.first_seen < end_date + \
    #         timedelta(days=1)
    # else:
    #     new_user_cond = True

    # traffic_filters = []
    # if start_date:
    #     traffic_filters.append(EventLog.created_at >= start_date)
    # if end_date:
    #     traffic_filters.append(
    #         EventLog.created_at < end_date + timedelta(days=1))

    stmt = (
        select(
            UTMParams.utm_campaign.label("campaign"),
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_conditions, EventLog.visitor_id))
                )
            ).label("new_users")
        )
        .select_from(UrlMapping)
        .outerjoin(
            UTMParams,
            UrlMapping.id == UTMParams.mapping_id
        )
        .outerjoin(
            EventLog,
            and_(
                # EventLog.mapping_id == UrlMapping.id,
                # EventLog.event_type.in_(["click", "scan"]),
                *eventlog_filter_conditions
            )
        )
        .outerjoin(
            first_seen_visitors,
            EventLog.visitor_id == first_seen_visitors.c.visitor_id
        )
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.isnot(None)
        )
        .group_by(UTMParams.utm_campaign)
        .order_by(func.count(EventLog.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_campaign_stats(result)


# async def get_campaign_with_type(db, user_id, event_type, start_date, end_date):

    # first_seen_visitors = (
    #     select(
    #         EventLog.visitor_id,
    #         func.min(EventLog.created_at).label("first_seen")
    #     )
    #     .where(EventLog.visitor_id.isnot(None))
    #     .group_by(EventLog.visitor_id)
    #     .subquery()
    # )
    first_seen_visitors = get_first_seen_visitors_subquery()

    eventlog_filter_conditions = build_eventlog_filter_conditions(
        event_type,  start_date, end_date)

    new_user_conditions = build_new_user_condition(
        start_date, end_date, first_seen_visitors)

    # if start_date and end_date:
    #     new_user_cond = (first_seen_visitors.c.first_seen >= start_date) & (
    #         first_seen_visitors.c.first_seen < end_date + timedelta(days=1))
    # elif start_date:
    #     new_user_cond = first_seen_visitors.c.first_seen >= start_date
    # elif end_date:
    #     new_user_cond = first_seen_visitors.c.first_seen < end_date + \
    #         timedelta(days=1)
    # else:
    #     new_user_cond = True

    # traffic_conditions = []
    # if start_date:
    #     traffic_conditions.append(EventLog.created_at >= start_date)
    # if end_date:
    #     traffic_conditions.append(
    #         EventLog.created_at < end_date + timedelta(days=1))

    stmt = (
        select(
            UTMParams.utm_campaign.label("campaign"),
            func.count(EventLog.id).label("total_interactions"),
            func.count(
                distinct(
                    case((new_user_conditions, EventLog.visitor_id))
                )
            ).label("new_users")
        )
        .join(UrlMapping, UTMParams.mapping_id == UrlMapping.id)
        .outerjoin(
            EventLog,
            and_(
                # EventLog.mapping_id == UrlMapping.id,
                # EventLog.event_type == event_type if event_type else True,
                *eventlog_filter_conditions
            )
        )
        .outerjoin(first_seen_visitors, EventLog.visitor_id == first_seen_visitors.c.visitor_id)
        .where(
            UrlMapping.user_id == user_id,
            UTMParams.utm_campaign.isnot(None)
        )
        .group_by(UTMParams.utm_campaign)
        .order_by(func.count(EventLog.id).desc())
    )

    result = db.execute(stmt).mappings().all()
    return summarize_campaign_stats(result)
