bl_info = {
    "name": "School Horror Local Bridge",
    "author": "OpenAI",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Horror Bridge",
    "description": "Local-only, token-protected asset commands for a Roblox school horror workflow",
    "category": "3D View",
}

import bpy
import json
import queue
import secrets
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

_COMMANDS = queue.Queue()
_SERVER = None
_SERVER_THREAD = None
_TOKEN = None
_TIMER_REGISTERED = False

# Only these safe, predefined build actions are accepted. No arbitrary Python/code.
ALLOWED_ASSETS = {"locker", "school_desk", "classroom_door"}


def _material(name, color, metallic=0.0, roughness=0.7):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.diffuse_color = (*color, 1.0)
    mat.metallic = metallic
    mat.roughness = roughness
    return mat


def _cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj


def _build_asset(asset):
    metal = _material("HorrorBridge_DullMetal", (0.18, 0.20, 0.22), metallic=0.55)
    dark = _material("HorrorBridge_DarkTrim", (0.045, 0.05, 0.06), metallic=0.2)
    wood = _material("HorrorBridge_WornWood", (0.28, 0.20, 0.13), roughness=0.9)
    glass = _material("HorrorBridge_FrostedGlass", (0.12, 0.18, 0.19), roughness=0.3)

    if asset == "locker":
        root = _cube("SchoolLocker", (0, 0, 1.0), (0.85, 0.55, 2.0), metal)
        _cube("Locker_DoorPanel", (0, -0.285, 1.0), (0.76, 0.035, 1.9), dark)
        _cube("Locker_DoorInset", (0, -0.308, 1.0), (0.68, 0.018, 1.82), metal)
        _cube("Locker_Handle", (0.25, -0.34, 1.0), (0.035, 0.025, 0.16), dark)
        for z in (1.55, 1.62, 1.69):
            _cube("Locker_Vent", (0, -0.33, z), (0.25, 0.018, 0.018), dark)
        root["asset_type"] = "locker"
    elif asset == "school_desk":
        _cube("SchoolDesk_Top", (0, 0, 0.82), (1.2, 0.8, 0.12), wood)
        for x in (-0.48, 0.48):
            for y in (-0.28, 0.28):
                _cube("SchoolDesk_Leg", (x, y, 0.4), (0.055, 0.055, 0.78), dark)
        _cube("SchoolDesk_FrontPanel", (0, 0.34, 0.59), (0.85, 0.045, 0.32), wood)
    elif asset == "classroom_door":
        _cube("ClassroomDoor_Frame", (0, 0, 1.1), (1.25, 0.16, 2.2), dark)
        _cube("ClassroomDoor", (0, -0.095, 1.1), (1.08, 0.08, 2.05), wood)
        _cube("Door_Window", (0, -0.15, 1.55), (0.45, 0.025, 0.38), glass)
        _cube("Door_Handle", (0.38, -0.16, 1.0), (0.06, 0.04, 0.12), metal)
    else:
        raise ValueError("Unsupported asset")

    # Put the created asset in a collection for easy selection/export.
    collection_name = "SchoolHorror_Assets"
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
    for obj in list(bpy.context.selected_objects):
        for old_collection in list(obj.users_collection):
            old_collection.objects.unlink(obj)
        collection.objects.link(obj)
    return asset


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/build":
            self.send_error(404)
            return
        if self.headers.get("Authorization") != "Bearer " + _TOKEN:
            self.send_error(401)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 4096:
                self.send_error(400, "Invalid request size")
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            asset = payload.get("asset")
            if asset not in ALLOWED_ASSETS:
                self.send_error(400, "Allowed assets: locker, school_desk, classroom_door")
                return
            _COMMANDS.put(asset)
            body = json.dumps({"queued": True, "asset": asset}).encode("utf-8")
            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.send_error(400, "Invalid JSON")
    def log_message(self, *_args):
        pass


def _process_queue():
    while not _COMMANDS.empty():
        asset = _COMMANDS.get_nowait()
        try:
            _build_asset(asset)
            print("[Horror Bridge] Built:", asset)
        except Exception as exc:
            print("[Horror Bridge] Build failed:", exc)
    return 0.25


def _start_server():
    global _SERVER, _SERVER_THREAD, _TOKEN, _TIMER_REGISTERED
    if _SERVER is not None:
        return
    _TOKEN = secrets.token_urlsafe(24)
    try:
        _SERVER = HTTPServer(("127.0.0.1", 8765), _Handler)
        _SERVER.timeout = 0.5
        _SERVER_THREAD = threading.Thread(target=_SERVER.serve_forever, daemon=True)
        _SERVER_THREAD.start()
        if not _TIMER_REGISTERED:
            bpy.app.timers.register(_process_queue, first_interval=0.25, persistent=True)
            _TIMER_REGISTERED = True
        print("[Horror Bridge] Listening only on 127.0.0.1:8765")
        print("[Horror Bridge] Temporary token (keep private):", _TOKEN)
        return True, "Bridge started. Copy the token from Blender's system console."
    except Exception as exc:
        _SERVER = None
        return False, "Could not start bridge: " + str(exc)


def _stop_server():
    global _SERVER, _SERVER_THREAD, _TOKEN
    if _SERVER:
        _SERVER.shutdown()
        _SERVER.server_close()
    _SERVER = None
    _SERVER_THREAD = None
    _TOKEN = None
    return True, "Bridge stopped."


class HORRORBRIDGE_OT_start(bpy.types.Operator):
    bl_idname = "horror_bridge.start"
    bl_label = "Start Local Bridge"
    def execute(self, context):
        ok, message = _start_server()
        self.report({'INFO' if ok else 'ERROR'}, message)
        return {'FINISHED' if ok else 'CANCELLED'}


class HORRORBRIDGE_OT_stop(bpy.types.Operator):
    bl_idname = "horror_bridge.stop"
    bl_label = "Stop Local Bridge"
    def execute(self, context):
        _stop_server()
        self.report({'INFO'}, "Bridge stopped.")
        return {'FINISHED'}


class HORRORBRIDGE_OT_build(bpy.types.Operator):
    bl_idname = "horror_bridge.build_asset"
    bl_label = "Build Asset"
    asset: bpy.props.EnumProperty(
        items=[
            ("locker", "Creepy Locker", "Build a school locker"),
            ("school_desk", "School Desk", "Build a school desk"),
            ("classroom_door", "Classroom Door", "Build a classroom door"),
        ],
        default="locker",
    )
    def execute(self, context):
        _build_asset(self.asset)
        self.report({'INFO'}, "Created " + self.asset)
        return {'FINISHED'}


class HORRORBRIDGE_PT_panel(bpy.types.Panel):
    bl_label = "School Horror Bridge"
    bl_idname = "HORRORBRIDGE_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Horror Bridge"
    def draw(self, context):
        layout = self.layout
        layout.label(text="Local-only command bridge")
        layout.operator("horror_bridge.start")
        layout.operator("horror_bridge.stop")
        layout.separator()
        for asset, label in [
            ("locker", "Build Creepy Locker"),
            ("school_desk", "Build School Desk"),
            ("classroom_door", "Build Classroom Door"),
        ]:
            op = layout.operator("horror_bridge.build_asset", text=label)
            op.asset = asset
        layout.label(text="HTTP: 127.0.0.1:8765/build")


_CLASSES = (
    HORRORBRIDGE_OT_start,
    HORRORBRIDGE_OT_stop,
    HORRORBRIDGE_OT_build,
    HORRORBRIDGE_PT_panel,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    _stop_server()
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
