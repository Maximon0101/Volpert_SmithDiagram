from programs.find_Zc import find_Zc
from programs.find_Zin import find_Zin
from programs.matching_by_train import matching_by_train
from utils.input_program_number import input_program_number


def choose_program_number():
    programs_count = 3

    number_of_program = input_program_number(programs_count)

    match number_of_program:
        case 1:
            find_Zin()
        case 2:
            find_Zc()
        case 3:
            matching_by_train()