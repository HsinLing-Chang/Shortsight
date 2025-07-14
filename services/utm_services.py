
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
