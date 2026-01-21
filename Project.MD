# Shaping Recorder 项目进度

## 项目概述
Blender 4.2+ 扩展，用于录制网格形变步骤和视口视图变化，支持插值回放和帧导出。

---

## 当前开发进度 (v3.1 - 模块拆分与国际化完善) - 阶段三进行中

### 阶段一：模块重构 (已完成)
**目标**：将单文件架构重构为模块化结构，提高代码可维护性

**已完成**：
- ✅ 拆分 `handlers.py` / `persistence.py` / `recording.py` / `playback.py`
- ✅ `operators.py` 仅保留 Operator 类与薄封装
- ✅ 旧单体 `recorder.py` 迁移到 `legacy/recorder.py`
- ✅ 现有 UI/Operator/函数接口保持不变

**文件结构变化**：
```
ShapingRecorder/
├── __init__.py              # 入口文件
├── operators.py             # Operator 薄封装
├── recording.py             # 录制流程
├── playback.py              # 回放/跳转
├── persistence.py           # 持久化
├── handlers.py              # Handlers
├── translations.py          # 国际化翻译数据
├── core/
│   ├── __init__.py
│   ├── data.py              # 序列化/反序列化
│   └── mesh_ops.py          # 网格操作和插值
└── legacy/
    └── recorder.py          # 旧单体归档
```

### 阶段二：UI布局重构 (已完成)
**目标**：优化用户界面，提升可用性

**已完成**：
- ✅ 统一录制播放按钮：将三个按钮组改为单选模式 + 一组按钮
- ✅ 边显示设置折叠：移动到步骤设置框内，支持折叠
- ✅ 默认播放模式：设置为"From Start"
- ✅ 保持所有原有功能

**UI变化**：
- 播放模式选择器：○ From Active ○ From Range ● From Start
- 统一按钮组：[Record] [Play] [Stop]
- 边显示设置：折叠在步骤设置框内

### 阶段三：国际化完善 (部分完成)
**目标**：实现完整的多语言支持

**已完成**：
- ✅ 扩展翻译字典：添加10个缺失的翻译项
- ✅ 支持13种语言：zh_HANS, zh_HANT, ja_JP, es, de_DE, fr_FR, it_IT, ko_KR, pl_PL, pt_BR, pt_PT, ru_RU, uk_UA
- ✅ 动态文本翻译：步骤编号、对象名称等
- ✅ 枚举描述翻译：播放模式选项描述

**当前状态**：
- ✅ 简体中文：Object显示和步骤列表正确，其他部分仍为英文
- 🔄 其他语言：翻译数据已准备，但未测试

**实验区域**：优先完善简体中文翻译作为测试基准

### 阶段四：录制 (recording) / 回放 (playback) 模块改善 (待启动)
**目标**：提升录制与回放稳定性、交互提示与可维护性

**当前状态**：
- ✅ 模块重构完成，复杂场景 E2E 通过
- 🔄 代码回滚至 E2E 基线，等待改进方案
- 🔄 待处理：删除步骤不回退状态
- 🔄 待处理：点/边倒角插值方向不正确
- 🔄 待处理：Loop Cut 记录分段（确认切数一次、滑动后一次）

### 阶段五：翻译系统优化 (计划中)
**目标**：解决剩余英文显示问题

**待解决**：
- 🔄 属性名称翻译（如"Step Duration"等）
- 🔄 操作符标签翻译
- 🔄 枚举项描述翻译
- 🔄 其他硬编码英文文本

**策略**：
1. 以简体中文为实验区域，逐步完善
2. 验证翻译系统工作正常后，扩展到其他语言
3. 确保所有UI文本都能正确本地化

---

## 上一轮开发进度 (v2.2 - 变动边显示功能) - 已完成

### 需求
1. 属性名从 `moving_edge` 改为 `new_edge`
2. 在 GN Spreadsheet 的 edge domain 中能看到 `new_edge` 布尔属性
3. 取消自动计算，改为用户手动标记边
4. 边需要跟随网格变形移动
5. 切换步骤时正确隐藏/显示边
6. 播放时边也要正确显示

### 最终实现方案

**核心思路**：边显示基于"源步骤"而非"目标步骤"
- 从步骤 N 变形到步骤 N+1 时，显示步骤 N 的标记边
- 变形完成后自动清除边显示
- 播放时每帧更新边坐标以跟随网格变形

**关键修改**：

1. `update_edge_draw_coords(step_index=None)` - 重构为接受步骤索引参数
2. `get_edge_indices_for_step(step_index)` - 新增辅助函数获取指定步骤的边数据
3. `on_step_select()` - 使用源步骤 (`target_idx - 1`) 的边数据
4. `start_interpolated_jump()` - 开始跳转时更新边显示，存储 `source_step_idx`
5. `jump_step()` - 网格变形时更新边坐标，完成时清除
6. `play_step()` - 步骤开始时更新边显示，插值后更新坐标，完成时清除

**行为变化**：

| 场景 | 之前 | 之后 |
|------|------|------|
| 点击步骤3 | 显示步骤3的边 | 显示步骤2的边（变形过程中） |
| 变形完成 | 边保持显示 | 边自动消失 |
| 播放时 | 边不显示 | 边跟随网格变形显示 |
| `new_edge` 属性 | 仅切换时更新 | 播放时也更新 |

---

## 已完成功能

### 核心功能
- 录制网格形变步骤（顶点、边、面变化）
- 录制视口视图状态（位置、旋转、距离）
- 录制场景摄影机状态
- 支持 Undo/Redo 检测

### 多对象支持 (v2.0)
- 不同对象可以有独立的录制记录
- 点击已录制对象自动切换面板显示
- 取消选择时保持当前面板显示
- 删除对象时自动移除该对象的记录
- 录制时锁定其他对象（hide_select=True）
- 面板顶部显示当前对象名称

### 回放功能
- 顺序播放所有步骤（带插值动画）
- 步骤列表 UIList（类似 Shape Keys）
- 点击步骤跳转（带插值动画过渡）
- Step 0 (Initial) 立即跳转（无动画）
- 播放时列表自动跟随当前步骤
- From Active 模式需选择活动步骤 (active step)，否则提示后取消

### 时间设置
- 全局设置：Camera Duration, Mesh Duration, Interpolation Steps
- 每步独立设置：Use Custom Timing, Camera Duration, Mesh Duration
- 有自定义时间的步骤在列表中显示 `*` 标记

### 删除/恢复功能
- 每个步骤（除 Step 0）有删除按钮
- 支持恢复最近一次删除的步骤
- 删除后保持列表位置不变

### 数据持久化
- 录制数据保存到 .blend 文件
- 打开文件时自动恢复数据
- 支持多对象数据格式
- 兼容旧版单对象格式（自动迁移）

### 帧导出
- 支持 Viewport 和 Final Render 模式
- 输出到 Render Properties 的输出路径
- **视频导出** (v2.1)：
  - 根据 `render.image_settings.file_format` 自动判断输出类型
  - 图片格式（PNG/JPEG等）：直接输出序列帧
  - 视频格式（FFMPEG/AVI_JPEG/AVI_RAW）：
    1. 先渲染临时 PNG 序列到 `{render.filepath}/_temp_frames/`
    2. 通过 VSE 合成视频（使用 `strips.new_image()` API）
    3. 自动清理临时文件和 VSE strip
  - 支持 VSE 状态备份/恢复（不影响用户已有的 VSE 内容）
  - UI 面板显示导出进度（当前帧数）

### 国际化 (v3.0 增强)
- 支持多语言：zh_HANS, zh_HANT, ja_JP, es, de_DE, fr_FR, it_IT, ko_KR, pl_PL, pt_BR, pt_PT, ru_RU, uk_UA
- 翻译项数量：75+ 个完整条目
- 支持动态文本翻译：步骤编号、对象名称等
- 模块化翻译管理：所有翻译数据统一在 `translations.py` 中维护

---

## 关键文件结构 (v3.1 重构后)

```
ShapingRecorder/
├── __init__.py              # 入口注册
├── operators.py             # Operator 薄封装
├── recording.py             # 录制流程
├── playback.py              # 回放/跳转
├── persistence.py           # 持久化
├── handlers.py              # Handlers
├── translations.py          # 国际化翻译数据 (75+ 翻译项)
├── core/
│   ├── __init__.py
│   ├── data.py              # 数据序列化/反序列化函数
│   └── mesh_ops.py          # 网格操作和插值函数
├── legacy/
│   └── recorder.py          # 旧单体归档
├── blender_manifest.toml
├── AGENTS.md
└── Project.MD               # 本文件
```

## 代码架构 (v3.1 重构后)

### 模块拆分
- `__init__.py`：注册入口，绑定 translations/handlers/GPU draw handler
- `operators.py`：Operator 类与薄封装
- `recording.py`：录制流程与 modal 计时器
- `playback.py`：回放/跳转/插值与 overlay 控制
- `persistence.py`：场景持久化与步序同步
- `handlers.py`：load_post/depsgraph handlers
- `legacy/recorder.py`：旧单体归档

### 核心模块 (core/)
#### data.py - 数据序列化
- `serialize_view()` / `deserialize_view()`
- `serialize_camera()` / `deserialize_camera()`
- `serialize_state()` / `deserialize_state()`

#### mesh_ops.py - 网格操作
- `get_mesh_hash()` - 计算网格哈希
- `save_mesh_state()` - 保存网格状态
- `update_mesh_vertices()` - 更新顶点位置
- `build_vertex_mapping()` - 构建顶点映射
- `compute_step_cache()` - 计算插值缓存
- `interpolate_states_cached()` - 缓存插值

### 翻译系统 (translations.py)
- **翻译项**：75+ 个完整条目
- **支持语言**：13种
- **功能**：静态文本、动态文本、枚举描述

### 全局状态变量
- `object_records` - 多对象记录字典
- `current_display_obj` - 当前显示对象名称
- `playback_mode` - 播放模式 (START/ACTIVE/RANGE)
- `show_edge_settings` - 边显示设置折叠状态
- UI 控制变量 (_edge_draw_handler, _current_edge_coords 等)

### UI 组件
- `MeshRecorderPanel` - 主面板 (重构后UI)
- `MESH_UL_recorder_steps` - 步骤列表
- `MeshRecorderSettings` - 设置属性组
- 统一操作符：`RecordUnifiedOperator`, `PlayUnifiedOperator`

### v2.2 新增全局变量 (~560)
- `_edge_draw_handler` - GPU 绘制 handler
- `_current_edge_coords` - 当前绘制的边坐标列表
- `_is_marking_edge` - 是否处于边标记模式
- `_marking_step_index` - 当前标记的步骤索引

### v2.2 当前代码状态（第二次尝试后）

**已删除的函数**：
- `get_changed_edges_obj_name()` - 已删除
- `compute_changed_edges()` - 已删除
- `get_or_create_changed_edges_object()` - 已删除
- `hide_all_changed_edge_objects()` - 已删除

**新增的函数**：
- `update_mesh_new_edge_attribute(obj, edge_indices)` - 在主网格上更新 `new_edge` 属性

**修改的函数**：
- `update_edge_draw_coords()` - 从主网格实时获取边坐标
- `on_step_select()` - 切换步骤时更新主网格属性
- `ToggleChangedEdgesOperator.execute()` - 切换时更新/清除属性
- `ConfirmEdgeOperator.execute()` - 存储顶点索引对
- `save_to_scene()` - 持久化 `marked_edges` 和 `show_edges`
- `load_from_scene()` - 加载 `marked_edges` 和 `show_edges`

### v2.2 新增属性
```python
# MeshRecorderStepItem
show_changed_edges: BoolProperty(default=False)
marked_edge_indices: StringProperty(default="")  # JSON: "[[0,1],[2,3]]"

# MeshRecorderSettings
edge_color: FloatVectorProperty(subtype='COLOR_GAMMA', size=4, default=(1,1,0,1))
edge_width: FloatProperty(default=2.0, min=1.0, max=10.0)
edge_glow: FloatProperty(default=0.0, min=0.0, max=5.0)
```

### v2.2 新增操作符
- `MarkEdgeOperator` (`mesh.mark_new_edge`) - 进入编辑模式标记边
- `ConfirmEdgeOperator` (`mesh.confirm_new_edge`) - 确认标记并退出

---

## 数据结构

### object_records 字典
```python
object_records = {
    "Cube": {
        "initial_mesh": {...},  # 初始状态
        "history": [...],       # 操作历史列表
        "redo": [],             # 重做栈
    },
    "Sphere": {
        "initial_mesh": {...},
        "history": [...],
        "redo": [],
    },
}
```

### 场景数据格式 (mesh_recorder_data)
```python
{
    "object_records": {
        "Cube": {
            "initial_mesh": {...},
            "history": [...],
        },
    },
    "current_display_obj": "Cube",
    "step_timing": {
        "Cube": [
            {"use_custom": False, "cam": 0.5, "mesh": 0.5},
            ...
        ],
    },
}
```

---

## 测试路径
- 源码：`Z:\Playground\CurrentWorking\ShapingRecorder`
- 安装位置：`C:\Users\Houpy\AppData\Roaming\Blender Foundation\Blender\5.1\scripts\addons\ShapingRecorder`

## 更新插件方式
- 复制源码到 add-on 目录后，在 Blender 中禁用/启用插件完成 reload

---

## 下一轮开发计划

### 阶段四：录制 (recording) / 回放 (playback) 模块改善
**目标**：提升录制与回放稳定性、交互提示与可维护性

**当前状态**：
- ✅ 模块重构完成，复杂场景 E2E 通过
- 🔄 代码回滚至 E2E 基线，等待改进方案
- 🔄 待处理：删除步骤不回退状态
- 🔄 待处理：点/边倒角插值方向不正确
- 🔄 待处理：Loop Cut 记录分段（确认切数一次、滑动后一次）


### 阶段五：翻译系统深度优化
**目标**：解决所有剩余英文显示问题，实现完整本地化

**当前状态**：
- ✅ 动态文本翻译：Object显示、步骤列表正确
- ✅ 静态属性翻译：Step Duration、Interpolation Steps等已修复
- ✅ 操作符标签：按钮文本已修复
- ✅ 枚举描述：枚举项描述已修复
- 🔄 属性描述翻译：tooltip 显示机制争议

**实验策略**：
1. **简体中文优先**：以zh_HANS作为实验区域，逐步完善翻译
2. **分层验证**：
   - UI文本层：标签、按钮、提示信息
   - 属性层：设置面板中的属性名称
   - 操作层：操作符标签和描述
   - 枚举层：下拉选项和单选按钮描述
3. **基准测试**：确保简体中文完全正确后，扩展到其他语言

**具体任务**：
- ✅ 完善属性名称翻译 (Property类型)
- ✅ 完善操作符标签翻译 (Operator类型)
- ✅ 完善枚举项描述翻译
- ✅ 添加缺失的UI文本翻译
- 🔄 验证翻译系统完整性

**当前争议点**：
1. **属性 description 的翻译机制**：
   - **争议**：是否应该在属性定义中使用 `iface_()` 还是纯英文字符串
   - **当前方案**：使用纯英文字符串，依赖 Blender 自动翻译 `("*", key)`
   - **备选方案**：使用 `iface_()`，查找 `("*", key)`
   - **影响**：纯字符串方案更简洁，但可能在某些情况下不生效

2. **翻译上下文的选择**：
   - **争议**：操作符 bl_label 使用 `("*", key)` 还是 `("Operator", key)`
   - **当前方案**：统一使用 `("*", key)`，因为 `iface_()` 查找全局上下文
   - **影响**：需要确保翻译字典中所有相关项都使用 `("*", key)`

3. **缺失翻译项的识别**：
   - **争议**：某些 tooltip 显示 "undocumented" 或英文，原因可能是翻译项缺失或上下文不匹配
   - **当前状态**：已添加所有已知缺失项，但可能还有未发现的
   - **验证方法**：重启 Blender，检查所有 UI 元素的 tooltip

### 开发环境
- **源码路径**：`C:\Users\Houpy\Desktop\Zed\# Blender\Extension\ShapingRecorder\ShapingRecorder\`
- **插件路径**：`C:\Users\Houpy\AppData\Roaming\Blender Foundation\Blender\5.1\extensions\user_default\shapingrecorder\`
- **测试语言**：zh_HANS (简体中文) - 实验区域

### 翻译争议总结
**核心问题**：Blender 扩展的翻译系统复杂，涉及多个上下文和调用方式的选择。

**已解决争议**：
- 属性 name/description：使用纯字符串 + `("*", key)` 翻译
- 操作符 bl_label/bl_description：使用 `iface_()` + `("*", key)` 翻译
- 枚举项：name 使用 `iface_()`，description 使用纯字符串

**待验证争议**：
- 属性 description 的 tooltip 是否正确显示中文
- 操作符 tooltip 是否消除 "undocumented"
- 是否还有其他未发现的英文文本

**下一轮尝试策略**：
1. 重启 Blender 进行全面测试
2. 检查所有属性和操作符的 tooltip
3. 如果仍有问题，考虑切换到 `iface_()` 方案
4. 记录所有发现的未翻译项并补充

### 翻译测试清单
**✅ 已完成**：
- 动态文本：`Object: {name}`, `Step {n}`, `Step {n} Settings`
- 播放模式描述：`Play/record from beginning` 等
- 基础UI文本：按钮、标签、提示信息

**🔄 待完善 (简体中文实验区)**：
- 属性名称：`Step Duration`, `Interpolation Steps`, `Start Step`, `End Step`, `File Prefix`, `Export Render Mode`, `Camera Duration`, `Mesh Duration`, `Edge Color`, `Edge Width`, `Edge Glow`
- 操作符标签：`Set Start`, `Set End`, `Mark Edge`, `Confirm`
- 枚举项：`Viewport`, `Final Render`, `Use OpenGL viewport render`, `Use scene render engine`
- 其他文本：`Use Custom Timing`, `Resetting...`, `No recorded object`

**🎯 验证标准**：
- 简体中文界面中无任何英文文本显示
- 所有按钮、标签、属性名称正确翻译
- 动态文本正确格式化
- 枚举选项正确翻译

### 版本控制
使用 jj (Jujutsu) 进行版本控制：
- `jj st` - 查看状态
- `jj log` - 查看日志
- `jj describe -m "message"` - 添加描述
- `jj new` - 创建新变更

### 翻译争议总结
**核心问题**：Blender 扩展的翻译系统复杂，涉及多个上下文和调用方式的选择。

**已解决争议**：
- 属性 name/description：使用纯字符串 + `("*", key)` 翻译
- 操作符 bl_label/bl_description：使用 `iface_()` + `("*", key)` 翻译
- 枚举项：name 使用 `iface_()`，description 使用纯字符串

**待验证争议**：
- 属性 description 的 tooltip 是否正确显示中文
- 操作符 tooltip 是否消除 "undocumented"
- 是否还有其他未发现的英文文本

**下一轮尝试策略**：
1. 重启 Blender 进行全面测试
2. 检查所有属性和操作符的 tooltip
3. 如果仍有问题，考虑切换到 `iface_()` 方案
4. 记录所有发现的未翻译项并补充
