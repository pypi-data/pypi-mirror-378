from hight_bod_heavy import CalculadoraIMC, CalculadoraGrasaCorporal, CalculadoraMasaMuscular

# Calcular IMC
imc = CalculadoraIMC.calcular(70, 1.75)
categoria = CalculadoraIMC.clasificar(imc)

# Calcular porcentaje de grasa
grasa = CalculadoraGrasaCorporal.calcular(imc, 30, 'M')

# Calcular masa muscular
composicion = CalculadoraMasaMuscular.calcular(70, grasa)

print(f"IMC: {imc:.2f} ({categoria})")
print(f"Grasa corporal: {grasa:.2f}%")
print(f"Masa magra: {composicion['masa_magra_kg']:.2f}kg")