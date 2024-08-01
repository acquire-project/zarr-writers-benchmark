FROM continuumio/miniconda3

# set working dir for docker app
WORKDIR /app

# install system dependencies including OpenGL
RUN apt-get update && apt-get install -y \
    python3-opengl \
    mesa-utils \
    libgl1-mesa-glx \
    libgl1-mesa-dri

# move environment.yml from source to docker app
COPY environment.yml ./

# installing dependancies
RUN conda env create -n benchmark --file environment.yml

# had source instead of conda here
RUN echo "source activate benchmark" > ~/.bashrc 

# set conda to path
ENV PATH=/opt/conda/envs/benchmark/bin:$PATH

# copy source code into docker app
COPY . .

# running the benchmark
CMD [ "python", "main.py" ]