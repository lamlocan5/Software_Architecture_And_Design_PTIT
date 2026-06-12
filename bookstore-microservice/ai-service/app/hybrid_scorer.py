import numpy as np
from app.models import UserBehavior, ProductNode, ProductSimilarity
from app.lstm_model import get_lstm_recommendations
from app.graph_engine import Neo4jGraphEngine

def get_hybrid_recommendations(user_id, limit=6):
    """
    Computes a hybrid recommendation list by blending:
    1. LSTM Sequence Prediction Score (Weight: 0.4)
    2. Neo4j Graph Collaborative & Similar Path Score (Weight: 0.4)
    3. Content Database Similarity Score (Weight: 0.2)
    """
    # 1. Fetch user's behavior history
    behaviors = UserBehavior.objects.filter(user_id=user_id).order_by('-timestamp')
    history_pids = list(behaviors.values_list('product_id', flat=True))
    # Keep unique items in chronological order (reverse of history_pids since it's ordered by -timestamp)
    seen_pids = list(dict.fromkeys(reversed(history_pids)))

    # Candidates score dictionaries
    lstm_scores = {}
    graph_scores = {}
    content_scores = {}

    # --- A. LSTM Predictions ---
    try:
        lstm_recs = get_lstm_recommendations(user_id, seen_pids, limit=30)
        for pid, score in lstm_recs:
            lstm_scores[pid] = score
    except Exception as e:
        print(f"Error getting LSTM recs in Hybrid Scorer: {e}")

    # --- B. Neo4j Graph Predictions ---
    graph = None
    try:
        graph = Neo4jGraphEngine()
        if graph.driver:
            collab_recs = graph.get_collaborative_recommendations(user_id, limit=30)
            similar_recs = graph.get_similar_recommendations(user_id, limit=30)
            
            # Combine collaborative filtering and graph similarity
            for pid, score in collab_recs:
                graph_scores[pid] = graph_scores.get(pid, 0.0) + score
                
            for pid, score in similar_recs:
                graph_scores[pid] = graph_scores.get(pid, 0.0) + score
    except Exception as e:
        print(f"Error getting Neo4j recs in Hybrid Scorer: {e}")
    finally:
        if graph:
            graph.close()

    # --- C. Content DB Similarity Predictions ---
    try:
        if seen_pids:
            # Query similarity table for items similar to user history
            similarities = ProductSimilarity.objects.filter(
                product_id_1__in=seen_pids
            ).exclude(product_id_2__in=seen_pids)
            
            for sim in similarities:
                pid = sim.product_id_2
                # Accumulate similarity scores
                content_scores[pid] = content_scores.get(pid, 0.0) + sim.similarity_score
    except Exception as e:
        print(f"Error getting content recs in Hybrid Scorer: {e}")

    # --- D. Normalize and Blend Scores ---
    all_candidates = set(lstm_scores.keys()) | set(graph_scores.keys()) | set(content_scores.keys())
    
    # Exclude items user already interacted with
    all_candidates = {pid for pid in all_candidates if pid not in seen_pids}
    
    def normalize_dict(d):
        if not d:
            return {}
        max_val = max(d.values())
        min_val = min(d.values())
        diff = max_val - min_val
        if diff == 0:
            return {k: 1.0 for k in d.keys()}
        return {k: (v - min_val) / diff for k, v in d.items()}

    norm_lstm = normalize_dict(lstm_scores)
    norm_graph = normalize_dict(graph_scores)
    norm_content = normalize_dict(content_scores)

    # Weights
    w_lstm = 0.4
    w_graph = 0.4
    w_content = 0.2

    final_rank = []
    for pid in all_candidates:
        s_lstm = norm_lstm.get(pid, 0.0)
        s_graph = norm_graph.get(pid, 0.0)
        s_content = norm_content.get(pid, 0.0)
        
        score = w_lstm * s_lstm + w_graph * s_graph + w_content * s_content
        final_rank.append((pid, score))

    # Sort candidates
    final_rank.sort(key=lambda x: x[1], reverse=True)
    recommended_ids = [pid for pid, _ in final_rank[:limit]]

    # --- E. Fallback Seeding if candidates are insufficient ---
    if len(recommended_ids) < limit:
        # Pull available product nodes not in history & recommendations
        needed = limit - len(recommended_ids)
        available_nodes = ProductNode.objects.exclude(
            product_id__in=seen_pids + recommended_ids
        ).values_list('product_id', flat=True)[:needed]
        recommended_ids.extend(list(available_nodes))

    # Absolute fallback to return any product nodes if still empty
    if not recommended_ids:
        recommended_ids = list(ProductNode.objects.values_list('product_id', flat=True)[:limit])

    return recommended_ids
