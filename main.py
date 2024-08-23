import matplotlib.pyplot as plt 
from zarr_libraries import *


def main() -> None:
    
    def run_all_tests(shape: list, chunks: list) -> None:
        fig, graph = plt.subplots(2, 2)
        bandwidth_map = {}
        zarr_writers = {
            "TensorStore" : Tensorstore(shape=shape, chunks=chunks),
            "Zarr Python" : Zarr_Python(shape=shape, chunks=chunks),
            "OME Zarr"    : Ome_Zarr(shape=shape, chunks=chunks),
            "Cpp Zarr"    : Cpp_Zarr(shape=shape, chunks=chunks)
        }
        
        '''
        Append Tests:
        - These tests benchmark the continuous appending to a single zarr folder.
        - These tests are best suited for the following libraries:
            * TensorStore
            * Zarr Python
        '''
        for name, writer in zarr_writers.items():
            if name != "TensorStore" and name != "Zarr Python":
                continue

            bandwidth_map[name + " Append"] = (
                writer.continuous_append_test(graph=graph[1][0], avg_graph=graph[1][1], append_dim_size=100)
            ) 
        
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
        '''
        for name, writer in zarr_writers.items():
            bandwidth_map[name + " Write"] = (
                writer.continuous_write_test(graph=graph[0][0], avg_graph=graph[0][1], append_dim_size=51, step=5)
            ) 
         
        # print the average bandwidth for each of the tests
        print(f"Shape {shape}, Chunks {chunks}")
        print("----------Bandwidth----------")
        for test, bandwidth in bandwidth_map.items():
            print(f"{test} : {bandwidth} GBps")
        print("\n\n")
        
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
        
    
    run_all_tests(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    plt.show()
    

if __name__ == "__main__":
    main()
