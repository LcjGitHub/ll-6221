# 城市报时声采样点

MVP：报时声采样点的列表展示与增删改查。前后端分离，数据持久化于 SQLite。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Naive UI + @vueuse/core + axios，端口 **5101** |
| 后端 | FastAPI + SQLite（`backend/data/chime.db`），端口 **5000** |

## 字段说明

- **地点**：采样位置
- **声源类型**：如古钟、电子钟、鼓声
- **可听时间段**：可听到报时的时段
- **方向**：相对采样点的方位
- **备注**：补充说明

首次启动后端会自动写入 **5 条** 种子数据。

## 目录结构

```
.
├── backend/          # FastAPI 后端
│   ├── main.py
│   ├── data/         # SQLite 数据库（自动生成）
│   └── requirements.txt
├── frontend/         # Vue 3 前端
│   └── src/
└── README.md
```

## 环境要求

- Python 3.10+
- Node.js 18+（使用项目内 `npm`，无需全局 pnpm/yarn）

## 启动方式

### 1. 后端（一条命令）

在项目根目录执行：

```bash
cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && uvicorn main:app --reload --port 5000
```

**Linux / macOS：**

```bash
cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --port 5000
```

后端地址：<http://localhost:5000>  
API 文档：<http://localhost:5000/docs>

### 2. 前端

新开一个终端，在项目根目录执行：

```bash
cd frontend && npm install && npm run dev
```

前端地址：<http://localhost:5101>

开发模式下，前端通过 Vite 代理将 `/api` 请求转发到后端 `5000` 端口。

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sampling-points` | 列表 |
| GET | `/api/sampling-points/{id}` | 详情 |
| POST | `/api/sampling-points` | 新建 |
| PUT | `/api/sampling-points/{id}` | 更新 |
| DELETE | `/api/sampling-points/{id}` | 删除 |
| GET | `/api/health` | 健康检查 |
