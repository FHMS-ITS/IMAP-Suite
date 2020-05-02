from lark import Tree

class AbstractParser:
	def tree_to_string(self, tree):
		data = ""
		if isinstance(tree, Tree):
			for subtree in tree.children:
				data = data + self.tree_to_string(subtree)
		else:
			data = str(tree)
		return data

