# Engineering Skills

可复用的电子工程制图技能 / Reusable electronic engineering drawing skills.

## 可焊接电路工程制图

`skills/draw-solderable-layouts` 包含：

- 基于真实孔位、铜箔和电路网络建模，保持正反面坐标一致。
- 高对比度配色、明确端点和交叉关系、分组施工图规范。
- 焊锡桥、短裸线、绝缘飞线的选用与连接表。
- Python 标准库脚本，用于基础 SVG、CSV 和理想端点连通性检查。

不包含任何特定项目的接线方案、GPIO 分配或私人资料。

## 使用

将 `skills/draw-solderable-layouts` 文件夹放入支持 `SKILL.md` 的工具的技能目录。按所用工具的规则加载；在 Codex 中可使用：

```text
使用 $draw-solderable-layouts，根据提供的电路与板子资料生成正反面焊接布局和连接表。
```

提供板子尺寸、真实铜箔结构、电路网络、元件尺寸及固定位置。缺失信息应标记待确认。

基础脚本（Python 3.9+，无第三方依赖）：

```sh
python3 skills/draw-solderable-layouts/scripts/board_model.py model.json --out output
```

模型格式和检查范围见 `references/model-and-validation.md`；视觉规范见 `references/visual-grammar.md`。

## Important limits

The script renders an explicitly supplied model; it is not an autorouter or circuit simulator. It checks ideal copper/jumper endpoints, not contacts along wire paths, component footprints, polarity, current ratings, insulation, or physical clearance. Gray copper trees are connectivity references, not trace artwork. PDF assembly and dense project-specific drawings require further rendering and visual inspection. Software checks never replace physical measurements.

## License

MIT. See LICENSE.
