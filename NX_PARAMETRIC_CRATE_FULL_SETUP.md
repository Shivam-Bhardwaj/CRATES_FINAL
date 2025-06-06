# NX Parametric Crate: Full Setup Instructions

This guide provides the complete step-by-step instructions for setting up the entire parametric crate project in Siemens NX, from the base components to the final drawing and Bill of Materials (BOM).

---

## Overall Setup

### Assembly Structure
Your top-level assembly should be structured as follows:

```
_TEMPLATE.prt (Top-Level Assembly)
├── SHIPPING_BASE.prt
│   ├── SKID_LUMBER.prt (instances)
│   └── FLOOR_BOARD_LUMBER.prt (instances)
├── CRATE_CAP.prt
│   ├── LEFT_END_PANEL_ASSY.prt
│   ├── RIGHT_END_PANEL_ASSY.prt
│   ├── FRONT_PANEL_ASSY.prt
│   │   ├── FRONT_PANEL_Plywood.prt
│   │   └── FRONT_PANEL_Cleat.prt
│   ├── BACK_PANEL_ASSY.prt
│   └── TOP_PANEL_ASSY.prt
```

### Coordinate System
- **Origin (0,0,0):** Center of the crate's width (X), absolute front face of the crate (Y), ground level (Z).
- **Z-axis:** Points Up.
- **Y-axis:** Points along the crate's length (inwards from the front).
- **X-axis:** Points across the crate's width.
- The SHIPPING_BASE and CRATE_CAP sub-assemblies are both placed at the origin (0,0,0) of the _TEMPLATE assembly.

---

## Step 1: Generate & Import Expressions

1. **Run Python Script:** Execute the final Python GUI script (e.g., `main.py`). Enter all product, clearance, and panel parameters.
2. **Generate .exp file:** Click the "Generate Expressions File" button and save the file.
3. **Import to NX:**
    - Open your `_TEMPLATE.prt` assembly.
    - Make it the Work Part.
    - Go to **Tools > Expressions**.
    - Import the generated `.exp` file.
    - Verify that all expressions (Skid_..., FB_..., PANEL_..., FP_...) are loaded correctly.

---

## Step 2: SHIPPING_BASE Assembly

### A. Skids
1. **Prepare SKID_LUMBER.prt (Master Part):**
    - Open the part file. Model a block driven by internal expressions (e.g., `p_Length`, `p_Width`, `p_Thickness`).
    - Go to **File > Properties > Attributes**. Create/set these master attributes:
        - `DB_PART_NAME`: (String) SKID, LUMBER
        - `CUT_THICKNESS`: (Number) Link its value to `p_Thickness`.
        - `CUT_WIDTH`: (Number) Link its value to `p_Width`.
        - `CUT_LENGTH`: (Number) Link its value to `p_Length`.
2. **Assemble and Pattern Skids in SHIPPING_BASE.prt:**
    - Make `SHIPPING_BASE.prt` the Work Part.
    - **Add First Skid:** Add one instance of `SKID_LUMBER.prt`.
    - **Override Its Parameters:** Right-click the instance > Properties > Parameters. Set:
        - `p_Thickness = "_TEMPLATE"::Skid_Actual_Height`
        - `p_Width = "_TEMPLATE"::Skid_Actual_Width`
        - `p_Length = "_TEMPLATE"::Skid_Actual_Length`
    - **Constrain First Skid:** Position its origin (e.g., front-bottom-left corner) at:
        - `X = "_TEMPLATE"::X_Master_Skid_Origin_Offset`
        - `Y = 0`
        - `Z = 0`
    - **Pattern the Skid:** Use Pattern Component.
        - Vector: X-axis
        - Count: `"_TEMPLATE"::CALC_Skid_Count`
        - Pitch Distance: `"_TEMPLATE"::CALC_Skid_Pitch`

### B. Floorboards
1. **Prepare FLOOR_BOARD_LUMBER.prt (Master Part):**
    - Open the part file. Model a block driven by internal expressions (e.g., `p_Length`, `p_Width`, `p_Thickness`).
    - Go to **File > Properties > Attributes**. Create/set:
        - `DB_PART_NAME`: (String) FLOORBOARD, LUMBER
2. **Set Up Floorboard Instances in SHIPPING_BASE.prt:**
    - Add MAX_NX_FLOORBOARD_INSTANCES (e.g., 20) instances of `FLOOR_BOARD_LUMBER.prt`. Rename them (e.g., FB_INSTANCE_1, etc.).
    - For each Instance j (from 1 to 20):
        - **a. Override Instance Parameters (Geometry):**
            - `p_Length = "_TEMPLATE"::FB_Board_Actual_Length`
            - `p_Thickness = "_TEMPLATE"::FB_Board_Actual_Thickness`
            - `p_Width = "_TEMPLATE"::FB_Inst_j_Actual_Width`
        - **b. Apply Assembly Constraints (Positioning):**
            - Y-Position: Constrain its "front" face at a distance of `"_TEMPLATE"::FB_Inst_j_Y_Pos_Abs` from the SHIPPING_BASE XZ plane.
            - Z-Position: Constrain its bottom face to the top face of the skids (`Z = "_TEMPLATE"::Skid_Actual_Height`).
            - X-Position: Center it or align it flush with skid ends.
        - **c. Create/Set Instance Attributes (for BOM):**
            - `CUT_LENGTH`: Link to `"_TEMPLATE"::FB_Board_Actual_Length`
            - `CUT_THICKNESS`: Link to `"_TEMPLATE"::FB_Board_Actual_Thickness`
            - `CUT_WIDTH`: Link to `"_TEMPLATE"::FB_Inst_j_Actual_Width`
        - **d. Drive Component Suppression:**
            - f(x) next to "Suppressed". Formula: `"_TEMPLATE"::FB_Inst_j_Suppress_Flag`

---

## Step 3: CRATE_CAP Assembly

### A. Panel Part Modeling
- Create individual part files for each panel component. Model them as blocks driven by expressions from _TEMPLATE.
- **FRONT_PANEL_Plywood.prt:**
    - Width(X)=FP_Plywood_Width, Height(Y)=FP_Plywood_Height, Thickness(Z)=FP_Plywood_Thickness.
    - Set `DB_PART_NAME` attribute to "PANEL, PLYWOOD". Set `CUT_...` attributes.
- **FRONT_PANEL_Cleat.prt:**
    - Width(Y)=FP_Cleat_Width, Thickness(Z)=FP_Cleat_Thickness. Use an internal `p_Length` expression for its length (X).
    - Set `DB_PART_NAME` attribute to "CLEAT". Set `CUT_...` attributes.

### B. Assembling the FRONT_PANEL_ASSY
- Make `FRONT_PANEL_ASSY.prt` the Work Part. Assume its origin is the inner, bottom-left corner.
- **Add Plywood:** Add `FRONT_PANEL_Plywood.prt`. Constrain it fixed at the assembly origin (0,0,0).
- **Add Vertical Edge Cleats (2):**
    - Add two instances of `FRONT_PANEL_Cleat.prt`.
    - Override `p_Length` for both to `"_TEMPLATE"::FP_Edge_Vert_Cleat_Length`.
    - Constrain to the left and right edges of the plywood.
- **Add Horizontal Edge Cleats (2):**
    - Add two instances of `FRONT_PANEL_Cleat.prt`.
    - Override `p_Length` for both to `"_TEMPLATE"::FP_Edge_Horiz_Cleat_Length`.
    - Constrain to the top and bottom edges, between the vertical cleats.
- **Add & Pattern Intermediate Cleats:**
    - Add one `FRONT_PANEL_Cleat.prt`. Override its `p_Length` to `"_TEMPLATE"::FP_Inter_Cleat_Length`.
    - Constrain its starting position (e.g., from an edge cleat at a distance of `"_TEMPLATE"::FP_Inter_Cleat_Pitch`).
    - Use Pattern Component. Count=`FP_Inter_Cleat_Count`, Pitch=`FP_Inter_Cleat_Pitch`.
    - Suppress the Pattern Feature using the formula: if (`"_TEMPLATE"::FP_Inter_Cleat_Count > 0`) then 0 else 1.

### D. Detailed Front Panel Modeling (with NX Expression Linking)

This section provides explicit modeling and assembly steps for the front panel, ensuring all expressions are linked to the _TEMPLATE part for NX compatibility.

#### 1. FRONT_PANEL_Plywood.prt (Plywood Body)
- **Create a new part file** named `FRONT_PANEL_Plywood.prt`.
- **Model a block** using the following expressions (all with _TEMPLATE linking):
    - Width (X): `"_TEMPLATE"::FP_Plywood_Width`
    - Height (Y): `"_TEMPLATE"::FP_Plywood_Height`
    - Thickness (Z): `"_TEMPLATE"::FP_Plywood_Thickness`
- **Set attributes** (File > Properties > Attributes):
    - `DB_PART_NAME`: `PANEL, PLYWOOD`
    - `CUT_THICKNESS`: Link to `"_TEMPLATE"::FP_Plywood_Thickness`
    - `CUT_WIDTH`: Link to `"_TEMPLATE"::FP_Plywood_Width`
    - `CUT_LENGTH`: Link to `"_TEMPLATE"::FP_Plywood_Height`
- **Origin:** Place the block's lower-left-front corner at (0,0,0) for easy assembly.

#### 2. FRONT_PANEL_Cleat.prt (Cleat Body)
- **Create a new part file** named `FRONT_PANEL_Cleat.prt`.
- **Model a block** using the following expressions:
    - Length (X): `p_Length` (to be overridden per instance)
    - Width (Y): `"_TEMPLATE"::FP_Cleat_Width`
    - Thickness (Z): `"_TEMPLATE"::FP_Cleat_Thickness`
- **Set attributes:**
    - `DB_PART_NAME`: `CLEAT`
    - `CUT_THICKNESS`: Link to `"_TEMPLATE"::FP_Cleat_Thickness`
    - `CUT_WIDTH`: Link to `"_TEMPLATE"::FP_Cleat_Width`
    - `CUT_LENGTH`: Link to `p_Length`
- **Origin:** Place the block's lower-left-front corner at (0,0,0).

#### 3. Assembling FRONT_PANEL_ASSY.prt
- **Create a new assembly** `FRONT_PANEL_ASSY.prt` with origin at the inner, bottom-left corner of the panel.

##### a. Add Plywood
- Add `FRONT_PANEL_Plywood.prt` at the assembly origin (0,0,0). Fix or fully constrain it.

##### b. Add Vertical Edge Cleats (2)
- Add two instances of `FRONT_PANEL_Cleat.prt`.
- **Override `p_Length`** for both to `"_TEMPLATE"::FP_Edge_Vert_Cleat_Length`.
- **Positioning:**
    - Left cleat: X=0, Y=0, Z=0 (flush with left edge)
    - Right cleat: X=`"_TEMPLATE"::FP_Plywood_Width - "_TEMPLATE"::FP_Cleat_Thickness`, Y=0, Z=0 (flush with right edge)
- **Constrain** each cleat's face to the plywood edge.

##### c. Add Horizontal Edge Cleats (2)
- Add two more instances of `FRONT_PANEL_Cleat.prt`.
- **Override `p_Length`** for both to `"_TEMPLATE"::FP_Edge_Horiz_Cleat_Length`.
- **Positioning:**
    - Bottom cleat: X=`"_TEMPLATE"::FP_Cleat_Thickness`, Y=0, Z=0 (between vertical cleats, flush with bottom)
    - Top cleat: X=`"_TEMPLATE"::FP_Cleat_Thickness`, Y=`"_TEMPLATE"::FP_Plywood_Height - "_TEMPLATE"::FP_Cleat_Thickness`, Z=0 (between vertical cleats, flush with top)
- **Constrain** to plywood and vertical cleats.

##### d. Add & Pattern Intermediate Cleats
- Add one instance of `FRONT_PANEL_Cleat.prt`.
- **Override `p_Length`** to `"_TEMPLATE"::FP_Inter_Cleat_Length`.
- **Positioning:**
    - X=`"_TEMPLATE"::FP_Cleat_Thickness`, Y=`"_TEMPLATE"::FP_Inter_Cleat_First_Y`, Z=0 (between vertical cleats, at first intermediate position)
- **Pattern Component:**
    - Direction: Y-axis
    - Count: `"_TEMPLATE"::FP_Inter_Cleat_Count`
    - Pitch: `"_TEMPLATE"::FP_Inter_Cleat_Pitch`
- **Suppression:**
    - Use the formula: `if ("_TEMPLATE"::FP_Inter_Cleat_Count > 0) then 0 else 1` for the pattern feature's suppression.

##### e. Best Practices
- **Fully constrain** all cleats to the plywood and to each other for parametric stability.
- **Use expressions** for all dimensions and positions, always referencing the _TEMPLATE part, to ensure the panel updates automatically with new parameters.
- **Test** by changing key expressions (e.g., cleat count, pitch, panel size) and regenerating the assembly.

### C. Assembling the Main Panels into CRATE_CAP
- Make `CRATE_CAP.prt` the Work Part. Constraints are relative to the global planes.
- **Add LEFT_END_PANEL_ASSY.prt:**
    - Z-Position: Align bottom edge at `Z = "_TEMPLATE"::INPUT_Ground_Clearance_End_Panels`.
    - X-Position: Align inner face at `X = - ("_TEMPLATE"::crate_overall_width_od_in / 2)`.
    - Y-Position: Align front face to the global Y=0 plane.
- **Add RIGHT_END_PANEL_ASSY.prt:**
    - Z-Position: Same as Left.
    - X-Position: Align inner face at `X = ("_TEMPLATE"::crate_overall_width_od_in / 2)`.
    - Y-Position: Same as Left.
- **Add FRONT_PANEL_ASSY.prt:**
    - Z-Position: Align bottom face at `Z = "_TEMPLATE"::Skid_Actual_Height`.
    - Y-Position: Align outer face to the global XZ plane (Y=0).
    - X-Position: Align center plane to the global YZ plane (X=0).
- **Add BACK_PANEL_ASSY.prt:**
    - Z-Position: Align bottom face at `Z = "_TEMPLATE"::Skid_Actual_Height`.
    - Y-Position: Align outer face at `Y = "_TEMPLATE"::crate_overall_length_od_in`.
    - X-Position: Align center plane to X=0.
- **Add TOP_PANEL_ASSY.prt:**
    - Z-Position: Align bottom face at `Z = "_TEMPLATE"::Skid_Actual_Height + "_TEMPLATE"::PANEL_Front_Calc_Height`.
    - Center it in X and Y.

---

## Part 4: Drawing and BOM

1. **Create Drawing of _TEMPLATE.prt.**
2. **Add Parts List.**
3. **Configure "DESCRIPTION" Column with the formula:**
    ```
    <W$=@CUT_THICKNESS> + " X " + <W$=@CUT_WIDTH> + " X " + <W$=@CUT_LENGTH> + " , " + <W$=@DB_PART_NAME>
    ```
4. **Configure Grouping:** Ensure the "DESCRIPTION" column is a Key Field.

---

For further details, refer to your Siemens NX documentation or consult your CAD administrator.
