from dataclasses import dataclass

    

@dataclass
class CategoryNode:
    id: int
    title: str
    parent_id: int


class Category:
    def __init__(self, data):
        self.dataset = self._prepare_dataset(data)
        self.nodes = {d["id"]: CategoryNode(d["id"], d["title"], d["parent_id"]) for d in self.dataset}

    @staticmethod
    def _prepare_dataset(data: list[{}]):
        for element in data:
            if 'parent_id' not in element.keys():
                element['parent_id'] = None
        return data

    def get_headers(self):
        return [head[1] for head in self.nodes.items() if head[1].parent_id is None]

    def get_parent(self, node_id: int) -> CategoryNode:
        return self.nodes.get(self.nodes[node_id].parent_id)

    def get_children(self, node_id: int) -> list[CategoryNode]:
        children = []
        for id, node in self.nodes.items():
            if node.parent_id == node_id:
                children.append(node)
        return children

