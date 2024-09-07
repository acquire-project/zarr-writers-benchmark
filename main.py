import matplotlib.pyplot as plt 
from benchmark import Benchmark


def main() -> None:
    fig, graph = plt.subplots(2, 2)
    benchmark = Benchmark(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    
    benchmark.run_all_tests(
        append_test_gigabytes=50, write_test_gigabytes=5, choose_lib="Cpp Zarr",
        append_graph=graph[1][0], append_avg_graph=graph[1][1],
        write_graph=graph[0][0], write_avg_graph=graph[0][1]
    )
    
    # setting up graph for append tests
    graph[1][0].set_xlabel("Write Number")
    graph[1][0].set_title("Continuous Append Test")
    graph[1][0].legend()
    
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
        
    fig.canvas.manager.set_window_title(f'shape: {benchmark.shape}, chunks: {benchmark.chunks}')
    plt.tight_layout()
    plt.show()
    

if __name__ == "__main__":
    main()
