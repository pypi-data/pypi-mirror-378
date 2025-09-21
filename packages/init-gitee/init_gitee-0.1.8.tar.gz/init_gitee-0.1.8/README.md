# Gitee 仓库管理工具

一个命令行工具，用于管理 Gitee 代码仓库，支持创建、列出和删除仓库等操作。

## 功能特性

- 创建个人或组织仓库
- 列出用户所有仓库
- 删除指定仓库
- 支持多种仓库配置选项

## 安装

### 通过 pip 安装

```bash
pip install init-gitee
```

## 使用说明

### 基本命令

```bash
init-gitee [OPTIONS] COMMAND [ARGS]...
```

## 命令列表

### 创建仓库

```bash
init-gitee create-repo <仓库名称> [OPTIONS]
```

选项：

-g, --org TEXT 组织名称
-p, --path TEXT 仓库路径
-d, --description TEXT 仓库描述
-h, --homepage TEXT 项目主页
-r, --private 设为私有仓库 (默认: True)
-a, --auto-init 创建初始提交

### 列出仓库

```bash
init-gitee list-repos [OPTIONS]
```

选项：

-p, --page INTEGER 页码 (默认: 1)
-r, --repos-per-page INTEGER 每页数量 (默认: 20)

### 删除仓库

```bash
init-gitee delete-repos <仓库名称> [OPTIONS]
```

选项：

-o, --owner TEXT 仓库所有者 (必须)

### 配置

工具会默认读取 ~/.init-gitee/config.ini 配置文件，格式如下：


```ini
Apply
[auth]
access_token = 您的Gitee访问令牌
```

## 示例

创建个人仓库：

```bash
init-gitee create-repo my-project --description "我的项目"
```

创建组织仓库：

```bash
init-gitee create-repo org-project --org my-org
```

列出仓库：

```bash
init-gitee list-repos --page 2
```

删除仓库：

```bash
init-gitee delete-repos my-project --owner my-username
```

许可证

MIT License

