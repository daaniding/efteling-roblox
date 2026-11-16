-- Gondoletta-water naast de Pagode (zelfde oeverlijnen als build/16_gondoletta.py). Draai NA plaats_pagode.luau.
-- Waterpeil NAP 9.25, bodem NAP 8.0; land eromheen vlak gras NAP 9.5 tot x 445; eilandjes gras NAP 9.6.
-- Terrein (grond) rendert ~2 stud boven de FillBlock-bovenkant: daar -2 stud. WATER niet: gemeten in Studio
-- (bovenkant Y -0.25 -> peil NAP 8.77, +1.20 -> 9.73, +0.47 -> 9.49): voor NAP ~9.3 de bovenkant op Y +0.28.
local S, G = 3, 2
local t = workspace.Terrain
local function Y(nap) return G + (nap - 10) * S - 2 end
local BODEM = G - 30
local BX, BY = 397.0, 52.5

local OEVER = {{-20, 386.0}, {-10, 388.6}, {0, 387.0}, {10, 388.2}, {20, 390.0}, {30, 390.7}, {40, 389.3}, {45, 388.5}}
local function xw(y)
  if y <= OEVER[1][1] then return OEVER[1][2] end
  for i = 1, #OEVER - 1 do
    local a, b = OEVER[i], OEVER[i + 1]
    if y >= a[1] and y <= b[1] then return a[2] + (b[2] - a[2]) * (y - a[1]) / (b[1] - a[1]) end
  end
  return OEVER[#OEVER][2]
end
local function yn(x)                     -- noordoever (zuidrand van het noordpad)
  if x < 412 then return 66.5 elseif x < 420 then return 66.5 + (x - 412) * 0.45 elseif x < 430 then return 70.1 + (x - 420) * 0.4 end
  return 74.1 + (x - 430) * 0.2
end
local EILAND = {{414.3, 45.0, 2.4, 4.4}, {397.5, 7.5, 2.6, 4.8}}

local function water(x, y)
  if x > 445 then return false end
  local r = math.sqrt((x - BX) ^ 2 + (y - BY) ^ 2)
  if r < 8.7 then return false end                       -- platform
  for _, e in ipairs(EILAND) do if ((x - e[1]) / e[3]) ^ 2 + ((y - e[2]) / e[4]) ^ 2 < 1 then return false end end
  if x > 403 and x < 411.6 and y > 60.8 then return false end   -- vlonder bij de steiger
  if r < 14.5 then return true end                        -- ring van het havenbekken
  if y < -12 and x > 371 then return true end            -- zuidwestarm
  if y < 45 then
    if x > 425.5 and y > 8 and y < 60 then return false end      -- bomenstrook oostoever
    return x > xw(y)
  end
  if x > 405 and y < yn(x) then return not (x > 425.5 and y < 60) end
  return false
end

-- land eerst: vlak gras tot x 445 (oost van het AHN-stuk)
local function vul(x0, x1, y0, y1, nap, mat)
  t:FillBlock(CFrame.new((x0 + x1) / 2 * S, (Y(nap) + BODEM) / 2, -(y0 + y1) / 2 * S), Vector3.new((x1 - x0) * S, Y(nap) - BODEM, (y1 - y0) * S), mat)
end
vul(430, 445, -20, 112, 9.5, Enum.Material.Grass)
vul(385, 430, -20, 15, 9.5, Enum.Material.Grass)
vul(300, 385, -20, 15, 9.5, Enum.Material.Grass)          -- zuid van het AHN-stuk

local nw, ne = 0, 0
for x = 371, 444 do
  for y = -20, 79 do
    local cx, cy = x + 0.5, y + 0.5
    if water(cx, cy) then
      t:FillBlock(CFrame.new(cx * S, 6, -cy * S), Vector3.new(S, 112, S), Enum.Material.Air)
      t:FillBlock(CFrame.new(cx * S, (Y(8.0) + BODEM) / 2, -cy * S), Vector3.new(S, Y(8.0) - BODEM, S), Enum.Material.Mud)
      t:FillBlock(CFrame.new(cx * S, (0.28 + Y(8.0)) / 2, -cy * S), Vector3.new(S, 0.28 - Y(8.0), S), Enum.Material.Water)
      nw += 1
    else
      for _, e in ipairs(EILAND) do
        if ((cx - e[1]) / (e[3] + 0.3)) ^ 2 + ((cy - e[2]) / (e[4] + 0.3)) ^ 2 < 1 then
          t:FillBlock(CFrame.new(cx * S, (Y(9.6) + BODEM) / 2, -cy * S), Vector3.new(S, Y(9.6) - BODEM, S), Enum.Material.Grass)
          ne += 1
        end
      end
    end
    if (x * 100 + y) % 400 == 0 then task.wait() end
  end
end
return "water " .. nw .. " kolommen, eiland " .. ne
