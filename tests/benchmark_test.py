from benchmark import Benchmark
import pytest


def test_benchmark_get_shape():
    shape = [256, 256, 256]
    chunks = [64, 64, 64]
    benchmark = Benchmark(shape=shape, chunks=chunks)
    
    assert benchmark.shape == shape
    
    
def test_benchmark_get_chunks():
    shape = [256, 256, 256]
    chunks = [64, 64, 64]
    benchmark = Benchmark(shape=shape, chunks=chunks)
    
    assert benchmark.chunks == chunks
    
    
@pytest.mark.parametrize(
    ("lib_name"),
    [
        (""),
        ("."),
        (" ")
    ]
)
def test_if_incorrect_lib_name_in_write_tests_fails(lib_name: str):
    shape = [256, 256, 256]
    chunks = [64, 64, 64]
    benchmark = Benchmark(shape=shape, chunks=chunks)
    
    with pytest.raises(ValueError):
        benchmark.run_write_tests(num_of_gigabytes=1, show_results=False, choose_lib=lib_name) 


@pytest.mark.parametrize(
    ("lib_name"),
    [
        (""),
        ("."),
        (" ")
    ]
)
def test_if_incorrect_lib_name_in_append_tests_fails(lib_name: str):
    shape = [256, 256, 256]
    chunks = [64, 64, 64]
    benchmark = Benchmark(shape=shape, chunks=chunks)    
    
    with pytest.raises(ValueError):
        benchmark.run_append_tests(num_of_gigabytes=1, show_results=False, choose_lib=lib_name)


@pytest.mark.parametrize(
    ("lib_name"),
    [
        (""),
        ("."),
        (" ")
    ]
)
def test_if_incorrect_lib_name_in_run_all_tests_fails(lib_name: str):
    shape = [256, 256, 256]
    chunks = [64, 64, 64]
    benchmark = Benchmark(shape=shape, chunks=chunks)  
    
    with pytest.raises(ValueError):
        benchmark.run_all_tests(append_test_gigabytes=1, write_test_gigabytes=1, choose_lib=lib_name)  
