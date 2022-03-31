<%page args="component_config"/>
environment:
    mqtt:
        server: "192.168.67.165"
logging:
  version: 1
  loggers:
    robinson.components.DataPortOutput:
      level: "ERROR"
    vebas.tracking.components.cv.ColoredCircleDetection:
      level: "WARN"

${component_config}
