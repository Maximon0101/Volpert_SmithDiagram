def input_program_number(programs_count: int) -> int:
    number_of_program = simple_input_program_number()

    if number_of_program not in range(1, programs_count + 1):
        print("\nВы ввели некорректное значение. Попробуйте ещё раз")
        number_of_program = simple_input_program_number()
    return number_of_program

def simple_input_program_number() -> int:
    print("Введите номер исполняемой программы:\n"
          "[1] - Согласовании линии с комплексной нагрузкой при помощи шлейфа\n"
          "[2] - Aboba\n")
    return int(input("Поле для ввода: "))