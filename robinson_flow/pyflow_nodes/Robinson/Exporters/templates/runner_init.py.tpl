runner = QtComponentRunner('runner')

runner += external
% for uid, node in base.computation_nodes().items():
runner += ${node.name().lower() | pyname}
% endfor

runner.config_update(**settings["components"])
