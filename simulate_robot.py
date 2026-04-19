import matplotlib.pyplot as plt

def simulate():
    program_filename = "robot_program.txt"
    points_filename = "robot_points.csv"
    
    # Сначала загружаем точки из CSV
    points = {}
    try:
        with open(points_filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(";")
                if len(parts) >= 5:
                    name = parts[0]
                    try:
                        points[name] = (float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]))
                    except ValueError:
                        continue
    except FileNotFoundError:
        print(f"File {points_filename} not found! First run generate_program.py.")
        return

    # Загружаем саму программу
    try:
        with open(program_filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {program_filename} not found! First run generate_program.py.")
        return

    paths = []
    current_path = []
    pen_down = False
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith("//"):
            continue
            
        parts = line.split()
        if parts[0] == "MOVEPTP":
            if len(parts) >= 2:
                pt_name = parts[1].replace("@", "")
                if pt_name in points:
                    x, y, z, r = points[pt_name]
                    
                    # В нашей системе координат:
                    # Z=0.0 - это высоко над поверхностью (фломастер поднят)
                    # Z=15.7 - фломастер опущен на бумагу!
                    # Z=106.8 - место хранения фломастера (очень низко)
                    # Будем считать, что рисуем, если Z от 10 до 50
                    is_pen_down = 10.0 <= z <= 50.0 
                    
                    if is_pen_down:
                        if not pen_down:
                            pen_down = True
                            current_path = [(x, y)]  # Начинаем вести новую линию
                        else:
                            current_path.append((x, y)) # Делаем продолжение линии
                    else:
                        if pen_down:
                            pen_down = False
                            if len(current_path) > 1:
                                paths.append(current_path)
                            current_path = []
        elif parts[0] == "HOME":
            if pen_down:
                pen_down = False
                if len(current_path) > 1:
                    paths.append(current_path)
                current_path = []
    
    # Если скрипт закончился, а линия рисовалась
    if pen_down and len(current_path) > 1:
        paths.append(current_path)

    if not paths:
        print("No paths found with pen down (Z around 15.7). Drawing is empty!")
        return

    # Отрисовываем картинку
    plt.figure(figsize=(10, 7))
    for p in paths:
        xs = [pt[0] for pt in p]
        ys = [pt[1] for pt in p]
        plt.plot(xs, ys, marker='.', color='darkblue', linewidth=2)

    plt.title('Симуляция рисунка робота (Вид сверху)')
    plt.xlabel('Координата X робота (мм)')
    plt.ylabel('Координата Y робота (мм)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.axis('equal') 
    plt.show()

if __name__ == "__main__":
    simulate()
