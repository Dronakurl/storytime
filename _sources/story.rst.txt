Story Class
===========

.. automodule:: storytime_ai.story

Attributes
----------
.. currentmodule:: storytime_ai.story
.. autoclass:: storytime_ai.story.Story

.. automethod:: Story.__init__
   
Basic Functionality
-------------------

.. currentmodule:: storytime_ai.story
.. automethod:: Story.next_dialog        
.. automethod:: Story.exec_logic         
.. automethod:: Story.addchoice          
.. automethod:: Story.back_dialog        

Save and Load markdown
----------------------

.. automethod:: Story.save_markdown      
.. automethod:: Story.to_markdown        
.. automethod:: Story.from_markdown      
.. automethod:: Story.from_markdown_file 

NetworkX Graph
--------------

.. automethod:: Story.create_graph       
.. automethod:: Story.plot_graph         
.. automethod:: Story.has_subgraphs      

Integrity Checks and corrections
--------------------------------
.. automethod:: Story.check_integrity    
.. automethod:: Story.prune_dangling_choices
.. automethod:: Story.restrict_to_largest_substory

Story Generation
----------------
.. automethod:: Story.generate_story_from_file
.. automethod:: Story.generate_story     

