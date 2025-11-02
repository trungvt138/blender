import bpy, json, os, sys

def grab(obj, fields):
    out = {}
    for f in fields:
        if hasattr(obj, f):
            v = getattr(obj, f)
            try:
                out[f] = v if isinstance(v, (int,float,str,bool)) else str(v)
            except:
                out[f] = str(v)
    return out

def dump():
    scn = bpy.context.scene
    data = {
        "blender_version": bpy.app.version_string,
        "filepath": bpy.data.filepath,
        "render_engine": scn.render.engine,
        "render": grab(scn.render, [
            "resolution_x","resolution_y","resolution_percentage",
            "fps","fps_base","film_transparent","use_motion_blur",
            "tile_x","tile_y","use_high_quality_normals","use_overwrite",
            "use_placeholder","use_file_extension","use_persistent_data"
        ]),
        "output": {
            "file_format": scn.render.image_settings.file_format,
            "color_mode": scn.render.image_settings.color_mode,
            "color_depth": scn.render.image_settings.color_depth,
            "compression": scn.render.image_settings.compression,
        },
        "units": grab(scn.unit_settings, [
            "system","scale_length","length_unit","mass_unit","time_unit",
            "temperature_unit","use_separate","system_rotation"
        ]),
        "color_management": {
            "display_device": scn.display_settings.display_device,
            "view_transform": scn.view_settings.view_transform,
            "look": scn.view_settings.look,
            "gamma": scn.view_settings.gamma,
            "exposure": scn.view_settings.exposure
        },
        "world": (
            {"use_nodes": scn.world.use_nodes if scn.world else None,
             "color": tuple(scn.world.color) if scn.world and not scn.world.use_nodes else None}
        ),
        "view_layer": {
            "name": bpy.context.view_layer.name,
            "use_pass_cryptomatte_object": bpy.context.view_layer.use_pass_cryptomatte_object,
            "use_pass_cryptomatte_material": bpy.context.view_layer.use_pass_cryptomatte_material
        },
        "engine_specific": {}
    }

    # Cycles
    if scn.render.engine == 'CYCLES':
        cyc = scn.cycles
        data["engine_specific"]["cycles"] = grab(cyc, [
            "device","samples","preview_samples","use_adaptive_sampling",
            "adaptive_min_samples","adaptive_threshold",
            "use_denoising","use_fast_gi","use_progressive_refine",
            "blur_glossy","max_bounces","diffuse_bounces","glossy_bounces",
            "transmission_bounces","transparent_max_bounces"
        ])

    # Eevee / Eevee-Next
    if scn.render.engine.startswith('BLENDER_EEVEE'):
        ee = scn.eevee
        data["engine_specific"]["eevee"] = grab(ee, [
            "use_gtao","gtao_distance","gtao_factor","gtao_quality",
            "use_ssr","ssr_quality","ssr_thickness","ssr_max_roughness",
            "use_bloom","bloom_intensity","bloom_threshold",
            "shadow_cube_size","shadow_cascade_size","gi_irradiance_smoothing"
        ])

    # A light snapshot of objects: count modifiers by type (avoids huge dumps)
    mod_counts = {}
    for ob in bpy.data.objects:
        for m in ob.modifiers:
            mod_counts[m.type] = mod_counts.get(m.type, 0) + 1
    data["modifier_summary"] = mod_counts

    # Write JSON next to the .blend
    base = os.path.splitext(os.path.basename(bpy.data.filepath))[0] or "unsaved"
    out_path = os.path.join(os.path.dirname(bpy.data.filepath) or os.getcwd(), f"{base}_settings.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("WROTE", out_path)

dump()
