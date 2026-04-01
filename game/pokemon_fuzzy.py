import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

'''
Cria um sistema Fuzzy que recebe como input a diferença dos niveis
e o efeito do ataque e devolve como input a probabilidade de ganhar
'''

level_universe = np.arange(-10, 11, 1)
level_diff = ctrl.Antecedent(level_universe, "level_diff")

# "low" = em desvantagem ou igual; cai a zero perto de +1
# "high" = vantagem de nível, sobe a partir de 0 e pico ~ +4
level_diff["low"] = fuzz.trimf(level_universe, [-10, -10, 1])
level_diff["high"] = fuzz.trimf(level_universe, [0, 4, 10])

effect_universe = np.array([0.0, 0.25, 0.5, 1.0, 2.0, 4.0])
effect = ctrl.Antecedent(effect_universe, "effect")

# fraco / neutro / forte no produto de efeitos
effect["weak"] = fuzz.trimf(effect_universe, [0.0, 0.0, 0.75])
effect["normal"] = fuzz.trimf(effect_universe, [0.25, 1.0, 2.25])
effect["strong"] = fuzz.trimf(effect_universe, [0.75, 2.5, 4.0])

prob_universe = np.arange(0, 1.01, 0.10)
probability = ctrl.Consequent(prob_universe, "probability")

probability["low"] = fuzz.trimf(prob_universe, [0.0, 0.0, 0.40])
probability["medium"] = fuzz.trimf(prob_universe, [0.20, 0.50, 0.80])
probability["high"] = fuzz.trimf(prob_universe, [0.55, 0.80, 1.00])


rule1 = ctrl.Rule(level_diff['high'] & effect['strong'], probability['high'])   # forte + super eficaz → alto
rule2 = ctrl.Rule(level_diff['high'] & effect['normal'], probability['high'])   # forte + neutro → alto
rule3 = ctrl.Rule(level_diff['high'] & effect['weak'],   probability['medium']) # forte + fraco → médio
rule4 = ctrl.Rule(level_diff['low']  & effect['strong'], probability['medium']) # fraco + super eficaz → médio
rule5 = ctrl.Rule(level_diff['low']  & effect['normal'], probability['low'])    # fraco + neutro → baixo
rule6 = ctrl.Rule(level_diff['low']  & effect['weak'],   probability['low'])    # fraco + fraco → baixo

def calculate_prob(level_input, effect_input) -> float:
    
    level_input  = int(max(-6, min(8, round(level_input))))
    effect_input = float(max(0.0, min(4.0, float(effect_input))))
    
    # PASSO 1) proposições atómicas (robusto)
    l_pos = np.where(level_diff.universe == level_input)[0][0]
    e_pos = np.where(effect.universe == effect_input)[0][0]

    l_high = level_diff['high'].mf[l_pos]
    l_low = level_diff['low'].mf[l_pos]
    e_strong = effect['strong'].mf[e_pos]
    e_normal = effect['normal'].mf[e_pos]
    e_weak = effect['weak'].mf[e_pos]

    # PASSO 2) condições lógicas (AND = min)
    r1 = min(l_high, e_strong)  # high & strong
    r2 = min(l_high, e_normal)  # high & normal
    r3 = min(l_high, e_weak)    # high & weak
    r4 = min(l_low, e_strong)   # low  & strong
    r5 = min(l_low, e_normal)   # low  & normal
    r6 = min(l_low, e_weak)     # low  & weak

    # PASSO 3) implicação (min) — rules 1 & 2 share 'high', combine with max
    high_activation = np.maximum(
        np.minimum(r1, probability["high"].mf),
        np.minimum(r2, probability["high"].mf),
    )
    medium_activation = np.maximum(
        np.minimum(r3, probability["medium"].mf),
        np.minimum(r4, probability["medium"].mf),
    )
    low_activation = np.maximum(
        np.minimum(r5, probability["low"].mf),
        np.minimum(r6, probability["low"].mf),
    )

    # PASSO 4) agregação (max)
    aggregated = np.maximum(high_activation, medium_activation)
    aggregated = np.maximum(aggregated, low_activation)

    # PASSO 5) defuzzificação
    if np.allclose(aggregated, 0):
        return 0.0

    prob_output = fuzz.defuzz(probability.universe, aggregated, "centroid")
    return float(prob_output) if prob_output is not None else 0.0



