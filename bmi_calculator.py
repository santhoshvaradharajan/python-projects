def bmi_calculator(weight, height):
    bmi = weight / height ** 2
    return round(bmi, 1)

def get_category(bmi):
    if bmi < 18.5:
        return("lower weight")
    elif bmi < 25:
        return("Normal")
    elif bmi < 30:
        return("Over Weight")
    else:
        return("obese")         

def main():
    weight = float(input("Your Heigh(kg): "))
    height = float(input("Your Weight(m): "))
    bmi = bmi_calculator(height, weight)
    category = get_category(bmi)
    print(f"BMI: {bmi}")
    print(f"CATEGORY: {category}")

main()