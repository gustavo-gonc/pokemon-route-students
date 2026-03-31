import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

'''
Cria um sistema Fuzzy que recebe como input a diferença dos niveis
e o efeito do ataque e devolve como input a probabilidade de ganhar
'''

level    = ctrl.Antecedent(np.arange(-10, 11, 1), 'level')
effect    = ctrl.Antecedent(np.array([0.0, 0.25, 0.5, 1.0, 2.0, 4.0]), 'effect')
probability = ctrl.Consequent(np.arange(0, 1.01, 0.10), 'probability')

level['low'] = np.array([
    1.0,  # -10
    1.0,  # -9
    1.0,  # -8
    1.0,  # -7
    1.0,  # -6
    0.9,  # -5
    0.8,  # -4
    0.7,  # -3
    0.6,  # -2
    0.5,  # -1
    0.4,  # 0
    0.3,  # 1
    0.2,  # 2
    0.1,  # 3
    0.0,  # 4
    0.0,  # 5
    0.0,  # 6
    0.0,  # 7
    0.0,  # 8
    0.0,  # 9
    0.0   # 10
])  

level['high'] = np.array([
    0.0,  # -10
    0.0,  # -9
    0.0,  # -8
    0.0,  # -7
    0.0,  # -6
    0.0,  # -5
    0.0,  # -4
    0.0,  # -3
    0.1,  # -2
    0.2,  # -1
    0.3,  # 0
    0.4,  # 1
    0.5,  # 2
    0.6,  # 3
    0.7,  # 4
    0.8,  # 5
    0.9,  # 6
    1.0,  # 7
    1.0,  # 8
    1.0,  # 9
    1.0   # 10
])

effect['weak'] = np.array([
    1.0,   # 0.0
    0.7,   # 0.25
    0.5,   # 0.5
    0.3,   # 1.0
    0.1,   # 2.0
    0.0    # 4.0
])

effect['strong'] = np.array([
    0.0,   # 0.0
    0.2,   # 0.25
    0.4,   # 0.5
    0.7,   # 1.0
    0.9,   # 2.0
    1.0    # 4.0
])

probability['low'] = np.array([1.0, 0.8, 0.6, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
probability['medium'] = np.array([0.0, 0.0, 0.2, 0.6, 1.0, 1.0, 1.0, 0.6, 0.2, 0.0, 0.0])
probability['high'] = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

# encontra o índice mais próximo de um valor num universo
def _closest_index(universe, value):
    value = float(np.clip(value, universe[0], universe[-1]))
    return int(np.argmin(np.abs(universe - value)))

def calculate_prob(level_input, effect_input):
    
    rule1 = ctrl.Rule(level['high'] & effect['strong'], probability['high'])
    rule2 = ctrl.Rule(level['high'] & effect['weak'], probability['high'])
    rule3 = ctrl.Rule(level['low'] & effect['strong'], probability['medium'])
    rule4 = ctrl.Rule(level['low'] & effect['weak'], probability['low'])

    # PASSO 1) proposições atómicas (robusto)
    level_pos = _closest_index(level.universe, level_input)
    effect_pos = _closest_index(effect.universe, effect_input)

    l_high = level['high'].mf[level_pos]
    l_low = level['low'].mf[level_pos]
    e_strong = effect['strong'].mf[effect_pos]
    e_weak = effect['weak'].mf[effect_pos]

    # PASSO 2) condições lógicas (AND = min)
    rule1_fire = min(l_high, e_strong)   # high & strong
    rule2_fire = min(l_high, e_weak)     # high & weak
    rule3_fire = min(l_low, e_strong)    # low  & strong
    rule4_fire = min(l_low, e_weak)      # low  & weak

    # PASSO 3) implicação (min) — rules 1 & 2 share 'high', combine with max
    high_activation = np.maximum(
        np.minimum(rule1_fire, probability['high'].mf),
        np.minimum(rule2_fire, probability['high'].mf),
    )
    medium_activation = np.minimum(rule3_fire, probability['medium'].mf)
    low_activation    = np.minimum(rule4_fire, probability['low'].mf)

    # PASSO 4) agregação (max)
    aggregated = np.maximum(high_activation, medium_activation)
    aggregated = np.maximum(aggregated, low_activation)

    # PASSO 5) defuzzificação
    if np.allclose(aggregated, 0):
        return 0.0

    prob_output = fuzz.defuzz(probability.universe, aggregated, "centroid")
    return float(np.clip(prob_output, 0.0, 1.0))
