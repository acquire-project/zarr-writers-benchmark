from zarr_libraries import *
import numpy as np
import shutil
import matplotlib.axes

class Benchmark:
    def __init__(self, shape: list, chunks: list) -> None:
        self.__shape = shape
        self.__chunks = chunks
        self.__average_bandwidth = {}
        self.__zarr_writers = {
            "TensorStore" : Tensorstore(),
            "Zarr Python" : Zarr_Python(),
            "OME Zarr"    : Ome_Zarr(),
            "Cpp Zarr"    : Cpp_Zarr()
        }
    
    
    def run_write_tests(self, num_of_gigabytes: int, graph: matplotlib.axes._axes.Axes, avg_graph: matplotlib.axes._axes.Axes, show_results: bool) -> None:
        gb_in_bytes = 1073741824 # represents number of bytes in a GB
        
        for name, writer in self.__zarr_writers.items():
            print(f"\n\n--------{name} Stress Test--------\n\n")
            
            multiplier = 1 # multiplier that increases shape of zarr folder written
            curr_data_size = 0 # test will run until curr_data_size reaches specified GB size passed into the function
            write_speeds = []
            file_sizes = []
            
            while curr_data_size < (num_of_gigabytes * gb_in_bytes):
                # modify the append dimension, unpack the rest 
                new_shape = (self.__shape[0] * (multiplier), *self.__shape[1:]) 
                
                # Cpp zarr implementation creates data in cpp_zarr.cpp, skip here to avoid making unused data 
                if name != "Cpp Zarr":
                    zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
                
                # returns time taken to write zarr folder 
                total_time = writer.write_zarr(shape=new_shape, chunks=self.__chunks, zarr_data=zarr_data)
                
                # prints info to the terminal 
                print(f"Multiplier on first dimension : {multiplier}x\n{name} -> creating zarr : {total_time} seconds")
                print(f"The zarr folder is of size {folder_size(writer.get_data_path())}\n\n")
                
                curr_data_size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
                file_sizes.append(curr_data_size * 10**-9) # converts bytes to GB
                write_speeds.append((curr_data_size * 10**-9) / total_time) # GB/s
        
                # goes from 1 to 5, then adds 5 every time after that
                multiplier += 4 if multiplier == 1 else 5 
                
                shutil.rmtree(writer.get_data_path())
                
            graph.plot(file_sizes, write_speeds, label=name)
            avg_graph.bar(name, np.average(write_speeds))
            self.__average_bandwidth[name + " Write"] = np.average(write_speeds)
            print("--------------------------------------------------------------\n\n")
            
        if show_results:
            self.__print_results()


    def run_append_test(self, num_of_gigabytes: int, graph: matplotlib.axes._axes.Axes, avg_graph: matplotlib.axes._axes.Axes, show_results: bool) -> None:
        gb_in_bytes = 1073741824 # represents number of bytes in a GB
        write_size = np.prod(self.__shape) # amount of bytes appended on in each function call
        
        for name, writer in self.__zarr_writers.items():
            # these are the only libraries that allow for appending of data
            if name != "TensorStore" and name != "Zarr Python":
                continue
            
            print(f"\n\n--------{name} Append Stress Test--------\n\n")
            
            multiplier = 1 # multiplier that increases shape of zarr folder written
            curr_data_size = 0 # test will run until curr_data_size reaches specified GB size passed into the function
            write_speeds = []
            write_numbers = []
            
            while curr_data_size < (num_of_gigabytes * gb_in_bytes):
                # modify the append dimension, unpack the rest 
                new_shape = (self.__shape[0] * (multiplier), *self.__shape[1:]) 
                
                # creating new data and adjusting the shape
                zarr_data = np.random.randint(low=0, high=256, size=self.__shape, dtype=np.uint8)
                
                # returns time taken to write zarr folder / both libraries use a different approach hence the if statements
                if name == "TensorStore":
                    total_time = writer.append_zarr(shape=self.__shape, chunks=self.__chunks, new_shape=new_shape, zarr_data=zarr_data, multiplier=multiplier) 
                elif name == "Zarr Python":
                    total_time = writer.append_zarr(shape=self.__shape, chunks=self.__chunks, zarr_data=zarr_data) 
                
                # prints info to the terminal 
                print(f"Multiplier on first dimension : {multiplier}x\n{name} -> appending zarr : {total_time} seconds")
                print(f"The zarr folder is of size {folder_size(writer.get_data_path())}\n\n")
                
                curr_data_size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
                write_numbers.append(multiplier) # converts bytes to GB
                write_speeds.append((write_size * 10**-9) / total_time) # GB/s
        
                multiplier += 1
                
            shutil.rmtree(writer.get_data_path()) 
                
            graph.plot(write_numbers, write_speeds, label=name)
            avg_graph.bar(name, np.average(write_speeds))
            self.__average_bandwidth[name + " Append"] = np.average(write_speeds)
            print("--------------------------------------------------------------\n\n")
            
        if show_results:
            self.__print_results()
    
    
    def run_all_tests(self, write_test_gigabytes: int, append_test_gigabytes: int, 
                      write_graph: matplotlib.axes._axes.Axes, write_avg_graph: matplotlib.axes._axes.Axes,
                      append_graph: matplotlib.axes._axes.Axes, append_avg_graph: matplotlib.axes._axes.Axes,) -> None:
        
        self.run_write_tests(num_of_gigabytes=write_test_gigabytes, graph=write_graph, avg_graph=write_avg_graph, show_results=False)
        self.run_append_test(num_of_gigabytes=append_test_gigabytes, graph=append_graph, avg_graph=append_avg_graph, show_results=False)
        self.__print_results()
    
    
    def test_single_library(self) ->None:
        pass 
    
    def __print_results(self):
        print(f"Shape {self.__shape}, Chunks {self.__chunks}")
        print("----------Bandwidth----------")
        for test, bandwidth in self.__average_bandwidth.items():
            print(f"{test} : {bandwidth} GBps")
        print("\n\n")
    