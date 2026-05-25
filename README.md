# FileSweeper

一个智能的文件整理工具，可根据文件扩展名自动分类整理文件，支持 dry-run 预览模式和撤销操作。

## 功能特性

- **扫描目录** - 递归扫描目录中的所有文件（自动排除隐藏文件）
- **按扩展名分类** - 自动识别文件类型并分类为 Images、Documents、Python、Others
- **dry-run 预览** - 在实际移动文件前预览将要执行的操作
- **撤销操作** - 支持撤销上一步文件整理操作
- **命令行界面** - 提供 CLI 接口方便快速使用

## 安装与使用

### 环境要求

- Python 3.8+

### 安装步骤

1. 克隆项目到本地：
```bash
git clone <repository-url>
cd file_sweeper
```

2. 创建虚拟环境并激活：
```bash
# 使用 venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 或使用 Poetry
poetry install
```

3. 运行测试验证安装：
```bash
pytest tests/ -v
```

### Python API 使用

```python
from pathlib import Path
from file_sweeper import FileOrganizer

# 创建整理器实例
organizer = FileOrganizer(Path("./my_documents"))

# 预览整理操作（dry-run）
records = organizer.organize(dry_run=True)
for record in records:
    print(f"{record['src']} -> {record['dst']} ({record['category']})")

# 执行实际整理
organizer.organize(dry_run=False)

# 撤销上一步操作
if organizer.undo_last():
    print("撤销成功！")
```

### 命令行使用

```bash
# 使用 Python 模块方式运行
python -m file_sweeper <directory-path>

# 预览操作而不实际移动文件
python -m file_sweeper --dry-run <directory-path>

# 示例
python -m file_sweeper ~/Downloads
python -m file_sweeper -n ~/Downloads
```

## 项目结构

```
file_sweeper/
├── src/
│   └── file_sweeper/
│       ├── __init__.py      # 包初始化文件
│       └── core.py          # 核心功能实现
├── tests/
│   └── test_core.py         # 单元测试
├── pyproject.toml           # Poetry 配置文件
├── README.md                # 项目说明文档
└── CLAUDE.md                # 项目开发规范
```

## 依赖项

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | ^3.8 | 运行环境 |
| Click | ^8.1.0 | 命令行界面 |
| pytest | ^7.4.0 | 单元测试 |

## 测试方法

运行项目提供的测试套件：

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_core.py -v

# 运行测试并显示输出
pytest tests/ -v -s
```

## 文件分类规则

| 扩展名 | 分类 |
|--------|------|
| .jpg, .jpeg, .png, .gif | Images |
| .txt, .md | Documents |
| .py, .pyw | Python |
| 其他文件 | Others |

## 注意事项

- 隐藏文件（以 `.` 开头的文件）会被自动排除，不会被整理
- 目录内会自动创建相应的分类子目录
- 使用 `dry-run` 模式可以安全地预览操作结果
- 撤销功能会将文件移回原始位置

## 许可证

MIT License
