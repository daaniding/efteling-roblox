-- Kopie van de ModuleScripts in ServerStorage.AHN_Delta (15 nov). Zie AHN_README.md.

--==== Veld
local f=script.Parent
local X0,Z0,C,NX,NZ=f:GetAttribute("X0"),f:GetAttribute("Z0"),f:GetAttribute("cell"),f:GetAttribute("nx"),f:GetAttribute("nz")
local B="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
local idx={} for i=1,64 do idx[string.sub(B,i,i)]=i-1 end
local G={}
for line in string.gmatch(f.rle.Value,"[^\n]+") do
  local row={}; local prev=500; local k=1
  while k<=#line do
    local ch=string.sub(line,k,k)
    if ch=="!" then
      local val=idx[string.sub(line,k+1,k+1)]*64+idx[string.sub(line,k+2,k+2)]; local n=idx[string.sub(line,k+3,k+3)]
      for _=1,n do row[#row+1]=(val-500)/10 end; prev=val; k+=4
    else prev=prev+idx[ch]-32; row[#row+1]=(prev-500)/10; k+=1 end
  end
  G[#G+1]=row
end
local M={}
function M.dy(x,z)
  local u=(x-X0)/C; local v=(z-Z0)/C
  if u<0 or v<0 or u>NX-1 or v>NZ-1 then return 0 end
  local i=math.floor(u); local j=math.floor(v); local fu=u-i; local fv=v-j
  local i1=math.min(i+1,NX-1); local j1=math.min(j+1,NZ-1)
  local a=G[j+1][i+1]; local b=G[j+1][i1+1]; local c=G[j1+1][i+1]; local d=G[j1+1][i1+1]
  return (a*(1-fu)+b*fu)*(1-fv)+(c*(1-fu)+d*fu)*fv
end
M.box={X0,Z0,X0+C*(NX-1),Z0+C*(NZ-1)}
return M

--==== Schuif (aanroep: require(Schuif)(-796, 360))
local V=require(script.Parent.Veld)
local t=workspace.Terrain
local AIR=Enum.Material.Air
local YB,YT=-40,40
return function(z0,z1)
  local n=0
  for z=z0,z1-1,64 do
    for x=-280,651,64 do
      local reg=Region3.new(Vector3.new(x,YB,z),Vector3.new(math.min(x+64,652),YT,math.min(z+64,z1)))
      local m,o=t:ReadVoxels(reg,4)
      local sx,sy,sz=#m,#m[1],#m[1][1]
      local changed=false
      for a=1,sx do for c=1,sz do
        local d=V.dy(x+(a-1)*4+2, z+(c-1)*4+2)
        if math.abs(d)>=0.05 then
          changed=true
          local k=d/4
          local om,oo={}, {}
          for b=1,sy do om[b]=m[a][b][c]; oo[b]=o[a][b][c] end
          for b=1,sy do
            local s=b-k
            local i=math.floor(s); local fr=s-i
            local o1=(i>=1 and i<=sy) and oo[i] or 0
            local o2=(i+1>=1 and i+1<=sy) and oo[i+1] or 0
            local v=o1*(1-fr)+o2*fr
            local mat=AIR
            if v>0.001 then
              if fr<0.5 then mat=(o1>0 and om[i]) or om[i+1] or AIR else mat=(o2>0 and om[i+1]) or om[i] or AIR end
              if mat==AIR then mat=(om[i] and om[i]~=AIR and om[i]) or om[i+1] or AIR end
              if mat==AIR then v=0 end
            end
            m[a][b][c]=mat; o[a][b][c]=v
          end
        end
      end end
      if changed then t:WriteVoxels(reg,4,m,o); n+=1 end
    end
    task.wait()
  end
  return n
end

--==== Objecten (aanroep: require(Objecten)({namen van workspace-kinderen}))
-- VAST = plateau-waarden per klein v1-model (uitvoer tools/hoogteveld.py), PERDEEL = grote v1-modellen per onderdeel,
-- al het andere (Groen-mappen, bos, layout) per item op de eigen plek. Zie de Studio-versie voor de volledige tabellen.

--==== Terugdraaien
return function()
  local tr=game.ServerStorage:FindFirstChild("Backup_Terrein_voor_AHN_15nov")
  if tr then workspace.Terrain:PasteRegion(tr, Vector3int16.new(-72,-10,-201), true) end
  local n=0
  for _,d in ipairs(workspace:GetDescendants()) do
    local dy=d:GetAttribute("AHN_dY")
    if dy then
      if d:IsA("BasePart") then d.CFrame=d.CFrame-Vector3.new(0,dy,0) elseif d:IsA("Model") then d:PivotTo(d:GetPivot()-Vector3.new(0,dy,0)) end
      d:SetAttribute("AHN_dY",nil); n+=1
    end
  end
  return n
end
