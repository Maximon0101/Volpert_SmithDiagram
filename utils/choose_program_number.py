from programs.find_Zc import find_Zc
from programs.find_Zin import find_Zin
from programs.find_Zin_by_twr import find_Zin_by_twr
from programs.find_twr_and_swr import find_twr_and_swr
from programs.matching_by_train import matching_by_train
from programs.matching_by_transformer import matching_by_transformer
from utils.input_program_number import input_program_number


def choose_program_number():
    programs_count = 6

    number_of_program = input_program_number(programs_count)

    match number_of_program:
        case 0:
            print()
        case 1:
            find_twr_and_swr()
        case 2:
            find_Zin_by_twr()
        case 3:
            find_Zin()
        case 4:
            find_Zc()
        case 5:
            matching_by_train()
        case 6:
            matching_by_transformer()