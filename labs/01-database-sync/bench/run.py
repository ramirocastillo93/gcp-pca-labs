#!/usr/bin/env python3
"""Run mixed writes on the VM and observe replication to Cloud SQL.

Run this on the VM as the Linux postgres user. No database password is written
to a file or passed as a command-line argument.
"""

import argparse
import concurrent.futures
import getpass
import ipaddress
import json
import os
import pathlib
import pwd
import subprocess
import sys
import tempfile
import time
import uuid


DATABASE = "lab"
TABLE = "public.legacy_owned"
SUBSCRIPTION = "vm_to_cloud"


def query(sql, *, cloud_ip=None, cloud_password=None):
    command = ["psql", "-X", "-q", "-w", "-A", "-t", "-v", "ON_ERROR_STOP=1"]
    environment = os.environ.copy()
    environment.pop("PGPASSWORD", None)

    if cloud_ip is None:
        command += ["-h", "/var/run/postgresql", "-U", "postgres"]
    else:
        command += ["-h", cloud_ip, "-p", "5432", "-U", "postgres"]
        environment["PGPASSWORD"] = cloud_password
        environment["PGSSLMODE"] = "require"

    command += ["-d", DATABASE, "-c", sql]
    result = subprocess.run(command, env=environment, capture_output=True, text=True)
    if result.returncode:
        target = "Cloud SQL" if cloud_ip else "VM"
        raise RuntimeError(f"{target} query failed: {result.stderr.strip()}")
    return result.stdout.strip()


def count_rows(*, cloud_ip=None, cloud_password=None):
    return int(query(f"SELECT count(*) FROM {TABLE}", cloud_ip=cloud_ip,
                     cloud_password=cloud_password))


def fingerprint(*, cloud_ip=None, cloud_password=None):
    # Include every id and note in a stable order. The count helps explain a
    # mismatch; the hash also catches changed values when counts are equal.
    result = query(f"""
        SELECT json_build_object(
            'rows', count(*),
            'md5', md5(COALESCE(
                string_agg(jsonb_build_array(id, note)::text, E'\\n' ORDER BY id),
                ''
            ))
        )
        FROM {TABLE}
    """, cloud_ip=cloud_ip, cloud_password=cloud_password)
    return json.loads(result)


def prepare_sequence():
    # The table already has manually assigned IDs. A VM-only sequence gives
    # pgbench unique IDs without changing the replicated table's schema.
    query("CREATE SEQUENCE IF NOT EXISTS public.legacy_owned_bench_seq")
    query("""
        SELECT setval(
            'public.legacy_owned_bench_seq',
            GREATEST(
                (SELECT COALESCE(max(id), 1) FROM public.legacy_owned),
                (SELECT last_value FROM public.legacy_owned_bench_seq)
            )
        )
    """)


def seed_benchmark_rows(run_tag):
    # Leave a starting pool so UPDATE and DELETE can touch real rows even if
    # pgbench selects either operation before its first INSERT.
    return int(query(f"""
        WITH inserted AS (
            INSERT INTO {TABLE} (id, note)
            SELECT nextval('public.legacy_owned_bench_seq'), '{run_tag}-seed'
            FROM generate_series(1, 100)
            RETURNING id
        )
        SELECT min(id) FROM inserted
    """))


def write_benchmark_scripts(directory, run_tag, first_id):
    # pgbench chooses one script per transaction using these relative weights.
    # The id boundary and run tag restrict UPDATE/DELETE to this run's rows.
    # Pick a random ID, then use the primary-key order to find a live row.
    # This avoids sorting the whole run with ORDER BY random().
    candidate = (
        f"SELECT id FROM {TABLE} WHERE id >= ("
        f"SELECT {first_id} + floor(random() * "
        f"GREATEST(last_value - {first_id} + 1, 1))::bigint "
        "FROM public.legacy_owned_bench_seq) "
        f"AND note LIKE '{run_tag}%' ORDER BY id LIMIT 1 "
        "FOR UPDATE SKIP LOCKED"
    )
    fallback = (
        f"SELECT id FROM {TABLE} WHERE id >= {first_id} "
        f"AND note LIKE '{run_tag}%' ORDER BY id LIMIT 1 "
        "FOR UPDATE SKIP LOCKED"
    )
    scripts = {
        "insert": (
            "INSERT INTO public.legacy_owned (id, note) "
            "VALUES (nextval('public.legacy_owned_bench_seq'), "
            f"'{run_tag}-insert');\n"
        ),
        "update": (
            f"UPDATE {TABLE} SET note = '{run_tag}-updated-' || md5(random()::text) "
            f"WHERE id = COALESCE(({candidate}), ({fallback}));\n"
        ),
        "delete": (
            f"DELETE FROM {TABLE} WHERE id = COALESCE("
            f"({candidate}), ({fallback}));\n"
        ),
    }
    weighted_files = []
    for operation, weight in (("insert", 50), ("update", 30), ("delete", 20)):
        path = pathlib.Path(directory) / f"{operation}.sql"
        path.write_text(scripts[operation])
        weighted_files += ["-f", f"{path}@{weight}"]
    return weighted_files


def marker_delay_ms(cloud_ip, cloud_password):
    # Measure from the acknowledged VM commit to the first Cloud SQL read
    # that can see this row. Polling makes this an upper-bound estimate.
    marker = "marker-" + uuid.uuid4().hex
    marker_id = int(query(
        f"INSERT INTO {TABLE} (id, note) "
        f"VALUES (nextval('public.legacy_owned_bench_seq'), '{marker}') "
        "RETURNING id"
    ))
    committed_at = time.monotonic()
    deadline = committed_at + 15
    while time.monotonic() < deadline:
        visible = query(
            f"SELECT EXISTS (SELECT 1 FROM {TABLE} WHERE id = {marker_id})",
            cloud_ip=cloud_ip, cloud_password=cloud_password,
        )
        if visible == "t":
            return round((time.monotonic() - committed_at) * 1000)
        time.sleep(0.1)
    return None


def wait_for_cloud_row(row_id, expected_note, cloud_ip, cloud_password):
    # expected_note is generated locally as a UUID-based string, never user SQL.
    started = time.monotonic()
    deadline = started + 15
    while time.monotonic() < deadline:
        actual = query(
            f"SELECT note FROM {TABLE} WHERE id = {row_id}",
            cloud_ip=cloud_ip, cloud_password=cloud_password,
        )
        if actual == expected_note:
            return round((time.monotonic() - started) * 1000)
        time.sleep(0.1)
    raise RuntimeError(f"Cloud SQL did not show expected row {row_id} within 15 seconds")


def verify_changes(cloud_ip, cloud_password):
    # Touch only a uniquely identified probe row on the VM. Its final DELETE
    # leaves no probe row in either database once replication catches up.
    probe = "integrity-" + uuid.uuid4().hex
    row_id = int(query(
        f"INSERT INTO {TABLE} (id, note) "
        f"VALUES (nextval('public.legacy_owned_bench_seq'), '{probe}') "
        "RETURNING id"
    ))
    insert_ms = wait_for_cloud_row(row_id, probe, cloud_ip, cloud_password)

    updated = probe + "-updated"
    query(f"UPDATE {TABLE} SET note = '{updated}' WHERE id = {row_id}")
    update_ms = wait_for_cloud_row(row_id, updated, cloud_ip, cloud_password)

    query(f"DELETE FROM {TABLE} WHERE id = {row_id}")
    delete_ms = wait_for_cloud_row(row_id, "", cloud_ip, cloud_password)
    print(json.dumps({"change_replication_ms": {
        "insert": insert_ms, "update": update_ms, "delete": delete_ms,
    }}, separators=(",", ":")), flush=True)


def verify_fingerprint(cloud_ip, cloud_password):
    # Call only after the load and probe writes have stopped. Allow the
    # subscriber up to 30 seconds to catch up before declaring a mismatch.
    deadline = time.monotonic() + 30
    while True:
        vm = fingerprint()
        cloud = fingerprint(cloud_ip=cloud_ip, cloud_password=cloud_password)
        matching = vm == cloud
        if matching or time.monotonic() >= deadline:
            print(json.dumps({"integrity": {
                "VM": vm, "CloudSQL": cloud, "equal": matching,
            }}, separators=(",", ":")), flush=True)
            if not matching:
                raise RuntimeError("row counts or fingerprints differ after 30 seconds")
            return
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cloud_sql_ip", help="private IP of the lab Cloud SQL instance")
    parser.add_argument("--seconds", type=int, default=60, help="test duration (default: 60)")
    parser.add_argument("--rps", type=int, default=100,
                        help="target transactions per second (default: 100)")
    parser.add_argument("--clients", type=int, default=2,
                        help="concurrent pgbench clients (default: 2)")
    parser.add_argument("--threads", type=int, default=1,
                        help="pgbench worker threads (default: 1)")
    parser.add_argument("--sample-every", type=int, default=1,
                        help="seconds between row-count samples (default: 1)")
    parser.add_argument("--integrity-only", action="store_true",
                        help="check INSERT/UPDATE/DELETE and compare all rows without pgbench")
    args = parser.parse_args()

    try:
        address = ipaddress.IPv4Address(args.cloud_sql_ip)
    except ipaddress.AddressValueError:
        parser.error("cloud_sql_ip must be an IPv4 address")
    if not address.is_private:
        parser.error("cloud_sql_ip must be a private IPv4 address")
    if not 1 <= args.seconds <= 600:
        parser.error("--seconds must be between 1 and 600")
    if not 1 <= args.rps <= 10000:
        parser.error("--rps must be between 1 and 10000")
    if not 1 <= args.clients <= 128:
        parser.error("--clients must be between 1 and 128")
    if not 1 <= args.threads <= args.clients:
        parser.error("--threads must be between 1 and --clients")
    if not 1 <= args.sample_every <= 60:
        parser.error("--sample-every must be between 1 and 60")
    if os.geteuid() != pwd.getpwnam("postgres").pw_uid:
        parser.error("run on the VM as the Linux postgres user (sudo -u postgres)")

    cloud_password = getpass.getpass("Cloud SQL postgres password: ")
    if not cloud_password:
        parser.error("Cloud SQL password cannot be empty")

    # Fail before writing anything if the table or subscription is absent.
    count_rows()
    count_rows(cloud_ip=args.cloud_sql_ip, cloud_password=cloud_password)
    enabled = query(
        f"SELECT EXISTS (SELECT 1 FROM pg_subscription "
        f"WHERE subname = '{SUBSCRIPTION}' AND subenabled)",
        cloud_ip=args.cloud_sql_ip, cloud_password=cloud_password,
    )
    if enabled != "t":
        parser.error(f"Cloud SQL subscription {SUBSCRIPTION} is not enabled")

    prepare_sequence()
    if args.integrity_only:
        verify_changes(args.cloud_sql_ip, cloud_password)
        verify_fingerprint(args.cloud_sql_ip, cloud_password)
        return

    run_tag = "bench-" + uuid.uuid4().hex
    first_id = seed_benchmark_rows(run_tag)
    print(json.dumps({"workload": {
        "mix": {"insert": 50, "update": 30, "delete": 20},
        "seeded_rows": 100,
    }}, separators=(",", ":")), flush=True)
    with tempfile.TemporaryDirectory(prefix="pca-sync-bench-") as directory:
        weighted_files = write_benchmark_scripts(directory, run_tag, first_id)
        bench = subprocess.Popen(
            ["pgbench", "-n", "-c", str(args.clients), "-j", str(args.threads),
             "-R", str(args.rps),
             "-T", str(args.seconds), *weighted_files, "-h", "/var/run/postgresql",
             "-U", "postgres", DATABASE],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        started = time.monotonic()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                marker_result = None
                sample_times = sorted(set(range(args.sample_every, args.seconds + 1,
                                                args.sample_every)) | {args.seconds})
                for second in sample_times:
                    if bench.poll() is not None:
                        break
                    time.sleep(max(0, started + second - time.monotonic()))
                    if bench.poll() is not None:
                        break
                    if marker_result is None and second >= max(1, args.seconds // 3):
                        marker_result = pool.submit(
                            marker_delay_ms, args.cloud_sql_ip, cloud_password
                        )
                    vm_result = pool.submit(count_rows)
                    cloud_result = pool.submit(
                        count_rows, cloud_ip=args.cloud_sql_ip,
                        cloud_password=cloud_password,
                    )
                    vm_count = vm_result.result()
                    cloud_count = cloud_result.result()
                    print(json.dumps({
                        "second": second,
                        "elapsed_s": round(time.monotonic() - started, 2),
                        "data": {"VM": vm_count, "CloudSQL": cloud_count},
                        "gap": vm_count - cloud_count,
                    }, separators=(",", ":")), flush=True)
                    if bench.poll() is not None:
                        break
                if marker_result is not None:
                    print(json.dumps({"marker_visibility_ms": marker_result.result()}),
                          flush=True)
            bench_output, _ = bench.communicate()
        finally:
            if bench.poll() is None:
                bench.terminate()
                bench.communicate()

    print(bench_output, file=sys.stderr, end="")
    if bench.returncode:
        raise RuntimeError(f"pgbench exited with status {bench.returncode}")
    verify_changes(args.cloud_sql_ip, cloud_password)
    verify_fingerprint(args.cloud_sql_ip, cloud_password)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
