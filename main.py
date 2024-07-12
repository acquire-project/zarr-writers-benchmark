import matplotlib.pyplot as plt 
from zarr_libraries import *
import time


def main() -> None:
    zarr_python = Zarr_Python(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    tensorstore = Tensorstore(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    ome_zarr = Ome_Zarr(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    
    '''
    Append Tests:
    - These tests benchmark the continuous appending to a single zarr folder.
    - These tests are best suited for the following libraries:
        * TensorStore
        * Zarr Python
    '''
    t = time.perf_counter()
    zarr_python.continuous_append_test(append_dim_size=200)
    tensorstore.continuous_append_test(append_dim_size=200) 
    print(f"\n\nTotal time for continuous append tests : {time.perf_counter() - t} seconds\n\n")
   
    '''
    Continuous write tests:
    - These tests benchmark the creation of many increasingly large zarr folders.
    - These tests are best suited for the following libraries:
        * TensorStore
        * Zarr Python
        * OME Zarr
    '''
    t = time.perf_counter()
    tensorstore.continuous_write_test(append_dim_size=200)
    zarr_python.continuous_write_test(append_dim_size=200)
    ome_zarr.continuous_write_test(append_dim_size=90)   # crashes at anything above 16gigs
    print(f"\n\nTotal time for continuous write tests : {time.perf_counter() - t} seconds\n\n")
   
    plt.legend()
    plt.xlabel("Data Size (GB)")
    plt.ylabel("Bandwidth (GBps)")
    plt.show()


if __name__ == "__main__":
    main()
