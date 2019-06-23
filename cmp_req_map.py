import sys
from GUI.RequirementComponentApp import RequirementComponentApp
from GUI.ComponentRequirementMapper import ComponentRequirementMapper

create_map = len(sys.argv) > 1 and sys.argv[1] == 'create_map'

if __name__ == '__main__':
    if not create_map:
        RequirementComponentApp().run()
    else:
        ComponentRequirementMapper().run()
