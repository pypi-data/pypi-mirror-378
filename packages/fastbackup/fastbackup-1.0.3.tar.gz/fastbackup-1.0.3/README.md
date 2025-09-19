# FastBackup ⚡

<div align="center">

**一行导入式Python项目实验备份工具**

*再也不用担心忘记上次的实验参数了！*



</div>

---

## 🤔 为什么需要 FastBackup？

作为一个经常跑实验的开发者，你是否遇到过这些痛点：

- 🔄 "这次实验用的什么参数来着？"
- 😅 "上次的学习率是0.001还是0.01？"
- 😰 "改了一堆参数，结果还不如之前的版本..."
- 🤦‍♂️ "想回到上周的配置，但是记不清改了什么..."

**FastBackup 一行代码解决所有问题！**

## 🚀 特点

- **🎯 零配置**: 只需一行导入，无需任何配置文件
- **💾 智能备份**: 只在文件真正变化时才创建备份，避免重复
- **📁 自动检测**: 智能识别项目根目录，无需手动指定路径
- **🔍 完整历史**: 保留所有备份记录，支持一键恢复
- **🏃‍♂️ 超轻量**: 纯Python标准库实现，零外部依赖
- **🛡️ 安全无忧**: 本地存储，自动忽略git，不会泄露代码

## 📦 安装

```bash
pip install fastbackup
```

## 🎯 使用方法

### 最简单的使用 - 一行导入

在你的Python脚本开头添加这一行：

```python
import fastbackup  # 🎉 就这么简单！

# 你的实验代码
def train_model():
    learning_rate = 0.001  # 这次用0.001
    batch_size = 32        # 批次大小32
    epochs = 100           # 训练100轮
    
    # 模型训练代码...
    model = create_model()
    optimizer = Adam(lr=learning_rate)
    
    for epoch in range(epochs):
        # 训练逻辑...
        pass

if __name__ == "__main__":
    train_model()
```

**就是这样！** 每次运行脚本时，FastBackup会：
- ✅ 自动检测你的项目目录
- ✅ 智能判断是否有文件变化
- ✅ 只在需要时创建备份
- ✅ 在项目根目录创建 `.fastbackup` 文件夹存储备份

## 📁 备份位置示例

假设你的项目结构：
```
my_experiment/
├── train.py          # 你在这里 import fastbackup
├── model.py
├── config.py
└── utils.py
```

运行后自动创建：
```
my_experiment/
├── train.py
├── model.py
├── config.py
├── utils.py
├── .fastbackup/                    # 🆕 备份目录
│   ├── backup_20240310_143022/     # 第一个版本
│   │   ├── train.py
│   │   ├── model.py
│   │   ├── config.py
│   │   ├── utils.py
│   │   └── backup_info.json
│   ├── backup_20240310_150134/     # 修改参数后的版本
│   │   └── ...
│   └── backup_20240311_091245/     # 今天的版本
│       └── ...
└── .gitignore                      # 🆕 自动更新
```

## 🔍 查看备份历史

### 命令行方式
```bash
$ fastbackup --list

📋 FastBackup 历史记录 (5 个备份):
------------------------------------------------------------
 1. 2024-03-11 09:12:45 | 4 文件 | backup_20240311_091245
 2. 2024-03-10 16:30:22 | 4 文件 | backup_20240310_163022  
 3. 2024-03-10 15:01:34 | 4 文件 | backup_20240310_150134
 4. 2024-03-10 14:30:22 | 4 文件 | backup_20240310_143022
 5. 2024-03-09 18:45:11 | 4 文件 | backup_20240309_184511
```

### Python代码方式
```python
import fastbackup
fastbackup.list_backups()
```

## 🎮 恢复备份

当你发现新版本效果不好，想回到之前的版本：

### 命令行恢复
```bash
$ fastbackup --restore backup_20240310_143022

🔄 恢复备份: backup_20240310_143022
  ✅ train.py
  ✅ model.py  
  ✅ config.py
  ✅ utils.py
✨ 恢复完成! 共恢复 4 个文件
```

### Python代码恢复
```python
import fastbackup
fastbackup.restore("backup_20240310_143022")
```

## 🎯 实际使用场景

### 场景1：深度学习调参
```python
import fastbackup

# Week 1: Baseline
learning_rate = 0.001
batch_size = 32
# Result: 85% accuracy

# Week 2: 尝试更大的学习率
learning_rate = 0.01   # 修改这里
batch_size = 32
# Result: 82% accuracy (更差了)

# Week 3: 回到baseline，尝试更大的batch size
learning_rate = 0.001  # 恢复baseline
batch_size = 64        # 只改这个
# Result: 87% accuracy (更好了!)
```

每次修改都会自动备份，你可以随时对比和恢复任何版本！

### 场景2：机器学习特征工程
```python
import fastbackup

def preprocess_data():
    # V1: 基础预处理
    normalize = True
    remove_outliers = False
    feature_scaling = "standard"
    
    # V2: 加上异常值处理
    # remove_outliers = True  # 效果提升2%
    
    # V3: 尝试不同的缩放方法
    # feature_scaling = "minmax"  # 效果下降了
```

### 场景3：Web开发配置调试
```python
import fastbackup

# 数据库配置实验
DATABASE_CONFIG = {
    "pool_size": 10,      # 连接池大小
    "timeout": 30,        # 超时时间
    "retry_times": 3,     # 重试次数
}

# API限流配置
RATE_LIMIT = {
    "requests_per_minute": 100,
    "burst_size": 20,
}
```

## 📊 运行时输出示例

```bash
$ python train.py
💾 FastBackup: 创建备份 backup_20240311_091245 (4 个文件)
Starting training...
Epoch 1/100: loss=0.45, accuracy=0.82
...

$ python train.py  # 没有修改文件
🔄 FastBackup: 使用现有备份 backup_20240311_091245
Starting training...
...
```

## 🛠️ 高级功能

### 手动触发备份
```python
import fastbackup

# 在关键节点手动备份
fastbackup.backup()
print("重要版本已备份！")
```

### 跨项目查看备份
```python
import fastbackup

# 查看其他项目的备份
fastbackup.list_backups("/path/to/another/project")

# 恢复其他项目的备份
fastbackup.restore("backup_name", "/path/to/another/project")
```

### 命令行工具
```bash
# 查看版本
fastbackup --version

# 查看帮助
fastbackup --help

# 指定项目路径
fastbackup --list --project /path/to/project
```

## 🔧 配置说明

FastBackup 采用零配置设计，但你可以了解它的行为：

- **备份位置**: 项目根目录的 `.fastbackup/` 文件夹
- **备份内容**: 只备份 `.py` 文件
- **忽略目录**: 自动跳过 `.git`、`__pycache__`、`venv`、`node_modules` 等
- **变化检测**: 基于文件MD5哈希，确保准确检测变化
- **Git集成**: 自动将 `.fastbackup/` 添加到 `.gitignore`

## 🚫 不会备份的内容

- 数据文件 (`.csv`, `.json`, `.txt` 等)
- 模型权重 (`.pth`, `.h5`, `.ckpt` 等)  
- 虚拟环境 (`venv/`, `env/`, `.venv/`)
- Git目录 (`.git/`)
- 缓存文件 (`__pycache__/`, `.pytest_cache/`)
- 依赖目录 (`node_modules/`)

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 报告问题
如果你遇到bug或有功能建议，请[创建一个Issue](https://github.com/chenziwenhaoshuai/fastbackup/issues)。


## ❓ 常见问题

### Q: 会影响程序运行速度吗？
A: 几乎不会。FastBackup采用智能检测，只在文件真正变化时才执行备份操作，通常耗时不超过几毫秒。

### Q: 备份会占用很多空间吗？
A: 通常不会。只备份`.py`文件，而且可以定期清理旧备份。一个中型项目的备份通常只有几MB。

### Q: 支持哪些Python版本？
A: Python 3.6+ 都支持，无外部依赖。

### Q: 可以在生产环境使用吗？
A: FastBackup主要为开发和实验设计。在生产环境建议使用专业的版本控制和部署工具。

### Q: 如何删除旧备份？
A: 直接删除 `.fastbackup/` 目录下的对应文件夹即可，或者我们计划在未来版本中添加自动清理功能。

## 📜 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🎉 致谢

感谢所有为这个项目做出贡献的开发者！

---

<div align="center">

**如果 FastBackup 帮到了你，请给我们一个 ⭐ 星标！**

Made with ❤️ by developers, for developers.

</div>