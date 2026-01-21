# Shaping Recorder 重构实施计划 (Implement Plan)

## 元信息 (Metadata)
| 项 | 值 |
| --- | --- |
| 目标仓库路径 | `Z:\Playground\CurrentWorking\ShapingRecorder` |
| 源仓库路径 | `Z:\Playground\CurrentWorking\ShapingRecorderDev` |
| 插件类型 | Blender 扩展 (Blender Add-on) |
| 运行版本 | Blender 4.2+ |
| 调试方式 | WebSocket 调试 (WebSocket) + 代码注入 + 截屏 |
| 端到端测试 | 仅必要时由用户手动执行 |
| 语言 | 简体中文 (UI 文本已国际化) |

## 当前文件与职责 (File Map)
| 文件 | 角色 | 备注 |
| --- | --- | --- |
| `__init__.py` | 注册入口 | 注册类、translations、handlers、GPU draw handler |
| `state.py` | 全局状态 | recording/playback 状态与缓存、UI 控制变量 |
| `properties.py` | 属性组 | `MeshRecorderSettings`、`MeshRecorderStepItem`、`on_step_select()` |
| `ui.py` | UI 面板 | 列表、按钮、设置区布局 |
| `graphics.py` | GPU 辅助 | 高亮边绘制、`new_edge` 属性更新 |
| `view_utils.py` | 视口/相机 | 视口/相机状态保存、应用、插值、锁定 |
| `export_utils.py` | 导出 | 视口/最终渲染帧导出、视频合成 (VSE) |
| `handlers.py` | Handlers | `load_post_handler`/`depsgraph_update_handler` |
| `persistence.py` | 持久化 | `save_to_scene`/`load_from_scene`/`sync_step_list` |
| `recording.py` | 录制 | `MeshRecorderModal`/`start_recording`/`stop_recording` |
| `playback.py` | 回放 | `play_forward`/`play_step`/`jump_*`/`stop_playing` |
| `operators.py` | Operator 封装 | 仅保留 Operator 类与薄封装 |
| `core/data.py` | 序列化 (serialization) | view/camera/state 序列化/反序列化 |
| `core/mesh_ops.py` | 网格操作 | hash、保存状态、插值缓存与插值 |
| `translations.py` | 国际化 (i18n) | 多语言字典 |
| `legacy/recorder.py` | 旧单体 | 归档备查 |

## 关键全局状态 (Global State)
| 变量 | 含义 | 位置 |
| --- | --- | --- |
| `object_records` | 多对象记录字典 | `state.py` |
| `current_display_obj` | 当前显示对象 | `state.py` |
| `redo_history` | redo 栈 | `state.py` |
| `is_recording / is_playing` | 录制/回放状态 | `state.py` |
| `current_step / interp_progress` | 回放步骤与进度 | `state.py` |
| `_step_cache` | 插值缓存 | `state.py` |
| `_playback_start_idx / _playback_end_idx` | 回放范围 | `state.py` |
| `_jump_state` | 跳转状态 | `state.py` |
| `_edge_draw_handler / _current_edge_coords` | 边绘制 | `state.py` |
| `_is_marking_edge / _marking_step_index` | 标记边模式 | `state.py` |
| `_is_exporting_frames / _render_frame_idx` | 导出状态 | `state.py` |

## 关键数据结构 (Data Structures)
| 名称 | 形态 | 说明 |
| --- | --- | --- |
| `object_records` | `dict[str, {initial_mesh, history, redo}]` | 每对象一套历史 |
| `step_items` | CollectionProperty | 每步 timing + edge 标记 |
| `marked_edge_indices` | JSON 字符串 | `[[v0, v1], ...]` |
| `mesh_recorder_data` | JSON 字符串 | 保存到 `scene` 自定义属性 |

```json
{
  "object_records": {
    "Cube": {
      "initial_mesh": {"verts": [], "edges": [], "faces": [], "view": {}, "camera": {}, "hash": 123},
      "history": ["..."]
    }
  },
  "current_display_obj": "Cube",
  "step_timing": {
    "Cube": [
      {"use_custom": false, "cam": 0.5, "mesh": 0.5, "marked_edges": "[]", "show_edges": false}
    ]
  }
}
```

## 核心流程 (Core Flow)
| 流程 | 入口 | 关键步骤 |
| --- | --- | --- |
| 录制 (recording) | `start_recording()` | 设置目标对象 -> `MeshRecorderModal` 定时检测 hash -> 记录状态 -> `stop_recording()` 保存到 scene |
| 回放 (playback) | `play_forward()` | 计算范围 -> 设初始状态 -> timer 触发 `play_step()` -> 插值更新 -> `stop_playing()` |
| 步骤跳转 | `on_step_select()` | 选择目标步 -> `start_interpolated_jump()` -> timer `jump_step()` |
| 高亮边 | `get_edge_indices_for_step()` | 更新 `new_edge` 属性与 GPU 绘制缓存 |

## 现有接口保持清单 (Interface Invariants)
| 类型 | 名称 | 说明 |
| --- | --- | --- |
| 函数 | `start_recording()` / `stop_recording()` | 录制流程外部入口 |
| 函数 | `play_forward()` / `play_step()` / `stop_playing()` | 回放主流程 |
| 函数 | `start_interpolated_jump()` / `jump_step()` | 步骤跳转流程 |
| 函数 | `save_to_scene()` / `load_from_scene()` | 数据持久化 |
| Operator | `mesh.recorder_modal` | 录制计时器 |
| Operator | `mesh.start_recording` / `mesh.stop_recording` | 录制控制 |
| Operator | `mesh.play_unified` / `mesh.record_unified` / `mesh.stop_playing` | 回放与导出 |
| Operator | `mesh.delete_recorder_step` / `mesh.restore_recorder_step` | 步骤删除/恢复 |
| Operator | `mesh.reset_step_view` / `mesh.confirm_step_view` | 视口重设 |
| Operator | `mesh.set_start_step` / `mesh.set_end_step` | 回放范围 |
| Operator | `mesh.toggle_changed_edges` / `mesh.mark_new_edge` / `mesh.confirm_new_edge` | 高亮边 |
| Operator | `mesh.play_from_active` / `mesh.play_from_range` / `mesh.play_from_start` | 兼容旧入口 |
| Operator | `mesh.record_from_active` / `mesh.record_from_range` / `mesh.record_from_start` | 兼容旧入口 |

## 主要问题 (Issues)
| 问题 | 影响 |
| --- | --- |
| `operators.py` 逻辑过度集中 | 难以替换回放/插值策略 |
| 录制、回放、持久化、handlers 混在一起 | 可维护性差，难定向优化 |
| `recorder.py` 旧单体 | 容易误用与分叉 |
| 回放核心逻辑分散 | 难定位几何回放问题 |

## 重构目标 (Goals)
| 目标 | 说明 |
| --- | --- |
| 结构拆分 | 将 recording/playback/persistence/handlers 独立模块化 |
| 接口不变 | 现有 UI/Operator/函数名完全保持 |
| 聚焦改进 | 后续只针对 playback/interpolation 做持续优化 |

## 目标结构 (Target Structure)
```text
ShapingRecorder/
├── __init__.py
├── state.py
├── properties.py
├── ui.py
├── translations.py
├── graphics.py
├── view_utils.py
├── export_utils.py
├── handlers.py
├── persistence.py
├── recording.py
├── playback.py
├── operators.py
├── core/
│   ├── data.py
│   ├── mesh_ops.py
│   └── interpolation.py   # 可选：后续拆分
├── legacy/
│   └── recorder.py
└── docs/
    ├── AGENTS.md
    ├── CODE_OF_CONDUCT.md
    ├── CONTRIBUTING.md
    ├── Project.MD
    ├── implementplan.md
    └── instruct.md
```

## 实施步骤 (Step Plan)
| 步骤 | 动作 | 影响文件 | 目标输出 | 测试方式 |
| --- | --- | --- | --- | --- |
| 0 | 复制 `ShapingRecorderDev` 到 `ShapingRecorder`，排除 `.jj`/`__pycache__` | 全部 | 新工作目录 | 无 |
| 1 | `git init`，提交基线 | 全部 | 基线可回滚 | 无 |
| 2 | 新增 `handlers.py`，迁移 `load_post_handler`/`depsgraph_update_handler` | `operators.py` -> `handlers.py` | handlers 独立 | WebSocket |
| 3 | 新增 `persistence.py`，迁移 `save_to_scene`/`load_from_scene`/`sync_step_list` | `operators.py` -> `persistence.py` | 持久化独立 | WebSocket |
| 4 | 新增 `recording.py`，迁移 `MeshRecorderModal`/`start_recording`/`stop_recording` | `operators.py` -> `recording.py` | 录制独立 | WebSocket |
| 5 | 新增 `playback.py`，迁移 `play_forward`/`play_step`/`jump_*`/`stop_playing` | `operators.py` -> `playback.py` | 回放独立 | WebSocket |
| 6 | `operators.py` 仅保留 Operator 类和薄封装 | `operators.py` | 结构清晰 | WebSocket |
| 7 | `recorder.py` 移入 `legacy/` | `recorder.py` | 避免误用 | 无 |
| 8 | 回归测试全流程 | 全部 | 功能等价 | WebSocket + 用户必要时手动 |

## 执行状态 (Status)
- 步骤 0-8 已完成，重构通过
- WebSocket 快检与手动 E2E 通过
- 当前代码回滚至 E2E 基线，等待录制/回放改进启动

## WebSocket 调试流程 (WebSocket Workflow)
| 动作 | 目的 |
| --- | --- |
| 注入代码并 reload addon | 快速验证重构是否破坏注册 |
| 捕获异常堆栈 | 定位回放/录制问题 |
| 截屏对比 | 验证 UI 与回放结果 |

## 测试清单 (Test Checklist)
| 类型 | 场景 | 说明 |
| --- | --- | --- |
| WebSocket | 录制基本操作 | 顶点移动、挤出、倒角、环切 |
| WebSocket | 回放模式 | From Start / From Selected / By Range |
| WebSocket | 步骤跳转 | Step 0 与中间步骤 |
| WebSocket | 高亮边 | 标记 -> 播放 -> 自动更新 |
| WebSocket | 导出 | Viewport / Final Render |
| 手动 E2E | 复杂场景 | 仅在 WebSocket 无法确认时执行 |

## Git 提交策略 (Git)
| 原则 | 说明 |
| --- | --- |
| 每步一提交 | 每个模块拆分完成后提交 |
| 信息聚焦“为什么” | 描述结构调整与后续收益 |
| 推送到 GitHub | 新仓库 `main` 分支 |

## 约束 (Constraints)
| 约束 | 说明 |
| --- | --- |
| 数据格式不变 | `mesh_recorder_data` JSON 结构保持 |
| 接口不变 | 函数名与 `bl_idname` 不改 |
| UI 文本不变 | `translations.py` 暂不调整 |
| 不清理用户已有文件 | 仅在新工作目录操作 |

## 待确认项 (Open Items)
| 项 | 说明 |
| --- | --- |
| GitHub 远端地址 | 新仓库 URL |
| 默认分支名 | 推荐 `main` |
| WebSocket 工具指令 | 连接/注入/截屏命令 |
