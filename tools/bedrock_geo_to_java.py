#!/usr/bin/env python3
"""
Bedrock .geo.json + texture  ->  Java (Mojang-mapped, MC 1.21.11) EntityModel + repacked texture.

Why a repack? Bedrock per-face UVs can't be expressed by Java's box-UV cubes, so every cube
gets its own slot in a new atlas laid out the way Java expects, and the pixels of each face are
copied into it. Cube *geometry* is decoupled from UV size with CubeDeformation.

Usage:
  python3 bedrock_geo_to_java.py GEO.json TEXTURE.png OUT_MODEL.java OUT_TEXTURE.png PACKAGE

Conventions (set FLIP_X if the result looks left/right mirrored):
  x/z same as Bedrock, y flipped (java_y = 24 - bedrock_y); rotation (rx,ry,rz) -> (rx,-ry,-rz).
"""
import json, math, sys
from PIL import Image

FLIP_X = False  # set True if the converted model appears mirrored left<->right

geo_path, tex_path, out_java, out_tex, package = sys.argv[1:6]
geo = json.load(open(geo_path))["minecraft:geometry"][0]
src = Image.open(tex_path).convert("RGBA")
SW, SH = src.size
TW0 = geo["description"].get("texture_width", SW)
TH0 = geo["description"].get("texture_height", SH)
sx_scale, sy_scale = SW / TW0, SH / TH0  # in case texture was upscaled

bones = {b["name"]: b for b in geo["bones"]}
children = {}
for b in geo["bones"]:
    children.setdefault(b.get("parent"), []).append(b["name"])

def has_cubes(name):
    b = bones[name]
    return bool(b.get("cubes")) or any(has_cubes(c) for c in children.get(name, []))

def fx(x):  # x-flip option
    return -x if FLIP_X else x

# ---------- pass 1: collect every cube + its UV slot size ----------
cubes = []  # dicts

def slot_dims(cu):
    uv = cu["uv"]
    def a(face, k):  # abs size of face along axis k
        d = uv.get(face)
        return abs(d["uv_size"][k]) if d else 0
    sxv = max(a("north", 0), a("south", 0), a("up", 0), a("down", 0))
    syv = max(a("north", 1), a("south", 1), a("east", 1), a("west", 1))
    szv = max(a("east", 0), a("west", 0), a("up", 1), a("down", 1))
    S = []
    for v, real in zip((sxv, syv, szv), cu["size"]):
        v = int(round(v))
        if v == 0 and real > 0.01:
            v = 1
        S.append(v)
    return S

for name, b in bones.items():
    for i, cu in enumerate(b.get("cubes", [])):
        cubes.append({"bone": name, "cu": cu, "S": slot_dims(cu)})

# ---------- shelf-pack atlas ----------
ATLAS_W = 256
for c in cubes:
    SX, SY, SZ = c["S"]
    c["w"], c["h"] = 2 * SZ + 2 * SX, SZ + SY
order = sorted(range(len(cubes)), key=lambda i: -cubes[i]["h"])
x = y = shelf_h = 0
for i in order:
    c = cubes[i]
    if x + c["w"] > ATLAS_W:
        x, y, shelf_h = 0, y + shelf_h, 0
    c["U"], c["V"] = x, y
    x += c["w"]
    shelf_h = max(shelf_h, c["h"])
ATLAS_H = y + shelf_h
atlas = Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))

def sample(u, v):
    px = int(math.floor(u * sx_scale)); py = int(math.floor(v * sy_scale))
    if 0 <= px < SW and 0 <= py < SH:
        return src.getpixel((px, py))
    return (0, 0, 0, 0)

def copy_face(face_uv, slot_x, slot_y, W, H, flip_t):
    if not face_uv or W <= 0 or H <= 0:
        return
    u, v = face_uv["uv"]; uw, vh = face_uv["uv_size"]
    for j in range(H):
        tp = (j + 0.5) / H
        t = 1 - tp if flip_t else tp
        for i in range(W):
            s = (i + 0.5) / W
            atlas.putpixel((slot_x + i, slot_y + j), sample(u + s * uw, v + t * vh))

for c in cubes:
    SX, SY, SZ = c["S"]; U, V = c["U"], c["V"]; uv = c["cu"]["uv"]
    copy_face(uv.get("north"), U + SZ,               V + SZ, SX, SY, False)
    copy_face(uv.get("east"),  U,                    V + SZ, SZ, SY, False)
    copy_face(uv.get("south"), U + SZ + SX + SZ,     V + SZ, SX, SY, False)
    copy_face(uv.get("west"),  U + SZ + SX,          V + SZ, SZ, SY, False)
    copy_face(uv.get("up"),    U + SZ,               V,      SX, SZ, False)
    copy_face(uv.get("down"),  U + SZ + SX,          V,      SX, SZ, True)
atlas.save(out_tex)

# ---------- pass 2: emit Java ----------
def F(v):
    s = f"{v:.5f}".rstrip("0").rstrip(".")
    if s in ("", "-0"): s = "0"
    return s + "F"

lines = []
counter = [0]
def new_var():
    counter[0] += 1
    return f"p{counter[0]}"

cube_lookup = {}
for c in cubes:
    cube_lookup.setdefault(c["bone"], []).append(c)

def box_code(c, ref):
    cu = c["cu"]; SX, SY, SZ = c["S"]
    ox, oy, oz = cu["origin"]; w, h, d = cu["size"]
    rx = fx(ox) - fx(ref[0]) if not FLIP_X else (-(ox + w)) - (-ref[0])
    ry = ref[1] - oy - h
    rz = oz - ref[2]
    gx, gy, gz = (w - SX) / 2, (h - SY) / 2, (d - SZ) / 2
    return (f".texOffs({c['U']}, {c['V']}).addBox({F(rx + gx)}, {F(ry + gy)}, {F(rz + gz)}, "
            f"{SX}F, {SY}F, {SZ}F, new CubeDeformation({F(gx)}, {F(gy)}, {F(gz)}))")

def rot_args(rot):
    rx, ry, rz = rot
    return f"r({F(rx)}), r({F(-ry)}), r({F(-rz)})"

paths = {}  # bone -> list of names from root

def emit(name, parent_var, parent_pivot, path):
    b = bones[name]
    piv = b.get("pivot", [0, 0, 0])
    dx = fx(piv[0]) - fx(parent_pivot[0])
    dy = parent_pivot[1] - piv[1]
    dz = piv[2] - parent_pivot[2]
    plain = [c for c in cube_lookup.get(name, []) if "rotation" not in c["cu"] or not any(c["cu"]["rotation"])]
    rotated = [c for c in cube_lookup.get(name, []) if c not in plain]
    cl = "CubeListBuilder.create()" + "".join(box_code(c, piv) for c in plain)
    rot = b.get("rotation", [0, 0, 0])
    pose = (f"PartPose.offsetAndRotation({F(dx)}, {F(dy)}, {F(dz)}, {rot_args(rot)})"
            if any(rot) else f"PartPose.offset({F(dx)}, {F(dy)}, {F(dz)})")
    v = new_var()
    lines.append(f'        PartDefinition {v} = {parent_var}.addOrReplaceChild("{name}", {cl}, {pose});')
    paths[name] = path + [name]
    for k, c in enumerate(rotated):
        cu = c["cu"]; cp = cu.get("pivot", piv)
        cdx, cdy, cdz = fx(cp[0]) - fx(piv[0]), piv[1] - cp[1], cp[2] - piv[2]
        lines.append(
            f'        {v}.addOrReplaceChild("c{k}", CubeListBuilder.create(){box_code(c, cp)}, '
            f'PartPose.offsetAndRotation({F(cdx)}, {F(cdy)}, {F(cdz)}, {rot_args(cu["rotation"])}));')
    for ch in children.get(name, []):
        if has_cubes(ch):
            emit(ch, v, piv, paths[name])

roots = [n for n in children.get(None, []) if has_cubes(n)]
for r in roots:
    emit(r, "root", [0, 24, 0] if False else [0, 24, 0], [])
# note: roots are placed with pivot-parent (0,24,0) => java abs y = 24 - bedrock y (see below)

# fix: root-level offsets must be absolute java coords => parent pivot in bedrock coords is (0,24,0)->dy = 24 - piv_y.

def getchain(name):
    return "".join(f'.getChild("{p}")' for p in paths[name])

def find(*cands):
    for c in cands:
        if c in paths:
            return c
    return None

head = find("Head"); lleg = find("LeftLeg"); rleg = find("RightLeg")
fields = []; inits = []
for field, bone in (("head", head), ("leftLeg", lleg), ("rightLeg", rleg)):
    if bone:
        fields.append(f"    private final ModelPart {field};")
        inits.append(f"        this.{field} = root{getchain(bone)};")
anim = []
if head:
    anim.append("        this.head.yRot += state.yRot * ((float) Math.PI / 180F) * 0.6F;")
    anim.append("        this.head.xRot += state.xRot * ((float) Math.PI / 180F) * 0.6F;")
if lleg:
    anim.append("        this.leftLeg.xRot += Mth.cos(pos * 0.6662F) * 1.0F * speed;")
if rleg:
    anim.append("        this.rightLeg.xRot += Mth.cos(pos * 0.6662F + (float) Math.PI) * 1.0F * speed;")

java = f"""package {package};

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.util.Mth;

/** GENERATED by tools/bedrock_geo_to_java.py from {geo["description"]["identifier"]} - do not edit by hand. */
public class PenguinModel extends EntityModel<LivingEntityRenderState> {{
{chr(10).join(fields)}

    public PenguinModel(ModelPart root) {{
        super(root);
{chr(10).join(inits)}
    }}

    private static float r(float degrees) {{
        return degrees * (float) Math.PI / 180F;
    }}

    public static LayerDefinition createLayer() {{
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
{chr(10).join(lines)}
        return LayerDefinition.create(mesh, {ATLAS_W}, {ATLAS_H});
    }}

    @Override
    public void setupAnim(LivingEntityRenderState state) {{
        super.setupAnim(state);
        float pos = state.walkAnimationPos;
        float speed = state.walkAnimationSpeed;
{chr(10).join(anim)}
    }}
}}
"""
open(out_java, "w").write(java)
print(f"cubes={len(cubes)} bones_emitted={counter[0]} atlas={ATLAS_W}x{ATLAS_H} legs={lleg},{rleg} head={head}")
