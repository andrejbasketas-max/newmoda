--[[
	GOLD TYCOON - server skripta (sve u jednom fajlu)

	Sta radi:
	  * Pravi kodom 8 placeva u krugu (bez ikakvog modelovanja u Studiju)
	  * Svaki igrac automatski dobija svoj plac
	  * Dropperi spustaju rudu na traku, traka je nosi do kolektora, kolektor daje novac
	  * Dugme na placu kupuje sledecu nadogradnju (dropperi, veca vrednost rude, brzina)
	  * Cuva napredak (novac + nadogradnje) u DataStore

	Podesavanja su odmah ispod.
]]

local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")
local DataStoreService = game:GetService("DataStoreService")
local Debris = game:GetService("Debris")

---------------------------------------------------------------------------
-- PODESAVANJA
---------------------------------------------------------------------------
local MAX_PLOTS = 8 -- koliko igraca staje (podesi i Max Players u Game Settings)
local PLOT_RING_RADIUS = 95
local START_CASH = 50
local START_INTERVAL = 2 -- sekundi izmedju ispustanja rude
local BELT_SPEED = 12
local ORE_LIFETIME = 25
local AUTOSAVE_SECONDS = 60
local DATASTORE_NAME = "GoldTycoonV1"

-- vrednost rude po nivou droppera
local ORE_BASE_VALUE = { 2, 6, 20, 60 }
local ORE_COLORS = {
	Color3.fromRGB(205, 127, 50),
	Color3.fromRGB(190, 190, 200),
	Color3.fromRGB(255, 205, 40),
	Color3.fromRGB(80, 220, 255),
}

-- redosled kupovine; dugme uvek nudi sledecu stavku
local ITEMS = {
	{ name = "Dropper 1", price = 50, kind = "dropper", tier = 1 },
	{ name = "Dropper 2", price = 150, kind = "dropper", tier = 2 },
	{ name = "Ruda x2", price = 400, kind = "value", mult = 2 },
	{ name = "Dropper 3", price = 1000, kind = "dropper", tier = 3 },
	{ name = "Brze ispustanje", price = 2000, kind = "speed", mult = 0.6 },
	{ name = "Ruda x2", price = 6000, kind = "value", mult = 2 },
	{ name = "Dropper 4", price = 15000, kind = "dropper", tier = 4 },
	{ name = "Brze ispustanje", price = 35000, kind = "speed", mult = 0.6 },
	{ name = "Ruda x3", price = 100000, kind = "value", mult = 3 },
	{ name = "Brze ispustanje", price = 250000, kind = "speed", mult = 0.7 },
}

---------------------------------------------------------------------------
-- POMOCNE FUNKCIJE
---------------------------------------------------------------------------
local function formatNumber(n: number): string
	local suffixes = { "", "K", "M", "B", "T" }
	local i = 1
	while n >= 1000 and i < #suffixes do
		n /= 1000
		i += 1
	end
	if i == 1 then
		return tostring(math.floor(n))
	end
	return string.format("%.1f%s", n, suffixes[i])
end

local function makePart(parent: Instance, name: string, cf: CFrame, size: Vector3, color: Color3, material: Enum.Material?)
	local p = Instance.new("Part")
	p.Name = name
	p.Anchored = true
	p.Size = size
	p.CFrame = cf
	p.Color = color
	p.Material = material or Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function makeLabel(part: BasePart, text: string, offsetY: number, width: number?)
	local gui = Instance.new("BillboardGui")
	gui.Name = "Label"
	gui.Size = UDim2.fromOffset(width or 220, 60)
	gui.StudsOffset = Vector3.new(0, offsetY, 0)
	gui.AlwaysOnTop = true
	gui.MaxDistance = 90
	gui.Parent = part

	local t = Instance.new("TextLabel")
	t.Name = "Text"
	t.Size = UDim2.fromScale(1, 1)
	t.BackgroundTransparency = 1
	t.Font = Enum.Font.GothamBold
	t.TextScaled = true
	t.TextColor3 = Color3.new(1, 1, 1)
	t.TextStrokeTransparency = 0.3
	t.Text = text
	t.Parent = gui
	return t
end

---------------------------------------------------------------------------
-- MAPA: zemlja + placevi
---------------------------------------------------------------------------
local world = Instance.new("Folder")
world.Name = "GoldTycoon"
world.Parent = Workspace

local oresFolder = Instance.new("Folder")
oresFolder.Name = "Ores"
oresFolder.Parent = world

makePart(world, "Ground", CFrame.new(0, -1, 0), Vector3.new(500, 2, 500), Color3.fromRGB(70, 130, 70), Enum.Material.Grass)

-- centralni spawn za igrace dok nemaju plac
local lobby = Instance.new("SpawnLocation")
lobby.Name = "LobbySpawn"
lobby.Anchored = true
lobby.Size = Vector3.new(10, 1, 10)
lobby.Position = Vector3.new(0, 0.5, 0)
lobby.Neutral = true
lobby.Duration = 0
lobby.Parent = world

type Plot = {
	index: number,
	cf: CFrame,
	owner: Player?,
	progress: number,
	tier: number,
	valueMult: number,
	interval: number,
	droppers: { Part },
	button: Part,
	buttonText: TextLabel,
	sign: TextLabel,
}

local plots: { Plot } = {}

local function worldCF(plot: Plot, x: number, y: number, z: number): CFrame
	return plot.cf * CFrame.new(x, y, z)
end

local function buildPlot(index: number): Plot
	local angle = (index - 1) / MAX_PLOTS * math.pi * 2
	local center = Vector3.new(math.cos(angle) * PLOT_RING_RADIUS, 0, math.sin(angle) * PLOT_RING_RADIUS)
	local cf = CFrame.lookAt(center, Vector3.new(0, 0, 0))

	local model = Instance.new("Model")
	model.Name = "Plot" .. index
	model.Parent = world

	local plot = {
		index = index,
		cf = cf,
		owner = nil,
		progress = 0,
		tier = 0,
		valueMult = 1,
		interval = START_INTERVAL,
		droppers = {},
	} :: any

	-- baza
	makePart(model, "Base", cf * CFrame.new(0, 0.5, 0), Vector3.new(44, 1, 44), Color3.fromRGB(60, 60, 70), Enum.Material.Concrete)

	-- traka
	local belt = makePart(model, "Belt", worldCF(plot, 0, 1.5, 0), Vector3.new(32, 1, 5), Color3.fromRGB(35, 35, 40), Enum.Material.Metal)
	belt.AssemblyLinearVelocity = cf:VectorToWorldSpace(Vector3.new(BELT_SPEED, 0, 0))
	for _, side in ipairs({ -3, 3 }) do
		makePart(model, "Rail", worldCF(plot, 0, 3, side), Vector3.new(32, 2, 0.5), Color3.fromRGB(200, 70, 40), Enum.Material.Metal)
	end
	makePart(model, "BackStop", worldCF(plot, 17, 3, 0), Vector3.new(0.5, 2, 6), Color3.fromRGB(200, 70, 40), Enum.Material.Metal)

	-- kolektor (nevidljivi trigger na kraju trake)
	local collector = makePart(model, "Collector", worldCF(plot, 15.5, 4, 0), Vector3.new(2, 5, 5), Color3.fromRGB(80, 255, 120), Enum.Material.Neon)
	collector.CanCollide = false
	collector.Transparency = 0.6
	makeLabel(collector, "KOLEKTOR", 4, 160)

	-- dropperi (skriveni dok se ne kupe)
	for i = 1, 4 do
		local d = makePart(model, "Dropper" .. i, worldCF(plot, -14 + (i - 1) * 6, 8, 0), Vector3.new(3, 3, 3), ORE_COLORS[i], Enum.Material.Metal)
		d.Transparency = 1
		d.CanCollide = false
		plot.droppers[i] = d
	end

	-- spawn pad (mesto gde se igrac pojavljuje)
	local pad = makePart(model, "SpawnPad", worldCF(plot, -16, 1.2, 12), Vector3.new(6, 0.4, 6), Color3.fromRGB(90, 160, 255), Enum.Material.Neon)
	pad.CanCollide = true
	plot.sign = makeLabel(pad, "Slobodan plac", 5, 260)

	-- dugme za kupovinu
	local button = makePart(model, "BuyButton", worldCF(plot, 4, 1.3, 14), Vector3.new(9, 0.4, 6), Color3.fromRGB(255, 190, 40), Enum.Material.Neon)
	plot.button = button
	plot.buttonText = makeLabel(button, "", 4, 300)

	-- kolektor: dodaje novac vlasniku
	collector.Touched:Connect(function(hit)
		local value = hit:GetAttribute("OreValue")
		if not value or hit:GetAttribute("Collected") then
			return
		end
		hit:SetAttribute("Collected", true)
		local owner = plot.owner
		if owner and owner.Parent then
			local ls = owner:FindFirstChild("leaderstats")
			local cash = ls and ls:FindFirstChild("Cash")
			if cash then
				cash.Value += value
			end
		end
		hit:Destroy()
	end)

	return plot :: Plot
end

for i = 1, MAX_PLOTS do
	plots[i] = buildPlot(i)
end

---------------------------------------------------------------------------
-- LOGIKA PLACA
---------------------------------------------------------------------------
local function refreshButton(plot: Plot)
	local item = ITEMS[plot.progress + 1]
	if item then
		plot.buttonText.Text = string.format("%s\n$%s", item.name, formatNumber(item.price))
		plot.button.Transparency = 0
		plot.button.CanTouch = true
	else
		plot.buttonText.Text = "SVE KUPLJENO!"
		plot.button.Transparency = 0.7
		plot.button.CanTouch = false
	end
end

local function applyItem(plot: Plot, item)
	if item.kind == "dropper" then
		plot.tier = math.max(plot.tier, item.tier)
		local d = plot.droppers[item.tier]
		d.Transparency = 0
	elseif item.kind == "value" then
		plot.valueMult *= item.mult
	elseif item.kind == "speed" then
		plot.interval *= item.mult
	end
end

local function clearOres(plot: Plot)
	for _, ore in ipairs(oresFolder:GetChildren()) do
		if ore:GetAttribute("PlotIndex") == plot.index then
			ore:Destroy()
		end
	end
end

local function resetPlot(plot: Plot)
	plot.owner = nil
	plot.progress = 0
	plot.tier = 0
	plot.valueMult = 1
	plot.interval = START_INTERVAL
	for _, d in ipairs(plot.droppers) do
		d.Transparency = 1
	end
	clearOres(plot)
	plot.sign.Text = "Slobodan plac"
	plot.buttonText.Text = ""
	plot.button.Transparency = 1
	plot.button.CanTouch = false
end

local function restoreProgress(plot: Plot, progress: number)
	plot.progress = 0
	plot.tier = 0
	plot.valueMult = 1
	plot.interval = START_INTERVAL
	for i = 1, math.min(progress, #ITEMS) do
		applyItem(plot, ITEMS[i])
		plot.progress = i
	end
	refreshButton(plot)
end

local function spawnOre(plot: Plot, tier: number)
	local dropper = plot.droppers[tier]
	local ore = Instance.new("Part")
	ore.Name = "Ore"
	ore.Size = Vector3.new(1.4, 1.4, 1.4)
	ore.Color = ORE_COLORS[tier]
	ore.Material = Enum.Material.Neon
	ore.TopSurface = Enum.SurfaceType.Smooth
	ore.BottomSurface = Enum.SurfaceType.Smooth
	ore.CFrame = dropper.CFrame * CFrame.new(0, -2.5, 0)
	ore:SetAttribute("OreValue", ORE_BASE_VALUE[tier] * plot.valueMult)
	ore:SetAttribute("PlotIndex", plot.index)
	ore.Parent = oresFolder
	Debris:AddItem(ore, ORE_LIFETIME)
end

-- petlja ispustanja: po jedna za svaki plac
for _, plot in ipairs(plots) do
	task.spawn(function()
		while true do
			task.wait(plot.interval)
			if plot.owner then
				for tier = 1, plot.tier do
					spawnOre(plot, tier)
				end
			end
		end
	end)
end

-- kupovina dugmetom
local debounce: { [Player]: number } = {}
for _, plot in ipairs(plots) do
	plot.button.Touched:Connect(function(hit)
		local player = Players:GetPlayerFromCharacter(hit.Parent)
		if not player or player ~= plot.owner then
			return
		end
		local now = os.clock()
		if (debounce[player] or 0) + 0.4 > now then
			return
		end
		debounce[player] = now

		local item = ITEMS[plot.progress + 1]
		if not item then
			return
		end
		local cash = player.leaderstats.Cash
		if cash.Value < item.price then
			return
		end
		cash.Value -= item.price
		applyItem(plot, item)
		plot.progress += 1
		refreshButton(plot)
	end)
end

---------------------------------------------------------------------------
-- IGRACI: dodela placa, spawn, cuvanje
---------------------------------------------------------------------------
local store = DataStoreService:GetDataStore(DATASTORE_NAME)
local plotOf: { [Player]: Plot } = {}
local canSave: { [Player]: boolean } = {}

local function saveData(player: Player)
	local plot = plotOf[player]
	if not plot or not canSave[player] then
		return
	end
	local cash = player:FindFirstChild("leaderstats") and player.leaderstats:FindFirstChild("Cash")
	if not cash then
		return
	end
	local data = { cash = cash.Value, progress = plot.progress }
	local ok, err = pcall(function()
		store:SetAsync("Player_" .. player.UserId, data)
	end)
	if not ok then
		warn("[GoldTycoon] Cuvanje nije uspelo:", err)
	end
end

local function moveToPlot(player: Player, character: Model)
	local plot = plotOf[player]
	if not plot then
		return
	end
	local root = character:WaitForChild("HumanoidRootPart", 5)
	if root then
		character:PivotTo(worldCF(plot, -16, 5, 12))
	end
end

local function onPlayerAdded(player: Player)
	local leaderstats = Instance.new("Folder")
	leaderstats.Name = "leaderstats"
	leaderstats.Parent = player
	local cash = Instance.new("NumberValue")
	cash.Name = "Cash"
	cash.Value = START_CASH
	cash.Parent = leaderstats

	-- nadji slobodan plac
	local plot: Plot? = nil
	for _, p in ipairs(plots) do
		if not p.owner then
			plot = p
			break
		end
	end
	if not plot then
		player:Kick("Server je pun - svi placevi su zauzeti. Pokusaj ponovo.")
		return
	end
	plot.owner = player
	plotOf[player] = plot
	plot.sign.Text = player.DisplayName .. " - Tycoon"

	player.CharacterAdded:Connect(function(character)
		moveToPlot(player, character)
	end)

	-- ucitaj sacuvano
	local ok, data = pcall(function()
		return store:GetAsync("Player_" .. player.UserId)
	end)
	if ok then
		canSave[player] = true
		if data then
			cash.Value = data.cash or START_CASH
			restoreProgress(plot, data.progress or 0)
		else
			restoreProgress(plot, 0)
		end
	else
		-- DataStore nedostupan (npr. API pristup nije ukljucen u Studiju): igra radi, ali ne cuva
		warn("[GoldTycoon] Ucitavanje nije uspelo, cuvanje je iskljuceno za ovu sesiju:", data)
		canSave[player] = false
		restoreProgress(plot, 0)
	end

	if player.Character then
		moveToPlot(player, player.Character)
	end
end

local function onPlayerRemoving(player: Player)
	saveData(player)
	local plot = plotOf[player]
	if plot then
		resetPlot(plot)
	end
	plotOf[player] = nil
	canSave[player] = nil
	debounce[player] = nil
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)
for _, player in ipairs(Players:GetPlayers()) do
	task.spawn(onPlayerAdded, player)
end

for _, plot in ipairs(plots) do
	resetPlot(plot)
end

task.spawn(function()
	while true do
		task.wait(AUTOSAVE_SECONDS)
		for _, player in ipairs(Players:GetPlayers()) do
			saveData(player)
		end
	end
end)

game:BindToClose(function()
	for _, player in ipairs(Players:GetPlayers()) do
		saveData(player)
	end
end)
