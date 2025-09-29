# Mod Environment Server

这是一个用于接收和管理Minecraft Mod环境信息的Flask服务器。

## 功能

1. 接收客户端上传的mod环境信息
2. 存储mod环境信息到JSON文件
3. 提供API接口查询mod环境信息
4. 每日自动备份数据，最多保留30天的备份

## API接口

### 上传mod环境信息
- **URL**: `/upload`
- **方法**: `POST`
- **数据格式**: JSON
- **示例**:
```json
{
  "modid1": "required",
  "modid2": "optional",
  "modid3": "unsupported"
}
```

### 获取所有mod环境信息
- **URL**: `/mod_environments`
- **方法**: `GET`
- **返回**: JSON格式的所有mod环境信息

### 获取特定mod的环境信息
- **URL**: `/mod_environment/<modid>`
- **方法**: `GET`
- **返回**: JSON格式的特定mod环境信息

### 手动触发备份
- **URL**: `/backup`
- **方法**: `POST`
- **说明**: 手动触发一次数据备份

## 数据存储

- 主数据文件: `data/mod_environments.json`
- 备份文件: `backups/mod_environments_YYYYMMDD.json`
- 系统会自动在每天首次数据上传时创建当天的备份
- 系统会自动清理超过30天的备份文件

## 安装和运行

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行服务器:
```bash
python app.py
```

服务器将在 `http://localhost:5000` 上运行。