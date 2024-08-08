# Benchmarking Zarr Writers 

This benchmarking suite compares the following Zarr writers (click for documentation):
- [Acquire](https://acquire-project.github.io/acquire-docs/) 
- [TensorStore](https://google.github.io/tensorstore/)
- [Zarr-Python](https://zarr.readthedocs.io/en/stable/index.html)
- [OME-Zarr](https://ome-zarr.readthedocs.io/en/stable/)

## Building and Running

To build and run the benchmark in this program, you need to install the various Zarr writers on your machine. Refer below to see what options you have for your operating system.

### Linux

An "environment.yml" has been provided for simplifying the dependency process on Linux. Simply download [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) and execute the following commands to run the program.
```bash
conda env create -n benchmark --file environment.yml
conda activate benchmark
python main.py
```

### Mac and Windows

Since some of the dependencies are only available on Linux, a Dockerfile has been left to allow building on other systems. Simply download [Docker](https://www.docker.com/) and execute the following commadns to run the program.

```bash
docker build -t benchmark .
docker run -it benchmark
```
