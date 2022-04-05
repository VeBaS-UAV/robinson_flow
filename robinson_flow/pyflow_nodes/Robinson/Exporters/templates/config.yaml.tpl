<%page args="component_config"/>
logging:
  version: 1
  loggers:
    robinson.components.DataPortOutput:
      level: "ERROR"
    vebas:
      level: "DEBUG"
    robinson:
      level: "DEBUG"

${component_config}
