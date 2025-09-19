# rcline

A 2D simulation package for cat and line interaction with collision detection.

## Overview

rcline is a Python library designed to simulate interactions between "cat" entities and line entities in a 2D environment, with built-in collision detection. It provides an easy-to-use interface for creating and visualizing simulations where cats can move (either controlled by user input or programmatically) and interact with various types of lines.

## Features

- 2D simulation environment with customizable grid
- Controllable cat entities with physics-based movement
- Line entities (both solid/collidable and non-solid)
- Real-time collision detection between entities
- Visual feedback for collisions and movement
- Customizable colors and visual properties

### From Source

```bash
git clone https://github.com/waliwuao/rcline.git
cd rcline
pip install .
```

For development (with optional dev dependencies):

```bash
pip install ".[dev]"
```

## Quick Start

Here's a simple example to create a simulation with a controllable cat and some lines:

```python
from rcline import Map, Cat, Line

# Create a 10x10 simulation map
sim_map = Map(width=10, height=10, title="Simple Cat Simulation")

# Add some lines (solid lines are collidable)
sim_map.add_entity(Line(2, 2, 8, 2, solid=True))
sim_map.add_entity(Line(2, 8, 8, 8, solid=True))
sim_map.add_entity(Line(5, 2, 5, 5))  # Non-solid line

# Add a controllable cat
sim_map.add_entity(Cat(5, 5, radius=0.5, controllable=True))

# Start the simulation
sim_map.start_simulation()
```

Use arrow keys to move the cat. The cat will collide with solid lines but can pass through non-solid lines.

## Core Components

### Map

The `Map` class is the main simulation container that manages all entities and visualization.

```python
Map(width=10, height=10, title="Simulation Map", grid_step=1)
```

Key methods:
- `add_entity(entity)`: Add an entity to the simulation
- `remove_entity(entity)`: Remove an entity from the simulation
- `start_simulation(interval=50)`: Start the animation with specified interval (ms)
- `stop_simulation()`: Stop the animation

### Cat

The `Cat` class represents a circular entity that can move and collide with other entities.

```python
Cat(x, y, color=None, radius=1, vx=0, vy=0, ax=0, ay=0, 
    move_acceleration=2, friction=0.9, controllable=False)
```

- `x`, `y`: Initial position
- `radius`: Radius of the cat
- `vx`, `vy`: Initial velocity components
- `controllable`: If True, can be controlled with arrow keys
- `move_acceleration`: Acceleration when moving
- `friction`: Friction coefficient (0-1) that reduces velocity over time

### Line

The `Line` class represents line segments that can be either solid (collidable) or non-solid.

```python
Line(start_x, start_y, end_x, end_y, color=None, solid=False)
```

- `start_x`, `start_y`: Starting coordinates
- `end_x`, `end_y`: Ending coordinates
- `solid`: If True, cats will collide with this line
- `color`: Custom color (uses default from `ENTITY_COLORS` if not specified)

### Collision Detection

The `Collide` class provides static methods for detecting collisions between entities:
- `check_collision(entity1, entity2)`: General collision check between any two entities
- Supports circle-circle (cat-cat) and circle-line (cat-line) collisions

## Customization

### Colors

You can customize colors using the constants from `rcline.colors`:

```python
from rcline import colors

# Example: Change primary color
colors.PRIMARY_COLOR = '#FF5733'

# Entity-specific colors
colors.ENTITY_COLORS['cat'] = '#33FF57'
colors.ENTITY_COLORS['solid_line'] = '#3357FF'
```

Available color constants:
- `PRIMARY_COLOR`, `SECONDARY_COLOR`, `ACCENT_COLOR`
- `LIGHT_GRAY`, `MEDIUM_GRAY`, `DARK_GRAY`
- `BACKGROUND_COLOR`, `GRID_MAJOR_COLOR`, `GRID_MINOR_COLOR`
- `ENTITY_COLORS`: Dictionary with colors for 'cat', 'line', and 'solid_line'

## Advanced Usage

### Creating Custom Entities

You can create custom entities by subclassing the `Entity` base class:

```python
from rcline import Entity
import matplotlib.pyplot as plt

class Square(Entity):
    def __init__(self, x, y, size, color=None):
        super().__init__(color or '#888888')
        self.x = x
        self.y = y
        self.size = size
        self.type = 'square'
        
    def draw(self, ax):
        square = plt.Rectangle(
            (self.x - self.size/2, self.y - self.size/2),
            self.size, self.size,
            color=self.color
        )
        ax.add_patch(square)
        
    def update(self, dt, entity_list=None):
        # Add custom update logic here
        pass
```

### Adding Collision Logic

To add collision detection for custom entities, extend the `Collide` class with new collision methods:

```python
from rcline import Collide

@staticmethod
def _square_line_collision(square, line):
    # Implement square-line collision logic
    return False

Collide._square_line_collision = _square_line_collision

# Update the general collision check
def check_collision(entity1, entity2):
    # Existing checks...
    if type1 == 'square' and type2 == 'line':
        return Collide._square_line_collision(entity1, entity2)
    # More checks...
    
Collide.check_collision = check_collision
```

## Dependencies

- matplotlib >= 3.5.0
- numpy >= 1.21.0
- keyboard >= 0.13.5

## License

Apache License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Issues

Please report any issues or feature requests on the [GitHub Issue Tracker](https://github.com/waliwuao/rcline/issues).

## Author

WallyHao (1276672206@qq.com)

## Acknowledgments

- matplotlib for visualization capabilities
- numpy for numerical operations
- keyboard library for input handling

# rcline

一个用于猫与线条交互的2D模拟库，包含碰撞检测功能。

## 概述

rcline是一个Python库，旨在模拟2D环境中"猫"实体与线条实体之间的交互，并内置碰撞检测功能。它提供了易于使用的接口，用于创建和可视化模拟场景，其中猫可以移动（通过用户输入或编程控制）并与各种类型的线条进行交互。

## 特性

- 可自定义网格的2D模拟环境
- 具有基于物理运动的可控猫实体
- 线条实体（包括实心/可碰撞和非实心两种类型）
- 实体间的实时碰撞检测
- 碰撞和运动的视觉反馈
- 可自定义的颜色和视觉属性


### 从源码安装

```bash
git clone https://github.com/waliwuao/rcline.git
cd rcline
pip install .
```

开发环境安装（包含可选的开发依赖）：

```bash
pip install ".[dev]"
```

## 快速入门

下面是一个简单的示例，创建一个包含可控猫和一些线条的模拟场景：

```python
from rcline import Map, Cat, Line

# 创建一个10x10的模拟地图
sim_map = Map(width=10, height=10, title="简单的猫模拟")

# 添加一些线条（实心线条是可碰撞的）
sim_map.add_entity(Line(2, 2, 8, 2, solid=True))
sim_map.add_entity(Line(2, 8, 8, 8, solid=True))
sim_map.add_entity(Line(5, 2, 5, 5))  # 非实心线条

# 添加一个可控的猫
sim_map.add_entity(Cat(5, 5, radius=0.5, controllable=True))

# 启动模拟
sim_map.start_simulation()
```

使用方向键移动猫。猫会与实心线条发生碰撞，但可以穿过非实心线条。

## 核心组件

### Map（地图）

`Map`类是主要的模拟容器，用于管理所有实体和可视化。

```python
Map(width=10, height=10, title="模拟地图", grid_step=1)
```

主要方法：
- `add_entity(entity)`：向模拟中添加实体
- `remove_entity(entity)`：从模拟中移除实体
- `start_simulation(interval=50)`：以指定的时间间隔（毫秒）启动动画
- `stop_simulation()`：停止动画

### Cat（猫）

`Cat`类表示一个圆形实体，可以移动并与其他实体发生碰撞。

```python
Cat(x, y, color=None, radius=1, vx=0, vy=0, ax=0, ay=0, 
    move_acceleration=2, friction=0.9, controllable=False)
```

- `x`, `y`：初始位置
- `radius`：猫的半径
- `vx`, `vy`：初始速度分量
- `controllable`：如果为True，可以用方向键控制
- `move_acceleration`：移动时的加速度
- `friction`：摩擦系数（0-1），用于随时间减小速度

### Line（线条）

`Line`类表示线段，可以是实心（可碰撞）或非实心。

```python
Line(start_x, start_y, end_x, end_y, color=None, solid=False)
```

- `start_x`, `start_y`：起始坐标
- `end_x`, `end_y`：结束坐标
- `solid`：如果为True，猫会与这条线发生碰撞
- `color`：自定义颜色（如果未指定，则使用`ENTITY_COLORS`中的默认值）

### 碰撞检测

`Collide`类提供静态方法用于检测实体之间的碰撞：
- `check_collision(entity1, entity2)`：检查任意两个实体之间的碰撞
- 支持圆-圆（猫-猫）和圆-线（猫-线）碰撞

## 自定义

### 颜色

您可以使用`rcline.colors`中的常量来自定义颜色：

```python
from rcline import colors

# 示例：更改主色调
colors.PRIMARY_COLOR = '#FF5733'

# 实体特定颜色
colors.ENTITY_COLORS['cat'] = '#33FF57'
colors.ENTITY_COLORS['solid_line'] = '#3357FF'
```

可用的颜色常量：
- `PRIMARY_COLOR`（主色调）、`SECONDARY_COLOR`（辅助色）、`ACCENT_COLOR`（强调色）
- `LIGHT_GRAY`（浅灰）、`MEDIUM_GRAY`（中灰）、`DARK_GRAY`（深灰）
- `BACKGROUND_COLOR`（背景色）、`GRID_MAJOR_COLOR`（主网格色）、`GRID_MINOR_COLOR`（次网格色）
- `ENTITY_COLORS`：包含'cat'、'line'和'solid_line'的颜色字典

## 高级用法

### 创建自定义实体

您可以通过继承`Entity`基类来创建自定义实体：

```python
from rcline import Entity
import matplotlib.pyplot as plt

class Square(Entity):
    def __init__(self, x, y, size, color=None):
        super().__init__(color or '#888888')
        self.x = x
        self.y = y
        self.size = size
        self.type = 'square'
        
    def draw(self, ax):
        square = plt.Rectangle(
            (self.x - self.size/2, self.y - self.size/2),
            self.size, self.size,
            color=self.color
        )
        ax.add_patch(square)
        
    def update(self, dt, entity_list=None):
        # 在这里添加自定义更新逻辑
        pass
```

### 添加碰撞逻辑

要为自定义实体添加碰撞检测，可以扩展`Collide`类，添加新的碰撞方法：

```python
from rcline import Collide

@staticmethod
def _square_line_collision(square, line):
    # 实现正方形-线条碰撞逻辑
    return False

Collide._square_line_collision = _square_line_collision

# 更新通用碰撞检查
def check_collision(entity1, entity2):
    # 现有检查...
    if type1 == 'square' and type2 == 'line':
        return Collide._square_line_collision(entity1, entity2)
    # 更多检查...
    
Collide.check_collision = check_collision
```

## 依赖项

- matplotlib >= 3.5.0
- numpy >= 1.21.0
- keyboard >= 0.13.5

## 许可证

Apache许可证

## 贡献

1. Fork仓库
2. 创建您的特性分支（`git checkout -b feature/amazing-feature`）
3. 提交您的更改（`git commit -m 'Add some amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 打开Pull Request

## 问题反馈

请在[GitHub Issue Tracker](https://github.com/waliwuao/rcline/issues)上报告任何问题或功能请求。

## 作者

WallyHao（1276672206@qq.com）

## 致谢

- matplotlib提供的可视化功能
- numpy提供的数值运算支持
- keyboard库提供的输入处理功能