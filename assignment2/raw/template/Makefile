CUDA_ROOT=$(CUDA_HOME)
INC=-I./inc
LIB=
ifneq ($(strip $(CUDA_ROOT)),)
INC+=-I"$(CUDA_ROOT)/include"
LIB+=-L"$(CUDA_ROOT)/lib64"
endif
NVCC=nvcc
NVCC_FLAGS=-O2 -std=c++14 --compiler-options "-O2 -Wall -Wextra"

.PHONY: build es2.1 es2.2 es2.3 clean rebuild
build: es2.1 es2.2 es2.3

es2.1: ./bin/nullKernelAsync ./bin/nullKernelAsyncVarious
es2.2: ./bin/waitKernel
es2.3: ./bin/pcie_benchmark

clean:
	rm -f ./bin/nullKernelAsync ./bin/nullKernelAsyncVarious ./bin/waitKernel ./bin/pcie_benchmark

rebuild: clean
	$(MAKE) build

./bin:
	mkdir -p $@

./bin/nullKernelAsync: ./src/es2.1/nullKernelAsync.cu ./inc/chTimer.h | ./bin
	$(NVCC) $(NVCC_FLAGS) -o $@ $< $(INC) $(LIB)

./bin/nullKernelAsyncVarious: ./src/es2.1/nullKernelAsyncVarious.cu ./inc/chTimer.h | ./bin
	$(NVCC) $(NVCC_FLAGS) -o $@ $< $(INC) $(LIB)

./bin/waitKernel: ./src/es2.2/waitKernel.cu ./inc/chTimer.h | ./bin
	$(NVCC) $(NVCC_FLAGS) -o $@ $< $(INC) $(LIB)

./bin/pcie_benchmark: ./src/es2.3/pcie_benchmark.cu | ./bin
	$(NVCC) $(NVCC_FLAGS) -o $@ $< $(INC) $(LIB)
