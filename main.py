import matplotlib.pyplot as plt 
from zarr_libraries import *


def main() -> None:
    zarr_python = Zarr_Python(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    tensorstore = Tensorstore(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    ome_zarr = Ome_Zarr(shape=[64, 1080, 1920], chunks=[64, 540, 960])
    '''
    Append Tests:
    - These tests benchmark the continuous appending to a single zarr folder 
    - The append dimension size passed in equates to ~26 gigs of data
    '''
    #zarr_python.continuous_append_test(append_dim_size=30)
    #tensorstore.continuous_append_test(append_dim_size=12) 
    # at around 17 gigs of data ome-zarr throws an error
    #ome_zarr.continuous_append_test(append_dim_size=12) 
   
    '''
    Continuous write tests:
    - These tests benchmark the creation of many increasingly large zarr folders
    '''
    #acquire_radialSin_test()
    #tensorstore.continuous_write_test(append_dim_size=10)
    #zarr_python.continuous_write_test(append_dim_size=10)
    #ome_zarr.continuous_write_test(append_dim_size=10)
   
    plt.legend()
    plt.xlabel("Data Size (GB)")
    plt.ylabel("Bandwidth (GBps)")
    plt.show()


if __name__ == "__main__":
    main()
