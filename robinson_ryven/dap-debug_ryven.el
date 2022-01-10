;; Eval Buffer with `M-x eval-buffer' to register the newly created template.

(dap-register-debug-template
  "mamoge-ryven"
  (list :type "python"
        :args ""
        :cwd nil
        :module nil
        :program "/home/matthias/src/mamoge/mamoge-ryven/robinson_ryven/__main__.py"
        :request "launch"
        :name "mamoge-ryven"))
