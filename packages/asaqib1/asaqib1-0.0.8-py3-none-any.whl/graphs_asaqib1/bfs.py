def bfs(graph, start):
    visited = set()
    queue = [start]
    order = []

    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            order.append(node)
            queue.extend(n for n in graph.get(node, {}) if n not in visited)

    return order