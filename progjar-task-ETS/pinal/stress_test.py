import time
import os
import random
import string
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from client_worker import upload_file, download_file

def generate_test_file(filepath, size_mb):
    with open(filepath, "wb") as f:
        f.write(os.urandom(size_mb * 1024 * 1024))

def run_task(op, size_mb, port, worker_id, storage_dir):
    temp_file = f"{storage_dir}/temp_{worker_id}_{size_mb}MB.dat"
    if op == "upload":
        generate_test_file(temp_file, size_mb)
        start = time.time()
        msg, success = upload_file(port, temp_file)
        end = time.time()
        total_time = end - start
        bytes_sent = size_mb * 1024 * 1024 if success else 0
        return (success, total_time, bytes_sent)
    elif op == "download":
        start = time.time()
        filename = f"test_{size_mb}MB.dat"
        msg, success = download_file(port, filename, storage_dir)
        end = time.time()
        total_time = end - start
        bytes_received = size_mb * 1024 * 1024 if success else 0
        return (success, total_time, bytes_received)
    return (False, 0, 0)

def stress_test(op, size_mb, client_workers, port, mode="thread"):
    results = []

    # make sure file exists for download test
    if op == "download":
        testfile = f"test_{size_mb}MB.dat"
        if not os.path.exists(testfile):
            generate_test_file(testfile, size_mb)
            upload_file(port, testfile)

    args = [(op, size_mb, port, i, "stress_temp") for i in range(client_workers)]
    os.makedirs("stress_temp", exist_ok=True)

    start = time.time()

    if mode == "thread":
        with ThreadPoolExecutor(max_workers=client_workers) as executor:
            results = list(executor.map(lambda arg: run_task(*arg), args))
    elif mode == "process":
        with Pool(processes=client_workers) as pool:
            results = pool.starmap(run_task, args)

    end = time.time()
    total_duration = end - start

    success_count = sum(1 for res in results if res[0])
    fail_count = client_workers - success_count
    total_bytes = sum(res[2] for res in results if res[0])
    avg_time = sum(res[1] for res in results if res[0]) / success_count if success_count else 0
    throughput = total_bytes / total_duration if total_duration > 0 else 0

    return {
        "op": op,
        "size_mb": size_mb,
        "workers": client_workers,
        "success": success_count,
        "fail": fail_count,
        "total_time": round(total_duration, 2),
        "avg_time": round(avg_time, 2),
        "throughput": round(throughput, 2)
    }
