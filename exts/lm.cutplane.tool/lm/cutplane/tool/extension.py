import omni.ext
import omni.ui as ui
import omni.kit.commands
from pxr import Usd, UsdGeom, Sdf, Tf, Gf

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class CutplaneTool(omni.ext.IExt):

    # Activate or deactivate a plane on the given axis
    # @param isOn   Checks if the plane is currently active
    # @param axis   Specifies which axis the plane is constrained to, i.e. "X"
    def spawn_plane(self, isOn, axis):
        transformVecs = {"Z": Gf.Vec3d(90, 0.0, 0.0), "Y": Gf.Vec3d(0.0, 0.0, 0.0), "X": Gf.Vec3d(0.0, 0.0, 90)}
        if isOn:
            omni.kit.commands.execute('CreateMeshPrim', prim_type="Plane",
                                attributes={})
            omni.kit.commands.execute('MovePrims', paths_to_move={'/World/Plane': '/World/lm_cutplane_tool/' + axis + 'Plane'})
            omni.kit.commands.execute('TransformPrimSRT', path=Sdf.Path('/World/lm_cutplane_tool/' + axis + 'Plane'),
	                new_rotation_euler=transformVecs[axis], old_rotation_euler=Gf.Vec3d(0.0, 0.0, 0.0))
        else:
            omni.kit.commands.execute('DeletePrims', paths=['/World/lm_cutplane_tool/' + axis + 'Plane'])

    # Translate the given plane along its axis by the given amount, if it is active
    # @param isOn   Checks if the plane is currently active
    # @param value  The amount by which to translate the plane, multiplied by 100
    # @param axis   Speficies which plane is being shited, i.e. "X"
    def move_plane(self, isOn, value, axis):
        transformVecs = {"X": Gf.Vec3d(value*100, 0.0, 0.0), "Y": Gf.Vec3d(0.0, value*100, 0.0), "Z": Gf.Vec3d(0.0, 0.0, value*100)}
        if isOn:
            omni.kit.commands.execute('TransformPrimSRT',
	            path=Sdf.Path('/World/lm_cutplane_tool/' + axis + 'Plane'),
                new_translation=transformVecs[axis],
	            old_translation=Gf.Vec3d(0.0, 0.0, 0.0))
        else:
            print('[lm.cutplane.tool] Activate ' + axis + ' cutplane first')

    # Abstract container for setting up UI elements and functions
    # @param axis   Which plane this UI element controls
    def plane_stack(self, axis):
        with ui.HStack():
            label = ui.Label(axis + "-axis")
            box = ui.CheckBox()
            box.model.add_value_changed_fn(lambda x: self.spawn_plane(box.model.get_value_as_bool(), axis))
            val = ui.FloatDrag()
            val.model.add_value_changed_fn(lambda x: self.move_plane(box.model.get_value_as_bool(),
            val.model.get_value_as_float(), axis))
    
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[lm.cutplane.tool] Cut Plane Tool startup")

        self._window = ui.Window("Cut plane tool", width=300, height=300)   # Intialize an empty UI window
        self._active_planes = {"X": False, "Y": False, "Z": False}  # Used to track which plane(s) is/are active, if any

        # Create a unique scope in the stage to store the cut planes in
        # This helps keep the user from creating path conflicts
        omni.kit.commands.execute('CreatePrimWithDefaultXform', prim_type='Scope', attributes={}, select_new_prim=False)
        omni.kit.commands.execute('MovePrims', paths_to_move={'/World/Scope': '/World/lm_cutplane_tool'})

        # Set up the UI window
        with self._window.frame:
            with ui.VStack():
                x = self.plane_stack("X")
                y = self.plane_stack("Y")
                z = self.plane_stack("Z")

    # Shut down the extension and remove any active planes from the scene
    def on_shutdown(self):
        # Remove any active planes from the scene
        for plane in self._active_planes:
            if self._active_planes[plane]:
                omni.kit.commands.exectue('DeletePrims', paths=['/World/lm_cutplane_tool/' + plane + 'Plane'])

        omni.kit.commands.execute('DeletePrims', paths=['/World/lm_cutplane_tool'])

        print("[lm.cutplane.tool] Cut Plane Tool shutdown")
