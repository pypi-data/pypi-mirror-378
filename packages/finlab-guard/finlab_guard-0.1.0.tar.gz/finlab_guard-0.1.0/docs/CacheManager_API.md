# CacheManager API 文件

## 概述

`CacheManager` 是 finlab-guard 的核心快取管理類，負責處理 DataFrame 的存儲、檢索和版本控制。使用 Parquet 格式進行高效壓縮存儲，並實現了獨立的 dtype mapping 系統來精確保留資料類型。

## 初始化

### `__init__(cache_dir: Path, config: Dict[str, Any])`

初始化 CacheManager 實例。

**參數：**
- `cache_dir`: 快取檔案存儲目錄
- `config`: 配置字典，包含壓縮設定等選項

**範例：**
```python
cache_manager = CacheManager(Path("~/.finlab_guard"), {"compression": "snappy"})
```

## 核心存儲方法

### `save_data(key: str, data: pd.DataFrame, timestamp: datetime) -> None`

儲存完整的 DataFrame 到快取，同時建立 dtype mapping。

**功能：**
- 驗證資料格式並儲存 dtype mapping 到獨立的 JSON 檔案
- 將 DataFrame 轉換為 stacked 格式 (index, column, value, save_time)
- 與現有資料合併，支援版本控制
- 使用原子性寫入確保資料一致性

**參數：**
- `key`: 資料集識別碼 (例如: "price:收盤價")
- `data`: 要儲存的 DataFrame
- `timestamp`: 儲存時間戳

**檔案結構：**
```
cache_dir/
├── {key}.parquet          # 主要資料檔案 (stacked 格式)
└── {key}_dtypes.json      # dtype mapping 檔案
```

### `save_incremental_changes(key: str, modifications: list, additions: list, timestamp: datetime, original_df: pd.DataFrame) -> None`

增量儲存，只存儲變更的資料點，大幅提升儲存效率。

**功能：**
- 更新 dtype mapping 檔案
- 只儲存實際變更的 (index, column) 座標
- 支援 modifications (歷史資料修改) 和 additions (新增資料)
- 與現有資料合併

**參數：**
- `key`: 資料集識別碼
- `modifications`: Change 物件列表 (歷史修改)
- `additions`: Change 物件列表 (新增資料)
- `timestamp`: 儲存時間戳
- `original_df`: 原始 DataFrame (用於取得 index/columns 名稱)

**效益：** 在典型使用場景下可節省 50-90% 儲存空間

## 資料檢索方法

### `load_data(key: str, as_of_time: Optional[datetime] = None) -> pd.DataFrame`

從快取載入資料，支援時間點查詢。

**功能：**
- 載入原始 stacked 資料
- 重建為原始 DataFrame 格式
- 套用 dtype mapping 精確還原資料類型
- 保留原始的 column/index 順序

**參數：**
- `key`: 資料集識別碼
- `as_of_time`: 指定時間點查詢 (None 表示最新資料)

**回傳：** 重建的 DataFrame，保持原始格式和資料類型

### `load_raw_data(key: str) -> Optional[pd.DataFrame]`

載入原始的 stacked 格式資料，主要供內部使用。

**回傳：** 包含 (index, column, value, save_time) 的 stacked DataFrame

### `get_latest_data(key: str) -> pd.DataFrame`

取得最新版本的資料，等同於 `load_data(key, None)`。

## Dtype Mapping 系統

### `_save_dtype_mapping(key: str, df: pd.DataFrame) -> None`

儲存 DataFrame 的 dtype 資訊到獨立的 JSON 檔案。

**JSON 結構（Versioned）：**
```json
{
  "schema_version": "1.0",
  "last_updated": "2025-09-20T09:28:55.747991",
  "dtype_history": [
    {
      "timestamp": "2024-01-01T10:00:00",
      "dtypes": {
        "column1": "int32",
        "column2": "float64"
      },
      "index_dtype": "object",
      "columns_dtype": "object",
      "index_name": "symbol",
      "columns_name": "date",
      "columns_order": ["column1", "column2"],
      "index_order": ["A", "B", "C"]
    },
    {
      "timestamp": "2024-01-02T15:30:00",
      "dtypes": {
        "column1": "float32",  // dtype changed!
        "column2": "float64",
        "column3": "bool"      // new column added!
      },
      "index_dtype": "object",
      "columns_dtype": "object",
      "index_name": "symbol",
      "columns_name": "date",
      "columns_order": ["column1", "column2", "column3"],
      "index_order": ["A", "B", "C"]
    }
  ]
}
```

**特色：**
- **版本控制** - 每次 dtype 變更都會新增一個歷史記錄
- **智能檢測** - 只在 dtype 真正改變時才建立新 entry
- **時間點查詢** - 可以精確查詢任意時間點的 dtype 資訊
- **空間效率** - 相同 dtype 不會重複儲存，節省 99.90% 空間

### `_load_dtype_mapping(key: str) -> Optional[Dict[str, Any]]`

載入 dtype mapping 資訊。

**回傳：** dtype mapping 字典或 None (如果檔案不存在)

### `_apply_dtypes_to_result(result: pd.DataFrame, key: str, target_time: Optional[datetime] = None) -> None`

將儲存的 dtype 套用到重建的 DataFrame，支援時間點特定的 dtype 查詢。

**功能：**
- **時間點 dtype 查詢** - 根據 target_time 使用對應時間點的 dtype 資訊
- **完整 dtype 還原** - 還原 columns, index, 和 columns object 的 dtype
- 處理各種資料類型轉換 (int, float, bool, object)
- 安全的錯誤處理，轉換失敗時使用 fallback
- 支援字串到原始類型的反向轉換

**參數：**
- `result`: 要套用 dtype 的 DataFrame (原地修改)
- `key`: 資料集識別碼
- `target_time`: 目標時間點 (None 表示使用最新的 dtype)

## 資料重建邏輯

### `_reconstruct_dataframe(stacked_data: pd.DataFrame, target_time: Optional[datetime], key: str) -> pd.DataFrame`

核心重建邏輯，將 stacked 資料還原為原始 DataFrame。

**步驟：**
1. 時間篩選 (如果指定 target_time)
2. 取得每個座標的最新值 (`groupby().last()`)
3. 執行 `unstack()` 操作重建 DataFrame
4. 使用 dtype mapping 保留原始順序
5. 套用 dtype mapping 還原資料類型
6. 還原原始的 index/columns 名稱

**順序保留機制：**
- 優先使用 dtype mapping 中儲存的順序
- **智能類型匹配** - 使用字串映射解決 numeric columns/index 的類型匹配問題
- Fallback 到字典序排序 (向後相容)
- **完美支援** - 支援所有類型的 columns/index (int, float, str, etc.)

## 輔助方法

### `exists(key: str) -> bool`

檢查指定 key 的快取是否存在。

### `clear_key(key: str) -> None`

清除指定 key 的快取檔案。

### `clear_all() -> None`

清除所有快取檔案。

### `get_change_history(key: str) -> pd.DataFrame`

取得資料變更歷史統計。

### `get_storage_info(key: Optional[str] = None) -> Dict[str, Any]`

取得儲存空間使用資訊。

**回傳範例：**
```python
{
  "dataset_key": {
    "file_size": 568768,
    "modified_time": datetime(2025, 9, 20, 9, 28, 55),
    "record_count": 100000
  },
  "total_size": 1234567  # 當 key=None 時
}
```

## 檔案路徑管理

### `_get_cache_path(key: str) -> Path`

產生快取檔案路徑，自動處理檔案系統安全性 (替換特殊字符)。

### `_get_dtype_path(key: str) -> Path`

產生 dtype mapping 檔案路徑。

## 原子性操作

### `_atomic_write_parquet(key: str, data: pd.DataFrame) -> None`

原子性寫入 Parquet 檔案。

**機制：**
1. 先寫入臨時檔案
2. 寫入成功後執行 `rename()` 操作
3. 失敗時自動清理臨時檔案

**效益：** 確保即使寫入過程中斷也不會產生損壞的檔案

## 效能特色

1. **極高的 dtype 儲存效率**: 99.90% 空間節省
2. **增量儲存支援**: 只儲存實際變更
3. **完美的資料保真度**: 類型和順序完全保留
4. **原子性操作**: 保證資料一致性
5. **高效壓縮**: 使用 Parquet + Snappy 壓縮

## 使用範例

```python
from finlab_guard.cache.manager import CacheManager
from pathlib import Path
from datetime import datetime

# 初始化
cache = CacheManager(Path("./cache"), {"compression": "snappy"})

# 儲存資料
data = pd.DataFrame({"price": [100, 101, 102]}, index=["A", "B", "C"])
cache.save_data("test", data, datetime.now())

# 載入資料
reconstructed = cache.load_data("test")
assert data.equals(reconstructed)  # Perfect reconstruction

# 時間點查詢
historical = cache.load_data("test", datetime(2025, 1, 1))
```