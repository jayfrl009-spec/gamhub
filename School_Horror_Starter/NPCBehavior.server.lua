-- SIMPLE CREEPY STUDENT AI
-- Place this Script in ServerScriptService alongside MapBuilder.
-- The block-built student slowly follows the nearest player.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local map = workspace:WaitForChild("SchoolHorrorMap")
local npc = map:WaitForChild("SuspiciousStudent")
local speed = 4
local followDistance = 60

RunService.Heartbeat:Connect(function(dt)
    local body = npc:FindFirstChild("Body")
    if not body then return end

    local nearestRoot
    local nearestDistance = math.huge
    for _, player in ipairs(Players:GetPlayers()) do
        local character = player.Character
        local root = character and character:FindFirstChild("HumanoidRootPart")
        if root then
            local distance = (root.Position - body.Position).Magnitude
            if distance < nearestDistance then
                nearestDistance = distance
                nearestRoot = root
            end
        end
    end

    if not nearestRoot or nearestDistance > followDistance then return end
    local target = Vector3.new(nearestRoot.Position.X, body.Position.Y, nearestRoot.Position.Z)
    local offset = target - body.Position
    if offset.Magnitude < 2 then return end

    local step = offset.Unit * math.min(speed * dt, offset.Magnitude - 1.5)
    local move = Vector3.new(step.X, 0, step.Z)
    for _, part in ipairs(npc:GetChildren()) do
        if part:IsA("BasePart") then
            part.Position += move
        end
    end
end)
