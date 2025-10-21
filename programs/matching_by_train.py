import numpy as np

# --- Глобальное определение функции арккотангенса ---
# В numpy нет встроенной функции arccot, поэтому определяем ее через arctan.
# np.arccot(x) = pi/2 - np.arctan(x)
np.arccot = lambda x: np.pi / 2 - np.arctan(x)


def matching_by_train():
    """
    Главная функция для запуска расчетов.
    """
    print("----------------------------------------------------------------------------------------------------------\n"
          "Согласование линии с комплексной нагрузкой при помощи шлейфа\n")
    try:
        W_input = input("Введите волновое сопротивление линии W (по умолчанию 1): ")
        W_val = float(W_input) if W_input != '' else 1.0

        Rn_input = input("Введите активную составляющую нагрузки Rn (по умолчанию 0): ")
        Rn = float(Rn_input) if Rn_input != '' else 0.0
        Xn_input = input("Введите реактивную составляющую нагрузки Xn со знаком (по умолчанию 0): ")
        Xn = float(Xn_input) if Xn_input != '' else 0.0
        Zn_val = complex(Rn, Xn)

        is_series_str = input(
            "Выберите тип согласования:\n 1. Последовательное (по умолчанию)\n 2. Параллельное\nВаш выбор (1/2): ")
        while is_series_str not in ['1', '2', '']:
            print("\nВы ввели некорректное значение. Попробуйте ещё раз")
            is_series_str = input("Ваш выбор (1/2): ")

        is_series = False if is_series_str == '2' else True

        if is_series:
            calculate_series_stub_matching(W=W_val, Zn=Zn_val)
        else:
            calculate_parallel_stub_matching(W=W_val, Zn=Zn_val)

    except ValueError:
        print("\nОшибка! Введено некорректное число. Пожалуйста, перезапустите программу"
              "\nПерепроверьте раскладку клавиатуры. Она должна быть EN")
        return


def calculate_parallel_stub_matching(W, Zn):
    """
    Рассчитывает параметры согласования с помощью ПАРАЛЛЕЛЬНОГО шлейфа.
    """
    print(f"\n--- Расчет ПАРАЛЛЕЛЬНОГО согласования для W={W} Ом, Zn={Zn} Ом ---")

    z0 = W
    z_load = Zn
    gamma_load = (z_load - z0) / (z_load + z0)

    min_diff = float('inf')
    best_solution = {}
    for d_in_lambda in np.linspace(0, 0.5, 2001):
        gamma_at_d = gamma_load * np.exp(-2j * 2 * np.pi * d_in_lambda)
        current_y_norm = (1 - gamma_at_d) / (1 + gamma_at_d)
        current_diff = abs(current_y_norm.real - 1.0)
        if current_diff < min_diff:
            min_diff = current_diff
            best_solution['dz_lambda'] = d_in_lambda
            best_solution['y_at_dz_norm'] = current_y_norm

    dz_lambda = best_solution['dz_lambda']
    y_at_dz_norm = best_solution['y_at_dz_norm']
    print(f"Результат: dz = {dz_lambda:.4f}λ")
    print(f"(Найденная нормализованная проводимость в точке: {y_at_dz_norm:.2f})")

    required_susceptance_norm = -y_at_dz_norm.imag
    print(f"\nТребуемая нормализованная проводимость шлейфа: {required_susceptance_norm:+.2f}j")

    cot_val_short = -required_susceptance_norm
    beta_l_short = np.arccot(cot_val_short)
    if beta_l_short < 0: beta_l_short += np.pi
    l_short_lambda = beta_l_short / (2 * np.pi)

    tan_val_open = required_susceptance_norm
    beta_l_open = np.arctan(tan_val_open)
    if beta_l_open < 0: beta_l_open += np.pi
    l_open_lambda = beta_l_open / (2 * np.pi)

    print(f"\nРезультат: l_short = {l_short_lambda:.4f}λ")
    print(f"Результат: l_open = {l_open_lambda:.4f}λ")

    y_at_dz = y_at_dz_norm / z0
    y_final = y_at_dz + 1j * (required_susceptance_norm / z0)
    z_final = 1 / y_final
    print("\n--- Проверка ---")
    print(f"Итоговое комплексное сопротивление схемы: {z_final.real:.2f}{z_final.imag:+.2f}j Ом")


def calculate_series_stub_matching(W, Zn):
    """
    Рассчитывает параметры ПОСЛЕДОВАТЕЛЬНОГО согласования.
    """
    print(f"\n--- Расчет ПОСЛЕДОВАТЕЛЬНОГО согласования для W={W} Ом, Zn={Zn} Ом ---")

    z0 = W
    z_load = Zn
    gamma_load = (z_load - z0) / (z_load + z0)

    min_diff = float('inf')
    best_solution = {}
    for d_in_lambda in np.linspace(0, 0.5, 2001):
        gamma_at_d = gamma_load * np.exp(-2j * 2 * np.pi * d_in_lambda)
        z_at_d = z0 * (1 + gamma_at_d) / (1 - gamma_at_d)
        current_z_norm = z_at_d / z0
        current_diff = abs(current_z_norm.real - 1.0)
        if current_diff < min_diff:
            min_diff = current_diff
            best_solution['dz_lambda'] = d_in_lambda
            best_solution['z_at_dz_norm'] = current_z_norm

    if min_diff > 0.01:
        print("\nРешение не найдено (физически невозможно для данных Zn и W).")
        return

    dz_lambda = best_solution['dz_lambda']
    z_at_dz_norm = best_solution['z_at_dz_norm']
    print(f"Результат: dz = {dz_lambda:.4f}λ")
    print(f"(Найденное нормализованное сопротивление в точке: {z_at_dz_norm:.2f})")

    required_reactance = -z_at_dz_norm.imag * z0
    print(f"\nТребуемое реактивное сопротивление шлейфа: {required_reactance:+.2f}j Ом")

    tan_val_short = required_reactance / z0
    beta_l_short = np.arctan(tan_val_short)
    if beta_l_short < 0: beta_l_short += np.pi
    l_short_lambda = beta_l_short / (2 * np.pi)

    cot_val_open = -required_reactance / z0
    beta_l_open = np.arccot(cot_val_open)
    if beta_l_open < 0: beta_l_open += np.pi
    l_open_lambda = beta_l_open / (2 * np.pi)

    print(f"\nРезультат: l_short = {l_short_lambda:.4f}λ")
    print(f"Результат: l_open = {l_open_lambda:.4f}λ")

    # --- 4. Проверка результата ---
    # Сопротивление в точке подключения (не нормированное)
    z_at_dz = z_at_dz_norm * z0
    # Суммируем сопротивления (т.к. соединение последовательное), шлейф добавляет только реактивность
    z_final = z_at_dz + 1j * required_reactance

    print("\n--- Проверка ---")
    print(f"Итоговое комплексное сопротивление схемы: {z_final.real:.2f}{z_final.imag:+.2f}j Ом")
