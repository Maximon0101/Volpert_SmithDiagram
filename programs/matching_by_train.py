import numpy as np
import skrf as rf  # skrf используется только для финальной проверки, не для основных расчетов

# --- Глобальное определение функции арккотангенса ---
# В numpy нет встроенной функции arccot, поэтому определяем ее через arctan.
# np.arccot(x) = pi/2 - np.arctan(x)

def matching_by_train():
    """
    Главная функция для запуска расчетов.
    """
    print("----------------------------------------------------------------------------------------------------------\n"
          "Согласовании линии с комплексной нагрузкой при помощи шлейфа\n")

    W_val = input("Введите волновое сопротивление линии W (по умолчанию 1): ")
    if W_val == '': W_val = 1.0
    else: W_val = float(W_val)

    Rn = float(input("Введите активную составляющую нагрузки Rn: "))
    Xn = float(input("Введите реактивную составляющую нагрузки Xn (со знаком и без j): "))
    Zn_val = complex(Rn, Xn)


    is_series_str = input("Последовательное включение? Если нет, то параллельное (Y/n): ")
    while (is_series_str not in ['Y', 'y', 'N', 'n', '']):
        print("\nВы ввели некорректное значение. Попробуйте ещё раз")
        is_series_str = input("Последовательное включение? Если нет, то параллельное (Y/n): ")

    if is_series_str in ['Y', 'y', '']: is_series = True
    else: is_series = False

    if is_series: calculate_series_stub_matching(W=W_val, Zn=Zn_val)
    else: calculate_parallel_stub_matching(W=W_val, Zn=Zn_val)


np.arccot = lambda x: np.pi / 2 - np.arctan(x)


def calculate_parallel_stub_matching(W, Zn):
    """
    Рассчитывает параметры согласования с помощью ПАРАЛЛЕЛЬНОГО шлейфа.
    Этот метод находит точку, БЛИЖАЙШУЮ к цели, что делает его надежным.
    """
    print(f"\n--- Расчет ПАРАЛЛЕЛЬНОГО согласования для W={W} Ом, Zn={Zn} Ом ---")


    # --- 1. Начальные расчеты ---
    z0 = W                                      # Присваиваем волновое сопротивление переменной z0 для краткости
    z_load = Zn                                 # Присваиваем сопротивление нагрузки
    gamma_load = (z_load - z0) / (z_load + z0)  # Рассчитываем коэффициент отражения от нагрузки по стандартной формуле


    # --- 2. Поиск точки подключения ---
    min_diff = float('inf')     # Задаем начальную "бесконечную" разницу для поиска минимума
    best_solution = {}          # Создаем словарь для хранения лучшего найденного решения

    # Проходим по всей возможной длине линии от 0 до половины длины волны
    for d_in_lambda in np.linspace(0, 0.5, 2001):
        gamma_at_d = gamma_load * np.exp(-2j * 2 * np.pi * d_in_lambda)     # "Движение по линии" - это поворот вектора Gamma в комплексной плоскости
        current_y_norm = (1 - gamma_at_d) / (1 + gamma_at_d)                # Преобразуем повернутый Gamma в НОРМАЛИЗОВАННУЮ ПРОВОДИМОСТЬ (y)

        current_diff = abs(current_y_norm.real - 1.0)                       # Находим, насколько реальная часть текущей проводимости отличается от 1.0


        # Если текущая точка ближе к цели (Re(y) = 1), чем все предыдущие...
        if current_diff < min_diff:
            min_diff = current_diff  # ...обновляем минимальную разницу...
            # ...и запоминаем все параметры этой лучшей точки
            best_solution['dz_lambda'] = d_in_lambda
            best_solution['y_at_dz_norm'] = current_y_norm


    # --- 3. Расчет длин шлейфов на основе найденной точки ---
    dz_lambda = best_solution['dz_lambda']          # Извлекаем расстояние до точки подключения
    y_at_dz_norm = best_solution['y_at_dz_norm']    # Извлекаем проводимость в этой точке

    print(f"Результат: dz = {dz_lambda:.4f}λ")
    print(f"(Найденная нормализованная проводимость в точке: {y_at_dz_norm:.2f})")

    # Чтобы согласовать цепь, шлейф должен создать проводимость, противоположную мнимой части в точке dz
    required_susceptance_norm = -y_at_dz_norm.imag
    print(f"\nТребуемая нормализованная проводимость шлейфа: {required_susceptance_norm:+.2f}j")


    # --- Расчет короткозамкнутого шлейфа (l_short) ---
    cot_val_short = -required_susceptance_norm      # Нормированная проводимость КЗ шлейфа: y = -j*cot(beta*l). Нам нужно решить это уравнение.
    beta_l_short = np.arccot(cot_val_short)         # Находим электрическую длину (beta*l) через арккотангенс

    # Если угол отрицательный, добавляем pi (пол-оборота), чтобы получить наименьшую положительную длину
    if beta_l_short < 0: beta_l_short += np.pi

    l_short_lambda = beta_l_short / (2 * np.pi)     # Превращаем электрическую длину в доли длины волны (lambda)


    # --- Расчет разомкнутого шлейфа (l_open) ---
    tan_val_open = required_susceptance_norm        # Нормированная проводимость ХХ шлейфа: y = j*tan(beta*l).
    beta_l_open = np.arctan(tan_val_open)           # Находим электрическую длину (beta*l) через арктангенс

    # Гарантируем положительную длину
    if beta_l_open < 0: beta_l_open += np.pi

    l_open_lambda = beta_l_open / (2 * np.pi)       # Превращаем в доли длины волны

    print(f"\nРезультат: l_short = {l_short_lambda:.4f}λ")
    print(f"Результат: l_open = {l_open_lambda:.4f}λ")


    # --- 4. Проверка результата ---
    y_at_dz = y_at_dz_norm / z0                                 # Проводимость в точке подключения (не нормированная)
    y_final = y_at_dz + 1j * (required_susceptance_norm / z0)   # Суммируем проводимости (т.к. соединение параллельное)
    z_final = 1 / y_final                                       # Итоговое сопротивление - это 1 / итоговая проводимость

    print("\n--- Проверка ---")
    print(f"Итоговое комплексное сопротивление схемы: {z_final.real:.2f}{z_final.imag:+.2f}j Ом")


def calculate_series_stub_matching(W, Zn):
    """
    Рассчитывает параметры ПОСЛЕДОВАТЕЛЬНОГО согласования.
    """
    print(f"\n--- Расчет ПОСЛЕДОВАТЕЛЬНОГО согласования для W={W} Ом, Zn={Zn} Ом ---")


    # --- 1. Начальные расчеты ---
    z0 = W
    z_load = Zn
    gamma_load = (z_load - z0) / (z_load + z0)


    # --- 2. Поиск точки подключения ---
    min_diff = float('inf')
    best_solution = {}

    for d_in_lambda in np.linspace(0, 0.5, 2001):
        gamma_at_d = gamma_load * np.exp(-2j * 2 * np.pi * d_in_lambda)

        # Преобразуем повернутый Gamma в НОРМАЛИЗОВАННОЕ СОПРОТИВЛЕНИЕ (z)
        z_at_d = z0 * (1 + gamma_at_d) / (1 - gamma_at_d)
        current_z_norm = z_at_d / z0

        # Ищем точку, ближайшую к цели Re(z)=1
        current_diff = abs(current_z_norm.real - 1.0)
        if current_diff < min_diff:
            min_diff = current_diff
            best_solution['dz_lambda'] = d_in_lambda
            best_solution['z_at_dz_norm'] = current_z_norm

    # Проверяем, смогли ли мы приблизиться к цели. Если нет - согласование невозможно.
    if min_diff > 0.01:
        print("Решение не найдено (физически невозможно для данных Zn и W).")
        return


    # --- 3. Расчет длин шлейфов ---
    dz_lambda = best_solution['dz_lambda']
    z_at_dz_norm = best_solution['z_at_dz_norm']
    print(f"Результат: dz = {dz_lambda:.4f}λ")

    # Шлейф должен создать сопротивление, противоположное мнимой части в точке dz
    required_reactance = -z_at_dz_norm.imag * z0
    print(f"\nТребуемое реактивное сопротивление шлейфа: {required_reactance:+.2f}j Ом")


    # --- Расчет короткозамкнутого шлейфа (l_short) ---
    # Нормированное сопротивление КЗ шлейфа: z = j*tan(beta*l).
    tan_val_short = required_reactance / z0
    beta_l_short = np.arctan(tan_val_short)

    if beta_l_short < 0: beta_l_short += np.pi

    l_short_lambda = beta_l_short / (2 * np.pi)


    # --- Расчет разомкнутого шлейфа (l_open) ---
    # Нормированное сопротивление ХХ шлейфа: z = -j*cot(beta*l).
    cot_val_open = -required_reactance / z0
    beta_l_open = np.arccot(cot_val_open)

    if beta_l_open < 0: beta_l_open += np.pi

    l_open_lambda = beta_l_open / (2 * np.pi)

    print(f"\nРезультат: l_short = {l_short_lambda:.4f}λ")
    print(f"Результат: l_open = {l_open_lambda:.4f}λ")
