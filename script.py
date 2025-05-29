import os
import bpy
import numpy as np
import mathutils

path_to_trajectory = '/home/lark/Documents/Projects/HFMD/trajectory.xyz'
bonding = {0: [1,2], 3:[4,5]}

RADII = {'H':1.1, 'O':1.52}
SPHERE_SEGMENTS = 64
SPHERE_RINGS = 64
BOND_RADIUS = 0.5
COLORS = {'H': (1.0, 1.0, 1.0, 1.0), 'O':(1.0, 0.0, 0.0, 1.0), 'bond':(0.2, 0.2, 0.2, 1.0)}

render_path = '/home/lark/Renders/TwoWater/'

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def get_or_create_material(species):
    mat_name = species + '_mat'
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = COLORS[species]
            bsdf.inputs['Roughness'].default_value = 1.0
    return mat


def create_atom(species, location):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=RADII[species],
        segments=SPHERE_SEGMENTS,
        ring_count=SPHERE_RINGS,
        location=location
    )
    obj = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    obj.name = species
    obj.data.name = obj.name
    # Assign material
    mat = get_or_create_material(species)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def create_bond(coord1, coord2):
    vec = mathutils.Vector(coord2) - mathutils.Vector(coord1)
    length = vec.length
    bpy.ops.mesh.primitive_cylinder_add(
        radius = BOND_RADIUS,
        depth = length,
        location = (0,0,0)
    )
    cylinder = bpy.context.active_object
    # Aligning
    cylinder.location = (mathutils.Vector(coord1) + mathutils.Vector(coord2))/2
    cylinder.rotation_mode = 'QUATERNION'
    cylinder.rotation_quaternion = vec.to_track_quat('Z', 'Y')
    mat = get_or_create_material('bond')
    if cylinder.data.materials:
        cylinder.data.materials[0] = mat
    else:
        cylinder.data.materials.append(mat)

def parse_geom(geom):
    n_atom = int(geom[0].strip())
    # Parse the geometry string
    species = []
    coords = np.zeros((n_atom, 3))
    for i in range(2, n_atom+2):
        s, x, y, z = geom[i].strip().split()
        species.append(s)
        x = float(x)
        y = float(y)
        z = float(z)
        coords[i-2, :] = [x,y,z]
    return species, coords

def build_molecule(geom):
    species, coords = parse_geom(geom)
    # Add the spheres representing the atoms
    for i in range(len(species)):
        create_atom(species[i], coords[i,:])
        #if i in bonding.keys():
            # Add cylinders representing bonds
            #for j in bonding[i]:
            #    create_bond(coords[i,:], coords[j,:])

def update_molecule(geom, frame_nr):
    species, coords = parse_geom(geom)
    species_count = {}
    for i in range(len(species)):
        count = species_count.get(species[i], 0)
        if count==0:
            obj_name = species[i]
        else:
            obj_name = species[i] + f'.{count:03d}'
        count += 1
        species_count[species[i]] = count
        obj = bpy.data.objects[obj_name]
        obj.location = coords[i,:]
        obj.keyframe_insert(data_path='location', frame=frame_nr)


def setup_basic_scene():
    # Setup light
    bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.transform.rotate(value=1.5708, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
    bpy.context.object.data.energy = 4
    # Camera
    bpy.ops.object.camera_add(enter_editmode=False,
                                align='VIEW',
                                location=(0, 0, 0),
                                rotation=(0, 0, 0),
                                scale=(1, 1, 1))
    # Move camera along x-axis
    bpy.ops.transform.translate(value=(9.10401, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
    # Rotate it so z-axis is up
    bpy.ops.transform.rotate(value=1.5708, orient_axis='Y', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, True, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
    bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
    # Set to orthographic and change scale and shift
    bpy.context.object.data.type = 'ORTHO'
    bpy.context.object.data.ortho_scale = 14.1
    bpy.context.object.data.shift_x = -0.16
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.render.resolution_x = 600
    bpy.context.scene.render.resolution_y = 600
    # Color management
    bpy.context.scene.render.image_settings.color_management = 'OVERRIDE'
    bpy.context.scene.render.image_settings.view_settings.view_transform = 'Standard'
    # World
    bpy.context.scene.world.cycles_visibility.diffuse = False
    bpy.context.scene.world.cycles_visibility.glossy = False
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 100


def animate_trajectory(filepath):
    with open(filepath, 'r') as infile:
        lines = infile.readlines()
    n_atom = int(lines[0].strip())
    lines_per_geom = n_atom + 3
    n_geoms = len(lines) // lines_per_geom
    for i in range(n_geoms):
        if i==0:
            clear_scene()
            setup_basic_scene()
            build_molecule(lines[i*lines_per_geom:(i+1)*lines_per_geom])
        else:
            update_molecule(lines[i*lines_per_geom:(i+1)*lines_per_geom], i)
        #bpy.context.scene.render.filepath = os.path.join(render_path, f'Frame_{i:03d}.png')
        #bpy.ops.render.render(write_still=True);

animate_trajectory(path_to_trajectory)
