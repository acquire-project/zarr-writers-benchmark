import matplotlib.pyplot as plt 
from zarr_libraries import *


def main() -> None:
    shape = [64, 1080, 1920]
    chunks = [64, 540, 960]
    fig, graph = plt.subplots(2, 2)
    
    zarr_python = Zarr_Python(shape=shape, chunks=chunks)
    tensorstore = Tensorstore(shape=shape, chunks=chunks)
    ome_zarr = Ome_Zarr(shape=shape, chunks=chunks)
    #z5 = Z5(shape=shape, chunks=chunks)
    
    '''
    Append Tests:
    - These tests benchmark the continuous appending to a single zarr folder.
    - These tests are best suited for the following libraries:
        * TensorStore
        * Zarr Python
    '''
    zarr_python.continuous_append_test(graph=graph[1][0], avg_graph=graph[1][1], append_dim_size=10)
    tensorstore.continuous_append_test(graph=graph[1][0], avg_graph=graph[1][1], append_dim_size=10) 
    
    # setting up graph for append tests
    graph[1][0].set_xlabel("Write Number")
    graph[1][0].set_title("Continuous Append Test")
    graph[1][0].legend()
   
    '''
    Continuous write tests:
    - These tests benchmark the creation of many increasingly large zarr folders.
    - These tests are best suited for the following libraries:
        * TensorStore
        * Zarr Python
        * OME Zarr
        * z5py
    '''
    tensorstore.continuous_write_test(graph=graph[0][0], avg_graph=graph[0][1], append_dim_size=1, step=1)
    zarr_python.continuous_write_test(graph=graph[0][0], avg_graph=graph[0][1], append_dim_size=1, step=1)
    ome_zarr.continuous_write_test(graph=graph[0][0], avg_graph=graph[0][1], append_dim_size=1, step=1)   # crashes at anything above 16gigs (append_dim_size 90 on my machine)
    #z5.continuous_write_test(graph=graph[0][0], avg_graph=graph[0][1], append_dim_size=10, step=1)
    
    # setting up graphs for write tests
    graph[0][0].set_xlabel("Data Size (GB)")
    graph[0][0].set_title("Continuous Write Test")
    graph[0][0].legend()
    
    # setting up graphs for average bandwidth
    graph[0][1].set_title("Average Bandwidth:\nContinuous Write Test")
    graph[1][1].set_title("Average Bandwidth:\nContinuous Append Test")
   
    for graph in fig.get_axes():
        graph.set_ylabel("Bandwidth (GBps)")
        graph.grid()
        
    fig.canvas.manager.set_window_title(f'shape: {shape}, chunks: {chunks}')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
