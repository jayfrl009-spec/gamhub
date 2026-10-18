-- SCHOOL HORROR: SIMPLE MAP BUILDER
-- Place this Script in ServerScriptService, then press Play.

local Workspace = game:GetService("Workspace")
local Lighting = game:GetService("Lighting")

local old = Workspace:FindFirstChild("SchoolHorrorMap")
if old then old:Destroy() end

local map = Instance.new("Folder")
map.Name = "SchoolHorrorMap"
map.Parent = Workspace

Lighting.ClockTime = 0
Lighting.Brightness = 1
Lighting.FogStart = 25
Lighting.FogEnd = 160
Lighting.Ambient = Color3.fromRGB(45, 48, 58)
Lighting.OutdoorAmbient = Color3.fromRGB(20, 22, 30)

local function makePart(parent, name, size, position, color, material)
    local p = Instance.new("Part")
    p.Name = name
    p.Size = size
    p.Position = position
    p.Anchored = true
    p.Color = color or Color3.fromRGB(70, 72, 78)
    p.Material = material or Enum.Material.Concrete
    p.TopSurface = Enum.SurfaceType.Smooth
    p.BottomSurface = Enum.SurfaceType.Smooth
    p.Parent = parent
    return p
end

-- Floor, roof, and outer walls
makePart(map, "Floor", Vector3.new(100, 1, 70), Vector3.new(0, -0.5, 0), Color3.fromRGB(55, 57, 62))
makePart(map, "Roof", Vector3.new(100, 1, 70), Vector3.new(0, 14, 0), Color3.fromRGB(30, 32, 37))
makePart(map, "BackWall", Vector3.new(100, 14, 1), Vector3.new(0, 7, -35))
makePart(map, "LeftWall", Vector3.new(1, 14, 70), Vector3.new(-50, 7, 0))
makePart(map, "RightWall", Vector3.new(1, 14, 70), Vector3.new(50, 7, 0))
makePart(map, "FrontWallLeft", Vector3.new(38, 14, 1), Vector3.new(-31, 7, 35))
makePart(map, "FrontWallRight", Vector3.new(38, 14, 1), Vector3.new(31, 7, 35))

-- Hallway side walls
makePart(map, "HallLeftWall", Vector3.new(1, 12, 52), Vector3.new(-15, 6, -5), Color3.fromRGB(78, 80, 86))
makePart(map, "HallRightWall", Vector3.new(1, 12, 52), Vector3.new(15, 6, -5), Color3.fromRGB(78, 80, 86))

-- Lockers
for i = 1, 6 do
    local z = -27 + (i - 1) * 9
    makePart(map, "Locker_L_" .. i, Vector3.new(2, 6, 3), Vector3.new(-19, 3, z), Color3.fromRGB(28, 72, 110), Enum.Material.Metal)
    makePart(map, "Locker_R_" .. i, Vector3.new(2, 6, 3), Vector3.new(19, 3, z), Color3.fromRGB(28, 72, 110), Enum.Material.Metal)
end

-- Classroom doors and signs
for i = 1, 3 do
    local z = -23 + (i - 1) * 17
    local door = makePart(map, "ClassroomDoor_" .. i, Vector3.new(1, 8, 5), Vector3.new(-14, 4, z), Color3.fromRGB(105, 65, 43), Enum.Material.Wood)
    door.CanCollide = false
    local sign = Instance.new("BillboardGui")
    sign.Size = UDim2.fromOffset(130, 30)
    sign.StudsOffset = Vector3.new(0, 5, 0)
    sign.AlwaysOnTop = true
    sign.Parent = door
    local label = Instance.new("TextLabel")
    label.Size = UDim2.fromScale(1, 1)
    label.BackgroundTransparency = 1
    label.Text = "CLASSROOM " .. i
    label.TextColor3 = Color3.new(1, 1, 1)
    label.TextScaled = true
    label.Font = Enum.Font.GothamBold
    label.Parent = sign
end

-- Exit at the front
local exit = makePart(map, "EXIT", Vector3.new(10, 9, 1), Vector3.new(0, 4.5, 34), Color3.fromRGB(35, 190, 95), Enum.Material.Neon)
exit.Transparency = 0.25
exit.CanCollide = false
local prompt = Instance.new("ProximityPrompt")
prompt.ActionText = "Escape"
prompt.ObjectText = "School Exit"
prompt.HoldDuration = 1
prompt.MaxActivationDistance = 12
prompt.Parent = exit
prompt.Triggered:Connect(function(player)
    local gui = Instance.new("ScreenGui")
    gui.Name = "EscapeMessage"
    gui.ResetOnSpawn = false
    gui.Parent = player:WaitForChild("PlayerGui")
    local label = Instance.new("TextLabel")
    label.Size = UDim2.fromScale(0.6, 0.18)
    label.Position = UDim2.fromScale(0.2, 0.4)
    label.BackgroundColor3 = Color3.fromRGB(8, 12, 18)
    label.Text = "YOU ESCAPED... FOR NOW."
    label.TextColor3 = Color3.fromRGB(100, 255, 170)
    label.TextScaled = true
    label.Font = Enum.Font.GothamBlack
    label.Parent = gui
end)

local spawn = Instance.new("SpawnLocation")
spawn.Name = "HallwaySpawn"
spawn.Size = Vector3.new(6, 1, 6)
spawn.Position = Vector3.new(0, 0.2, 0)
spawn.Anchored = true
spawn.Neutral = true
spawn.Parent = map

-- Creepy block-built student
local npc = Instance.new("Model")
npc.Name = "SuspiciousStudent"
npc.Parent = map
makePart(npc, "Body", Vector3.new(2, 3, 1), Vector3.new(0, 2, -18), Color3.fromRGB(20, 20, 24), Enum.Material.SmoothPlastic)
local head = makePart(npc, "Head", Vector3.new(2, 1, 1), Vector3.new(0, 4, -18), Color3.fromRGB(190, 155, 125), Enum.Material.SmoothPlastic)
makePart(npc, "LeftLeg", Vector3.new(0.7, 2, 0.7), Vector3.new(-0.55, 0, -18), Color3.fromRGB(25, 25, 28))
makePart(npc, "RightLeg", Vector3.new(0.7, 2, 0.7), Vector3.new(0.55, 0, -18), Color3.fromRGB(25, 25, 28))
makePart(npc, "LeftArm", Vector3.new(0.6, 2.5, 0.6), Vector3.new(-1.3, 2, -18), Color3.fromRGB(25, 25, 28))
makePart(npc, "RightArm", Vector3.new(0.6, 2.5, 0.6), Vector3.new(1.3, 2, -18), Color3.fromRGB(25, 25, 28))

local face = Instance.new("SurfaceGui")
face.Face = Enum.NormalId.Front
face.Parent = head
local eyes = Instance.new("TextLabel")
eyes.Size = UDim2.fromScale(1, 1)
eyes.BackgroundTransparency = 1
eyes.Text = "●  ●"
eyes.TextColor3 = Color3.fromRGB(255, 35, 35)
eyes.TextScaled = true
eyes.Font = Enum.Font.GothamBlack
eyes.Parent = face

print("School Horror map created.")
