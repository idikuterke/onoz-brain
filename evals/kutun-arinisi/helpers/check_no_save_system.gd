extends SceneTree

# Eval KA-11: D-008 kanon karari makineyle korunur.
#
# 00_CANON/DECISIONS.md D-008 -> "Save/load yok. Demo tek oturumdur.
# Ajanlarin kendiliginden eklemesini engellemek icin acikca yasaklandi."
# Karar bugune kadar yalniz belgede duruyordu; bu script onu denetlenebilir
# hale getirir.
#
# Aranan: kalici DURUM YAZIMI isaretleri. Salt-okur dosya erisimi mesrudur
# (DataDB manifest'i FileAccess.READ ile okur) ve bilerek isaretlenmez.
#
# Cikis sozlesmesi:
#   exit 0 = ihlal yok            (SAVE_IHLAL=0 basilir)
#   exit 1 = D-008 ihlal edildi   (her ihlal SAVE_IHLAL_SATIR ile listelenir)
#   exit 2 = hic .gd taranmadi    (sessiz gecis engeli)

const TARANAN_KOK := "res://scripts"
const SKIP_DIRS := [".godot", "build"]

# Her biri kalici yazim demektir; salt-okur erisim listede YOKTUR.
const IHLAL_DESENLERI := [
	"user://",
	"FileAccess.WRITE",
	"FileAccess.READ_WRITE",
	"ResourceSaver",
	"store_var",
	"store_string",
	"store_line",
	"store_buffer",
]


func _walk(dir_path: String, sayac: Array, ihlaller: Array) -> void:
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
				_walk(yol, sayac, ihlaller)
		elif ad.ends_with(".gd"):
			sayac[0] += 1
			_dosyayi_tara(yol, ihlaller)
		ad = dir.get_next()
	dir.list_dir_end()


func _dosyayi_tara(yol: String, ihlaller: Array) -> void:
	var f := FileAccess.open(yol, FileAccess.READ)
	if f == null:
		return
	var satir_no := 0
	while not f.eof_reached():
		var satir := f.get_line()
		satir_no += 1
		# Yorum satirlari sayilmaz: D-008'i ANLATAN metin ihlal degildir.
		var kirpik := satir.strip_edges()
		if kirpik.begins_with("#"):
			continue
		for desen in IHLAL_DESENLERI:
			if satir.find(desen) != -1:
				ihlaller.append("%s:%d %s" % [yol, satir_no, desen])
				print("SAVE_IHLAL_SATIR %s:%d -> %s" % [yol, satir_no, desen])
	f.close()


func _initialize() -> void:
	var sayac := [0]
	var ihlaller := []
	_walk(TARANAN_KOK, sayac, ihlaller)
	print("SAVE_TARANAN=%d" % sayac[0])
	print("SAVE_IHLAL=%d" % ihlaller.size())
	if sayac[0] == 0:
		print("HATA: hic .gd taranmadi, tarama yolu bozuk olabilir: %s" % TARANAN_KOK)
		quit(2)
	elif ihlaller.size() > 0:
		print("D-008 IHLALI: save/load sistemi eklenmis gorunuyor (DECISIONS.md D-008).")
		quit(1)
	else:
		quit(0)
