# 批量文件重命名 MCP 服务器

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP Protocol](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://github.com/anthropics/model-context-protocol)

功能强大、安全可靠的文件批量重命名工具，基于 MCP (Model Context Protocol) 构建，支持多种重命名模式和安全预览。

## ✨ 核心特性

### 🎯 多样化重命名模式
- **模板变量**: 使用 `{name}`, `{counter}`, `{date}`, `{time}` 等变量
- **正则表达式**: 支持复杂的模式匹配和替换，包括捕获组
- **大小写转换**: `upper:`, `lower:`, `title:` 转换文件名大小写
- **序号格式化**: 支持零填充格式如 `{counter:03d}`

### 🛡️ 安全性保障
- **预览模式**: 执行前预览所有更改，避免意外操作
- **路径安全验证**: 防止路径遍历攻击和非法文件名
- **原子性操作**: 操作失败时自动回滚，保证文件系统一致性
- **冲突解决**: 智能处理文件名冲突，支持跳过、覆盖、自动编号

### 📋 操作日志管理
- **完整日志记录**: 记录每次重命名操作的详细信息
- **一键撤销**: 支持撤销最近的重命名操作
- **历史查询**: 查看操作历史和统计信息

### 🔍 文件扫描功能
- **智能扫描**: 支持递归扫描和文件类型过滤
- **详细信息**: 显示文件大小、修改时间、权限等信息
- **性能优化**: 支持最大文件数限制，避免内存溢出

## 🚀 快速开始

### 安装要求

- Python 3.10 或更高版本
- MCP 1.0.0 或更高版本

### 安装方式

```bash
# 使用 pip 安装
pip install batch-rename-mcp

# 或者从源码安装
git clone https://github.com/fengjinchao/batch-rename-mcp.git
cd batch-rename-mcp
pip install -e .
```

### 基本使用

```bash
# 启动 MCP 服务器
batch-rename-mcp

# 或者使用 Python 模块方式
python -m src.server
```

## 📖 使用指南

### 1. 批量重命名工具 (batch_rename)

#### 基本语法
```json
{
  "target": "/path/to/files",
  "pattern": "重命名模式",
  "options": {
    "dry_run": true,
    "recursive": false,
    "file_filter": "*.jpg",
    "conflict_resolution": "auto_number"
  }
}
```

#### 重命名模式详解

##### 模板变量模式
```bash
# 添加序号
"photo_{counter:03d}"           # photo_001.jpg, photo_002.jpg

# 使用原文件名
"backup_{name}"                 # backup_image.jpg

# 添加日期时间
"IMG_{date}_{counter}"          # IMG_20240919_1.jpg

# 组合使用
"{date}_{name}_{counter:02d}"   # 20240919_photo_01.jpg
```

##### 正则表达式模式
```bash
# 基本替换
"regex:^test:fjc1"              # test_file.jpg -> fjc1_file.jpg

# 忽略大小写
"regex:IMG:PHOTO:i"             # IMG_123.jpg -> PHOTO_123.jpg

# 使用捕获组
"regex:IMG_(\\d+):PHOTO_$1"     # IMG_123.jpg -> PHOTO_123.jpg

# 复杂模式
"regex:(\\d{4})(\\d{2})(\\d{2}):$1-$2-$3"  # 20240919 -> 2024-09-19
```

##### 大小写转换模式
```bash
"upper:{name}"                  # 转为大写
"lower:{name}"                  # 转为小写
"title:{name}"                  # 转为标题格式
```

#### 选项参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `recursive` | boolean | `false` | 是否包含子目录 |
| `file_filter` | string | `"*"` | 文件类型过滤器 (如 `*.jpg`, `*.png`) |
| `conflict_resolution` | string | `"auto_number"` | 冲突处理: `skip`, `auto_number`, `overwrite` |
| `dry_run` | boolean | `false` | 预览模式，不实际执行 |

#### 使用示例

```json
// 示例1: 给照片添加序号前缀（预览模式）
{
  "target": "~/Desktop/photos",
  "pattern": "photo_{counter:03d}",
  "options": {
    "file_filter": "*.jpg",
    "dry_run": true
  }
}

// 示例2: 替换文件名前缀
{
  "target": "/Users/username/documents",
  "pattern": "regex:^old:new",
  "options": {
    "recursive": true,
    "conflict_resolution": "skip"
  }
}

// 示例3: 添加日期前缀
{
  "target": "./files",
  "pattern": "{date}_{name}",
  "options": {
    "dry_run": false
  }
}
```

### 2. 撤销重命名 (undo_rename)

```json
// 撤销最近一次操作
{}

// 撤销指定操作
{
  "operation_id": "operation_12345"
}
```

### 3. 文件扫描 (scan_files)

```json
{
  "path": "/path/to/scan",
  "recursive": true,
  "filter": "*.pdf",
  "max_files": 50
}
```

## 🔧 高级配置

### MCP 资源访问

服务器提供以下资源：

- `operation_log://recent` - 最近操作日志
- `config://current` - 当前配置信息
- `paths://info` - 路径信息

### 安全配置

默认安全设置包括：
- 禁止访问系统关键目录
- 文件名长度限制 (255 字符)
- 单次操作文件数量限制 (1000 个)
- 路径遍历攻击防护

### 日志配置

操作日志存储在 `~/.mcp/batch_rename/` 目录下，包含：
- 操作时间戳
- 重命名前后的文件路径
- 操作参数和结果
- 错误信息（如果有）

## 🛠️ 开发说明

### 项目结构

```
src/
├── server.py              # MCP 服务器主程序
├── core/                  # 核心功能模块
│   ├── renamer.py         # 重命名核心逻辑
│   ├── pattern_parser.py  # 模式解析器
│   └── operation_log.py   # 操作日志管理
├── tools/                 # MCP 工具实现
│   ├── batch_rename.py    # 批量重命名工具
│   ├── scan_files.py      # 文件扫描工具
│   └── undo_rename.py     # 撤销操作工具
└── utils/                 # 工具模块
    ├── security.py        # 安全验证
    ├── config_loader.py   # 配置加载
    └── paths.py           # 路径管理
```

### 运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black src/

# 类型检查
mypy src/
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Model Context Protocol](https://github.com/anthropics/model-context-protocol) - 强大的AI模型交互协议
- 所有贡献者和使用者的支持

## 📞 支持

如果遇到问题或有建议，请：

1. 查看 [Issues](https://github.com/fengjinchao/batch-rename-mcp/issues)
2. 创建新的 Issue
3. 联系维护者

---

**注意**: 使用批量重命名功能前，强烈建议先使用预览模式 (`dry_run: true`) 确认操作结果，避免意外的文件重命名。