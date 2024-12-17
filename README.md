# Gewechat Bot

## 简介

本项目是一个配合 [Gewechat](https://github.com/Devo919/Gewechat) 框架的微信机器人，旨在实现基本的登录、消息捕获、机器人下线告警以及接入 OpenAI/Claude API 进行对话。

**主要功能：**

-   **登录:** 使用 `login.py` 进行 Gewechat 的登录。
-   **消息捕获:** 捕获文本、图片和文件消息。
-   **机器人下线告警:** 通过邮件或 Telegram 发送机器人下线告警。
-   **AI 对话:** 集成 OpenAI 和 Claude API，实现智能对话。
-   **多级处理器:** 使用多级处理器架构，方便扩展和定制消息处理逻辑。
-   **灵活配置:** 通过 `config.yaml` 文件配置告警、监控、微信 API 和 AI 服务。

**注意：** 本项目依赖 Gewechat 框架，请确保已安装并运行 Gewechat 服务。

## 环境

-   Python 3.10+

## 依赖

-   通过 `pip install -r requirements.txt` 安装依赖。

## 使用方法

1.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **运行机器人主程序:**
    ```bash
    python bot.py
    ```

3.  **运行登录程序:**
    ```bash
    python login.py
    ```

## 配置

配置文件： `config.yaml`

### 告警配置 (`alerts`)

-   **email:**
    -   `enabled`: `true` 或 `false`，是否启用邮件告警。
    -   `recipient_email`: 接收告警邮件的邮箱地址 (例如：`xxx@qq.com`).
    -   `sender_email`: 发送告警邮件的邮箱地址 (例如：`xxx@qq.com`).
    -   `sender_password`: 发送邮箱的授权码 (例如：QQ 邮箱需要使用授权码).
    -   `smtp_port`: SMTP 端口 (例如：QQ 邮箱通常使用 `465`).
    -   `smtp_server`: SMTP 服务器地址 (例如：QQ 邮箱使用 `smtp.qq.com`).

    **注意:** 如果使用其他邮箱，可能需要修改代码以适应不同的 SMTP 设置。

-   **telegram:**
    -   `bot_token`: Telegram 机器人 Token.
    -   `chat_id`: Telegram 对话 ID.
    -   `enabled`: `true` 或 `false`，是否启用 Telegram 告警.

### 监控配置 (`monitoring`)

-   `check_interval`: 监控登录状态的时间间隔，单位为秒。默认 `30` 秒检查一次登录状态.

### Gewechat API 配置 (`wechat`)

-   `app_id`: (可选) Gewechat 的 App ID，如果已经配置在 Gewechat 中，可以不填。
-   `base_url`: Gewechat API 的地址 (例如：`http://localhost:2531/v2/api//Gewechat`).
-   `callback_url`: 消息回调地址，用于接收 Gewechat 发送的消息。可以在 `bot.py` 中修改，这里示例使用局域网地址，适合 Gewechat 使用 Docker 部署的情况 (例如：`http://192.168.1.2:8069/callback`).
-   `token`: (可选) Gewechat 的 Token，与 `app_id` 配对使用.

### AI 对话配置 (`ai_service`)

-   `proxy_host`: API 的 base URL，如果不需要使用代理，请直接修改 `ai_service.py` 的代码。
-   `default_provider`: 默认使用的 AI 提供商，可选 `openai` 或 `claude`。
-   `providers`: AI 提供商的配置。
    -   **claude:**
        -   `models`: Claude 的模型配置。
            -   `model_id`: 模型 ID.
            -   `input_cost`: 输入 Token 的成本（暂时未使用）。
            -   `output_cost`: 输出 Token 的成本（暂时未使用）。
        -   `api_keys`:
            -   `active`:  可用的 Claude API Keys 列表。
            -   `exhausted`:  已耗尽的 Claude API Keys 列表。
        -   `api_version`: Claude API 版本。
        -   `default_model`: 默认使用的 Claude 模型。
    -   **openai:**
        -   `models`: OpenAI 的模型配置。
            -   `model_id`: 模型 ID.
            -   `input_cost`: 输入 Token 的成本（暂时未使用）。
            -   `output_cost`: 输出 Token 的成本（暂时未使用）。
        -   `api_keys`:
            -   `active`: 可用的 OpenAI API Keys 列表。
            -   `exhausted`:  已耗尽的 OpenAI API Keys 列表。
        -   `default_model`: 默认使用的 OpenAI 模型。

## 消息处理逻辑

本项目使用多级处理器架构处理接收到的消息。

1.  **一级处理器:**
    -   接收 Gewechat 回调地址发送的 JSON 数据。
    -   根据消息类型进行初步处理。例如：判断是否为文本消息。
    -   如果匹配到处理逻辑，则将消息交给子处理器处理。
2.  **子处理器:**
    -   接收来自上一级处理器的消息。
    -   执行更细粒度的处理逻辑。例如：
        -   AI 对话功能：判断是否是文本消息，进一步判断是否需要调用 AI API 进行回复。
        -   （原计划）消息节流功能：防止用户多次发送消息，AI 回复时间可能过长导致堵塞（该功能存在 bug，尚未完成）。
3.  **AI API 调用:**
    -   由子处理器调用，将文本消息传递给 OpenAI 或 Claude API，并将返回的文本作为回复发送给用户。

### 处理器自定义

可以通过添加新的处理器类来扩展和自定义消息处理逻辑。

## 贡献

欢迎贡献代码，提交 Pull Requests 或 Issues。如果你觉得这个项目还不错，请给个 star!

## 项目链接

[Gewechat](https://github.com/Devo919/Gewechat) (本项目所依赖的框架)
