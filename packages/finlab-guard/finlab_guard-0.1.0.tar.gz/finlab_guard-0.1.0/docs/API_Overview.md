# finlab-guard API 總覽

## 概述

finlab-guard 是一個輕量級的 Python 套件，為 finlab 資料提供透明的本地快取和版本控制功能。確保回測結果的可重現性，當 finlab 資料被修改時提供檢測、警告與復原能力。

## 架構概覽

```
finlab-guard/
├── FinlabGuard          # 主要入口類別 - 使用者介面
├── CacheManager         # 快取管理 - 資料存儲引擎
├── DataValidator        # 變更檢測 - 高效能比較引擎
└── utils/
    ├── exceptions.py    # 自定義例外和資料結構
    └── ...
```

## 快速開始

### 安裝和基本使用

```python
import finlab_guard

# 一行安裝 - 自動設定 monkey patch
guard = finlab_guard.install()

# 現在正常使用 finlab，會自動快取
import finlab.data
data = finlab.data.get('price:收盤價')  # 自動快取和版本控制
```

### 手動控制

```python
from finlab_guard import FinlabGuard

# 手動初始化
guard = FinlabGuard(cache_dir="/custom/cache")
guard.install_patch()

# 使用完畢後清理
guard.remove_patch()
```

## 核心功能

### 1. 透明資料快取

```python
# 第一次調用 - 從 finlab 下載並快取
data1 = finlab.data.get('price:收盤價')

# 後續調用 - 自動檢測變更
data2 = finlab.data.get('price:收盤價')  # 快速回傳，檢測變更
```

### 2. 歷史資料修改檢測

```python
try:
    data = finlab.data.get('price:收盤價')
except DataModifiedException as e:
    print(f"檢測到 {len(e.changes)} 個歷史資料修改")

    # 選擇處理方式
    data = finlab.data.get('price:收盤價', force_download=True)  # 強制下載
```

### 3. 時間點查詢

```python
# 設定時間上下文
guard.set_time_context('2024-01-01 15:30:00')

# 所有後續調用都返回該時間點的資料
price_historical = finlab.data.get('price:收盤價')
volume_historical = finlab.data.get('volume:成交量')

# 清除時間上下文
guard.clear_time_context()
price_current = finlab.data.get('price:收盤價')  # 最新資料
```

## 核心類別 API

### FinlabGuard - 主要介面

| 方法 | 功能 | 回傳 |
|------|------|------|
| `__init__(cache_dir, config)` | 初始化 guard 實例 | - |
| `get(key, force_download)` | 取得資料 (替代 finlab.data.get) | `pd.DataFrame` |
| `install_patch()` | 安裝 monkey patch | - |
| `remove_patch()` | 移除 monkey patch | - |
| `set_time_context(datetime)` | 設定歷史查詢時間點 | - |
| `clear_time_context()` | 清除時間上下文 | - |
| `clear_cache(key)` | 清除快取 | - |
| `get_change_history(key)` | 取得變更歷史 | `pd.DataFrame` |
| `get_storage_info(key)` | 取得儲存資訊 | `Dict` |

### CacheManager - 快取引擎

| 方法 | 功能 | 回傳 |
|------|------|------|
| `save_data(key, data, timestamp)` | 儲存完整資料 | - |
| `save_incremental_changes(...)` | 增量儲存變更 | - |
| `load_data(key, as_of_time)` | 載入資料 | `pd.DataFrame` |
| `exists(key)` | 檢查快取存在 | `bool` |
| `clear_key(key)` | 清除指定快取 | - |
| `clear_all()` | 清除所有快取 | - |

### DataValidator - 變更檢測

| 方法 | 功能 | 回傳 |
|------|------|------|
| `validate_dataframe_format(df)` | 驗證 DataFrame 格式 | - |
| `detect_changes_detailed(...)` | 檢測詳細變更 | `(modifications, additions)` |

## 資料結構

### Change 物件

```python
@dataclass
class Change:
    coord: Tuple[Any, Any]      # (row_index, column_name)
    old_value: Optional[Any]    # 舊值 (None for additions)
    new_value: Any              # 新值
    timestamp: datetime         # 變更時間戳
```

### 配置選項

```python
default_config = {
    "compression": "snappy",        # Parquet 壓縮: snappy, lz4, gzip
    "progress_bar": True,           # 顯示進度條
    "log_level": "INFO",            # 日誌等級: DEBUG, INFO, WARNING, ERROR
}
```

## 例外處理

### 主要例外類型

```python
# 歷史資料被修改
try:
    data = guard.get('price:收盤價')
except DataModifiedException as e:
    print(f"修改數量: {len(e.changes)}")
    for change in e.changes:
        print(f"{change.coord}: {change.old_value} -> {change.new_value}")

# finlab 連線問題
except FinlabConnectionException as e:
    print(f"無法連接 finlab: {e}")

# 不支援的資料格式
except UnsupportedDataFormatException as e:
    print(f"資料格式不支援: {e}")
```

## 進階功能

### 增量儲存效率

```python
# 自動使用增量儲存
# - 只儲存實際變更的資料點
# - 大幅節省儲存空間 (50-90%)
# - 保持完整版本控制

data_modified = original_data.copy()
data_modified.loc['2330.TW', '2024-01-01'] = 105  # 只修改一個值

# guard 自動檢測並只儲存這一個變更
guard.get('price:收盤價')  # 增量儲存
```

### dtype 精確保留

```python
# 完美保留所有資料類型
original = pd.DataFrame({
    'int32_col': np.array([1, 2, 3], dtype='int32'),
    'float32_col': np.array([1.1, 2.2, 3.3], dtype='float32'),
    'bool_col': np.array([True, False, True], dtype='bool')
})

# 儲存和載入後，dtypes 完全相同
guard.cache_manager.save_data('test', original, datetime.now())
reconstructed = guard.cache_manager.load_data('test')

assert original.dtypes.equals(reconstructed.dtypes)  # True
```

### 儲存空間監控

```python
# 取得詳細儲存資訊
storage_info = guard.get_storage_info()

print(f"總快取大小: {storage_info['total_size']:,} bytes")

for key, info in storage_info.items():
    if key != 'total_size':
        print(f"{key}: {info['file_size']:,} bytes, {info['record_count']} records")
```

## 效能指標

### 變更檢測效能
- **處理速度**: >190,000 資料點/秒
- **適用規模**: 100,000+ 資料點
- **檢測延遲**: <0.5秒 (100K 資料點)

### 儲存效率
- **dtype 儲存**: 99.90% 空間節省
- **增量儲存**: 50-90% 空間節省 (依變更率而定)
- **壓縮比率**: ~60% (使用 snappy 壓縮)

### 記憶體使用
- **輕量級**: 最小記憶體 overhead
- **串流處理**: 大檔案支援
- **原子性**: 確保資料完整性

## 檔案結構

### 快取檔案組織

```
~/.finlab_guard/
├── price_收盤價.parquet           # 主要資料檔案
├── price_收盤價_dtypes.json       # dtype mapping
├── volume_成交量.parquet          # 另一個資料集
├── volume_成交量_dtypes.json      # 對應的 dtype
└── ...
```

### dtype mapping 範例（Versioned）

```json
{
  "schema_version": "1.0",
  "last_updated": "2025-09-20T09:28:55.747991",
  "dtype_history": [
    {
      "timestamp": "2024-01-01T10:00:00",
      "dtypes": {
        "2330.TW": "float32",
        "2454.TW": "float32"
      },
      "index_dtype": "object",
      "columns_dtype": "object",
      "index_name": "stock_code",
      "columns_name": "date",
      "columns_order": ["2330.TW", "2454.TW"],
      "index_order": ["2024-01-01", "2024-01-02"]
    },
    {
      "timestamp": "2024-02-01T15:30:00",
      "dtypes": {
        "2330.TW": "float64",  // finlab changed dtype!
        "2454.TW": "float64",
        "3008.TW": "float64"   // new stock added
      },
      "index_dtype": "object",
      "columns_dtype": "object",
      "index_name": "stock_code",
      "columns_name": "date",
      "columns_order": ["2330.TW", "2454.TW", "3008.TW"],
      "index_order": ["2024-01-01", "2024-01-02", "2024-02-01"]
    }
  ]
}
```

## 最佳實務

### 1. 初始化建議

```python
# 推薦：使用便利函數
guard = finlab_guard.install()

# 或自訂配置
guard = finlab_guard.install(
    cache_dir="/ssd/finlab_cache",  # 使用 SSD 提升效能
    config={"compression": "lz4"}   # 更快的壓縮
)
```

### 2. 錯誤處理模式

```python
def safe_get_data(key: str, retry_on_change: bool = True):
    """安全的資料取得函數"""
    try:
        return finlab.data.get(key)
    except DataModifiedException as e:
        if retry_on_change:
            logger.warning(f"Historical data changed for {key}, force downloading")
            return finlab.data.get(key, force_download=True)
        else:
            raise
    except FinlabConnectionException:
        logger.error(f"Cannot connect to finlab for {key}")
        # 嘗試從快取取得最新資料
        return guard.cache_manager.get_latest_data(key)
```

### 3. 批次歷史查詢

```python
def get_historical_portfolio(date: str, symbols: List[str]):
    """取得指定日期的投資組合資料"""
    guard.set_time_context(date)

    try:
        portfolio_data = {}
        for symbol in symbols:
            portfolio_data[symbol] = finlab.data.get(f'price:{symbol}')
        return portfolio_data
    finally:
        guard.clear_time_context()  # 確保清理
```

### 4. 效能監控

```python
def monitor_cache_performance():
    """監控快取效能"""
    storage_info = guard.get_storage_info()

    total_size_mb = storage_info['total_size'] / (1024 * 1024)
    print(f"快取使用空間: {total_size_mb:.1f} MB")

    if total_size_mb > 1000:  # 超過 1GB
        print("考慮清理舊快取或調整壓縮設定")
```

## 整合指南

### 與現有專案整合

```python
# 在專案開始時安裝
def setup_finlab_guard():
    import finlab_guard

    # 根據環境變數或配置檔設定
    cache_dir = os.getenv('FINLAB_CACHE_DIR', '~/.finlab_guard')

    guard = finlab_guard.install(cache_dir=cache_dir)

    # 設定日誌
    logging.getLogger('finlab_guard').setLevel(logging.INFO)

    return guard

# 在專案結束時清理
def cleanup_finlab_guard(guard):
    guard.remove_patch()
```

### Docker 部署

```dockerfile
# Dockerfile
ENV FINLAB_GUARD_CACHE_DIR=/app/cache
VOLUME ["/app/cache"]

# 確保快取目錄有適當權限
RUN mkdir -p /app/cache && chown app:app /app/cache
```

### 測試環境配置

```python
# 測試時使用臨時快取
import tempfile

def test_with_clean_cache():
    with tempfile.TemporaryDirectory() as temp_dir:
        guard = FinlabGuard(cache_dir=temp_dir)
        guard.install_patch()

        try:
            # 執行測試
            yield guard
        finally:
            guard.remove_patch()
```

finlab-guard 提供了完整而高效的資料版本控制解決方案，確保您的 finlab 回測結果具有完美的可重現性。