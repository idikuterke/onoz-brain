extends SceneTree

func _initialize() -> void:
	var gs := root.get_node_or_null(NodePath("GameState"))
	print("AUTOLOAD_GameState=", gs != null)
	var s = load("res://tests/test_envanter.gd")
	print("LOAD_test_envanter_null=", s == null)
	var s2 = load("res://scripts/ui/diyalog_kutusu.gd")
	print("LOAD_diyalog_null=", s2 == null)
	quit(0)