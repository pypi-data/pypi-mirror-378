# 网格矩阵操作类
class List2DEdit:
    def __init__(self):
        pass
    
    # 矩阵生成函数
    def create_matrix(self, height=None, width=None, default=None, element_type=None):
        try:
            if not isinstance(height, int) or height <= 0:
                height = 5  # 默认值
                print("Warning: height must be a positive integer, using default value 5")
            if not isinstance(width, int) or width <= 0:
                width = 5  # 默认值
                print("Warning: width must be a positive integer, using default value 5")
                
            if element_type == "str":
                return [[default for i in range(width)] for j in range(height)]
            elif element_type == "int":
                try:
                    return [[int(default) for i in range(width)] for j in range(height)]
                except (ValueError, TypeError):
                    print(f"Warning: Cannot convert '{default}' to int, using 0 instead")
                    return [[0 for i in range(width)] for j in range(height)]
            elif element_type == "float":
                try:
                    return [[float(default) for i in range(width)] for j in range(height)]
                except (ValueError, TypeError):
                    print(f"Warning: Cannot convert '{default}' to float, using 0.0 instead")
                    return [[0.0 for i in range(width)] for j in range(height)]
            elif element_type == "bool":
                return [[bool(default) for i in range(width)] for j in range(height)]
            else:
                print("Warning: element_type must be str, int, float or bool, using str instead")
                return [[str(default) for i in range(width)] for j in range(height)]
        except Exception as e:
            print(f"Error in create_matrix: {e}")
            # 返回默认矩阵以确保程序继续运行
            return [["" for i in range(5)] for j in range(5)]
    
    # 统一修改矩阵内所有元素的值
    def set_all_values(self, lists, value, element_type=None):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            if element_type == "str":
                for i in range(len(lists)):
                    for j in range(len(lists[i])):
                        try:
                            lists[i][j] = value
                        except Exception as e:
                            print(f"Warning: Cannot set value at position ({i}, {j}): {e}")
            return lists
        except Exception as e:
            print(f"Error in set_all_values: {e}")
            return lists
    
    # 统一修改矩阵内所有元素的类型  
    def set_all_types(self, lists, element_type=None):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            if element_type == "str":
                for i in range(len(lists)):
                    for j in range(len(lists[i])):
                        try:
                            lists[i][j] = str(lists[i][j])
                        except Exception as e:
                            print(f"Warning: Cannot convert element at position ({i}, {j}) to str: {e}")
            elif element_type == "int":
                for i in range(len(lists)):
                    for j in range(len(lists[i])):
                        try:
                            lists[i][j] = int(lists[i][j])
                        except Exception as e:
                            print(f"Warning: Cannot convert element at position ({i}, {j}) to int: {e}")
            elif element_type == "float":
                for i in range(len(lists)):
                    for j in range(len(lists[i])):
                        try:
                            lists[i][j] = float(lists[i][j])
                        except Exception as e:
                            print(f"Warning: Cannot convert element at position ({i}, {j}) to float: {e}")
            elif element_type == "bool":
                for i in range(len(lists)):
                    for j in range(len(lists[i])):
                        try:
                            lists[i][j] = bool(lists[i][j])
                        except Exception as e:
                            print(f"Warning: Cannot convert element at position ({i}, {j}) to bool: {e}")
            else:
                print("Warning: element_type must be str, int, float or bool, using str instead")
                for i in range(len(lists)):
                    for j in range(len(lists[i])):
                        try:
                            lists[i][j] = str(lists[i][j])
                        except Exception as e:
                            print(f"Warning: Cannot convert element at position ({i}, {j}) to str: {e}")
            return lists
        except Exception as e:
            print(f"Error in set_all_types: {e}")
            return lists
    
    # 交换两个坐标的矩阵元素位置
    def swap_elements(self, lists, pos1_row, pos1_col, pos2_row, pos2_col):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            # 检查坐标是否在矩阵范围内
            max_row = len(lists) - 1
            max_col = len(lists[0]) - 1
            
            # 确保坐标有效，如果超出范围则调整到最近的边缘
            pos1_row = max(0, min(pos1_row, max_row))
            pos1_col = max(0, min(pos1_col, max_col))
            pos2_row = max(0, min(pos2_row, max_row))
            pos2_col = max(0, min(pos2_col, max_col))
            
            # 交换元素
            lists[pos1_row][pos1_col], lists[pos2_row][pos2_col] = lists[pos2_row][pos2_col], lists[pos1_row][pos1_col]
            return lists
        except Exception as e:
            print(f"Error in swap_elements: {e}")
            return lists
    
    # 以一个位置的元素为中心，以8个方向距离某处进行互换位置（终点超出矩阵则选择边缘最近的）
    def swap_elements_by_direction(self, lists, center_row, center_col, directions, distances):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            # 检查中心坐标是否有效
            max_row = len(lists) - 1
            max_col = len(lists[0]) - 1
            center_row = max(0, min(center_row, max_row))
            center_col = max(0, min(center_col, max_col))
            
            # 定义8个方向的坐标偏移（上、右上、右、右下、下、左下、左、左上）
            directions_map = {
                0: (-1, 0),  # 上
                1: (-1, 1),  # 右上
                2: (0, 1),   # 右
                3: (1, 1),   # 右下
                4: (1, 0),   # 下
                5: (1, -1),  # 左下
                6: (0, -1),  # 左
                7: (-1, -1)  # 左上
            }
            
            # 确保directions是列表
            if not isinstance(directions, list):
                directions = [directions]
            
            # 确保distances是列表且长度与directions相同
            if not isinstance(distances, list):
                distances = [distances] * len(directions)
            elif len(distances) != len(directions):
                # 补充或截断distances以匹配directions的长度
                distances = distances[:len(directions)] + [1] * (len(directions) - len(distances))
            
            # 对每个方向进行元素交换
            for i, direction in enumerate(directions):
                # 确保方向索引有效
                if direction not in directions_map:
                    print(f"Warning: Invalid direction {direction}, using 0 (up) instead")
                    direction = 0
                
                # 获取方向偏移
                dr, dc = directions_map[direction]
                
                # 计算目标位置，并确保在矩阵范围内
                target_row = center_row + dr * distances[i]
                target_col = center_col + dc * distances[i]
                target_row = max(0, min(target_row, max_row))
                target_col = max(0, min(target_col, max_col))
                
                # 交换元素
                lists[center_row][center_col], lists[target_row][target_col] = lists[target_row][target_col], lists[center_row][center_col]
            
            return lists
        except Exception as e:
            print(f"Error in swap_elements_by_direction: {e}")
            return lists
    
    # 单独将某个矩阵中的某个列表的某个元素的类型或值
    def set_element(self, lists, row, col, value=None, element_type=None):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            # 检查坐标是否在矩阵范围内
            max_row = len(lists) - 1
            max_col = len(lists[0]) - 1
            row = max(0, min(row, max_row))
            col = max(0, min(col, max_col))
            
            # 设置值
            if value is not None:
                lists[row][col] = value
            
            # 设置类型
            if element_type is not None:
                try:
                    if element_type == "str":
                        lists[row][col] = str(lists[row][col])
                    elif element_type == "int":
                        lists[row][col] = int(lists[row][col])
                    elif element_type == "float":
                        lists[row][col] = float(lists[row][col])
                    elif element_type == "bool":
                        lists[row][col] = bool(lists[row][col])
                    else:
                        print("Warning: element_type must be str, int, float or bool, skipping type conversion")
                except Exception as e:
                    print(f"Warning: Cannot convert element at position ({row}, {col}) to {element_type}: {e}")
            
            return lists
        except Exception as e:
            print(f"Error in set_element: {e}")
            return lists
    
    # 删除矩阵中的指定行
    def delete_row(self, lists, row_index):
        try:
            if not isinstance(lists, list) or not lists:
                print("Warning: lists must be a non-empty list, cannot perform operation")
                return lists
                
            # 检查要删除的行是否在范围内
            if row_index < 0 or row_index >= len(lists):
                print(f"Warning: Row index {row_index} out of range, cannot remove")
            else:
                # 删除指定行
                del lists[row_index]
            
            return lists
        except Exception as e:
            print(f"Error in delete_row: {e}")
            return lists
    
    # 交换矩阵中的指定两行
    def swap_rows(self, lists, row1, row2):
        try:
            if not isinstance(lists, list) or not lists:
                print("Warning: lists must be a non-empty list, cannot perform operation")
                return lists
                
            # 检查行索引是否有效
            if 0 <= row1 < len(lists) and 0 <= row2 < len(lists):
                # 交换两行
                lists[row1], lists[row2] = lists[row2], lists[row1]
            else:
                print(f"Warning: Row index {row1} or {row2} out of range, cannot swap")
            
            return lists
        except Exception as e:
            print(f"Error in swap_rows: {e}")
            return lists
    
    # 获取指定坐标的元素值
    def get_element(self, lists, row, col):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return None
                
            # 检查坐标是否在矩阵范围内
            if row < 0 or row >= len(lists) or col < 0 or col >= len(lists[0]):
                print(f"Warning: Coordinates ({row}, {col}) out of range")
                return None
                
            return lists[row][col]
        except Exception as e:
            print(f"Error in get_element: {e}")
            return None
    
    # 获取指定行
    def get_row(self, lists, row_index):
        try:
            if not isinstance(lists, list) or not lists:
                print("Warning: lists must be a non-empty list, cannot perform operation")
                return None
                
            # 检查行索引是否在范围内
            if row_index < 0 or row_index >= len(lists):
                print(f"Warning: Row index {row_index} out of range")
                return None
                
            return lists[row_index].copy()  # 返回行的副本，避免直接修改原矩阵
        except Exception as e:
            print(f"Error in get_row: {e}")
            return None
    
    # 获取符合条件的行
    def get_rows_by_condition(self, lists, condition=None, **kwargs):
        try:
            if not isinstance(lists, list) or not lists:
                print("Warning: lists must be a non-empty list, cannot perform operation")
                return []
                
            result_rows = []
            result_indices = []
            
            # 如果提供了自定义条件函数
            if callable(condition):
                for i, row in enumerate(lists):
                    if condition(row, **kwargs):
                        result_rows.append(row.copy())
                        result_indices.append(i)
                return result_rows, result_indices
            
            # 默认条件处理
            # 条件1: 包含特定值的行
            if 'contains_value' in kwargs:
                value = kwargs['contains_value']
                for i, row in enumerate(lists):
                    if value in row:
                        result_rows.append(row.copy())
                        result_indices.append(i)
                return result_rows, result_indices
            
            # 条件2: 所有元素都大于特定值的行
            if 'all_greater_than' in kwargs:
                threshold = kwargs['all_greater_than']
                for i, row in enumerate(lists):
                    if all(element > threshold for element in row if isinstance(element, (int, float))):
                        result_rows.append(row.copy())
                        result_indices.append(i)
                return result_rows, result_indices
            
            # 条件3: 所有元素都小于特定值的行
            if 'all_less_than' in kwargs:
                threshold = kwargs['all_less_than']
                for i, row in enumerate(lists):
                    if all(element < threshold for element in row if isinstance(element, (int, float))):
                        result_rows.append(row.copy())
                        result_indices.append(i)
                return result_rows, result_indices
            
            # 条件4: 所有元素都等于特定值的行
            if 'all_equal_to' in kwargs:
                value = kwargs['all_equal_to']
                for i, row in enumerate(lists):
                    if all(element == value for element in row):
                        result_rows.append(row.copy())
                        result_indices.append(i)
                return result_rows, result_indices
            
            # 条件5: 行的长度等于特定值的行
            if 'length_equals' in kwargs:
                length = kwargs['length_equals']
                for i, row in enumerate(lists):
                    if len(row) == length:
                        result_rows.append(row.copy())
                        result_indices.append(i)
                return result_rows, result_indices
            
            # 默认返回空结果
            return result_rows, result_indices
        except Exception as e:
            print(f"Error in get_rows_by_condition: {e}")
            return [], []
    
    # 获取矩阵的宽度
    def get_width(self, lists):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return 0
                
            return len(lists[0])
        except Exception as e:
            print(f"Error in get_width: {e}")
            return 0
    
    # 获取矩阵的高度
    def get_height(self, lists):
        try:
            if not isinstance(lists, list):
                print("Warning: lists must be a list, cannot perform operation")
                return 0
                
            return len(lists)
        except Exception as e:
            print(f"Error in get_height: {e}")
            return 0
    
    # 清空矩阵
    def clear_matrix(self, lists):
        try:
            if not isinstance(lists, list):
                print("Warning: lists must be a list, cannot perform operation")
                return lists
                
            # 清空所有行
            lists.clear()
            return lists
        except Exception as e:
            print(f"Error in clear_matrix: {e}")
            return lists
    
    # 复制矩阵
    def copy_matrix(self, lists):
        try:
            if not isinstance(lists, list):
                print("Warning: lists must be a list, cannot perform operation")
                return []
                
            # 深度复制矩阵
            return [row.copy() for row in lists]
        except Exception as e:
            print(f"Error in copy_matrix: {e}")
            return []
    
    # 旋转矩阵函数 -1表示逆时针，1表示顺时针，x表示旋转次数
    def rotate_matrix(self, lists, direction=1, times=1):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            # 规范化方向和次数
            if direction not in [-1, 1]:
                direction = 1
                print("Warning: direction must be -1 or 1, using 1 (clockwise) instead")
            
            if not isinstance(times, int) or times < 1:
                times = 1
                print("Warning: times must be a positive integer, using 1 instead")
            
            # 执行旋转
            result = lists
            for _ in range(times):
                if direction == 1:  # 顺时针旋转90度
                    result = list(zip(*result[::-1]))
                else:  # 逆时针旋转90度
                    result = list(zip(*result))[::-1]
                
                # 转换为列表的列表格式
                result = [list(row) for row in result]
            
            return result
        except Exception as e:
            print(f"Error in rotate_matrix: {e}")
            return lists
    
    # 插入行函数
    def insert_row(self, lists, row_index, row_content=None):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            # 获取矩阵宽度
            width = len(lists[0])
            
            # 规范化行索引
            if not isinstance(row_index, int):
                row_index = len(lists)
                print("Warning: row_index must be an integer, appending to end")
            elif row_index < 0:
                row_index = 0
            elif row_index > len(lists):
                row_index = len(lists)
            
            # 准备要插入的行内容
            if row_content is None:
                # 使用矩阵中的第一个元素类型创建默认值的行
                default_value = lists[0][0] if lists and lists[0] else None
                row_content = [default_value] * width
            elif not isinstance(row_content, list):
                print("Warning: row_content must be a list, using default values")
                default_value = lists[0][0] if lists and lists[0] else None
                row_content = [default_value] * width
            else:
                # 确保行内容长度与矩阵宽度一致
                if len(row_content) < width:
                    # 补充默认值
                    default_value = lists[0][0] if lists and lists[0] else None
                    row_content += [default_value] * (width - len(row_content))
                elif len(row_content) > width:
                    # 截断多余的元素
                    row_content = row_content[:width]
            
            # 插入行
            lists.insert(row_index, row_content)
            return lists
        except Exception as e:
            print(f"Error in insert_row: {e}")
            return lists
    
    # 插入列函数
    def insert_column(self, lists, col_index, col_content=None):
        try:
            if not isinstance(lists, list) or not lists or not isinstance(lists[0], list):
                print("Warning: lists must be a non-empty 2D list, cannot perform operation")
                return lists
                
            # 获取矩阵高度
            height = len(lists)
            # 获取矩阵宽度
            width = len(lists[0])
            
            # 规范化列索引
            if not isinstance(col_index, int):
                col_index = width
                print("Warning: col_index must be an integer, appending to end")
            elif col_index < 0:
                col_index = 0
            elif col_index > width:
                col_index = width
            
            # 准备要插入的列内容
            if col_content is None:
                # 使用矩阵中的第一个元素类型创建默认值的列
                default_value = lists[0][0] if lists and lists[0] else None
                col_content = [default_value] * height
            elif not isinstance(col_content, list):
                print("Warning: col_content must be a list, using default values")
                default_value = lists[0][0] if lists and lists[0] else None
                col_content = [default_value] * height
            else:
                # 确保列内容长度与矩阵高度一致
                if len(col_content) < height:
                    # 补充默认值
                    default_value = lists[0][0] if lists and lists[0] else None
                    col_content += [default_value] * (height - len(col_content))
                elif len(col_content) > height:
                    # 截断多余的元素
                    col_content = col_content[:height]
            
            # 插入列
            for i in range(height):
                lists[i].insert(col_index, col_content[i])
            
            return lists
        except Exception as e:
            print(f"Error in insert_column: {e}")
            return lists

# 游戏专用的2D列表操作类
class List2DGame(List2DEdit):
    def __init__(self):
        super().__init__()
        
    # 检查两个矩形是否碰撞
    def check_rect_collision(self, rect1, rect2):
        try:
            # rect格式: [x1, y1, width, height]
            x1, y1, w1, h1 = rect1
            x2, y2, w2, h2 = rect2
            
            # 检查是否没有碰撞
            if x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1:
                return False
            return True
        except Exception as e:
            print(f"Error in check_rect_collision: {e}")
            return False
    
    # 检查点是否在矩形内
    def check_point_in_rect(self, point, rect):
        try:
            # point格式: (x, y), rect格式: [x, y, width, height]
            px, py = point
            rx, ry, rw, rh = rect
            
            if px >= rx and px <= rx + rw and py >= ry and py <= ry + rh:
                return True
            return False
        except Exception as e:
            print(f"Error in check_point_in_rect: {e}")
            return False
    
    # 简单的广度优先搜索路径查找
    def find_path(self, grid, start, end, blocked_value=None):
        try:
            if not grid or not grid[0]:
                print("Warning: Grid is empty or not properly formatted")
                return None
                
            # 获取网格尺寸
            rows = len(grid)
            cols = len(grid[0])
            
            # 检查起点和终点是否有效
            if (start[0] < 0 or start[0] >= rows or start[1] < 0 or start[1] >= cols or
                end[0] < 0 or end[0] >= rows or end[1] < 0 or end[1] >= cols):
                print("Warning: Start or end position out of bounds")
                return None
                
            # 检查起点和终点是否可通行
            if grid[start[0]][start[1]] == blocked_value or grid[end[0]][end[1]] == blocked_value:
                print("Warning: Start or end position is blocked")
                return None
                
            # 定义四个方向的移动（上、右、下、左）
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            
            # 记录访问过的位置和路径
            visited = set()
            parent = {}
            queue = [start]
            visited.add(start)
            
            # 广度优先搜索
            while queue:
                current = queue.pop(0)
                
                # 如果到达终点，回溯构建路径
                if current == end:
                    path = []
                    while current in parent:
                        path.append(current)
                        current = parent[current]
                    path.append(start)
                    path.reverse()
                    return path
                    
                # 探索四个方向
                for dx, dy in directions:
                    next_pos = (current[0] + dx, current[1] + dy)
                    # 检查位置是否有效且未访问且不阻塞
                    if (0 <= next_pos[0] < rows and 0 <= next_pos[1] < cols and
                        next_pos not in visited and grid[next_pos[0]][next_pos[1]] != blocked_value):
                        visited.add(next_pos)
                        parent[next_pos] = current
                        queue.append(next_pos)
                        
            # 无法找到路径
            print("Warning: No path found from start to end")
            return None
        except Exception as e:
            print(f"Error in find_path: {e}")
            return None
    
    # 检查两点之间是否有视线（直线上没有障碍物）
    def has_line_of_sight(self, grid, start, end, blocked_value=None):
        try:
            if not grid or not grid[0]:
                print("Warning: Grid is empty or not properly formatted")
                return False
                
            # 使用Bresenham算法检查视线
            x0, y0 = start
            x1, y1 = end
            
            dx = abs(x1 - x0)
            dy = abs(y1 - y0)
            
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            
            err = dx - dy
            
            while (x0, y0) != (x1, y1):
                # 检查当前点是否阻塞
                if (x0 < 0 or x0 >= len(grid) or y0 < 0 or y0 >= len(grid[0]) or
                    grid[x0][y0] == blocked_value):
                    return False
                    
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x0 += sx
                if e2 < dx:
                    err += dx
                    y0 += sy
                    
            # 检查终点是否阻塞
            if grid[x1][y1] == blocked_value:
                return False
                
            return True
        except Exception as e:
            print(f"Error in has_line_of_sight: {e}")
            return False
    
    # 世界坐标转网格坐标
    def world_to_grid(self, world_pos, cell_size):
        try:
            # 假设cell_size是网格单元的大小（宽度和高度）
            grid_x = int(world_pos[0] / cell_size)
            grid_y = int(world_pos[1] / cell_size)
            return (grid_x, grid_y)
        except Exception as e:
            print(f"Error in world_to_grid: {e}")
            return (0, 0)
    
    # 网格坐标转世界坐标
    def grid_to_world(self, grid_pos, cell_size):
        try:
            # 假设cell_size是网格单元的大小（宽度和高度）
            world_x = grid_pos[0] * cell_size + cell_size / 2
            world_y = grid_pos[1] * cell_size + cell_size / 2
            return (world_x, world_y)
        except Exception as e:
            print(f"Error in grid_to_world: {e}")
            return (0, 0)
    
    # 随机填充网格
    def random_fill(self, grid, fill_probability, fill_value, empty_value=None):
        try:
            if not grid or not grid[0]:
                print("Warning: Grid is empty or not properly formatted")
                return grid
                
            import random
            
            # 遍历网格并随机填充
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    if random.random() < fill_probability:
                        grid[i][j] = fill_value
                    elif empty_value is not None:
                        grid[i][j] = empty_value
                        
            return grid
        except Exception as e:
            print(f"Error in random_fill: {e}")
            return grid
    
    # 填充区域（类似于洪水填充算法）
    def fill_area(self, grid, start, fill_value, target_value=None):
        try:
            if not grid or not grid[0]:
                print("Warning: Grid is empty or not properly formatted")
                return grid
                
            # 获取网格尺寸
            rows = len(grid)
            cols = len(grid[0])
            
            # 检查起始位置是否有效
            if start[0] < 0 or start[0] >= rows or start[1] < 0 or start[1] >= cols:
                print("Warning: Start position out of bounds")
                return grid
                
            # 如果未指定目标值，使用起始位置的值
            if target_value is None:
                target_value = grid[start[0]][start[1]]
                
            # 如果起始位置已经是填充值，无需填充
            if grid[start[0]][start[1]] == fill_value:
                return grid
                
            # 定义四个方向的移动
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            
            # 使用队列进行广度优先填充
            queue = [start]
            grid[start[0]][start[1]] = fill_value
            
            while queue:
                x, y = queue.pop(0)
                
                # 探索四个方向
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    # 检查位置是否有效且是目标值
                    if (0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == target_value):
                        grid[nx][ny] = fill_value
                        queue.append((nx, ny))
                        
            return grid
        except Exception as e:
            print(f"Error in fill_area: {e}")
            return grid
    
    # 获取指定位置的邻域（周围的单元格）
    def get_neighbors(self, grid, pos, radius=1, include_diagonals=True):
        try:
            if not grid or not grid[0]:
                print("Warning: Grid is empty or not properly formatted")
                return []
                
            neighbors = []
            x, y = pos
            rows = len(grid)
            cols = len(grid[0])
            
            # 定义方向
            directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # 上、右、下、左
            if include_diagonals:
                directions.extend([(-1, 1), (1, 1), (1, -1), (-1, -1)])  # 右上、右下、左下、左上
                
            # 检查每个方向的邻域
            for dx, dy in directions:
                for r in range(1, radius + 1):
                    nx, ny = x + dx * r, y + dy * r
                    if 0 <= nx < rows and 0 <= ny < cols:
                        neighbors.append((nx, ny))
                        
            return neighbors
        except Exception as e:
            print(f"Error in get_neighbors: {e}")
            return []
    
    # 判断多个矩阵在特定位置的值是否相同
    def check_matrices_same_value(self, matrices, pos):
        try:
            if not matrices or len(matrices) < 2:
                print("Warning: Need at least 2 matrices to compare")
                return False
                
            if not matrices[0] or not matrices[0][0]:
                print("Warning: Matrices are empty or not properly formatted")
                return False
                
            x, y = pos
            
            # 检查位置是否在所有矩阵的范围内
            for matrix in matrices:
                if x < 0 or x >= len(matrix) or y < 0 or y >= len(matrix[0]):
                    print(f"Warning: Position {pos} out of bounds for one of the matrices")
                    return False
                    
            # 获取第一个矩阵在该位置的值作为参考
            ref_value = matrices[0][x][y]
            
            # 比较所有矩阵在该位置的值是否相同
            for matrix in matrices[1:]:
                if matrix[x][y] != ref_value:
                    return False
                    
            return True
        except Exception as e:
            print(f"Error in check_matrices_same_value: {e}")
            return False
            
    # 判断多个矩阵在特定位置的值的类型是否相同
    def check_matrices_same_type(self, matrices, pos):
        try:
            if not matrices or len(matrices) < 2:
                print("Warning: Need at least 2 matrices to compare")
                return False
                
            if not matrices[0] or not matrices[0][0]:
                print("Warning: Matrices are empty or not properly formatted")
                return False
                
            x, y = pos
            
            # 检查位置是否在所有矩阵的范围内
            for matrix in matrices:
                if x < 0 or x >= len(matrix) or y < 0 or y >= len(matrix[0]):
                    print(f"Warning: Position {pos} out of bounds for one of the matrices")
                    return False
                    
            # 获取第一个矩阵在该位置的值的类型作为参考
            ref_type = type(matrices[0][x][y])
            
            # 比较所有矩阵在该位置的值的类型是否相同
            for matrix in matrices[1:]:
                if type(matrix[x][y]) != ref_type:
                    return False
                    
            return True
        except Exception as e:
            print(f"Error in check_matrices_same_type: {e}")
            return False
            
    # 判断两个矩阵是否有特定值的重叠
    def check_matrices_value_overlap(self, matrix1, matrix2, target_value):
        try:
            if not matrix1 or not matrix1[0] or not matrix2 or not matrix2[0]:
                print("Warning: Matrices are empty or not properly formatted")
                return False, []
                
            # 获取矩阵尺寸
            rows = min(len(matrix1), len(matrix2))
            cols = min(len(matrix1[0]), len(matrix2[0]))
            
            overlap_positions = []
            
            # 遍历两个矩阵的公共区域
            for i in range(rows):
                for j in range(cols):
                    # 检查两个矩阵在该位置是否都有目标值
                    if matrix1[i][j] == target_value and matrix2[i][j] == target_value:
                        overlap_positions.append((i, j))
                        
            # 返回是否有重叠以及重叠的位置
            return len(overlap_positions) > 0, overlap_positions
        except Exception as e:
            print(f"Error in check_matrices_value_overlap: {e}")
            return False, []
    
    # 检测多个矩阵的碰撞值
    def check_matrices_collision_values(self, matrices):
        try:
            # 检查矩阵数量是否满足要求（至少4个且为偶数）
            if not matrices or len(matrices) < 4 or len(matrices) % 2 != 0:
                print("Warning: Need at least 4 matrices and the number must be even")
                return []
            
            # 分离数据矩阵和布尔矩阵（碰撞矩阵）
            data_matrices = matrices[:len(matrices)//2]
            collision_matrices = matrices[len(matrices)//2:]
            
            # 检查所有矩阵是否为空或格式不正确
            for matrix in matrices:
                if not matrix or not matrix[0]:
                    print("Warning: Matrices are empty or not properly formatted")
                    return []
            
            # 获取矩阵尺寸（取所有矩阵的最小尺寸）
            min_rows = min(len(matrix) for matrix in matrices)
            min_cols = min(len(matrix[0]) for matrix in matrices)
            
            # 存储碰撞位置对应的数据值
            collision_values = []
            
            # 遍历矩阵的公共区域
            for i in range(min_rows):
                for j in range(min_cols):
                    # 检查所有碰撞矩阵在该位置是否都为True
                    all_true = True
                    for collision_matrix in collision_matrices:
                        if not collision_matrix[i][j]:
                            all_true = False
                            break
                    
                    # 如果所有碰撞矩阵在该位置都为True，收集对应的数据值
                    if all_true:
                        data_values = []
                        for data_matrix in data_matrices:
                            data_values.append(data_matrix[i][j])
                        collision_values.append(data_values)
            
            return collision_values
        except Exception as e:
            print(f"Error in check_matrices_collision_values: {e}")
            return []

# 实例化类
def get_list_2d_edit():
    return List2DEdit()
    
# 实例化游戏类
def get_list_2d_game():
    return List2DGame()

#测试用例
if __name__ == "__main__":
    # 获取List2DEdit实例
    list_editor = get_list_2d_edit()
    
    print("=== 测试用例 1: 基本功能测试 ===")
    lists = list_editor.create_matrix(5, 5, "True", "int")
    print(lists)

    list_editor.set_all_values(lists, "False", "bool")
    print(lists)

    list_editor.set_all_types(lists, "str")
    print(lists)
    
    print("\n=== 测试用例 2: 边缘值测试 ===")
    # 测试负数高度
    lists2 = list_editor.create_matrix(-1, 5, "test", "str")
    print(f"负数高度后的矩阵大小: {len(lists2)}x{len(lists2[0])}")
    
    # 测试空列表
    empty_list = []
    result = list_editor.set_all_types(empty_list, "int")
    print(f"空列表处理结果: {result}")
    
    # 测试非2D列表
    not_2d_list = [1, 2, 3]
    result = list_editor.set_all_types(not_2d_list, "str")
    print(f"非2D列表处理结果: {result}")
    
    print("\n=== 测试用例 3: 类型转换错误测试 ===")
    # 创建一个包含不可转换值的矩阵
    mixed_list = [["abc", "123"], ["45.6", "True"]]
    result = list_editor.set_all_types(mixed_list, "int")
    print(f"混合类型转换结果: {result}")
    
    # 测试无效的element_type
    lists3 = list_editor.create_matrix(3, 3, "test", "invalid_type")
    print(f"无效element_type处理结果: {lists3}")
    
    print("\n=== 测试用例 4: 新增函数测试 ===")
    
    # 创建一个测试矩阵
    test_matrix = list_editor.create_matrix(5, 5, 0, "int")
    # 填充一些测试值
    for i in range(5):
        for j in range(5):
            test_matrix[i][j] = i * 10 + j
    print("原始测试矩阵:")
    for row in test_matrix:
        print(row)
    
    print("\n1. 测试swap_elements (交换(1,1)和(3,3)的元素):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.swap_elements(test_matrix_copy, 1, 1, 3, 3)
    for row in test_matrix_copy:
        print(row)
    
    print("\n2. 测试swap_elements (交换越界坐标):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.swap_elements(test_matrix_copy, 1, 1, 10, 10)  # 超出范围的坐标
    for row in test_matrix_copy:
        print(row)
    
    print("\n3. 测试swap_elements_by_direction (以(2,2)为中心，向上、右、下、左各交换1个距离):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.swap_elements_by_direction(test_matrix_copy, 2, 2, [0, 2, 4, 6], 1)
    for row in test_matrix_copy:
        print(row)
    
    print("\n4. 测试swap_elements_by_direction (以(2,2)为中心，向多个方向交换不同距离):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.swap_elements_by_direction(test_matrix_copy, 2, 2, [1, 3, 5, 7], [1, 2, 1, 2])
    for row in test_matrix_copy:
        print(row)
    
    print("\n5. 测试set_element (设置(2,2)位置的值为99):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.set_element(test_matrix_copy, 2, 2, 99)
    for row in test_matrix_copy:
        print(row)
    
    print("\n6. 测试set_element (将(2,2)位置的元素转换为字符串类型):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.set_element(test_matrix_copy, 2, 2, element_type="str")
    print(f"元素类型: {type(test_matrix_copy[2][2])}")
    
    print("\n7. 测试set_element (同时设置值和类型):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.set_element(test_matrix_copy, 2, 2, "新值", "str")
    print(f"元素值: {test_matrix_copy[2][2]}, 类型: {type(test_matrix_copy[2][2])}")
    
    print("\n8. 测试delete_row (删除第2行):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.delete_row(test_matrix_copy, 2)
    print(f"删除后的矩阵行数: {len(test_matrix_copy)}")
    for row in test_matrix_copy:
        print(row)
    
    print("\n9. 测试swap_rows (交换第0行和第2行):")
    test_matrix_copy = [row[:] for row in test_matrix]
    list_editor.swap_rows(test_matrix_copy, 0, 2)
    print(f"交换后的矩阵:")
    for row in test_matrix_copy:
        print(row)
    
    print("\n10. 测试get_element (获取(2,2)位置的元素):")
    value = list_editor.get_element(test_matrix, 2, 2)
    print(f"(2,2)位置的元素值: {value}")
    
    print("\n11. 测试get_row (获取第1行):")
    row = list_editor.get_row(test_matrix, 1)
    print(f"第1行的元素: {row}")
    
    print("\n12. 测试get_rows_by_condition (获取所有包含大于20的元素的行):")
    condition = lambda row: any(elem > 20 for elem in row)
    rows = list_editor.get_rows_by_condition(test_matrix, condition)
    print(f"符合条件的行数: {len(rows)}")
    for r in rows:
        print(r)
    
    print("\n13. 测试矩阵属性函数:")
    width = list_editor.get_width(test_matrix)
    height = list_editor.get_height(test_matrix)
    print(f"矩阵宽度: {width}, 高度: {height}")
    
    print("\n14. 测试copy_matrix (复制矩阵):")
    copied_matrix = list_editor.copy_matrix(test_matrix)
    print(f"原始矩阵和复制矩阵是否相同对象: {test_matrix is copied_matrix}")
    print(f"原始矩阵和复制矩阵内容是否相同: {test_matrix == copied_matrix}")
    
    print("\n15. 测试clear_matrix (清空矩阵):")
    matrix_to_clear = [row[:] for row in test_matrix]
    list_editor.clear_matrix(matrix_to_clear)
    print(f"清空后的矩阵行数: {len(matrix_to_clear)}")
    
    print("\n=== 测试用例 8: 矩阵旋转功能测试 ====")
    
    # 创建一个测试矩阵
    rotate_test_matrix = list_editor.create_matrix(3, 3, 0, "int")
    # 填充测试值
    for i in range(3):
        for j in range(3):
            rotate_test_matrix[i][j] = i * 10 + j
    print("原始矩阵:")
    for row in rotate_test_matrix:
        print(row)
    
    # 测试顺时针旋转90度
    rotated_matrix = list_editor.rotate_matrix([row[:] for row in rotate_test_matrix], direction=1, times=1)
    print("\n顺时针旋转90度后:")
    for row in rotated_matrix:
        print(row)
    
    # 测试逆时针旋转90度
    rotated_matrix = list_editor.rotate_matrix([row[:] for row in rotate_test_matrix], direction=-1, times=1)
    print("\n逆时针旋转90度后:")
    for row in rotated_matrix:
        print(row)
    
    # 测试顺时针旋转180度 (旋转2次90度)
    rotated_matrix = list_editor.rotate_matrix([row[:] for row in rotate_test_matrix], direction=1, times=2)
    print("\n顺时针旋转180度后:")
    for row in rotated_matrix:
        print(row)
    
    # 测试逆时针旋转270度 (旋转3次90度)
    rotated_matrix = list_editor.rotate_matrix([row[:] for row in rotate_test_matrix], direction=-1, times=3)
    print("\n逆时针旋转270度后:")
    for row in rotated_matrix:
        print(row)
    
    # 测试无效的direction参数
    print("\n测试无效的direction参数:")
    rotated_matrix = list_editor.rotate_matrix([row[:] for row in rotate_test_matrix], direction=2, times=1)
    for row in rotated_matrix:
        print(row)
    
    print("\n=== 测试用例 9: 插入行功能测试 ====")
    
    # 创建一个测试矩阵
    insert_test_matrix = list_editor.create_matrix(3, 3, 0, "int")
    # 填充测试值
    for i in range(3):
        for j in range(3):
            insert_test_matrix[i][j] = i * 10 + j
    print("原始矩阵:")
    for row in insert_test_matrix:
        print(row)
    
    # 在中间插入一行
    inserted_matrix = list_editor.insert_row([row[:] for row in insert_test_matrix], 1, [100, 101, 102])
    print("\n在索引1处插入一行[100, 101, 102]后:")
    for row in inserted_matrix:
        print(row)
    
    # 在开头插入一行
    inserted_matrix = list_editor.insert_row([row[:] for row in insert_test_matrix], 0)
    print("\n在开头插入一行默认值后:")
    for row in inserted_matrix:
        print(row)
    
    # 在末尾插入一行
    inserted_matrix = list_editor.insert_row([row[:] for row in insert_test_matrix], 10, [999, 999, 999])
    print("\n在末尾插入一行[999, 999, 999]后:")
    for row in inserted_matrix:
        print(row)
    
    # 测试自动调整插入行的长度
    inserted_matrix = list_editor.insert_row([row[:] for row in insert_test_matrix], 1, [200, 201])  # 长度不足
    print("\n插入长度不足的行(自动补充默认值)后:")
    for row in inserted_matrix:
        print(row)
    
    inserted_matrix = list_editor.insert_row([row[:] for row in insert_test_matrix], 1, [300, 301, 302, 303])  # 长度过长
    print("\n插入长度过长的行(自动截断)后:")
    for row in inserted_matrix:
        print(row)
    
    print("\n=== 测试用例 10: 插入列功能测试 ====")
    
    # 使用之前的测试矩阵
    print("原始矩阵:")
    for row in insert_test_matrix:
        print(row)
    
    # 在中间插入一列
    inserted_matrix = list_editor.insert_column([row[:] for row in insert_test_matrix], 1, [400, 401, 402])
    print("\n在索引1处插入一列[400, 401, 402]后:")
    for row in inserted_matrix:
        print(row)
    
    # 在开头插入一列
    inserted_matrix = list_editor.insert_column([row[:] for row in insert_test_matrix], 0)
    print("\n在开头插入一列默认值后:")
    for row in inserted_matrix:
        print(row)
    
    # 在末尾插入一列
    inserted_matrix = list_editor.insert_column([row[:] for row in insert_test_matrix], 10, [888, 888, 888])
    print("\n在末尾插入一列[888, 888, 888]后:")
    for row in inserted_matrix:
        print(row)
    
    # 测试自动调整插入列的长度
    inserted_matrix = list_editor.insert_column([row[:] for row in insert_test_matrix], 1, [500, 501])  # 长度不足
    print("\n插入长度不足的列(自动补充默认值)后:")
    for row in inserted_matrix:
        print(row)
    
    inserted_matrix = list_editor.insert_column([row[:] for row in insert_test_matrix], 1, [600, 601, 602, 603])  # 长度过长
    print("\n插入长度过长的列(自动截断)后:")
    for row in inserted_matrix:
        print(row)
    
    print("\n=== 所有测试完成 ====")
    
    # 测试List2DGame类的额外功能
    print("\n=== 开始测试List2DGame类 ====")
    game = get_list_2d_game()
    
    # 测试16: 测试矩形碰撞检测
    print("\n测试16: 矩形碰撞检测")
    rect1 = [0, 0, 2, 2]
    rect2 = [1, 1, 2, 2]
    rect3 = [3, 3, 2, 2]
    print(f"矩形1 {rect1} 和矩形2 {rect2} 是否碰撞: {game.check_rect_collision(rect1, rect2)}")  # 应该返回True
    print(f"矩形1 {rect1} 和矩形3 {rect3} 是否碰撞: {game.check_rect_collision(rect1, rect3)}")  # 应该返回False
    
    # 测试17: 测试点是否在矩形内
    print("\n测试17: 点是否在矩形内")
    point1 = (1, 1)
    point2 = (3, 3)
    rect = [0, 0, 2, 2]
    print(f"点 {point1} 是否在矩形 {rect} 内: {game.check_point_in_rect(point1, rect)}")  # 应该返回True
    print(f"点 {point2} 是否在矩形 {rect} 内: {game.check_point_in_rect(point2, rect)}")  # 应该返回False
    
    # 测试18: 测试路径查找
    print("\n测试18: 路径查找")
    # 创建一个简单的网格，0表示可通行，1表示障碍物
    grid = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    start = (0, 0)
    end = (4, 4)
    path = game.find_path(grid, start, end, 1)
    print(f"从{start}到{end}的路径: {path}")
    
    # 测试19: 测试视线检查
    print("\n测试19: 视线检查")
    # 创建一个简单的网格，0表示可通行，1表示障碍物
    grid = [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    start = (0, 0)
    end1 = (2, 4)
    end2 = (0, 4)
    print(f"从{start}到{end1}是否有视线: {game.has_line_of_sight(grid, start, end1, 1)}")  # 应该返回False
    print(f"从{start}到{end2}是否有视线: {game.has_line_of_sight(grid, start, end2, 1)}")  # 应该返回True
    
    # 测试20: 测试坐标转换
    print("\n测试20: 坐标转换")
    cell_size = 32
    world_pos = (48, 48)
    grid_pos = game.world_to_grid(world_pos, cell_size)
    converted_world_pos = game.grid_to_world(grid_pos, cell_size)
    print(f"世界坐标 {world_pos} 转换为网格坐标: {grid_pos}")
    print(f"网格坐标 {grid_pos} 转换为世界坐标: {converted_world_pos}")
    
    # 测试21: 测试随机填充
    print("\n测试21: 随机填充")
    grid = [[0 for _ in range(5)] for _ in range(3)]
    print("填充前的网格:")
    for row in grid:
        print(row)
    game.random_fill(grid, 0.5, 1, 0)
    print("随机填充(50%概率为1, 50%概率为0)后的网格:")
    for row in grid:
        print(row)
    
    # 测试22: 测试区域填充
    print("\n测试22: 区域填充")
    grid = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    print("填充前的网格:")
    for row in grid:
        print(row)
    game.fill_area(grid, (2, 2), 2)
    print("从(2,2)位置开始填充后的网格:")
    for row in grid:
        print(row)
    
    # 测试23: 测试获取邻域
    print("\n测试23: 获取邻域")
    grid = [[0 for _ in range(5)] for _ in range(5)]
    pos = (2, 2)
    neighbors_radius1 = game.get_neighbors(grid, pos, radius=1)
    neighbors_radius2 = game.get_neighbors(grid, pos, radius=2)
    neighbors_no_diag = game.get_neighbors(grid, pos, include_diagonals=False)
    print(f"位置 {pos} 半径为1的邻域: {neighbors_radius1}")
    print(f"位置 {pos} 半径为2的邻域: {neighbors_radius2}")
    print(f"位置 {pos} 不包含对角线的邻域: {neighbors_no_diag}")
    
    print("\n=== List2DGame类测试完成 ====")
    
    # 测试新增的矩阵比较函数
    print("\n=== 开始测试新增的矩阵比较函数 ====")
    
    # 测试24: 测试多个矩阵特定位置值是否相同
    print("\n测试24: 测试多个矩阵特定位置值是否相同")
    matrix1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    matrix2 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    matrix3 = [[1, 2, 3], [4, 10, 6], [7, 8, 9]]
    pos_same = (0, 0)
    pos_diff = (1, 1)
    print(f"矩阵1和矩阵2在位置{pos_same}的值是否相同: {game.check_matrices_same_value([matrix1, matrix2], pos_same)}")  # 应该返回True
    print(f"矩阵1和矩阵2和矩阵3在位置{pos_same}的值是否相同: {game.check_matrices_same_value([matrix1, matrix2, matrix3], pos_same)}")  # 应该返回True
    print(f"矩阵1和矩阵3在位置{pos_diff}的值是否相同: {game.check_matrices_same_value([matrix1, matrix3], pos_diff)}")  # 应该返回False
    
    # 测试25: 测试多个矩阵特定位置值的类型是否相同
    print("\n测试25: 测试多个矩阵特定位置值的类型是否相同")
    matrix_type1 = [[1, 2, 3], [4, 5, 6]]
    matrix_type2 = [[7, 8, 9], [10, 11, 12]]
    matrix_type3 = [["1", "2", "3"], ["4", "5", "6"]]
    pos = (0, 0)
    print(f"矩阵type1和矩阵type2在位置{pos}的值的类型是否相同: {game.check_matrices_same_type([matrix_type1, matrix_type2], pos)}")  # 应该返回True
    print(f"矩阵type1和矩阵type3在位置{pos}的值的类型是否相同: {game.check_matrices_same_type([matrix_type1, matrix_type3], pos)}")  # 应该返回False
    
    # 测试26: 测试两个矩阵特定值的重叠
    print("\n测试26: 测试两个矩阵特定值的重叠")
    matrix_overlap1 = [[0, 1, 0], [1, 1, 0], [0, 0, 1]]
    matrix_overlap2 = [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
    target_value = 1
    has_overlap, overlap_positions = game.check_matrices_value_overlap(matrix_overlap1, matrix_overlap2, target_value)
    print(f"两个矩阵是否有值为{target_value}的重叠: {has_overlap}")
    print(f"重叠的位置: {overlap_positions}")
    
    print("\n=== 新增函数测试完成 ====")
    
    # 测试27: 测试多个矩阵的碰撞值检测
    print("\n测试27: 测试多个矩阵的碰撞值检测")
    # 创建数据矩阵
    matrix_a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    matrix_b = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
    
    # 创建碰撞矩阵（布尔矩阵）
    matrix_c1 = [[True, False, False], [False, False, False], [False, False, True]]
    matrix_d1 = [[True, False, False], [True, False, False], [False, False, False]]
    
    matrix_c2 = [[True, False, False], [False, False, False], [False, False, True]]
    matrix_d2 = [[True, False, False], [True, False, False], [False, False, True]]
    
    # 测试用例1: 只有一个碰撞位置
    print("\n测试用例1: 只有一个碰撞位置")
    matrices1 = [matrix_a, matrix_b, matrix_c1, matrix_d1]
    result1 = game.check_matrices_collision_values(matrices1)
    print(f"碰撞位置的数据值: {result1}")  # 应该返回[[1, 'a']]
    
    # 测试用例2: 有多个碰撞位置
    print("\n测试用例2: 有多个碰撞位置")
    matrices2 = [matrix_a, matrix_b, matrix_c2, matrix_d2]
    result2 = game.check_matrices_collision_values(matrices2)
    print(f"碰撞位置的数据值: {result2}")  # 应该返回[[1, 'a'], [9, 'i']]
    
    print("\n=== 所有函数测试完成 ====")
