import numpy as np
import skrf as rf  # skrf нужен только для последней проверки, не для расчетов

# --- Глобальное определение функции арккотангенса ---
# np.arccot(x) = pi/2 - np.arctan(x)
np.arccot = lambda x: np.pi / 2 - np.arctan(x)


def calculate_parallel_stub_matching(W, soprotivlenie_nagruzki):
    """
    Рассчитывает параметры согласования с помощью ПАРАЛЛЕЛЬНОГО шлейфа.
    Этот метод находит точку, БЛИЖАЙШУЮ к цели, что делает его надежным.
    """
    print(f"\n--- Расчет ПАРАЛЛЕЛЬНОГО согласования для W={W} Ом, Zn={soprotivlenie_nagruzki} Ом ---")

    z0 = W
    z_load = soprotivlenie_nagruzki
    gamma_load = (z_load - z0) / (z_load + z0)

    # --- Новый, надежный алгоритм поиска ---
    min_diff = float('inf')  # Начальная "бесконечная" разница
    best_solution = {}  # Словарь для хранения лучшего найденного решения

    for d_in_lambda in np.linspace(0, 0.5, 2001):
        gamma_at_d = gamma_load * np.exp(-2j * 2 * np.pi * d_in_lambda)
        current_y_norm = (1 - gamma_at_d) / (1 + gamma_at_d)

        current_diff = abs(current_y_norm.real - 1.0)

        if current_diff < min_diff:
            # Если текущая точка ближе к цели, чем все предыдущие, запоминаем ее
            min_diff = current_diff
            best_solution['dz_lambda'] = d_in_lambda
            best_solution['y_at_dz_norm'] = current_y_norm

    if not best_solution:
        print("Решение не найдено.")
        return

    # --- Используем найденное лучшее решение ---
    dz_lambda = best_solution['dz_lambda']
    y_at_dz_norm = best_solution['y_at_dz_norm']

    print(f"Результат: dz = {dz_lambda:.4f}λ")
    print(f"       (Найденная нормализованная проводимость в этой точке: {y_at_dz_norm:.2f})")

    required_susceptance_norm = -y_at_dz_norm.imag
    cot_val_short = -required_susceptance_norm
    beta_l_short = np.arccot(cot_val_short)
    if beta_l_short < 0:
        beta_l_short += np.pi
    l_short_lambda = beta_l_short / (2 * np.pi)

    # Расчет для разомкнутого шлейфа
    tan_val_open = required_susceptance_norm
    beta_l_open = np.arctan(tan_val_open)
    if beta_l_open < 0:
        beta_l_open += np.pi
    l_open_lambda = beta_l_open / (2 * np.pi)

    print(f"Результат: l_short = {l_short_lambda:.4f}λ")
    print(f"Результат: l_open = {l_open_lambda:.4f}λ")

    # --- Проверка результата ---
    y_at_dz = y_at_dz_norm / z0
    y_final = y_at_dz + 1j * (required_susceptance_norm / z0)
    z_final = 1 / y_final
    print("\n--- Проверка ---")
    print(f"Итоговое комплексное сопротивление схемы: {z_final.real:.2f}{z_final.imag:+.2f}j Ом")


def calculate_series_stub_matching(W, soprotivlenie_nagruzki):
    """
    Рассчитывает параметры ПОСЛЕДОВАТЕЛЬНОГО согласования.
    """
    print(f"\n--- Расчет ПОСЛЕДОВАТЕЛЬНОГО согласования для W={W} Ом, Zn={soprotivlenie_nagruzki} Ом ---")

    z0 = W
    z_load = soprotivlenie_nagruzki
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

    # Проверяем, смогли ли мы вообще приблизиться к цели.
    # Если минимальная разница все еще большая, значит пересечения нет.
    if min_diff > 0.01:  # 0.01 - это допустимая погрешность
        print("Решение не найдено (физически невозможно для данных Zn и W).")
        return

    dz_lambda = best_solution['dz_lambda']
    z_at_dz_norm = best_solution['z_at_dz_norm']

    print(f"Результат: dz = {dz_lambda:.4f}λ")

    required_reactance = -z_at_dz_norm.imag * z0
    tan_val_short = required_reactance / z0
    beta_l_short = np.arctan(tan_val_short)
    if beta_l_short < 0:
        beta_l_short += np.pi
    l_short_lambda = beta_l_short / (2 * np.pi)

    print(f"Результат: l_short = {l_short_lambda:.4f}λ")


# --- Начальная функция, как вы просили ---
def matching_by_train():
    print("\n--------------------------\nНачали согласование шлейфом\n")

    W_val = 100.0
    Zn_val = 70 - 30j

    # Вызываем обе функции для демонстрации
    calculate_parallel_stub_matching(W=W_val, soprotivlenie_nagruzki=Zn_val)
    calculate_series_stub_matching(W=W_val, soprotivlenie_nagruzki=Zn_val)


