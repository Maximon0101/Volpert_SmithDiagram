from matching_by_train import matching_by_train
from utils.input_program_number import input_program_number


def choose_program_number():
    programs_count = 2

    number_of_program = input_program_number(programs_count)

    match number_of_program:
        case 1:
            matching_by_train()
        case 2:
            print("Aboba")