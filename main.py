import matplotlib.pyplot as plt 
from benchmark import Benchmark


def main() -> None:
    fig, graph = plt.subplots(2, 2)
    benchmark = Benchmark(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    
    benchmark.run_all_tests(
        write_test_gigabytes=2, append_test_gigabytes=2, 
        write_graph=graph[0][0], write_avg_graph=graph[0][1],
        append_graph=graph[1][0], append_avg_graph=graph[1][1]
    )
    

if __name__ == "__main__":
    main()
