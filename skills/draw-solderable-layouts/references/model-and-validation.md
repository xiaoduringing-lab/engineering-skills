# Baseline JSON model and checks

The bundled Python script uses only the standard library. Run:

```sh
python3 scripts/board_model.py /absolute/model.json --out /absolute/output
```

A model has the following fields (all measurements in millimetres):

- `board`: `width_mm`, `height_mm`, `pitch_mm`, `baseline_view` (`front` or `back`), `copper_side` (`front` or `back`), `copper_verified` (boolean).
- `holes`: list of `{id, x, y}` in the baseline view. Describe only real holes; arbitrary, nonrectangular patterns are supported.
- `copper_islands`: list of disjoint lists of hole IDs proven to conduct. Omitted holes are independent pads. Apply any physical cuts to these lists before running. Keep artwork and cut evidence alongside the model.
- `leads`: list of `{id, hole, net}`. Use literal `NC` only for intentionally unconnected leads. Actual finite impedance components do NOT join their distinct terminal nets in this copper graph.
- `components`: optional list of `{id, holes}` to render generic body bounding boxes. These are not dimensioned footprints. Detailed component models belong in a project renderer.
- `connections`: list of `{id, net, start, end, method, side, group, points?}`. `method` is `bridge`, `bare`, or `insulated`; `side` is `front` or `back`; `points` optionally lists intermediate `[x,y]` waypoints. Paths must avoid unintended bare-wire or bridge contact, independently of endpoint-only validation.
- `net_colors`: optional mapping from net name to SVG color, assigned by functional role. Keep magenta excluded.

The baseline checker validates IDs, finite geometry, hole existence, disjoint copper islands, connected required nets, NC isolation, different-net shorts and adjacent-hole bridge span. It outputs validation.json, connections.csv, and front/back SVGs. It mirrors horizontally about the actual board width; hole IDs do not change. Both installation sides are visible; dashed lines identify wires installed on the opposite side.

A validation failure stops delivery of construction drawings from the script. `copper_verified=false` permits provisional drawings with explicit incomplete status; it never grants a physical or electrical acceptance pass.

Important limits: the baseline checker validates ideal endpoints, not wire-to-wire contact along a path; it does not check footprints, pinout correctness, polarity, current ratings, resistor values, insulation integrity, voltage compatibility, source backfeed, 3D collisions, or actual cuts. It does not simulate components, switches or removable links. For removable links, check separate full models for open and closed configurations, keeping all other installed connections unchanged. For schematics, use a proper circuit drawing tool/model.

Build only synthetic fixtures for script smoke tests. Do not bundle a user's real board dimensions, wiring, program pin assignments, or private project documents with this reusable skill.
