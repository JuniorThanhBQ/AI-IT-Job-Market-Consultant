def reciprocal_rank_fusion(
    ranked_lists: list[list[int]], k: int = 60
) -> list[tuple[int, float]]:
    rrf_scores: dict[int, float] = {}
    for rank_list in ranked_lists:
        for rank, item in enumerate(rank_list, start=1):
            score = 1.0 / (k + rank)
            if item in rrf_scores:
                rrf_scores[item] += score
            else:
                rrf_scores[item] = score
    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
