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
- **Global Origin (0,0,0):** Located at the bottom of the crate, centered symmetrically about the Y-Z plane (X=0), with Z pointing up (away from the ground), and Y pointing into the crate (from the front face).
- All subassemblies and bounding boxes (such as `FRONT_PANEL_ASSY.prt`) are positioned relative to this global origin, ensuring the crate is always centered and sits on the ground plane.
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
- Make `FRONT_PANEL_ASSY.prt` the Work Part. Its origin is the inner, bottom-left corner of the front panel bounding box.
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
    - Constrain and pattern as required, using expressions for count and pitch.

**Bounding Box Placement in Global Assembly:**
- The entire `FRONT_PANEL_ASSY.prt` (bounding box and all features) is symmetrically constrained in the global crate assembly:
    - Centered on the Y-Z plane (X=0).
    - Bottom of the bounding box at the correct Z height (e.g., `skid_height`).
    - All front panel features are positioned relative to the bounding box origin, not the global assembly origin.

### D. Detailed Front Panel Modeling (with NX Expression Linking)

This section provides explicit modeling and assembly steps for the front panel, ensuring all expressions are linked to the _TEMPLATE part for NX compatibility.

#### 1. FRONT_PANEL_Plywood.prt (Plywood Body)
- **Create a new part file** named `FRONT_PANEL_Plywood.prt`.
- **Model a block** using the following expressions (all with _TEMPLATE linking):
    - Width (**X**, side-to-side): `"_TEMPLATE"::FP_Plywood_Width`
    - Thickness (**Y**, front-to-back): `"_TEMPLATE"::FP_Plywood_Thickness`
    - Height (**Z**, vertical): `"_TEMPLATE"::FP_Plywood_Height`
- **Set attributes** (File > Properties > Attributes):
    - `DB_PART_NAME`: `PANEL, PLYWOOD`
    - `CUT_THICKNESS`: Link to `"_TEMPLATE"::FP_Plywood_Thickness`
    - `CUT_WIDTH`: Link to `"_TEMPLATE"::FP_Plywood_Width`
    - `CUT_LENGTH`: Link to `"_TEMPLATE"::FP_Plywood_Height`
- **Origin:** Place the block's lower-left-front corner at (0,0,0) (X=left, Y=front, Z=bottom) for easy assembly.

#### 2. Cleat Parts (Separate for Each Type)
- **Create separate part files for each cleat type:**
    - `FRONT_PANEL_CLEAT_VERT_MAIN.prt` (main vertical edge cleat)
    - `FRONT_PANEL_CLEAT_HORIZ_MAIN.prt` (main horizontal edge cleat)
    - `FRONT_PANEL_CLEAT_VERT_PATTERN.prt` (vertical intermediate/patterned cleat)
    - `FRONT_PANEL_CLEAT_HORIZ_PATTERN.prt` (horizontal intermediate/patterned cleat)
- **Model each block** using the following expressions (all with _TEMPLATE linking):
    - For all cleat types:
        - **Width (X, side-to-side):** `"_TEMPLATE"::INPUT_Cleat_Actual_Width`
        - **Thickness (Y, front-to-back):** `"_TEMPLATE"::INPUT_Cleat_Thickness`
        - **Length (Z, vertical or horizontal):** Use the appropriate length expression for each cleat type (e.g., `"_TEMPLATE"::FP_Edge_Vert_Cleat_Length`, `"_TEMPLATE"::FP_Edge_Horiz_Cleat_Length`, or `"_TEMPLATE"::FP_Inter_Cleat_Length`)
- **Set attributes** (File > Properties > Attributes):
    - `DB_PART_NAME`: `CLEAT, VERT MAIN` / `CLEAT, HORIZ MAIN` / `CLEAT, VERT PATTERN` / `CLEAT, HORIZ PATTERN`
    - `CUT_THICKNESS`: Link to `"_TEMPLATE"::INPUT_Cleat_Thickness`
    - `CUT_WIDTH`: Link to `"_TEMPLATE"::INPUT_Cleat_Actual_Width`
    - `CUT_LENGTH`: Link to the appropriate length expression for each cleat type
- **Origin:** Place the block's lower-left-front corner at (0,0,0) (X=left, Y=front, Z=bottom) for all cleat types.

#### 3. Assembling the Front Panel (No Cleat Reuse)
- In your assembly (or directly in the global frame):
    - Add `FRONT_PANEL_Plywood.prt` at the correct global position (centered on X=0, bottom at Z=0, Y=0 for front face).
    - Add two `FRONT_PANEL_CLEAT_VERT_MAIN.prt` for the left and right edges.
    - Add two `FRONT_PANEL_CLEAT_HORIZ_MAIN.prt` for the top and bottom edges.
    - Add as many `FRONT_PANEL_CLEAT_VERT_PATTERN.prt` or `FRONT_PANEL_CLEAT_HORIZ_PATTERN.prt` as needed for intermediate cleats, using expressions for count and pitch.
- **Constrain** each cleat to the plywood and/or other cleats using global expressions, not local assembly origins.
- **Pattern** intermediate cleats as needed, using the correct cleat part for each orientation.

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


splice_cleat is one thing intermedi cleat another.

intermediate can be anythoin - end cleats | only more naming though

filler cleat -  every 24 inches
splice cleat - over a splice


end cleats  - picture frame


cost factor - less plywood cuts



horizontal cleats when there is a splice
verticle cleat table 7.2

