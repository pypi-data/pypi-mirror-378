class CalculadoraIMC:
    """Clase para calcular y clasificar el Índice de Masa Corporal"""
    
    @staticmethod
    def calcular(peso_kg: float, altura_m: float) -> float:
        
        if altura_m <= 0:
            raise ValueError("La altura debe ser mayor a cero")
        return peso_kg / (altura_m ** 2)
    
    @staticmethod
    def clasificar(imc: float) -> str:
       
        if imc < 18.5:
            return "Bajo peso"
        elif 18.5 <= imc < 25:
            return "Peso normal"
        elif 25 <= imc < 30:
            return "Sobrepeso"
        elif 30 <= imc < 35:
            return "Obesidad grado I"
        elif 35 <= imc < 40:
            return "Obesidad grado II"
        else:
            return "Obesidad grado III"


class CalculadoraGrasaCorporal:
    """Clase para calcular el porcentaje de grasa corporal"""
    
    @staticmethod
    def calcular(imc: float, edad: int, sexo: str) -> float:
      
        if sexo.upper() == 'M':
            return (1.20 * imc) + (0.23 * edad) - 16.2
        elif sexo.upper() == 'F':
            return (1.20 * imc) + (0.23 * edad) - 5.4
        else:
            raise ValueError("El sexo debe ser 'M' o 'F'")


class CalculadoraMasaMuscular:
    """Clase para calcular la masa muscular y composición corporal"""
    
    @staticmethod
    def calcular(peso_kg: float, porcentaje_grasa: float) -> dict:
      
        grasa_kg = (porcentaje_grasa / 100) * peso_kg
        masa_magra_kg = peso_kg - grasa_kg
        
        return {
            'peso_total_kg': peso_kg,
            'grasa_corporal_kg': grasa_kg,
            'masa_magra_kg': masa_magra_kg,
            'porcentaje_grasa': porcentaje_grasa
        }
