import numpy as np


def matching_by_transformer():
    """
    Главная функция для запуска расчета согласования трансформатором.
    """
    print("----------------------------------------------------------------------------------------------------------\n"
          "Согласование линии с комплексной нагрузкой при помощи трансформатора\n")
    try:
        # Изменено значение по умолчанию на 1
        W_input = input("Введите волновое сопротивление основной линии W (по умолчанию 1): ")
        W_val = float(W_input) if W_input != '' else 1.0

        Rn = float(input("Введите активную составляющую нагрузки Rn: "))
        Xn = float(input("Введите реактивную составляющую нагрузки Xn (со знаком): "))
        Zn_val = complex(Rn, Xn)

        # Вызываем основную расчетную функцию
        calculate_transformer_matching(W=W_val, Zn=Zn_val)

    except ValueError:
        print("\nОшибка! Введено некорректное число. Пожалуйста, перезапустите программу"
              "\nПерепроверьте раскладку клавиатуры. Она должна быть EN")
        return


def calculate_transformer_matching(W, Zn):
    """
    Рассчитывает параметры согласующей цепи на основе λ/4 трансформатора.
    Эта версия находит и выводит ОБА возможных решения.
    """
    print(f"\n--- Расчет согласования трансформатором для W={W} Ом, Zn={Zn} Ом ---")

    # --- 1. Начальные расчеты ---
    z0 = W
    z_load = Zn

    # Если нагрузка уже чисто активная, решение тривиально
    if np.isclose(z_load.imag, 0):
        print("\nНагрузка уже является чисто активной. Дополнительный отрезок линии не требуется (d1 = 0).")
        R_in_at_d1 = z_load.real
        Wt = np.sqrt(z0 * R_in_at_d1)
        print(f"\n--- Единственное решение ---")
        print(f"1. Волновое сопротивление трансформатора (Wt): {Wt:.2f} Ом")
        print(f"2. Длина трансформатора: 0.25λ")
        return

    # --- 2. Поиск ВСЕХ точек, где сопротивление становится чисто активным ---
    gamma_load = (z_load - z0) / (z_load + z0)
    solutions = []
    last_imag_sign = np.sign(z_load.imag)

    for d_in_lambda in np.linspace(0.0001, 0.5, 2000):
        gamma_at_d = gamma_load * np.exp(-2j * 2 * np.pi * d_in_lambda)
        z_at_d = z0 * (1 + gamma_at_d) / (1 - gamma_at_d)
        current_imag_sign = np.sign(z_at_d.imag)

        if current_imag_sign != last_imag_sign and last_imag_sign != 0:
            solutions.append({'d1_lambda': d_in_lambda, 'R_in': z_at_d.real})

        last_imag_sign = current_imag_sign

    if len(solutions) < 2:
        print("\nНе удалось найти два решения. Возможно, нагрузка чисто активная или находится на границе диаграммы.")
        # Если найдено хотя бы одно решение, все равно его покажем
        if not solutions: return

    # --- 3. Вывод результатов для КАЖДОГО найденного решения ---
    print(f"\nНайдено {len(solutions)} возможных решения:")

    for i, solution in enumerate(solutions):
        d1_lambda = solution['d1_lambda']
        R_in_at_d1 = solution['R_in']

        # Рассчитываем параметры трансформатора для этого конкретного решения
        Wt = np.sqrt(z0 * R_in_at_d1)
        d_transformer_lambda = 0.25

        # Определяем подпись для трансформатора
        if np.isclose(Wt, z0):
            label = "(Wt = W - согласование уже достигнуто, трансформатор не нужен)"
        elif Wt < z0:
            # Wt < W используется для согласования низкой R_in с высокой W (повышение)
            label = "(Wt < W - повышающий трансформатор сопротивления)"
        else:  # Wt > z0
            # Wt > W используется для согласования высокой R_in с низкой W (понижение)
            label = "(Wt > W - понижающий трансформатор сопротивления)"

        print(f"\n--- Решение {i + 1} ---")
        print(f"1. Длина отрезка до трансформатора (dzтр): {d1_lambda:.4f}λ")
        print(f"(В этой точке входное сопротивление становится: {R_in_at_d1:.2f} Ом)")
        print(f"2. Волновое сопротивление трансформатора (Wt): {Wt:.2f} Ом {label}")
        print(f"3. Длина трансформатора: {d_transformer_lambda:.2f}λ")
