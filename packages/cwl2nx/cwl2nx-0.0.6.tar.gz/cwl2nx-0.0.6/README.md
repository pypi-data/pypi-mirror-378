# CWL2Nx

Lightweight python module to load, validate and visualize CWL (Common Workflow Language) files through networkx graphs.
It uses [cwl_utils](https://github.com/common-workflow-language/cwl-utils) for parsing and validation.

## Installation

```
pip install cwl2nx
```

## Example Usage

> You will find an example of workflow in the GitHub repository : [workflow_example.cwl.yaml](https://raw.githubusercontent.com/mariusgarenaux/cwl2nx/refs/heads/main/workflow_example.cwl.yaml)

### Straightforward conversion


```python
from cwl2nx import CWLToNetworkxConnector

dir = "workflow_example.cwl.yaml"
dag = CWLToNetworkxConnector(dir).convert_to_networkx() # dag is networkx.DiGraph
print(dag.nodes, dag.edges)
```

### Basic networkx display

Once .cwl is loaded in networkx, you can use any visualization tool to display the dag.

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

![img](https://raw.githubusercontent.com/mariusgarenaux/cwl2nx/refs/heads/main/example_display.png)


### Using visualization libraries

> You'll need to install [`dagviz`](https://wimyedema.github.io/dagviz/index.html#installing) before

> Run the cell below in a notebook

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

## License

[Apache 2.0](LICENSE-2.0.txt)