import gc

class BKTree():

    def distance(self, v1, v2):
       s1 = v1.split("_")
       s2 = v2.split("_")
       return sum([1 for i, j in zip(s1, s2) if i != j])

    def __init__(self, items, usegc=False):
        self.nodes = {}
        try:
            self.root = next(items)
        except StopIteration:
            self.root = ""
            return

        self.nodes[self.root] = [] # the value is a list of tuples (word, distance)
        gc_on = gc.isenabled()
        if not usegc:
            gc.disable()
        for el in items:
            if el not in self.nodes: # do not add duplicates
                self._addLeaf(self.root, el)
        if gc_on:
            gc.enable()

    def _addLeaf(self, root, item):
        dist = self.distance(root, item)
        if dist > 0:
            for arc in self.nodes[root]:
                if dist == arc[1]:
                    self._addLeaf(arc[0], item)
                    break
            else:
                if item not in self.nodes:
                    self.nodes[item] = []
                self.nodes[root].append((item, dist))

    def find(self, item, threshold):
        "Return an array with all the items found with distance <= threshold from item."
        result = []
        if self.nodes:
            self._finder(self.root, item, threshold, result)
        return result

    def _finder(self, root, item, threshold, result):
        dist = self.distance(root, item)
        if dist <= threshold:
            result.append(root)
        dmin = dist - threshold
        dmax = dist + threshold
        for arc in self.nodes[root]:
            if dmin <= arc[1] <= dmax:
                self._finder(arc[0], item, threshold, result)

    def xfind(self, item, threshold):
        "Like find, but yields items lazily. This is slower than find if you need a list."
        if self.nodes:
            return self._xfinder(self.root, item, threshold)

    def _xfinder(self, root, item, threshold):
        dist = self.distance(root, item)
        if dist <= threshold:
            yield root
        dmin = dist - threshold
        dmax = dist + threshold
        for arc in self.nodes[root]:
            if dmin <= arc[1] <= dmax:
                for node in self._xfinder(arc[0], item, threshold):
                    yield node
