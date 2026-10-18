# School Horror Blender Local Bridge

A starter Blender add-on for making simple Roblox school-horror props and preparing a local command endpoint.

## Important limitation

This add-on runs on your PC and listens only on `127.0.0.1` (your own computer). This does **not** automatically connect this ChatGPT web conversation to Blender. ChatGPT custom MCP write integrations depend on account/workspace support; local servers also need an approved connection method. Do not expose this endpoint to the public internet.

## Install the add-on

1. Download `school_horror_bridge.py` from this folder.
2. Open Blender.
3. Go to **Edit → Preferences → Add-ons** (in newer Blender versions, use **Get Extensions** only for extension-store items; for a local script use the install add-on option if available).
4. Install the `.py` file and enable **School Horror Local Bridge**.
5. In the 3D View, press **N** to open the sidebar and select **Horror Bridge**.
6. Click **Build Creepy Locker**, **Build School Desk**, or **Build Classroom Door** to test asset generation.
7. Click **Start Local Bridge** only when you need the local endpoint. The token is printed in Blender's system console. Keep it private.

## Local endpoint

The add-on accepts only predefined asset names:
- `locker`
- `school_desk`
- `classroom_door`

It rejects arbitrary code and listens on loopback only. Example request from a local Python client (replace TOKEN with the temporary token printed by Blender):

```python
import json
import urllib.request

token = "TOKEN"
payload = json.dumps({"asset": "locker"}).encode("utf-8")
request = urllib.request.Request(
    "http://127.0.0.1:8765/build",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
    },
    method="POST",
)
print(urllib.request.urlopen(request).read().decode("utf-8"))
```

This is a prototype. It does not yet include a ChatGPT-compatible MCP server or automatic Roblox export. The endpoint is intended for trusted local tools only; never forward the port or remove its token check.
