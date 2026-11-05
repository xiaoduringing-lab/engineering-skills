---
name: draw-solderable-layouts
description: Create readable, solderable perfboard and stripboard engineering drawings from verified geometry and circuit nets. Use for front/back layouts, jumper rerouting with fixed components, solder bridges, grouped construction sheets, wiring tables, or continuity and mirror checks. Preserve real copper connectivity and physical hole identities; distinguish wiring layouts from electrical schematics. 绘制洞洞板、条形板正反面焊接布局、分组飞线图和连接表。
---

# Draw solderable layouts

Turn verified board geometry and circuit intent into coordinated drawings. Keep the ability generic: do not import any earlier project's dimensions, coordinates, GPIO allocation, BOM, or wiring unless supplied for the current task.

## 1. Establish evidence and a single model

- Read supplied circuit, board drawing, copper artwork, component data, and fixed positions before routing. Separate confirmed facts, proposed choices, and missing evidence.
- Confirm hole count, pitch, board outline, coordinate origin, baseline viewing side, flip axis, copper side, and copper segmentation. Never assume adjacent pads conduct.
- Preserve fixed component positions. Check body size, row spacing, sockets, lead access, mounting hardware, cable exit, and clearance on BOTH sides. Distinguish nominal pitch from measured fit.
- Assign one immutable physical ID to each existing hole. Use the same ID in both views, tables, and the netlist. Mirroring changes screen location, not electrical identity.
- Model actual copper islands separately from desired nets. Store component leads with pin ID, net, hole, and evidence. Explicitly mark NC leads. Add documented cuts to the copper model before adding wires.
- Keep unknown copper structure unresolved. Produce a provisional drawing if useful; do not issue a solder-ready pass until geometry and intended nets are sufficiently defined.

Read [references/model-and-validation.md](references/model-and-validation.md) for the small JSON schema and checker limitations. For complex imported artwork, adapt the model; do not force it into a rectangular-board assumption.

## 2. Route over conductive islands

1. Collapse known copper into conductive islands and attach component leads to them.
2. For each desired net, connect distinct islands only. Prefer a minimum necessary spanning set; avoid redundant wires unless explicitly justified.
3. Choose adjacent-pad solder bridges, short bare links, or insulated wires based on actual geometry, mechanical clearance, and construction access.
4. Reject connections joining different desired nets. Enumerate every pad involved in a multi-pad solder bridge. Never depict a gap as conductive by implication.
5. Penalize crossings, excessive length, crowded terminations, long shared paths for sensitive signals, and multiple leads in one hole. Electrical and mechanical correctness outrank wire count.
6. Preserve existing connections where useful. On revisions, supply retain/remove/add lists and explain necessary moves. Never leave obsolete wires implicit.
7. Distinguish electrical endpoints from the suggested physical wire route. Route bends are not solder joints. A schematic net label is not an installed jumper.

## 3. Draw with consistent visual grammar

Read [references/visual-grammar.md](references/visual-grammar.md) before drawing.

Use neutral board/copper layers, fixed component outlines, high-contrast functional colors, hollow square termination markers, and unambiguous crossing gaps. Do not use magenta. Show Pin 1, polarity, cut locations, legends, coordinate axes, and observation direction. Distinguish symbols by shape and text as well as color.

Build both sides and every group sheet from the same model. Never independently redraw or renumber a mirrored view. Gray out unrelated connections in group sheets; keep all component positions unchanged. Avoid hiding component polarity or pads beneath wires.

Use `scripts/board_model.py MODEL.json --out OUTPUT_DIRECTORY` for a dependency-free baseline SVG/CSV renderer and graph checker. It renders data already supplied; it does not infer a circuit, place components, route wires, or verify physical fit. Use a richer renderer for connectors, enclosure outlines, dense labels, complex copper, or native electrical symbols. Never represent its generic boxes as verified component footprints.

## 4. Validate before delivery

- Check hole existence, unique lead/connection IDs, endpoint membership, actual copper continuity, required-net connectivity, different-net isolation, NC isolation, legal solder bridges, and mirror identity.
- Check removable links in both open and closed configurations where relevant; document any alternative power/return paths. Account for installed wire crossings and copper cuts.
- Check claimed redundancy, all table rows, and the correspondence between model and rendered endpoints. Assess mechanical interference separately; graph connectivity is not physical fit.
- Render final SVG/PDF to images and inspect every page at readable scale. Fix clipped captions, unreadable IDs, overlapping labels, missing glyphs, and confusing crossings. Test all bundled scripts actually used.
- State exactly which checks ran and which remain pending. Use **Drawing / Netlist Validation Passed — Physical Verification Pending** only after the relevant model checks pass, and list any unverified copper assumptions next to that status. A graph pass alone is not a complete drawing or hardware pass.

## 5. Deliver a construction package

Normally provide editable front/back SVGs, a rendered PDF with overview and functional group sheets, a BOM/pin map, CSV connection table, and validation notes. Scale the package to the request; reuse PDF/document skills when applicable. Only provide a true electrical schematic when requested or useful, using proper circuit symbols and networks; a layout is not a schematic.

For each connection list ID, net, both physical hole IDs, component-pin purpose, method, installation side, and group. Include soldering order, cuts/bridges, shared-pad cautions, and remaining physical measurements. Label a rendering as to-scale only if physical page size and print scaling were verified.

Finish with the deliverables, validation scope, and material remaining uncertainties. Do not claim physical verification from drawing inspection.
