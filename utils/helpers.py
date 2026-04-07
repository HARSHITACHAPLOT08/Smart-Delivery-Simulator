def get_rank(score: int) -> str:
    if score >= 1000:
        return "🏆 Platinum"
    elif score >= 500:
        return "🥇 Gold"
    elif score >= 200:
        return "🥈 Silver"
    else:
        return "🥉 Bronze"
