;; Eval Buffer with `M-x eval-buffer' to register the newly created template.

(dap-register-debug-template
  "robinson-flow"
  (list :type "python"
        :args ""
        :cwd "/home/matthias/src/robinson/robinson_flow"
        :module "robinson_flow"
        ;; :program "/home/matthias/src/robinson/robinson_flow.ryven_nodes_ryven/__main__.py"
        :request "launch"
        :name "robinson-flow"))
