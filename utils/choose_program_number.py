from programs.find_Zc import find_Zc
from programs.find_Zin import find_Zin
from programs.matching_by_train import matching_by_train
from programs.matching_by_transformer import matching_by_transformer
from utils.input_program_number import input_program_number


def choose_program_number():
    programs_count = 4

    number_of_program = input_program_number(programs_count)

    match number_of_program:
        case 0:
            print()
        case 1:
            find_Zin()
        case 2:
            find_Zc()
        case 3:
            matching_by_train()
        case 4:
            matching_by_transformer()