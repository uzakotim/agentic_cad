import cadquery as cq
import math


# Fallback for show_object when running outside CQ-Editor / GUI
if 'show_object' not in globals():
    def show_object(obj, *args, **kwargs):
        pass
# ============================================================
# CHOCOLATE MOLD PARAMETERS
# ============================================================

# Overall dimensions
X_SIZE = 13.0
Y_SIZE = 8.0


# ============================================================
# MAIN MOLD BODY
# ============================================================

# Increased from 0.25 mm to 0.50 mm
BASE_H = 0.50

OUTER_R = 0.10


# ============================================================
# THIN LOWER FLANGE
# ============================================================

FLANGE_X = 13.10
FLANGE_Y = 8.10

FLANGE_H = 0.10
FLANGE_R = 0.10


# ============================================================
# TOP SURFACE
# ============================================================
#
# The top remains completely FLAT.
#
# There is NO raised perimeter rim.
#
# ============================================================


# ============================================================
# CHOCOLATE CAVITIES
# ============================================================

ROWS = 4
COLS = 6

CAVITY_D = 1.5 # Diameter

# Increased because the tray is now thicker.
#
# Top surface:
#     Z = 0.10 + 0.50 = 0.60
#
# Cavity floor:
#     Z = 0.60 - 0.30 = 0.30
#
CAVITY_DEPTH = 0.25


# Efficient spacing
X_SPACING = 2.00
Y_SPACING = 1.75


# ============================================================
# UNDERSIDE MATERIAL RELIEF
# ============================================================

# Larger circular supports than top cavities
#
# Top cavity       = 1.30 mm
# Bottom support   = 1.55 mm

BOTTOM_ISLAND_D = 1.55

# Material retained around outside
BOTTOM_WALL = 0.32

# Underside relief depth
#
# Bottom surface = Z 0
# Relief reaches  = Z 0.15
#
# Cavity floor    = Z 0.30
#
# Therefore:
#
#       0.30
#       ─────────────  cavity floor
#
#       0.15
#       ─────────────  underside relief
#
#       0
#       ─────────────  bottom
#
# Remaining material = 0.15 mm
#
BOTTOM_CUT_DEPTH = 0.2

BOTTOM_CUT_X = X_SIZE - 2.0 * BOTTOM_WALL
BOTTOM_CUT_Y = Y_SIZE - 2.0 * BOTTOM_WALL


# ============================================================
# STAR
# ============================================================

STAR_OUTER_R = 0.38
STAR_INNER_R = 0.17

STAR_LINE = 0.07

# Positive star height
STAR_HEIGHT = 0.07


# ============================================================
# HELPER: ROUNDED BOX
# ============================================================

def rounded_box(x, y, z, radius):

    obj = (
        cq.Workplane("XY")
        .box(
            x,
            y,
            z,
            centered=(True, True, False)
        )
    )

    if radius > 0:
        obj = obj.edges("|Z").fillet(radius)

    return obj


# ============================================================
# HELPER: 5-POINT STAR
# ============================================================

def make_star(outer_radius, inner_radius):

    points = []

    for i in range(10):

        angle = math.radians(
            90.0 + i * 36.0
        )

        radius = (
            outer_radius
            if i % 2 == 0
            else inner_radius
        )

        points.append(
            (
                radius * math.cos(angle),
                radius * math.sin(angle)
            )
        )

    return points


# ============================================================
# 1. LOWER FLANGE
# ============================================================

flange = (
    cq.Workplane("XY")
    .box(
        FLANGE_X,
        FLANGE_Y,
        FLANGE_H,
        centered=(True, True, False)
    )
)

flange = flange.edges("|Z").fillet(
    FLANGE_R
)


# ============================================================
# 2. MAIN BODY
# ============================================================

body = (
    cq.Workplane("XY")
    .box(
        X_SIZE,
        Y_SIZE,
        BASE_H,
        centered=(True, True, False)
    )
)

# Round the four vertical outside corners
body = body.edges("|Z").fillet(
    OUTER_R
)

# Place body on top of flange
body = body.translate(
    (0, 0, FLANGE_H)
)

model = flange.union(body)


# ============================================================
# 3. FLAT TOP SURFACE
# ============================================================

# Top of the tray
TOP_Z = FLANGE_H + BASE_H

# With current dimensions:
#
# TOP_Z = 0.10 + 0.50
#       = 0.60 mm
#

CAVITY_FLOOR_Z = TOP_Z - CAVITY_DEPTH


# ============================================================
# 4. CAVITY LOCATIONS
# ============================================================

x_start = -(
    (COLS - 1) * X_SPACING
) / 2.0

y_start = -(
    (ROWS - 1) * Y_SPACING
) / 2.0


# ============================================================
# 5. SAFETY CHECK
# ============================================================

# Bottom of main body
BODY_BOTTOM_Z = FLANGE_H

# Top of underside relief
BOTTOM_RELIEF_TOP_Z = BOTTOM_CUT_DEPTH

# Distance between cavity floor and underside relief
REMAINING_MATERIAL = (
    CAVITY_FLOOR_Z
    - BOTTOM_RELIEF_TOP_Z
)

if REMAINING_MATERIAL <= 0:

    raise ValueError(
        "Top cavity and underside cutout overlap."
    )


# ============================================================
# 6. CUT 24 CIRCULAR CHOCOLATE CAVITIES
# ============================================================

for row in range(ROWS):

    for col in range(COLS):

        x = (
            x_start
            + col * X_SPACING
        )

        y = (
            y_start
            + row * Y_SPACING
        )

        cavity = (
            cq.Workplane("XY")
            .workplane(
                offset=TOP_Z
            )
            .circle(
                CAVITY_D / 2.0
            )
            .extrude(
                -CAVITY_DEPTH
            )
        )

        cavity = cavity.translate(
            (x, y, 0)
        )

        # Small rounding at cavity opening
        try:

            cavity = cavity.edges(
                "%CIRCLE"
            ).fillet(0.04)

        except Exception:

            pass

        model = model.cut(
            cavity
        )


# ============================================================
# 7. UNDERSIDE CUTOUT
# ============================================================

# Large rectangular underside region
#
# This removes material BETWEEN the circular supports.

bottom_cut = (
    cq.Workplane("XY")
    .box(
        BOTTOM_CUT_X,
        BOTTOM_CUT_Y,
        BOTTOM_CUT_DEPTH,
        centered=(True, True, False)
    )
)

# Round the four corners
bottom_cut = bottom_cut.edges(
    "|Z"
).fillet(
    min(
        0.10,
        BOTTOM_WALL
    )
)


# ============================================================
# 8. PRESERVE LARGE CIRCULAR SUPPORTS
# ============================================================

for row in range(ROWS):

    for col in range(COLS):

        x = (
            x_start
            + col * X_SPACING
        )

        y = (
            y_start
            + row * Y_SPACING
        )

        support = (
            cq.Workplane("XY")
            .circle(
                BOTTOM_ISLAND_D / 2.0
            )
            .extrude(
                BOTTOM_CUT_DEPTH + 0.02
            )
        )

        # Start slightly below bottom surface
        support = support.translate(
            (x, y, -0.01)
        )

        # Remove support from cutting tool.
        #
        # This keeps the large circular support solid.
        bottom_cut = bottom_cut.cut(
            support
        )


# ============================================================
# 9. APPLY UNDERSIDE CUTOUT
# ============================================================

model = model.cut(
    bottom_cut
)


# ============================================================
# 10. CREATE STAR PROFILES
# ============================================================

outer_star_points = make_star(
    STAR_OUTER_R,
    STAR_INNER_R
)

inner_star_points = make_star(
    STAR_OUTER_R - STAR_LINE,
    STAR_INNER_R - STAR_LINE
)


# ============================================================
# 11. ADD POSITIVE STARS
# ============================================================

for row in range(ROWS):

    for col in range(COLS):

        x = (
            x_start
            + col * X_SPACING
        )

        y = (
            y_start
            + row * Y_SPACING
        )


        # ----------------------------------------------------
        # OUTER STAR
        # ----------------------------------------------------

        outer_star = (
            cq.Workplane("XY")
            .workplane(
                offset=CAVITY_FLOOR_Z
            )
            .polyline(
                outer_star_points
            )
            .close()
            .extrude(
                STAR_HEIGHT
            )
        )

        outer_star = outer_star.translate(
            (x, y, 0)
        )


        # ----------------------------------------------------
        # INNER STAR
        # ----------------------------------------------------

        inner_star = (
            cq.Workplane("XY")
            .workplane(
                offset=CAVITY_FLOOR_Z - 0.001
            )
            .polyline(
                inner_star_points
            )
            .close()
            .extrude(
                STAR_HEIGHT + 0.002
            )
        )

        inner_star = inner_star.translate(
            (x, y, 0)
        )


        # Create outlined star
        star = outer_star.cut(
            inner_star
        )


        # Add positive star
        model = model.union(
            star
        )


# ============================================================
# 12. EXPORT STL
# ============================================================

# cq.exporters.export(
    # model,
    # "task2.stl"
# )

# ============================================================
# RESULT
# ============================================================
solid = model
show_object(solid)