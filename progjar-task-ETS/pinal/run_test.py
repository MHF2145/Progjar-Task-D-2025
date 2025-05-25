import csv
from stress_test import stress_test

def run_all_tests(port, mode):
    ops = ["upload", "download"]
    sizes = [10, 50, 100]
    client_workers = [1, 5, 50]
    server_workers = [1, 5, 50]

    results = []
    counter = 1

    for op in ops:
        for size in sizes:
            for cw in client_workers:
                for sw in server_workers:
                    print(f"\n[#{counter:02}] {op.upper()} | {size}MB | Client:{cw} | Server:{sw} | Mode:{mode.upper()}")
                    result = stress_test(op, size, cw, port, mode)
                    result_row = {
                        "No": counter,
                        "Operasi": op,
                        "Volume (MB)": size,
                        "Client Workers": cw,
                        "Server Workers": sw,
                        "Waktu Total (s)": result["total_time"],
                        "Throughput (Bps)": result["throughput"],
                        "Client Sukses": result["success"],
                        "Client Gagal": result["fail"],
                        "Rata2 Waktu per Client": result["avg_time"]
                    }
                    results.append(result_row)
                    counter += 1

    filename = f"stress_results_{mode}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Semua tes selesai. Hasil disimpan di {filename}")

if __name__ == "__main__":
    print("=== RUNNING FOR THREAD SERVER ===")
    run_all_tests(port=3535, mode="thread")

    print("\n=== RUNNING FOR PROCESS SERVER ===")
    run_all_tests(port=3536, mode="process")
