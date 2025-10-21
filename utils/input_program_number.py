def input_program_number(programs_count: int) -> int:
    number_of_program = simple_input_program_number()

    while number_of_program not in range(1, programs_count + 1):
        print("\nВы ввели некорректное значение. Попробуйте ещё раз")
        number_of_program = simple_input_program_number()
    return number_of_program

def simple_input_program_number() -> int:
    print("Введите номер исполняемой программы:\n"
          "[1] - Поиск Кбв и Ксв через волновое сопротивление и сопротивление нагрузки\n"
          "[2] - Поиск входного сопротивления через Кбв и расстояние от минимума напряжения\n"
          "[3] - Поиск входного сопротивления на расстоянии от нагрузки\n"
          "[4] - Поиск комплексной нагрузки относительно входного сопротивления\n"
          "[5] - Согласование линии с комплексной нагрузкой при помощи шлейфа\n"
          "[6] - Согласование линии с комплексной нагрузкой при помощи трансформатора\n")
    try:
        program_number = int(input("Поле для ввода: "))
    except ValueError:
        print("\nВы ввели некорректное значение. Попробуйте ещё раз")
        return 0
    return program_number