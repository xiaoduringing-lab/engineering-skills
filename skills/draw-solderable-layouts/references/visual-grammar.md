# Visual grammar

## Layers, from background to annotations

1. White or pale neutral page, board outline, physical scale bar when validated.
2. Existing copper: light gray; clearly separate isolated pads from continuous strips. Copper visible through an opposite-side board view is a reference layer, not an exposed solder surface.
3. Hole centers: subdued gray circles with coordinate guides. Show missing holes as missing.
4. Component bodies: restrained outline/fill, reference designator, pin labels, polarity, body footprint/keep-out when known.
5. Proposed wires/bridges: stronger functional colors, connection IDs, layer/side indication.
6. Endpoint markers, connector Pin 1, cuts, caution callouts, and legend.

Suggested palette: supply #C43C28; return #263238; analog #007F78; digital #0068B5; control #A66A00; auxiliary #6845A5. Assign by current circuit function, not by position in a list. Never rely only on red/green contrast; supply names and different symbols remain necessary. No magenta.

## Marker meaning

| Mark | Meaning |
|---|---|
| Gray circular hole | Existing physical hole only |
| Hollow colored square | Actual installed jumper termination |
| Small filled junction | Intended electrical join between conductors |
| White halo/gap under crossing wire | Crossing without connection |
| Dashed or explicitly labeled path | Opposite-side or suggested routing, as declared in legend |
| Cut symbol plus cut ID | Documented removal of copper; never a mere visual decoration |

At a shared endpoint, label which leads share the pad and check solder access. A square does not prove that two leads fit through one hole. A wire passing across a hole does not connect to it unless declared as a termination or joint in the model.

## Front/back and grouped views

Always print baseline viewing side, mirrored viewing side, flip axis, coordinate-label convention, and copper side. Keep top/bottom invariant for a horizontal flip. For a vertical flip explicitly describe the changed reference. Apply the same transformation to holes, copper, component bodies, wire paths and annotations' anchor positions. Keep text upright.

Use an overview plus functional groups when an overview becomes dense. Each group must retain the full grid and identical component positions, fade unrelated routing, and list the relevant connection IDs. Supply a separate bridge-only view if useful. Do not imply all groups are distinct installation stages unless an order is defined.

## QA at final size

Inspect dense regions, crossings, sockets, header keying, power labels, axis labels, tables, and all font glyphs. Make callouts larger or split a drawing instead of relying on extreme zoom. Use monochrome symbols as a second reading channel. Do not use generative raster imagery for exact engineering geometry.
