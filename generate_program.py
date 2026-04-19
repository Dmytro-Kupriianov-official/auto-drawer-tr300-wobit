import codecs

# SVG данные (перевод пути в координаты)
SVG_DATA = "M 4 8 L 5.056 4.992 L 7.088 2.031 L 11.016 0.03 L 15.099 0.166 L 18.024 2.275 L 19.589 4.656 L 17.616 6.561 L 15.643 3.704 L 12.105 3.091 L 9.315 4.997 L 8.022 8.875 L 7.75 12.549 L 8.362 16.359 L 14.418 16.496 L 15.507 12.481 L 11.833 10.848 L 7.886 12.549 L 8.022 8.943 L 12.241 8.058 L 16.459 10.1 L 19.045 12.549 L 18.024 17.04 L 15.643 20.306 L 8.703 20.238 L 4.484 18.673 L 3.668 12.481 L 4.024 8.059 M 28.932 0.712 L 35.395 0.537 L 42.468 0.45 L 39.587 9.358 L 38.102 20.274 L 32.862 19.925 L 34.696 9.008 L 35.657 4.991 L 28.496 5.166 L 28.932 0.712 M 29.106 30.239 L 32.72 30.293 L 35.768 31.245 L 37.578 32.483 L 40.435 34.102 L 41.292 36.007 L 40.721 38.198 L 38.244 38.198 L 37.578 40.198 L 36.721 42.198 L 35.006 43.436 L 34.816 43.055 L 33.101 42.008 L 33.578 39.531 L 32.72 38.103 L 31.196 36.674 L 29.387 35.436 L 28.244 34.102 L 28.053 31.626 L 28.911 30.293"

# Базовые точки
POCZGORA = (28.2, 222.1, 0.0, -171.8)     # начало над местом с фломастером
POCZ = (28.2, 222.1, 106.8, -171.8)       # место где берем фломастер
SRODEKGORA = (109.5, 216.6, 0.0, -171.8)  # середина листа (в воздухе)
SRODEKDOL = (108.7, 219.8, 15.7, -171.8)  # середина листа (касаемся бумаги)

# ==========================================
# КАЛИБРОВКА ЛИСТА А4 ДЛЯ ИСПРАВЛЕНИЯ ИСКАЖЕНИЙ
# ==========================================
# Подведи маркером к 4 углам своего листа А4 или доски и запиши сюда их (X, Y):
PAPER_BL = (10, 10)   # Нижний левый угол (Пример)
PAPER_BR = (150, 10)  # Нижний правый угол
PAPER_TL = (10, 280)  # Верхний левый угол
PAPER_TR = (150, 280) # Верхний правый угол
# Обязательно замени эти координаты на реальные 4 угла твоего листа! 
# Эта математика выровняет масштаб и уберет сплющивание!

Z_UP = 0.0
Z_DOWN = SRODEKDOL[2]
R_ROTATION = -171.8

def transform_point(local_x, local_y):
    # local_x идет от 0 до 210 (ширина А4 в мм)
    # local_y идет от 0 до 297 (высота А4 в мм)
    dx = local_x / 210.0
    dy = local_y / 297.0
    
    bx = PAPER_BL[0] + dx * (PAPER_BR[0] - PAPER_BL[0])
    by = PAPER_BL[1] + dx * (PAPER_BR[1] - PAPER_BL[1])
    
    tx = PAPER_TL[0] + dx * (PAPER_TR[0] - PAPER_TL[0])
    ty = PAPER_TL[1] + dx * (PAPER_TR[1] - PAPER_TL[1])
    
    x = bx + dy * (tx - bx)
    y = by + dy * (ty - by)
    return round(x, 2), round(y, 2)

class RobotProgram:
    def __init__(self):
        self.points = {}
        self.instructions = []
        self.point_counter = 1
        
    def add_point(self, name, x, y, z, r):
        self.points[name] = (x, y, z, r)
        
    def move_to(self, name, x, y, z, r, comment=""):
        self.add_point(name, round(x, 2), round(y, 2), round(z, 2), round(r, 2))
        if comment:
            self.instructions.append(f"MOVEPTP @{name} // {comment}")
        else:
            self.instructions.append(f"MOVEPTP @{name}")
        self.instructions.append("WAITPOS")
        
    def add_command(self, cmd):
        self.instructions.append(cmd)
        
    def gen_point_name(self):
        name = f"p{self.point_counter}"
        self.point_counter += 1
        return name

    def export_csv(self, filename):
        with codecs.open(filename, "w", encoding="utf-8") as f:
            for name, (x,y,z,r) in self.points.items():
                f.write(f"{name};{x};{y};{z};{r}\n")

    def export_txt(self, filename):
        with codecs.open(filename, "w", encoding="utf-8") as f:
            for ins in self.instructions:
                f.write(ins + "\n")

def parse_svg(svg_string):
    parts = svg_string.split()
    paths = []
    current_path = []
    i = 0
    while i < len(parts):
        if parts[i] == 'M':
            if current_path:
                paths.append(current_path)
            current_path = [(float(parts[i+1]), float(parts[i+2]))]
            i += 3
        elif parts[i] == 'L':
            current_path.append((float(parts[i+1]), float(parts[i+2])))
            i += 3
        else:
            i += 1
    if current_path:
        paths.append(current_path)
    return paths

def generate():
    paths = parse_svg(SVG_DATA)
    if not paths:
        print("Не найдено путей в SVG!")
        return

    all_x = [pt[0] for path in paths for pt in path]
    all_y = [pt[1] for path in paths for pt in path]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    svg_center_x = (min_x + max_x) / 2.0
    svg_center_y = (min_y + max_y) / 2.0
    svg_width = max_x - min_x
    svg_height = max_y - min_y
    
    # Виртуальный лист А4: ширина 210, высота 297
    A4_WIDTH_MM = 210.0
    A4_HEIGHT_MM = 297.0
    
    # Желаемый размер рисунка в мм (чтобы он был квадратным в реальности и помещался)
    DESIRED_SIZE = 150.0  
    
    scale = DESIRED_SIZE / max(svg_width, svg_height)

    prog = RobotProgram()
    prog.add_command("SPEED = 5")
    prog.add_command("HOME")
    
    # --- НАЧАЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ВЗЯТИЯ ФЛОМАСТЕРА ---
    prog.add_command("SET OUT6 = ON // Открываем клешню чтобы взять фломастер")
    prog.add_command("DELAY 1")
    prog.move_to("poczgora", POCZGORA[0], POCZGORA[1], POCZGORA[2], POCZGORA[3], "Над фломастером")
    prog.move_to("pocz", POCZ[0], POCZ[1], POCZ[2], POCZ[3], "Опускаемся к фломастеру")
    prog.add_command("SET OUT6 = OFF // Закрываем клешню (берем фломастер)")
    prog.add_command("DELAY 1")
    prog.move_to("poczgora", POCZGORA[0], POCZGORA[1], POCZGORA[2], POCZGORA[3], "Поднимаем фломастер")
    
    # Выход на центр (используем математический центр листа по нашим точкам)
    center_robot_x, center_robot_y = transform_point(A4_WIDTH_MM/2, A4_HEIGHT_MM/2)
    prog.move_to("srodekgora", center_robot_x, center_robot_y, Z_UP, R_ROTATION, "Выход на центр листа")
    prog.move_to("srodekdol", center_robot_x, center_robot_y, Z_DOWN, R_ROTATION, "Маркер касается листа")

    last_x, last_y = center_robot_x, center_robot_y
    name_up = prog.gen_point_name()
    prog.move_to(name_up, last_x, last_y, Z_UP, R_ROTATION, "Поднимаем перед первой точкой")

    # --- РИСОВАНИЕ КАРТИНКИ ---
    for path in paths:
        if not path: continue
        
        # Переводим в виртуальные миллиметры, затем в физические
        sx_local = A4_WIDTH_MM/2.0 + (path[0][0] - svg_center_x) * scale
        sy_local = A4_HEIGHT_MM/2.0 + (path[0][1] - svg_center_y) * scale
        start_x, start_y = transform_point(sx_local, sy_local)
        
        name_over = prog.gen_point_name()
        prog.move_to(name_over, start_x, start_y, Z_UP, R_ROTATION, "Идем над началом линии (Z=0)")
        
        name_down = prog.gen_point_name()
        prog.move_to(name_down, start_x, start_y, Z_DOWN, R_ROTATION, "Опускаем (Z=15.7)")
        last_x, last_y = start_x, start_y
        
        for i in range(1, len(path)):
            pt_local_x = A4_WIDTH_MM/2.0 + (path[i][0] - svg_center_x) * scale
            pt_local_y = A4_HEIGHT_MM/2.0 + (path[i][1] - svg_center_y) * scale
            nx, ny = transform_point(pt_local_x, pt_local_y)
            
            p_name = prog.gen_point_name()
            prog.move_to(p_name, nx, ny, Z_DOWN, R_ROTATION)
            last_x, last_y = nx, ny
            
        name_end_up = prog.gen_point_name()
        prog.move_to(name_end_up, last_x, last_y, Z_UP, R_ROTATION, "Поднимаем после линии (Z=0)")

    prog.add_command("HOME")
    prog.export_txt("robot_program.txt")
    prog.export_csv("robot_points.csv")
    print("Files successfully generated: robot_program.txt, robot_points.csv")

if __name__ == "__main__":
    generate()
