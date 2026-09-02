extends SceneTree

# Eval KA-03: tum proje GDScript dosyalari gercek proje baglaminda (autoload'lar
# yuklu) load() ile derlenir. `--check-only --script` autoload'lari cozumlemedigi
# icin meşru proje scriptleri dahi "Identifier not found" ile dusuyor; bu script
# o yanlis-pozitifi ortadan kaldirir.
# Cikis sozlesmesi: PARSE_TOPLAM / PARSE_HATA satirlari bastirir.
#   exit 0 = bulunan tum .gd derlendi   exit 1 = parse hatasi var
#   exit 2 = hic .gd bulunamadi (sessiz gecis engeli)

const SKIP_DIRS := [".godot", "build"]

func _walk(dir_path: String, toplam: Array, hatalar: Array) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return
	dir.list_dir_begin()
	var ad := dir.get_next()
	while ad != "":
		if ad.begins_with("."):
			ad = dir.get_next()
			continue
		var yol := dir_path + "/" + ad
		if dir.current_is_dir():
			if not SKIP_DIRS.has(ad):
				_walk(yol, toplam, hatalar)
		elif ad.ends_with(".gd"):
			toplam[0] += 1
			var s = load(yol)
			if s == null:
				hatalar.append(yol)
				print("PARSE_FAIL %s" % yol)
		ad = dir.get_next()
	dir.list_dir_end()

func _initialize() -> void:
	var toplam := [0]
	var hatalar := []
	_walk("res://", toplam, hatalar)
	print("PARSE_TOPLAM=%d" % toplam[0])
	print("PARSE_HATA=%d" % hatalar.size())
	if toplam[0] == 0:
		quit(2)
	elif hatalar.size() > 0:
		quit(1)
	else:
		quit(0)