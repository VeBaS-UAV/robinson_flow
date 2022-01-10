;; Eval Buffer with `M-x eval-buffer' to register the newly created template.

(dap-register-debug-template
  "robinson-ryven"
  (list :type "python"
        :args ""
        :cwd "/home/matthias/src/robinson/robinson_ryven"
        :module "robinson_ryven"
        ;; :program "/home/matthias/src/robinson/robinson_ryven/robinson_ryven/__main__.py"
        :request "launch"
        :name "robinson-ryven"))
