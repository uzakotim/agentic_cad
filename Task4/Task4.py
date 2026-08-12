import cadquery as cq

l = 45
w = 2.5
h = 1.5

gap_scale = 0.3
gap = w * gap_scale
y_spacing = w + gap

blocks_rows = 4

blocks = (
    cq.Workplane()
    .rarray(1, y_spacing, 3, blocks_rows)
    .rect(l, w, h)
    .extrude(h)
)

bb = blocks.val().BoundingBox()
x_center = 0.5 * (bb.xmin + bb.xmax)
lead_y_center = bb.ymin - gap - w * 0.5

front_block_width_scale = 1.15
front_block = (
    cq.Workplane("XY")
    .center(x_center, lead_y_center)
    .rect(l * front_block_width_scale, w)
    .extrude(h)
)

bottom = blocks.union(front_block)
bb_bot = bottom.val().BoundingBox().

base_block_width_scale = 1.1
base_block = (
    cq.Workplane("XY", origin=(0, (bb_bot.ymax + bb_bot.ymin) * 0.5, 0))
    .rect(w * base_block_width_scale, bb_bot.ymax - bb_bot.ymin)
    .extrude(-h)
)

base_joiner_x_scale = 0.5
base_joiner_y_h_scale = 0.5
base_joiner_y_w_scale = 0.5
base_joiner_z_h_scale = 0.5
base_joiner_width_extra_w = 1.0
base_joiner_width_extra_h = 1.0

base_joiner = (
    cq.Workplane(
        "XY",
        origin=(
            l * base_joiner_x_scale,
            (bb_bot.ymax + bb_bot.ymin) * 0.5 + h * base_joiner_y_h_scale + w * base_joiner_y_w_scale,
            -bb_bot.zmax - h * base_joiner_z_h_scale,
        ),
    )
    .rect(h, bb_bot.ymax - bb_bot.ymin + w * base_joiner_width_extra_w + h * base_joiner_width_extra_h)
    .extrude(w)
)

base_joiner2 = base_joiner.mirror("YZ")
base_block = base_block.union(base_joiner).union(base_joiner2)
solid = bottom.union(base_block)

vertical_block_width_scale = 1.06
vertical_blocks_rows = 3
vertical_blocks = (
    cq.Workplane("XZ")
    .rarray(1, y_spacing, 3, vertical_blocks_rows)
    .rect(l * vertical_block_width_scale, w)
    .extrude(h)
)

bb_vert = vertical_blocks.val().BoundingBox()
vert_x_center = 0.5 * (bb_vert.xmin + bb_vert.xmax)
vert_y_center = bb_vert.zmin - gap - w * 0.5

bot_vertical_block_width_subtract_scale = 1.0
bot_vertical_block = (
    cq.Workplane("XZ")
    .center(vert_x_center, vert_y_center)
    .rect(l - h * bot_vertical_block_width_subtract_scale, w)
    .extrude(h)
)

vertical_translate_y_scale = 1.0
vertical_translate_z_scale = 1.75
vertical_blocks = vertical_blocks.union(bot_vertical_block).translate(
    (0, bb_bot.ymax + h * vertical_translate_y_scale, (bb_vert.zmax - bb_vert.zmin) * vertical_translate_z_scale)
)

bb_vert = vertical_blocks.val().BoundingBox()

joiner_top_extrude_z_scale = 1.75
joiner_top_extrude_h_scale = 0.35
joiner_top_translate_x_scale = 0.5
joiner_top_translate_x_h_scale = 1.0
joiner_top_translate_y_scale = 0.5
joiner_top_translate_z_scale = 0.45

joiner_top = (
    cq.Workplane("XY")
    .rect(h, w)
    .extrude((bb_vert.zmax - bb_vert.zmin) * joiner_top_extrude_z_scale - h * joiner_top_extrude_h_scale)
    .translate((l * joiner_top_translate_x_scale - h * joiner_top_translate_x_h_scale, bb_vert.ymax + w * joiner_top_translate_y_scale, -h * joiner_top_translate_z_scale), double)
)

joiner_top2 = joiner_top.mirror("YZ")

vertical_rotate_deg = 10
vertical_blocks = vertical_blocks.union(joiner_top).union(joiner_top2).rotate((0, 0, 0), (-1, 0, 0), vertical_rotate_deg)

solid = solid.union(vertical_blocks)

handle_origin_x_scale = 0.03
handle_origin_y_scale = 1.0
handle_origin_z_scale = 0.99
handle_width_scale = 0.06
handle_height_scale = 1.5
handle_rotate_deg = 1

handle = (
    cq.Workplane("XY", origin=(bb_vert.xmax - l * handle_origin_x_scale, w * handle_origin_y_scale, bb_vert.zmin * handle_origin_z_scale))
    .rect(l * handle_width_scale, (bb_bot.ymax - bb_bot.ymin) * handle_height_scale)
    .extrude(h)
    .rotate((0, 0, 0), (1, 0, 0), handle_rotate_deg)
)

bb_handle = handle.val().BoundingBox()

leg_w_scale = 1.1
leg_h_scale = 1.75
leg_s_scale = 3.0

W = w * leg_w_scale
H = (bb_vert.zmax - bb_vert.zmin) * leg_h_scale
S = w * leg_s_scale

leg_extrude_x_scale = 0.03
leg_y_shift_scale = 0.5
leg_z_shift_scale = 0.99

leg = (
    cq.Workplane("YZ")
    .polyline([(0, 0), (W, 0), (W + S, H), (S, H)])
    .close()
    .extrude(l * leg_extrude_x_scale)
    .translate((bb_handle.xmax - l * leg_extrude_x_scale, bb_handle.ymin - W * leg_y_shift_scale, bb_handle.zmin - H * leg_z_shift_scale))
)

leg2_translate_y_scale = 0.5
leg2 = leg.mirror("XZ").translate((0, w * leg2_translate_y_scale, 0))

def y_bounds_at_z(obj, z_cut, eps=0.05):
    bb = obj.val().BoundingBox()
    slab = (
        cq.Workplane("XY")
        .center((bb.xmin + bb.xmax) * 0.5, 0)
        .rect((bb.xmax - bb.xmin) * 3, (bb.ymax - bb.ymin) * 3)
        .extrude(eps)
        .translate((0, 0, z_cut))
    )
    sl = obj.intersect(slab)
    vals = sl.vals()
    ymins = [v.BoundingBox().ymin for v in vals]
    ymaxs = [v.BoundingBox().ymax for v in vals]
    return min(ymins), max(ymaxs)

bb_leg = leg.val().BoundingBox()

z_cut_scale = 0.7
z_cut = bb_leg.zmin * z_cut_scale

ymin1, ymax1 = y_bounds_at_z(leg, z_cut)
ymin2, ymax2 = y_bounds_at_z(leg2, z_cut)

y_left_inner = max(ymin1, ymin2)
y_right_inner = min(ymax1, ymax2)

if ymax1 <= ymin2:
    y0, y1 = ymax1, ymin2
elif ymax2 <= ymin1:
    y0, y1 = ymax2, ymin1
else:
    y0, y1 = y_left_inner, y_right_inner

taper_scale = 0.35
z_top_add_scale = 1.0

taper = W * taper_scale
z_top = z_cut + W * z_top_add_scale

p0 = (y0 - W, z_cut)
p1 = (y0 - W + taper, z_top)
p2 = (y1 + W - taper, z_top)
p3 = (y1 + W, z_cut)

leg_joiner_extrude_scale = 0.03
leg_joiner = (
    cq.Workplane("YZ", origin=(bb_leg.xmin, 0, 0))
    .polyline([p0, p1, p2, p3]).close()
    .extrude(-l * leg_joiner_extrude_scale)
)

handle = handle.union(leg).union(leg2).union(leg_joiner)
handle2 = handle.mirror("YZ")
handle = handle.union(handle2)
solid = solid.union(handle)

bb_leg_joiner = leg_joiner.val().BoundingBox()

base_joiner_p0_x_scale = 0.55
base_joiner_p0_y_scale = 0.1
base_joiner_p1_z_w_scale = 0.8
base_joiner_p2_subtract_h_scale = 1.0
base_joiner_p3_x_scale = 0.55
base_joiner_p3_y_scale = 1.1
base_joiner_extrude_w_scale = 1.0

p0 = (w * base_joiner_p0_x_scale, h * base_joiner_p0_y_scale)
p1 = (bb_leg_joiner.xmin, z_cut + W * base_joiner_p1_z_w_scale)
p2 = (bb_leg_joiner.xmin, z_cut + W * base_joiner_p1_z_w_scale - h * base_joiner_p2_subtract_h_scale)
p3 = (w * base_joiner_p3_x_scale, -h * base_joiner_p3_y_scale)

base_joiner = (
    cq.Workplane("XZ")
    .polyline([p0, p1, p2, p3]).close()
    .extrude(-w * base_joiner_extrude_w_scale)
)

base_joiner2 = base_joiner.mirror("ZY")
base_joiner = base_joiner.union(base_joiner2)

mid_width_scale = 0.8
mid_height_scale = 1.8
mid_translate_z_scale = 1.9

mid = (
    cq.Workplane("XZ")
    .rect(l * mid_width_scale, h * mid_height_scale)
    .extrude(-w)
    .translate(0, 0, -h * mid_translate_z_scale)
)

mid_cutter_p0_x_scale = 0.55
mid_cutter_p0_y_scale = 0.1
mid_cutter_p1_z_w_scale = 0.8
mid_cutter_p2_subtract_h_scale = 1.0
mid_cutter_extrude_w_scale = 0.5

p = (0, 0)
p0 = (w * mid_cutter_p0_x_scale, h * mid_cutter_p0_y_scale)
p1 = (bb_leg_joiner.xmin, z_cut + W * mid_cutter_p1_z_w_scale)
p2 = (bb_leg_joiner.xmin, z_cut + W * mid_cutter_p1_z_w_scale - h * mid_cutter_p2_subtract_h_scale)
p3 = (0, z_cut + W * mid_cutter_p1_z_w_scale - h * mid_cutter_p2_subtract_h_scale)

mid_cutter = (
    cq.Workplane("XZ")
    .polyline([p, p0, p1, p2, p3]).close()
    .extrude(-w * mid_cutter_extrude_w_scale)
)

mid_final = mid_cutter.intersect(mid)
mid_final2 = mid_final.mirror("XZY")

mid_final_translate_y_scale = 0.5
mid_final = mid_final.union(mid_final2).translate((0, -w * mid_final_translate_y_scale, 0))

solid = solid.union(base_joiner).union(mid_final)

show_object(solid)