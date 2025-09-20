import numpy as np
import cupy as cp
reflect_kernel = cp.RawKernel(r'''
extern "C" __global__
void mirror(float* arr, const int ndim, const long long* shape,
            const long long* strides, const int axis, const int i, const int mode) {
    long long idx = (long long)blockDim.x * (long long)blockIdx.x + (long long)threadIdx.x;
    long long size = 1;
    for (int d=0; d<ndim; d++) size *= shape[d];
    if (idx >= size) return;
    long long coords[16];
    long long tmp = idx;
    for (int d = ndim - 1; d >= 0; d--) {
        coords[d] = tmp % shape[d];
        tmp /= shape[d];
    }
    int j = (int)coords[axis];
    int n = (int)shape[axis];
    int dist = j - i;
    if (mode == 0 && dist > 0) {
        int mirror_j = i - dist;
        if (mirror_j >= 0) {
            coords[axis] = mirror_j;
        } else {
            return;
        }
    } else if (mode == 1 && dist < 0) {
        int mirror_j = i - dist;
        if (mirror_j < n) {
            coords[axis] = mirror_j;
        } else {
            return;
        }
    } else {
        return;
    }
    long long offset_src = 0;
    for (int d=0; d<ndim; d++) offset_src += coords[d] * strides[d];
    long long offset_dst = 0;
    tmp = idx;
    for (int d=ndim-1; d>=0; d--) {
        int c = (int)(tmp % shape[d]);
        tmp /= shape[d];
        offset_dst += (long long)c * strides[d];
    }
    arr[offset_dst] = arr[offset_src];
}
''', 'mirror')
def reflect(arr: cp.ndarray, i: int, axis: int = 0, mode: str = "out", out: cp.ndarray = None):
    if not isinstance(arr, cp.ndarray):
        raise TypeError("arr must be a cupy ndarray")
    if arr.dtype != cp.float32:
        raise TypeError(f"reflect only supports float32, got {arr.dtype}")
    if out is None:
        result = arr.copy()
    else:
        if not isinstance(out, cp.ndarray):
            raise TypeError("out must be a cupy ndarray or None")
        if out.shape != arr.shape:
            raise ValueError(f"output array shape {out.shape} does not match input shape {arr.shape}")
        if out.dtype != arr.dtype:
            raise ValueError(f"output array dtype {out.dtype} does not match input dtype {arr.dtype}")
        result = out
        if result is not arr:
            cp.copyto(result, arr)
    if axis < 0:
        axis += result.ndim
    if axis < 0 or axis >= result.ndim:
        raise IndexError(f"axis {axis} is out of bounds for array of dimension {result.ndim}")
    n = result.shape[axis]
    if i < 0:
        i += n
    if i < 0 or i >= n:
        raise IndexError(f"index {i} is out of bounds for axis {axis} with size {n}")
    size = result.size
    threads = 256
    blocks = (size + threads - 1) // threads
    shape_host = np.array(result.shape, dtype=np.int64)
    strides_host = np.array(result.strides, dtype=np.int64) // result.itemsize
    shape_dev = cp.asarray(shape_host)
    strides_dev = cp.asarray(strides_host)
    if mode == "out":
        mode_flag = 0
    elif mode == "in":
        mode_flag = 1
    else:
        raise ValueError("mode must be 'out' or 'in'")
    reflect_kernel((blocks,), (threads,),
                   (result, int(result.ndim),
                    int(shape_dev.data.ptr), int(strides_dev.data.ptr),
                    int(axis), int(i), int(mode_flag)))
    return result
if __name__ == "__main__":
    print("CUDA device:", cp.cuda.runtime.getDevice())
    print("CuPy version:", cp.__version__)
    A = cp.arange(2 * 3 * 3, dtype=cp.float32).reshape(2, 3, 3)
    print("A (test1) before:\n", A.get())
    B = reflect(A, 1, axis=0)
    print("A (test1) after reflect axis=0, i=1:\n", B.get())
    A2 = cp.random.rand(3, 3).astype(cp.float32)
    print("\nA2 before:\n", A2.get())
    R = reflect(A2, 1, axis=0)
    print("A2 after reflect(A2,1,axis=0):\n", R.get())
    A3 = cp.arange(3 * 4, dtype=cp.float32).reshape(3, 4)
    print("\nA3 before:\n", A3.get())
    print("reflect(A3,1,axis=1):\n", reflect(A3, 1, axis=1).get())
    print("\nDone.")

