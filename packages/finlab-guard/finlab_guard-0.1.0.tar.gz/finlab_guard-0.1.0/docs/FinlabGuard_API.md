# FinlabGuard API 文件

## 概述

`FinlabGuard` 是 finlab-guard 的主要入口類別，提供透明的 finlab 資料快取和版本控制功能。通過 monkey patching 機制攔截 `finlab.data.get()` 調用，確保回測結果的可重現性。

## 核心特色

- **透明攔截**: Monkey patch `finlab.data.get()` 不影響現有程式碼
- **變更檢測**: 自動檢測歷史資料修改並發出警告
- **時間點查詢**: 支援查看任意時間點的歷史資料
- **增量儲存**: 只儲存實際變更，節省儲存空間
- **單例模式**: 確保全域唯一的 guard 實例

## 初始化

### `__init__(cache_dir: str = "~/.finlab_guard", config: Optional[Dict[str, Any]] = None)`

初始化 FinlabGuard 實例。

**參數：**
- `cache_dir`: 快取檔案存儲目錄 (預設: `~/.finlab_guard`)
- `config`: 配置選項字典

**預設配置：**
```python
{
    "compression": "snappy",    # Parquet 壓縮演算法
    "progress_bar": True,       # 顯示進度條
    "log_level": "INFO"         # 日誌等級
}
```

**範例：**
```python
# 使用預設設定
guard = FinlabGuard()

# 自訂配置
guard = FinlabGuard(
    cache_dir="/custom/cache",
    config={"compression": "lz4", "log_level": "DEBUG"}
)
```

## 核心資料操作

### `get(key: str, force_download: bool = False) -> pd.DataFrame`

主要資料取得方法，替換原始的 `finlab.data.get()`。

**功能流程：**

1. **時間上下文檢查**: 如果設定了時間上下文，返回歷史資料
2. **資料獲取**: 從 finlab 取得最新資料
3. **格式驗證**: 驗證 DataFrame 格式
4. **變更檢測**: 比較與快取的差異
5. **儲存決策**: 根據變更類型決定儲存策略

**參數：**
- `key`: 資料集識別碼 (例如: `'price:收盤價'`)
- `force_download`: 強制下載，即使檢測到歷史修改

**回傳：** `pd.DataFrame` - 請求的資料

**例外：**
- `DataModifiedException`: 檢測到歷史資料被修改 (且 `force_download=False`)
- `FinlabConnectionException`: 無法連接到 finlab 服務

**變更處理邏輯：**

```python
if modifications:
    if force_download:
        # 儲存變更並發出警告
        self.cache_manager.save_incremental_changes(...)
        logger.warning("Historical data modified")
    else:
        # 拋出例外，要求使用者確認
        raise DataModifiedException(...)
else:
    # 正常情況：只儲存新增資料
    if additions:
        self.cache_manager.save_incremental_changes(...)
```

**使用範例：**
```python
# 正常使用
data = guard.get('price:收盤價')

# 強制下載 (忽略歷史修改警告)
data = guard.get('price:收盤價', force_download=True)
```

## 時間上下文管理

### `set_time_context(as_of_time: Optional[datetime] = None) -> None`

設定全域時間上下文，啟用歷史資料查詢模式。

**功能：**
- 所有後續的 `get()` 調用都會返回指定時間點的資料
- 支援字串自動轉換為 datetime
- 設定 None 清除時間上下文

**參數：**
- `as_of_time`: 目標時間點 (datetime 或字串)

**範例：**
```python
# 設定時間上下文
guard.set_time_context('2024-01-01 15:30:00')

# 所有 get() 調用都返回 2024-01-01 15:30:00 的資料
data1 = guard.get('price:收盤價')      # 歷史資料
data2 = guard.get('volume:成交量')     # 歷史資料
data3 = guard.get('financial:營收')   # 歷史資料

# 清除時間上下文
guard.clear_time_context()
data4 = guard.get('price:收盤價')      # 最新資料
```

### `clear_time_context() -> None`

清除時間上下文，回到正常模式。

### `get_time_context() -> Optional[datetime]`

取得當前的時間上下文設定。

## Monkey Patching 管理

### `install_patch() -> None`

安裝 monkey patch，攔截 `finlab.data.get()` 調用。

**功能：**
- 保存原始的 `finlab.data.get` 函數
- 設定全域單例實例
- 替換 `finlab.data.get` 為 patched 版本
- 防止重複安裝

**安全機制：**
- 檢查是否已安裝 patch
- 驗證 finlab 套件存在
- 單例模式確保唯一性

**例外：**
- `RuntimeError`: 已安裝或重複安裝
- `ImportError`: finlab 套件未找到

**範例：**
```python
guard = FinlabGuard()
guard.install_patch()

# 現在所有 finlab.data.get() 調用都會被攔截
import finlab.data
data = finlab.data.get('price:收盤價')  # 透過 guard.get() 處理
```

### `remove_patch() -> None`

移除 monkey patch，恢復原始的 `finlab.data.get()`。

**功能：**
- 恢復原始函數
- 清除全域實例
- 安全的錯誤處理

### `_fetch_from_finlab(key: str) -> pd.DataFrame`

內部方法：從 finlab 取得原始資料。

**功能：**
- 優先使用保存的原始函數 (`_original_get`)
- Fallback 到直接調用 (未 patch 時)
- 處理 finlab 套件缺失

## 時間戳管理

### `generate_unique_timestamp(key: str) -> datetime`

產生唯一的時間戳，避免衝突。

**功能：**
- 檢查指定 key 的現有時間戳
- 如果當前時間已存在，自動加 1 秒
- 確保時間戳的唯一性

**使用場景：**
- 同一秒內多次儲存同一 dataset
- 確保版本控制的正確性

**範例：**
```python
# 假設快取中最新時間是 2024-01-01 10:00:00
timestamp1 = guard.generate_unique_timestamp('test')  # 2024-01-01 10:00:01
timestamp2 = guard.generate_unique_timestamp('test')  # 2024-01-01 10:00:02
```

## 快取管理

### `clear_cache(key: Optional[str] = None) -> None`

清除快取資料。

**參數：**
- `key`: 指定的資料集 (None 表示清除全部)

**範例：**
```python
# 清除特定資料集
guard.clear_cache('price:收盤價')

# 清除所有快取
guard.clear_cache()
```

### `get_change_history(key: str) -> pd.DataFrame`

取得資料變更歷史。

**回傳：** 包含變更統計的 DataFrame

### `get_storage_info(key: Optional[str] = None) -> Dict[str, Any]`

取得儲存空間使用資訊。

**回傳：** 儲存資訊字典

## 全域單例機制

```python
_global_guard_instance: Optional['FinlabGuard'] = None
```

**特色：**
- 確保只有一個 FinlabGuard 實例可以安裝 patch
- 防止多個實例間的衝突
- 線程安全的設計

**使用場景：**
```python
# 第一次安裝 - 成功
guard1 = FinlabGuard()
guard1.install_patch()  # OK

# 第二次安裝 - 失敗
guard2 = FinlabGuard()
guard2.install_patch()  # RuntimeError: already installed

# 必須先移除
guard1.remove_patch()
guard2.install_patch()  # 現在可以
```

## 完整使用範例

### 基本設定和使用
```python
import finlab_guard

# 方法 1: 便利函數 (自動安裝 patch)
guard = finlab_guard.install()

# 方法 2: 手動安裝
guard = FinlabGuard()
guard.install_patch()

# 正常使用 finlab (透明攔截)
import finlab.data
data = finlab.data.get('price:收盤價')  # 自動快取
```

### 歷史資料查詢
```python
# 設定時間點查詢
guard.set_time_context('2024-01-01 15:30:00')

# 查詢歷史資料
historical_price = finlab.data.get('price:收盤價')
historical_volume = finlab.data.get('volume:成交量')

# 回到現在
guard.clear_time_context()
current_data = finlab.data.get('price:收盤價')
```

### 錯誤處理
```python
try:
    data = finlab.data.get('price:收盤價')
except DataModifiedException as e:
    print(f"歷史資料被修改: {len(e.changes)} 個變更")

    # 選項 1: 強制下載
    data = finlab.data.get('price:收盤價', force_download=True)

    # 選項 2: 檢查變更詳情
    for change in e.changes:
        print(f"座標 {change.coord}: {change.old_value} -> {change.new_value}")
```

### 效能監控
```python
# 檢查儲存使用
storage_info = guard.get_storage_info()
print(f"總快取大小: {storage_info['total_size']:,} bytes")

# 檢查變更歷史
history = guard.get_change_history('price:收盤價')
print(f"變更次數: {len(history)}")
```

### 清理和移除
```python
# 清除快取
guard.clear_cache('price:收盤價')  # 特定資料集
guard.clear_cache()               # 全部清除

# 移除 monkey patch
guard.remove_patch()
```

## 配置選項

### 支援的配置參數

```python
config = {
    "compression": "snappy",        # 壓縮演算法: snappy, lz4, gzip
    "progress_bar": True,           # 顯示進度條
    "log_level": "INFO",            # 日誌等級: DEBUG, INFO, WARNING, ERROR
}
```

### 環境變數支援

```bash
export FINLAB_GUARD_CACHE_DIR="/custom/cache/dir"
export FINLAB_GUARD_LOG_LEVEL="DEBUG"
```

## 整合和相容性

### 與 finlab 的整合
- 完全透明：不需要修改現有程式碼
- 向後相容：可以隨時移除 patch
- 錯誤隔離：guard 錯誤不影響 finlab 功能

### 多環境支援
- 支援 Python 3.9+
- 跨平台：Windows/Linux/macOS
- 容器友善：支援 Docker 部署

FinlabGuard 提供了強大而透明的資料版本控制功能，確保 finlab 資料的可重現性和一致性。