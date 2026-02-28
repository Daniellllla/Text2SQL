# Text2SQL 配送中心数据库查询

用自然语言查询配送中心数据库，基于 Qwen API 生成 SQL 并执行。

## 启动步骤

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **初始化数据库**（若尚未创建 `deliverycenter.db`）
   ```bash
   python init_db.py
   ```

3. **启动 Web 应用**
   ```bash
   python app.py
   ```

4. 浏览器打开 http://127.0.0.1:5000

## 示例问题

- 统计使用在线支付方式的订单数量
- 计算在线支付方式的平均支付手续费
- 查询配送距离最远的订单

## 安全说明

- `db_chat.py` 中的 API Key 建议改为环境变量：`os.environ.get('QWEN_API_KEY', 'your-key')`
- 仅支持 SELECT 查询，禁止 DROP、DELETE、UPDATE 等操作
