import skrf as rf
import numpy as np
import matplotlib.pyplot as plt


def matching_by_train():
    print("\n--------------------------\nНачали согласование шлейфом\n")

    # --- ИСХОДНЫЕ ДАННЫЕ ---
    # Задача 1 (ВАША): W=100, Zn=30-50j. Решения нет, т.к. zn=0.3-0.5j находится внутри r=1.
    # W_val = 100.0
    # Zn_val = 30 - 50j

    # Задача 2 (РАЗРЕШИМАЯ): W=50, Zn=100+50j. Решение есть, т.к. zn=2+1j находится снаружи r=1.
    W_val = 100.0
    Zn_val = 70 + 50j

    calculate_normalized_matching(W=W_val, soprotivlenie_nagruzki=Zn_val)


def calculate_normalized_matching(W, soprotivlenie_nagruzki):
    """
    Рассчитывает параметры согласования с помощью последовательного шлейфа,
    используя фундаментальные математические формулы.
    """
    print(f"\n--------------------------\nНачали нормированный расчет для W={W} Ом, Zn={soprotivlenie_nagruzki} Ом\n")

    # --- 1. Фундаментальные расчеты ---
    z0 = W
    z_load = soprotivlenie_nagruzki
    zn_load = z_load / z0

    # Проверка на физическую возможность согласования
    if zn_load.real < 1.0:
        # Для последовательного шлейфа мы должны пересечь круг r=1. Если мы внутри, это невозможно.
        # Точнее, если вся окружность КСВ лежит внутри круга r=1, согласование невозможно.
        # Это условие неполное, но для большинства случаев оно верно.
        # Более строгое условие - проверить, пересекается ли окружность |Gamma|=const с кругом r=1.
        # Для простоты пока оставим так.
        pass  # Уберем вывод об ошибке, чтобы код мог работать с другими методами в будущем

    gamma_load = (z_load - z0) / (z_load + z0)

    # --- 2. Поиск точки подключения (dz) через вращение Gamma ---
    z_at_dz_norm = None
    dz_lambda = None
    gamma_at_d_final = None

    for d_in_lambda in np.linspace(0, 0.5, 2001):
        phase_shift = np.exp(-2j * 2 * np.pi * d_in_lambda)
        gamma_at_d = gamma_load * phase_shift
        z_at_d = z0 * (1 + gamma_at_d) / (1 - gamma_at_d)
        current_z_norm = z_at_d / z0

        if np.isclose(current_z_norm.real, 1.0, atol=1e-4):  # atol - допустимая погрешность
            dz_lambda = d_in_lambda
            z_at_dz_norm = current_z_norm
            gamma_at_d_final = gamma_at_d
            break

    if dz_lambda is None:
        print(
            "Не удалось найти точку подключения. Это может означать, что для данных Zn и W согласование одним последовательным шлейфом физически невозможно.")
        return

    print(f"--- Результат 1: Точка подключения шлейфа ---")
    print(f"Расстояние от нагрузки (dz): {dz_lambda:.4f} * lambda")
    print(f"Нормализованное сопротивление в этой точке: {z_at_dz_norm:.2f}")

    # --- 3. Расчет длин шлейфов ---
    required_reactance = -z_at_dz_norm.imag * z0
    print(f"\nТребуемое реактивное сопротивление шлейфа: {required_reactance:+.2f}j Ом")

    # Для короткозамкнутого шлейфа: Z_stub = j*Z0*tan(beta*l)
    tan_val_short = required_reactance / z0
    beta_l_short = np.arctan(tan_val_short)
    if beta_l_short < 0:
        beta_l_short += np.pi
    l_short_lambda = beta_l_short / (2 * np.pi)

    # Для разомкнутого шлейфа: Z_stub = -j*Z0*cot(beta*l)
    tan_val_open = -z0 / required_reactance
    beta_l_open = np.arctan(tan_val_open)
    if beta_l_open < 0:
        beta_l_open += np.pi
    l_open_lambda = beta_l_open / (2 * np.pi)

    print(f"\n--- Результат 2: Длины шлейфов ---")
    print(f"Длина короткозамкнутого шлейфа: {l_short_lambda:.4f} * lambda")
    print(f"Длина разомкнутого шлейфа: {l_open_lambda:.4f} * lambda")

    # --- 4. Проверка и визуализация с помощью skrf ---
    frequency = rf.Frequency(start=1, stop=1, npoints=1, unit='Hz')
    load_network = rf.Network(frequency=frequency, s=np.array([[[gamma_load]]]), z0=z0)
    network_at_dz = rf.Network(frequency=frequency, s=np.array([[[gamma_at_d_final]]]), z0=z0)
    z_final = z_at_dz_norm * z0 + 1j * required_reactance
    gamma_final = (z_final - z0) / (z_final + z0)
    final_network = rf.Network(frequency=frequency, s=np.array([[[gamma_final]]]), z0=z0)

    print("\n--- Проверка ---")
    print(f"Итоговое комплексное сопротивление схемы: {final_network.z[0, 0, 0]:.2f} Ом")

    plt.figure(figsize=(10, 10))
    rf.plotting.smith()
    load_network.plot_s_smith(marker='o', s=100, color='red', label='Z нагрузки')
    network_at_dz.plot_s_smith(marker='x', s=150, color='blue', label='Z в точке dz')
    final_network.plot_s_smith(marker='*', s=200, color='green', label='Z после согласования')
    plt.legend()
    plt.title('Процесс согласования на диаграмме сопротивлений (математический расчет)')
    plt.show()
