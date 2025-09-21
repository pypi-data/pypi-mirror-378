# DataValidator API 文件

## 概述

`DataValidator` 是 finlab-guard 的資料驗證和變更檢測引擎，負責驗證 DataFrame 格式並執行超高效能的變更檢測。使用向量化的 pandas 操作實現了處理速度 >190,000 資料點/秒的性能。

## 核心職責

1. **格式驗證** - 確保 DataFrame 符合支援的格式
2. **變更檢測** - 區分歷史修改 vs 新增資料
3. **座標管理** - 高效處理 (row, column) 座標操作
4. **值比較** - 安全的 NaN 值比較

## 初始化

### `__init__()`

DataValidator 是無狀態的類別，不需要特殊的初始化參數。

```python
validator = DataValidator()
```

## 格式驗證

### `validate_dataframe_format(df: pd.DataFrame) -> None`

驗證 DataFrame 格式是否符合 finlab-guard 的支援範圍。

**檢查項目：**
- 確認輸入是 `pd.DataFrame` 類型
- 拒絕 MultiIndex columns (不支援)
- 拒絕 MultiIndex index (不支援)

**參數：**
- `df`: 待驗證的 DataFrame

**例外：**
- `InvalidDataTypeException`: 輸入不是 DataFrame
- `UnsupportedDataFormatException`: 包含不支援的格式

**範例：**
```python
# 支援的格式
df = pd.DataFrame({"price": [100, 101]}, index=["A", "B"])
validator.validate_dataframe_format(df)  # OK

# 不支援的格式
multi_df = pd.DataFrame(columns=pd.MultiIndex.from_tuples([("level1", "level2")]))
validator.validate_dataframe_format(multi_df)  # 拋出 UnsupportedDataFormatException
```

## 變更檢測

### `detect_changes_detailed(key: str, new_data: pd.DataFrame, cache_manager: CacheManager) -> Tuple[List[Change], List[Change]]`

核心變更檢測方法，使用超最佳化的向量化操作區分歷史修改和新增資料。

**演算法特色：**
- **向量化操作**: 使用 pandas intersection 和 difference 操作
- **座標導向**: 只處理實際存在的 (non-NaN) 座標
- **批次處理**: 避免逐一比較，大幅提升效能
- **記憶體效率**: 使用 index 操作減少資料複製

**參數：**
- `key`: 資料集識別碼
- `new_data`: 新的 DataFrame
- `cache_manager`: CacheManager 實例

**回傳：**
```python
(modifications, additions)
```
- `modifications`: 歷史資料被修改的 Change 物件列表
- `additions`: 新增資料點的 Change 物件列表

**效能指標：**
- 處理速度: >190,000 資料點/秒
- 適用規模: 100,000+ 資料點
- 變更檢測延遲: <0.5秒 (100K 資料點)

**演算法步驟：**

1. **資料預處理**
```python
new_stacked = new_data.stack()          # 只保留非 NaN 座標
existing_stacked = existing_data.stack()
```

2. **座標分析**
```python
common_coords = existing_stacked.index.intersection(new_stacked.index)  # 共同座標
new_only_coords = new_stacked.index.difference(existing_stacked.index)  # 新增座標
```

3. **向量化變更檢測**
```python
# 重新索引到共同座標
old_stacked_common = existing_stacked.reindex(common_coords)
new_stacked_common = new_stacked.reindex(common_coords)

# 向量化比較 (處理 NaN)
nan_safe_diff = (old_stacked_common != new_stacked_common) &
                ~(old_stacked_common.isna() & new_stacked_common.isna())
```

4. **批次建立 Change 物件**

## 座標管理

### `_get_coordinates(df: pd.DataFrame) -> List[Tuple]`

高效提取 DataFrame 中所有有效的 (row, column) 座標。

**最佳化機制：**
- 使用 `df.stack()` 自動過濾 NaN 值
- 直接取得座標列表，避免巢狀迴圈

**回傳：** `[(row_idx, col_idx), ...]` 座標列表

### `_get_value_at_coord(df: pd.DataFrame, row_idx, col_idx) -> any`

安全地取得指定座標的值。

**功能：**
- 邊界檢查 (index/column 存在性)
- 例外處理 (KeyError, IndexError)
- 回傳 None 表示座標不存在

## 值比較

### `_values_equal(val1, val2) -> bool`

NaN 安全的值比較方法。

**處理情況：**
1. **兩者都是 NaN**: 回傳 `True`
2. **一個是 NaN，一個不是**: 回傳 `False`
3. **兩者都不是 NaN**: 執行直接比較
4. **複雜類型**: Fallback 到字串比較

**範例：**
```python
validator._values_equal(float('nan'), float('nan'))  # True
validator._values_equal(1.0, 1)                     # True
validator._values_equal(None, float('nan'))         # False
```

## Change 物件建立

### `_create_changes_from_dataframe(df: pd.DataFrame, timestamp: datetime, is_addition: bool = True) -> List[Change]`

從 DataFrame 建立 Change 物件列表。

**參數：**
- `df`: 來源 DataFrame
- `timestamp`: 變更時間戳
- `is_addition`: True 表示新增，False 表示修改

**處理邏輯：**
- 遍歷所有座標
- 只處理非 NaN 值
- 根據 `is_addition` 設定 `old_value`

## Change 物件結構

```python
@dataclass
class Change:
    coord: Tuple[Any, Any]      # (row_index, column_name)
    old_value: Optional[Any]    # 舊值 (None for additions)
    new_value: Any              # 新值
    timestamp: datetime         # 變更時間戳
```

## 效能最佳化技術

### 1. 向量化操作
```python
# 避免: 雙重迴圈
for row in df.index:
    for col in df.columns:
        # 逐一比較

# 使用: 向量化操作
diff_mask = (old_values != new_values) & ~(old_values.isna() & new_values.isna())
changed_coords = coords[diff_mask]
```

### 2. Index 操作
```python
# 使用 pandas Index 的高效集合操作
common_coords = existing_index.intersection(new_index)      # O(n)
new_coords = new_index.difference(existing_index)          # O(n)
```

### 3. 座標過濾
```python
# 只處理實際存在的資料點
stacked = df.stack()  # 自動移除 NaN
coords = stacked.index  # 只有非 NaN 座標
```

## 使用範例

### 基本變更檢測
```python
validator = DataValidator()

# 原始資料
old_data = pd.DataFrame({"A": [1, 2], "B": [3, 4]})

# 新資料 (修改 + 新增)
new_data = pd.DataFrame({"A": [1, 5], "B": [3, 4], "C": [7, 8]})

# 檢測變更
modifications, additions = validator.detect_changes_detailed(
    "test", new_data, cache_manager
)

print(f"修改: {len(modifications)} 個座標")  # 1 個 (row=1, col=A: 2->5)
print(f"新增: {len(additions)} 個座標")     # 2 個 (C column)
```

### 格式驗證
```python
# 驗證 DataFrame 格式
try:
    validator.validate_dataframe_format(df)
    print("格式支援")
except UnsupportedDataFormatException as e:
    print(f"格式不支援: {e}")
```

### 效能監控
```python
import time

start = time.time()
modifications, additions = validator.detect_changes_detailed(key, large_df, cache_manager)
elapsed = time.time() - start

points_per_second = large_df.size / elapsed
print(f"處理速度: {points_per_second:,.0f} 點/秒")
```

## 依賴關係

- `pandas`: 核心資料操作
- `Change`: 自定義的變更物件 (來自 utils.exceptions)
- `CacheManager`: 快取管理 (注入依賴)

## 錯誤處理

所有方法都包含適當的錯誤處理：
- 型別檢查
- 邊界條件檢查
- 例外捕獲和日誌記錄
- Graceful degradation (fallback 機制)

DataValidator 是 finlab-guard 高效能的核心，確保在大型資料集上也能維持快速的變更檢測能力。