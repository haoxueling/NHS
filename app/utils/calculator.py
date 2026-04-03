"""Strictly implemented in accordance with the scoring rules specified in NHS.pdf"""


def calculate_dasi(answers):
    """DASI Questionnaire Scoring (NHS.pdf 1-1 to 1-52)"""
    score_map = {
        'self_care': 2.75 if answers.get('self_care') == 'yes' else 0,
        'walk_indoors': 1.75 if answers.get('walk_indoors') == 'yes' else 0,
        'walk_blocks': 2.75 if answers.get('walk_blocks') == 'yes' else 0,
        'climb_stairs': 5.5 if answers.get('climb_stairs') == 'yes' else 0,
        'run_short': 8 if answers.get('run_short') == 'yes' else 0,
        'light_work': 2.7 if answers.get('light_work') == 'yes' else 0,
        'moderate_work': 3.5 if answers.get('moderate_work') == 'yes' else 0,
        'heavy_work': 8 if answers.get('heavy_work') == 'yes' else 0,
        'yardwork': 4.5 if answers.get('yardwork') == 'yes' else 0,
        'sexual_relations': 5.25 if answers.get('sexual_relations') == 'yes' else 0,
        'moderate_recreation': 6 if answers.get('moderate_recreation') == 'yes' else 0,
        'strenuous_sports': 7.5 if answers.get('strenuous_sports') == 'yes' else 0
    }
    total_score = sum(score_map.values())

    # Calculating METs (NHS.pdf formulae 1–46)
    vo2_peak = 0.43 * total_score + 9.6
    mets = vo2_peak / 3.5

    # Level classification (NHS.pdf 1-51)
    if mets > 7:
        level = 'universal'
    elif 4 <= mets <= 7:
        level = 'targeted'
    else:
        level = 'specialist'

    return {'score': round(total_score, 2), 'level': level}


def calculate_phq4(answers):
    """PHQ-4 Questionnaire Scoring (NHS.pdf 1-53 to 1-97)"""
    total_score = sum(answers.values())

    # Level classification (NHS.pdf 1-96)
    if total_score <= 5:
        level = 'universal'
    elif 6 <= total_score <= 8:
        level = 'targeted'
    else:
        level = 'specialist'

    return {'score': total_score, 'level': level}


def calculate_pgsga(answers):
    """ PG-SGA Questionnaire Scoring (NHS.pdf 1-98 to 1-135)"""
    # 1. Weight History (Cumulative, NHS.pdf 1-129)
    weight_score = answers.get('weight_change', 0)

    # 2.    Food Intake (Take the highest score, NHS.pdf 1-129)
    food_compare = answers.get('food_intake_compare', 0)
    food_type = answers.get('food_intake_type', 0)
    food_score = max(food_compare, food_type)

    # 3.    Symptoms (Cumulative, NHS.pdf 1-129)
    symptoms_score = sum(answers.get('symptoms', {}).values(), 0)

    # 4.    Activity and Function (NHS.pdf 1-130)
    activity_score = answers.get('activity_level', 0)

    #   Total Score
    total_score = weight_score + food_score + symptoms_score + activity_score

    #   Level classification (NHS.pdf 1-134)
    if total_score <= 1:
        level = 'universal'
    elif 2 <= total_score <= 3:
        level = 'targeted'
    else:
        level = 'specialist'

    return {'score': total_score, 'level': level}


calculator_map = {
    'dasi': calculate_dasi,
    'phq4': calculate_phq4,
    'pgsga': calculate_pgsga
}