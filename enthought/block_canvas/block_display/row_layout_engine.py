""" Provides a row based layout algorithm for an acyclic directed graph.
"""

# Standard library imports
import warnings

# Enthought library imports
from enthought.traits.api import HasTraits


class RowLayoutEngine(HasTraits):
    """ Layout a visual representation of a graph such that the nodes
        are orgnaized into consecutive rows based on their dependencies. The
        algorithm is only suitable for acyclic graphs (and currently will hang
        if given a cyclic one).
    """

    #########################################################################
    # RowLayout Traits
    #########################################################################

    # Should nodes be centered (most common) or aligned to the left or right
    #justify = Enum('left', 'center', 'right')

    #########################################################################
    # RowLayout Interface
    #########################################################################

    def organize_rows(self, dep_graph):
        """ Convert the dependency graph into row based layout scheme.

            The layout organizes the nodes into rows based on their
            dependencies.  The first row is the elements without any
            dependencies.  The next row is the set of nodes that only
            depend on nodes in previous rows and so on.  In this way,
            the nodes progress from the "input" nodes on the first
            rows to the "output" nodes on the last row.

            The function returns a list of lists.  Each row in the
            list is the set of nodes that should be laid out on that
            row.

            Example:
                >>> g = {'foo': [],
                ...      'bar': ['foo'],
                ...      'baz': ['foo'],
                ...      'zi':  ['bar'],
                ...      'za':  ['baz'],
                ...      'ze':  ['baz'],
                ...      'zoo': ['zi','za', 'ze'],
                ...     }
                >>> layout_engine = RowLayoutEngine()
                >>> layout_engine._organize_rows(g)
                [['foo'], ['bar', 'baz'], ['zi', 'ze', 'za'], ['zoo']]

            Note: This only works for graphs that don't have any cycles
                  in them.  A cycle will currently cause this to fail
                  and print a warning on the status bar.
        """
        # Initialize the rows to avoid returning None
        rows = []

        # Check to see if there are any nodes to arrange
        if dep_graph:
            if self._acyclic(dep_graph):
                rows = self._create_hierarchy(dep_graph)
            else:
                warnings.warn("Cycle detected in graph.  Layout algorithm failed.")
        return rows

    #########################################################################
    # RowLayoutEngine Protected Interface
    #########################################################################

    def _successor_graph(self, dep_graph):
        """
            Given a dependency graph, reverse the dependency graph to create
            a list of successors for each node.
        """

        successors = {}
        for stop in dep_graph:
            # Initialize to empty list in case this is a leaf node
            if not stop in successors:
                successors[stop] = []

            # Reverse the dependency graph
            for start in dep_graph[stop]:
                if start in successors:
                    successors[start].append(stop)
                else:
                    successors[start] = [stop]
        return successors


    def _acyclic(self, dep_graph):
        """ Given a dependency graph, determine whether or not there is a cycle
            by performing a recursive depth-first search.
            Returns False if there is a cycle present, True otherwise.
        """

        seen = {}
        explored = []

        # Reorganize the dependency graph to view children of each node.
        successors = self._successor_graph(dep_graph)

        def _depth_first(graph, seen, explored, v):
            seen[v] = 1
            for w in graph[v]:
                if w not in seen:
                    if not _depth_first(graph, seen, explored, w):
                        return
                elif w in seen and w not in explored:
                    #cycle found
                    return False
            explored.insert(0,v)
            return v

        for v in successors:
            if v not in explored:
                if not _depth_first(successors, seen, explored, v):
                    return
        return True


    def _create_hierarchy(self, dep_graph):
        """
            Before calling create_hierarchy, make sure that the graph is acyclic.
            Building from the bottom-up.
            To Do:  Clean up code in depth-first search and combine with the search
                for cycles.

        """
        height = {}

        # Get the roots of the graph (with no dependencies)
        # Going to build graph top-down
        successors = self._successor_graph(dep_graph)
        roots = [node for node in dep_graph if dep_graph[node] == []]

        def _depth_first(graph, height, current_rank, v):
            if v in height:
                # Push children down
                if current_rank > height[v]:
                    height[v] = current_rank
            else:
                height[v] = current_rank
            if v in graph:
                for w in graph[v]:
                    _depth_first(graph, height, current_rank + 1, w)
            return v

        # Get the recursion started
        for v in roots:
            _depth_first(successors, height, 1, v)

        # Check for optimal height for leave nodes since they're
        # used to get the recursion started
        max_rank = max(height.values())
        for v in roots:
            children = successors[v]
            leaf_height = height[v]
            if len(children) > 0:
                min_child = min([height[c] for c in children])
                if leaf_height < min_child:
                    height[v] = min_child - 1

        # Construct the rows from the rank assigned in search.
        # The root nodes will start with a rank of 1
        rows = []
        row_rank = 1
        while row_rank <= max_rank:
            row = [node for node in height if height[node] == row_rank]
            rows.append(row)
            row_rank = row_rank + 1

        # First turn the dependency list into successors
        successors = self._successor_graph(dep_graph)

        # First pass move down the tree - assume fixed root nodes
        index = 1
        num_rows = len(rows)

        while index < num_rows:
            row = rows[index]
            previous_row = rows[index - 1]
            new_order = []
            for r in row:
                parents = dep_graph[r]
                if len(parents) > 0:
                    total = 0.0
                    for parent in parents:
                        try:
                            total += previous_row.index(parent)
                        except:
                            pass
                    avg = total / len(parents)
                    new_order.append((avg, r))
                else:
                    # This is a root node - will get reordered on the next pass
                    new_order.append((0.0, r))

            new_order.sort()
            new_row = []
            for each in new_order:
                new_row.append(each[1])
            rows[index] = new_row
            index = index + 1


        # Second pass - move back up the tree, chance to rearrange root nodes
        index = len(rows) - 2

        while index > -1:
            row = rows[index]
            next_row = rows[index + 1]
            new_order = []
            for r in row:
                children = successors[r]
                if len(children) > 0:
                    total = 0.0
                    for child in children:
                        try:
                            total += next_row.index(child)
                        except:
                            pass
                    avg = total / len(children)
                    new_order.append((avg, r))
                else:
                    # This is a leaf node
                    new_order.append((row.index(r), r))

            new_order.sort()
            new_row = []
            for each in new_order:
                new_row.append(each[1])
            rows[index] = new_row
            index = index - 1

        return rows

#EOF

