runner = ComponentRunner('runner')

% for uid, node in base.computation_nodes().items():
runner += ${node.name().lower()}
% endfor
