from utils.choose_program_number import choose_program_number


def main():
    do_program = True

    print("Добро пожаловать в программу для работы с диаграммой Вольперта-Смита\n")

    while do_program:
        choose_program_number()

        print("\n-----------------------------------------------------------------------------------------------------")
        do_program_text = input("Выйти из программы? (Y/n): ")
        while (do_program_text not in ['Y', 'y', 'N', 'n', '']):
            print("\nВы ввели некорректное значение. Попробуйте ещё раз")
            do_program_text = input("Выйти из программы? (Y/n): ")

        if do_program_text in ['Y', 'y', '']:
            do_program = False
        else: do_program = True

if __name__ == '__main__':
    main()
