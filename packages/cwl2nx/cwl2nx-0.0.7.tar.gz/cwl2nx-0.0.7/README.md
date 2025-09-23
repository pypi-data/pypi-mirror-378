# CWL2Nx

Lightweight python module to load, validate and visualize CWL (Common Workflow Language) files through networkx graphs.
It uses [cwl_utils](https://github.com/common-workflow-language/cwl-utils) for parsing and validation.

## Installation

```
pip install cwl2nx
```

## Example Usage

> You will find an example of workflow in the GitHub repository : [workflow_example.cwl.yaml](https://raw.githubusercontent.com/mariusgarenaux/cwl2nx/refs/heads/main/workflow_example.cwl.yaml). Other examples can be found here : https://workflowhub.org

### Straightforward conversion

```python
from cwl2nx import CWLToNetworkxConnector

dir = "workflow_example.cwl.yaml"
dag = CWLToNetworkxConnector(dir).convert_to_networkx() # dag is networkx.DiGraph
print(dag.nodes, dag.edges)
```

### Using dagviz

> You'll need to install [`dagviz`](https://wimyedema.github.io/dagviz/index.html#installing) before

> /!\ you need to run the code below in a jupyter notebook

```python
from cwl2nx import CWLToNetworkxConnector
import networkx as nx
import dagviz

dir = "workflow_example.cwl.yaml"
connector = CWLToNetworkxConnector(dir)
dag = connector.convert_to_networkx()


dagviz.Dagre(dag)

dagviz.Metro(dag) # github tree dag style
```

![Dagre](https://github.com/mariusgarenaux/cwl2nx/blob/main/doc/dagviz_Dagre.png?raw=true)

![Metro](https://github.com/mariusgarenaux/cwl2nx/blob/main/doc/dagviz_Metro.png?raw=true)

### Visualization in the terminal

To get a light visualization of the workflow in the terminal, just use the code from this GitHub repo [https://github.com/ctongfei/py-dagviz/blob/main/dagviz.py](https://github.com/ctongfei/py-dagviz/blob/main/dagviz.py) and import visualize_dag function :

```python
from cwl2nx import CWLToNetworkxConnector
import networkx as nx

dir = "workflow_example.cwl.yaml"
dag = CWLToNetworkxConnector(dir).convert_to_networkx(datasets_as_node=True)
print(visualization_function(dag))
```

output : 

```text
• #nsbas.proc
│ • #nsbas_config.json
│ │ • #parameter.py
╰─┴─│─• #tache_init
    │ ╰─• ivwgayim.dep
    ╰───┼─• #tache_inter1
        ╰─│─• #tache_inter2
          │ ╰─• azbouvks2.dep
          ╰───│─• azbouvks1.dep
              ╰─┴─• #tache_end
                  ╰─• agxlvirt.dep
```

### Basic networkx display

```python
from cwl2nx import CWLToNetworkxConnector
import networkx as nx
import matplotlib.pyplot as plt

dir = "workflow_example.cwl.yaml"
connector = CWLToNetworkxConnector(dir)
dag = connector.convert_to_networkx(datasets_as_nodes=True)
nx.draw_networkx(dag)
plt.show()
```

![](https://github.com/mariusgarenaux/cwl2nx/blob/main/doc/nx_display.png?raw=true)

## License

[Apache 2.0](LICENSE-2.0.txt)