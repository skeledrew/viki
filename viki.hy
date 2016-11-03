#! /usr/bin/hy

(import voice importlib)

(defn main []
      (print "Hello world!!!\n\n")
      (while True (do (.lual voice)
                      (print "Reloading modules...")
                      (.reload importlib voice)
                      (print "Reloaded!"))))

(main)
(print "\n\n\nGoodbye cruel world   :'-(")