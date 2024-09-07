FROM continuumio/miniconda3

# set directory to root for insatlling dependencies
WORKDIR /app

# install system dependencies 
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-opengl \
    gcc \
    build-essential \
    cmake \
    zlib1g-dev \
    uuid-dev

RUN git clone https://github.com/abcucberkeley/cpp-zarr && \
    cd cpp-zarr && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j && \
    make install

WORKDIR /app

RUN git clone https://github.com/microsoft/vcpkg.git && \
    cd vcpkg && ./bootstrap-vcpkg.sh

RUN pip install "pybind11[global]"

# set directory for code base
WORKDIR /app/benchmark

# move environment.yml from source to docker app
COPY environment.yml ./

# installing dependancies
RUN conda env create -n benchmark --file environment.yml

# activating conda env
RUN echo "source activate benchmark" > ~/.bashrc 

# set conda to path for working in docker terminal
ENV PATH=/opt/conda/envs/benchmark/bin:$PATH

# set vcpkg to path for cmake
ENV VCPKG_ROOT=/path/to/vcpkg
ENV PATH=$VCPKG_ROOT:$PATH

# copy source code into docker app
COPY . .

# build c++ code 
RUN cmake --preset=default && \
    cmake --build build

# running the benchmark
CMD [ "python", "main.py" ]