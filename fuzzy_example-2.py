import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Antecedents are the inputs of the rules
temperature = ctrl.Antecedent(np.arange(0, 41, 5), 'temperature')
humidity    = ctrl.Antecedent(np.arange(0, 101, 10), 'humidity')

# Consequents are the ouputs of the rules
fan_speed   = ctrl.Consequent(np.arange(0, 101, 10), 'fan_speed')

print(f"Universes: \n   temperature: {temperature.universe} \n   humidity: {humidity.universe} \n   fan_speed: {fan_speed.universe}")

# Memberships functions (discrete as in our classes)
temperature['hot'] = np.array([
    0.0,  # 0
    0.0,  # 5
    0.1,  # 10
    0.3,  # 15
    0.6,  # 20
    0.8,  # 25
    1.0,  # 30
    1.0,  # 35
    1.0   # 40
])

humidity['high'] = np.array([
    0.0,  # 0
    0.0,  # 10
    0.2,  # 20
    0.4,  # 30
    0.6,  # 40
    0.8,  # 50
    1.0,  # 60
    1.0,  # 70
    1.0,  # 80
    1.0,  # 90
    1.0   # 100
])

fan_speed['medium'] = np.array([
    0.0,  # 0
    0.3,  # 10
    0.6,  # 20
    1.0,  # 30
    1.0,  # 40
    1.0,  # 50
    0.6,  # 60
    0.3,  # 70
    0.0,  # 80
    0.0,  # 90
    0.0   # 100
])

fan_speed['fast'] = np.array([
    0.0,  # 0
    0.0,  # 10
    0.0,  # 20
    0.0,  # 30
    0.2,  # 40
    0.5,  # 50
    0.8,  # 60
    1.0,  # 70
    1.0,  # 80
    1.0,  # 90
    1.0   # 100
])

# function to print membership functions:
def print_membership(name, universe, mf, precision=1):

    items = [
        f"{u}/{mf_val:.{precision}f}"
        for u, mf_val in zip(universe, mf)
    ]
    print("     "+ name + ": { " + ", ".join(items) + " }")

print("\nMembership functions:")
print_membership("Temperature_Hot", temperature.universe, temperature['hot'].mf)
print_membership("Humidity_High", humidity.universe, humidity['high'].mf)
print_membership("Fan_speed_Medium", fan_speed.universe, fan_speed['medium'].mf)
print_membership("Fan_speed_Fast", fan_speed.universe, fan_speed['fast'].mf)

# Define rules
# Rule1 = (temperature is hot AND humidity is high) then fan speed is fast
rule1 = ctrl.Rule(
    temperature['hot'] & humidity['high'],
    fan_speed['fast']
)

# Rule2 = (temperature is hot OR humidity is high) then fan speed is medium
rule2 = ctrl.Rule(
    temperature['hot'] | humidity['high'],
    fan_speed['medium']
)

# Define inputs
temperature_input = 30
humidity_input = 40

# PASSO 1) Valor de verdade das proposições atómicas das condições das regras
t_pos = np.where(temperature.universe == temperature_input)[0][0]
h_pos = np.where(humidity.universe == humidity_input)[0][0]

t_hot = temperature['hot'].mf[t_pos]
h_high = humidity['high'].mf[h_pos]

print("\nPasso 1) Valores de verdade das proposições atómicas das condições das regras:")
print(f"μ_temp=hot({temperature_input}): {t_hot}")
print(f"μ_hum=high({humidity_input}): {h_high}")

# PASSO 2) Determinação dos valores de verdade das condições lógicas
# Definir os métodos a usar:

rule1_and = min(t_hot, h_high)
rule2_or  = max(t_hot, h_high)

print("\nPasso 2) Determinação dos valores de verdade das condições lógicas:")
print(f"Ө_temp=hot_AND_hum=high({temperature_input}, {humidity_input}): {rule1_and}")
print(f"Ө_temp=hot_OR_hum=high({temperature_input}, {humidity_input}): {rule2_or}")

# PASSO 3) Determinação das contribuições de cada uma das N regras
# Definir o metodo, neste caso truncate

fast_activation   = np.minimum(rule1_and, fan_speed['fast'].mf)
medium_activation = np.minimum(rule2_or,  fan_speed['medium'].mf)

print("\nPasso 3) Determinação das contribuições de cada uma das N regras:")
print_membership("Rule 1 (AND → fast) μ_fan_speed_1:", fan_speed.universe, fast_activation)
print_membership("Rule 2 (OR → medium) μ_fan_speed_2:", fan_speed.universe, medium_activation)

# PASSO 4) Else-link
# Definir o metodo, neste caso OR-link

aggregated = np.maximum(fast_activation, medium_activation)

print("\nPasso 4) Else-link:")
print_membership("μ_fan_speed", fan_speed.universe, aggregated)

# PASSO 5) Desfuzzification
# Definir o metodo

fan_output = fuzz.defuzz(
    fan_speed.universe,
    aggregated,
    "centroid"
)

print("\nPasso 5) Desfuzzy:")
print(f"Exact value of the fan speed: {fan_output:.2f}")