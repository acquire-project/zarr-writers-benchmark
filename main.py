import matplotlib.pyplot as plt 
from zarr_libraries import *


def main() -> None:
    fig, graph = plt.subplots(2, 1)
    zarr_python = Zarr_Python(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    tensorstore = Tensorstore(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    ome_zarr = Ome_Zarr(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    z5 = Z5(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    
    '''
    Append Tests:
    - These tests benchmark the continuous appending to a single zarr folder.
    - These tests are best suited for the following libraries:
        * TensorStore
        * Zarr Python
    '''
    zarr_python.continuous_append_test(graph=graph[1], append_dim_size=200)
    tensorstore.continuous_append_test(graph=graph[1], append_dim_size=200) 
    z5.continuous_append_test(graph=graph[1], append_dim_size=200)

    graph[1].set_xlabel("Write Number")
    graph[1].set_title("Continuous Append Test")
   
    '''
    Continuous write tests:
    - These tests benchmark the creation of many increasingly large zarr folders.
    - These tests are best suited for the following libraries:
        * TensorStore
        * Zarr Python
        * OME Zarr
        * z5py
    '''
    tensorstore.continuous_write_test(graph=graph[0], append_dim_size=200)
    zarr_python.continuous_write_test(graph=graph[0], append_dim_size=200)
    ome_zarr.continuous_write_test(graph=graph[0], append_dim_size=90)   # crashes at anything above 16gigs (append_dim_size 90 on my machine)
    z5.continuous_write_test(graph=graph[0], append_dim_size=200)
    
    graph[0].set_xlabel("Data Size (GB)")
    graph[0].set_title("Continuous Write Test")
   
    for graph in fig.get_axes():
        graph.set_xlabel("Data Size (GB)")
        graph.grid()
        graph.legend()
        
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
