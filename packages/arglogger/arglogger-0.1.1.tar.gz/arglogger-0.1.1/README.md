# ArgLogger

一个用于记录机器学习实验的 Python 包，可以根据 argparse 配置自动创建数据库表或 CSV 文件，方便保存和管理实验结果。

## 特性

- 🚀 **自动化**: 从 argparse 配置自动生成表结构
- 💾 **多后端支持**: 支持 SQLite 数据库和 CSV 文件存储
- 🔄 **灵活操作**: 支持增删改查操作
- ⏰ **时间戳**: 自动添加创建和更新时间
- 🎯 **类型推断**: 智能推断数据类型
- 📊 **易于统计**: 便于后续的结果分析和统计

## 安装

```bash
pip install arglogger
```

或者从源码安装：

```bash
git clone https://github.com/MinsGoing/arglogger.git
cd arglogger
pip install -e .
```

## 快速开始

### 基本用法

```python
import argparse
from arglogger import ArgLogger

# 创建 argparse parser
parser = argparse.ArgumentParser()
parser.add_argument('--learning_rate', type=float, default=0.001)
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--epochs', type=int, default=100)
parser.add_argument('--model', type=str, default='resnet50')

# 解析参数（这里是示例参数）
args = parser.parse_args(['--learning_rate', '0.01', '--batch_size', '64'])

# 创建实验记录器
logger = ArgLogger(
    experiment_name='my_experiment',
    backend='sqlite',  # 或者 'csv'
    parser=parser  # 或者传入 args=args
)

# 记录实验结果
logger.log_result({
    'learning_rate': args.learning_rate,
    'batch_size': args.batch_size,
    'epochs': args.epochs,
    'model': args.model,
    'accuracy': 0.95,
    'loss': 0.05
})

# 获取所有结果
results = logger.get_results()
print(results)

# 关闭连接
logger.close()
```

### 使用 CSV 后端

```python
from arglogger import ArgLogger

# 使用 CSV 文件存储
logger = ArgLogger(
    experiment_name='csv_experiment',
    backend='csv',
    storage_path='experiments/results.csv',
    args=args
)

# 记录结果
logger.log_result({
    'accuracy': 0.92,
    'precision': 0.88,
    'recall': 0.90,
    'f1_score': 0.89
})
```

### 完整的实验脚本示例

```python
import argparse
from arglogger import ArgLogger

def train_model(args):
    """模拟训练过程"""
    # 这里是你的训练代码
    accuracy = 0.95  # 假设的结果
    loss = 0.05
    return accuracy, loss

def main():
    # 设置参数
    parser = argparse.ArgumentParser(description='Machine Learning Experiment')
    parser.add_argument('--learning_rate', type=float, default=0.001)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--model', type=str, default='resnet50')
    parser.add_argument('--optimizer', type=str, default='adam')
    parser.add_argument('--dataset', type=str, default='cifar10')
    
    args = parser.parse_args()
    
    # 创建实验记录器
    logger = ArgLogger(
        experiment_name='ml_experiments',
        backend='sqlite',
        storage_path='experiments.db',
        args=args
    )
    
    # 训练模型
    accuracy, loss = train_model(args)
    
    # 记录结果
    logger.log_result({
        'learning_rate': args.learning_rate,
        'batch_size': args.batch_size,
        'epochs': args.epochs,
        'model': args.model,
        'optimizer': args.optimizer,
        'dataset': args.dataset,
        'accuracy': accuracy,
        'loss': loss,
        'notes': f'Experiment with {args.model} on {args.dataset}'
    })
    
    print(f'Experiment logged: Accuracy={accuracy:.4f}, Loss={loss:.4f}')
    
    # 查看历史结果
    results = logger.get_results(limit=5)
    print(f'\\nLast 5 experiments:')
    for result in results:
        print(f'ID: {result["id"]}, Model: {result["model"]}, Accuracy: {result["accuracy"]:.4f}')
    
    logger.close()

if __name__ == '__main__':
    main()
```

## 高级功能

### 更新和删除结果

```python
# 更新结果
logger.update_result(
    condition={'id': 1},  # 条件
    updates={'accuracy': 0.96, 'notes': 'Updated accuracy'}  # 更新内容
)

# 删除结果
logger.delete_results(condition={'id': 1})
```

### 动态添加列

```python
# 添加新列
logger.add_column('validation_accuracy', 'REAL')

# 记录包含新列的结果
logger.log_result({
    'accuracy': 0.95,
    'validation_accuracy': 0.92
})
```

### 查看表结构

```python
# 获取当前表结构
schema = logger.get_schema()
print(schema)
```

## API 文档

### ArgLogger 类

#### 构造函数

```python
ArgLogger(
    experiment_name: str,
    backend: str = 'sqlite',
    storage_path: Optional[str] = None,
    parser: Optional[argparse.ArgumentParser] = None,
    args: Optional[argparse.Namespace] = None,
    auto_timestamp: bool = True
)
```

**参数:**
- `experiment_name`: 实验名称（用作表名或文件名）
- `backend`: 存储后端，'sqlite' 或 'csv'
- `storage_path`: 存储路径（可选，默认使用实验名称）
- `parser`: ArgumentParser 实例（用于自动提取表结构）
- `args`: 解析后的参数对象（用于自动提取表结构）
- `auto_timestamp`: 是否自动添加时间戳列

#### 主要方法

- `log_result(results: Dict[str, Any], **kwargs)`: 记录实验结果
- `get_results(limit: Optional[int] = None)`: 获取实验结果
- `update_result(condition: Dict[str, Any], updates: Dict[str, Any])`: 更新结果
- `delete_results(condition: Dict[str, Any])`: 删除结果
- `add_column(column_name: str, column_type: str)`: 添加列
- `get_schema()`: 获取当前表结构
- `close()`: 关闭连接

## 支持的数据类型

- `INTEGER`: 整数
- `REAL`: 浮点数
- `TEXT`: 字符串
- `BOOLEAN`: 布尔值

复杂类型（如列表、字典）会自动序列化为 JSON 字符串存储。

## 示例场景

### 1. 机器学习模型比较

```python
models = ['resnet50', 'vgg16', 'mobilenet']
learning_rates = [0.001, 0.01, 0.1]

for model in models:
    for lr in learning_rates:
        # 训练模型
        accuracy = train_model(model, lr)
        
        # 记录结果
        logger.log_result({
            'model': model,
            'learning_rate': lr,
            'accuracy': accuracy
        })
```

### 2. 超参数搜索

```python
import itertools

# 定义超参数空间
param_grid = {
    'batch_size': [16, 32, 64],
    'learning_rate': [0.001, 0.01],
    'dropout': [0.2, 0.5]
}

# 网格搜索
for params in itertools.product(*param_grid.values()):
    param_dict = dict(zip(param_grid.keys(), params))
    
    # 训练和评估
    results = train_and_evaluate(**param_dict)
    
    # 记录结果
    logger.log_result({**param_dict, **results})
```

## 注意事项

1. SQLite 文件会自动创建，但 CSV 文件的目录需要存在
2. 表名和列名会自动清理，移除特殊字符
3. 自动时间戳使用 ISO 格式
4. CSV 后端依赖 pandas，确保已安装

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v0.1.0
- 初始版本
- 支持 SQLite 和 CSV 后端
- 自动从 argparse 生成表结构
- 基本的 CRUD 操作