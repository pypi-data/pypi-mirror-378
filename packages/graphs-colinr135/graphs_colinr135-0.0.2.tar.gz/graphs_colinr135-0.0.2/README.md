URL for your GitHub repository: https://github.com/ColinR135/graph_colinr135.git

This package contains the Dijkstra shortest path algorithm.
    The algorithm can be used with the function
    dijkstra(graph, source) # this returns the total distance and path taken

There is also another heap project added to support the use of the algorithm 
    heap = []            # creates an empty heap
    heappush(heap, item) # pushes a new item on the heap
    item = heappop(heap) # pops the smallest item from the heap
    item = heap[0]       # smallest item on the heap without popping it
    heapify(x)           # transforms list into a heap, in-place, in linear time
    item = heappushpop(heap, item) # pushes a new item and then returns
                                # the smallest item; the heap size is unchanged
    item = heapreplace(heap, item) # pops and returns smallest item, and adds
                                # new item; the heap size is unchanged
