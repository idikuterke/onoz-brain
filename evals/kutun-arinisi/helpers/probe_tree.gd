extends SceneTree

# Geçici sonda: -s absolute path ile yüklenmeyi test eder.
func _initialize() -> void:
	print("PROBE_TREE_OK root=", root)
	quit(0)
