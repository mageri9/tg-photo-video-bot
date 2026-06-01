# translation_cost.py
COST_PER_WORD_RUB = 0.0235

def calculate_translation_cost(prompt: str) -> float:
    """
    Считает стоимость перевода промпта (на русском)
    Возвращает цену в рублях
    """
    words = prompt.strip().split()
    word_count = len(words)
    return word_count * COST_PER_WORD_RUB