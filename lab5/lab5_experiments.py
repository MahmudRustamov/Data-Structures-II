"""Lab 5 experiments for Parts A-E, plus optional LRU challenge.
Based on Week 5 handout. Results depend on machine and Python hash seed.
Run: python3 lab5_experiments.py
"""
import csv
import json
import random
import statistics
import time
from bisect import bisect_left
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from lab5g_starter import (BOOK_FUNCTIONS, GOOD_FUNCTIONS, HashTable,
                           LRUCache, hash_a, hash_c, hash_python)

OUT = Path(__file__).resolve().parent / 'lab5_results'
OUT.mkdir(exist_ok=True)
rng = random.Random(2026)
report = {}

def write_csv(name, fields, rows):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def lookup_steps(table, keys):
    table.steps = 0
    for k in keys:
        table.get(k)
    return table.steps / len(keys)

def part_a():
    phone = {'Alice': '+998901234567', 'Bob': '+998911234567'}
    dns = {'example.com': '93.184.215.14', 'localhost': '127.0.0.1'}
    a1 = {'phone_found': phone['Alice'], 'phone_missing': phone.get('Nobody'),
          'dns_found': dns['localhost']}
    phone['Alice'] = '+998901234568'
    a1['phone_updated'] = phone['Alice']

    arrivals = [rng.randrange(15000) for _ in range(20000)]
    times, repeats = {}, {}
    for kind in ['list', 'dict', 'set']:
        seen = [] if kind == 'list' else {} if kind == 'dict' else set()
        start = time.perf_counter()
        repeat = 0
        for voter in arrivals:
            if voter in seen:
                repeat += 1
            else:
                if kind == 'list': seen.append(voter)
                elif kind == 'dict': seen[voter] = True
                else: seen.add(voter)
        times[kind] = time.perf_counter() - start
        repeats[kind] = repeat
    assert len(set(repeats.values())) == 1

    urls = [f'/page/{i}' for i in range(1, 201)]
    requests = rng.choices(urls, weights=[1 / i for i in range(1, 201)], k=5000)
    calls = 0
    def server(url):
        nonlocal calls
        calls += 1
        return f'<html>{url}</html>'
    cache = {}
    hits = 0
    def get_page(url):
        nonlocal hits
        if url in cache:
            hits += 1
            return cache[url]
        cache[url] = server(url)
        return cache[url]
    for url in requests: get_page(url)
    a3 = {'requests': len(requests), 'cache_calls': calls,
          'cache_hits': hits, 'cache_hit_rate': hits / len(requests),
          'no_cache_calls': len(requests), 'no_cache_server_s': 0.05 * len(requests),
          'cache_server_s': 0.05 * calls}
    report['A1'] = a1
    report['A2'] = {'seconds': times, 'repeats': repeats}
    report['A3'] = a3
    write_csv('table1_part_a.csv', ['measurement', 'list_no_cache', 'dict_or_cache'], [
        {'measurement': 'Voting: seconds for 20000 arrivals', 'list_no_cache': times['list'], 'dict_or_cache': times['dict']},
        {'measurement': 'Voting: repeat visits', 'list_no_cache': repeats['list'], 'dict_or_cache': repeats['dict']},
        {'measurement': 'Cache: server calls', 'list_no_cache': len(requests), 'dict_or_cache': calls},
        {'measurement': 'Cache: hit rate', 'list_no_cache': 0, 'dict_or_cache': hits / len(requests)},
        {'measurement': 'Cache: simulated server seconds', 'list_no_cache': 250, 'dict_or_cache': 0.05 * calls},
    ])
    return requests

def part_b():
    consistency = {
        'hash_a_same_input': hash_a('apple', 10) == hash_a('apple', 10),
        'python_hash_same_process': hash_python('apple', 10) == hash_python('apple', 10),
        'random_slot_not_guaranteed_consistent': True,
        'next_empty_slot_depends_on_table_contents': True,
    }

    # B2: Exercises 5.1-5.4
    def exercise_5_1(x):
        return 1

    def exercise_5_2(x):
        return random.random()

    slots = [None] * 10

    def exercise_5_3(x):
        for i, value in enumerate(slots):
            if value is None:
                slots[i] = x
                return i
        return None

    def exercise_5_4(x):
        return len(x)

    results = []

    for name, fn in [
        ("5.1", exercise_5_1),
        ("5.2", exercise_5_2),
        ("5.3", exercise_5_3),
        ("5.4", exercise_5_4)
    ]:
        first = fn("apple")
        second = fn("apple")

        results.append({
            "exercise": name,
            "first_call": first,
            "second_call": second,
            "consistent_in_test": first == second
        })

    report["B2"] = results

    for result in results:
        print(result)

    examples = [
        ['Esther', 'Ben', 'Bob', 'Dan'],
        ['A', 'AA', 'AAA', 'AAAA'],
        ['Maus', 'Fun Home', 'Watchmen'],
    ]
    rows = []
    for keys in examples:
        row = {'keys': ', '.join(keys)}
        for name, fn in {**BOOK_FUNCTIONS, **GOOD_FUNCTIONS}.items():
            indices = [fn(k, 10) for k in keys]
            row[name] = f'{indices} (collisions={len(indices) - len(set(indices))})'
        rows.append(row)
    write_csv('table2_part_b3.csv', ['keys', *BOOK_FUNCTIONS, *GOOD_FUNCTIONS], rows)
    report['B3'] = rows

    names = [f'{chr(97 + (i % 26))}{chr(97 + ((i // 26) % 26))}product{chr(97 + ((i // 676) % 26))}{i:05d}'
             for i in range(5000)]
    rows = []
    for name, fn in {**BOOK_FUNCTIONS, **GOOD_FUNCTIONS}.items():
        t = HashTable(1000, hash_fn=fn, resize=False)
        for k in names: t.put(k, 1)
        sizes = t.chain_lengths()
        steps = lookup_steps(t, names)
        rows.append({'function': name, 'slots_used': sum(x > 0 for x in sizes),
                     'longest_list': max(sizes), 'steps_per_lookup': round(steps, 3)})
    report['B4'] = rows
    write_csv('table3_part_b4.csv', ['function', 'slots_used', 'longest_list', 'steps_per_lookup'], rows)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([r['function'].split(':')[0] for r in rows], [r['slots_used'] for r in rows])
    ax.set(ylabel='Occupied slots (of 1000)', title='B4: Hash function distribution for 5000 keys')
    ax.tick_params(axis='x', labelrotation=25)
    fig.tight_layout(); fig.savefig(OUT / 'plot1_slots_used.png', dpi=170); plt.close(fig)

def part_c():
    t = HashTable(26, hash_fn=hash_c, resize=False)
    for item in ['apple', 'banana', 'avocado', 'cherry', 'apricot', 'blueberry', 'date', 'artichoke']:
        t.put(item, item)
    chains = {}
    for letter in 'abcdef':
        node, members = t.slots[ord(letter)-97], []
        while node:
            members.append(node.key); node = node.next
        chains[letter] = members
    t.steps = 0
    t.get('apple')
    report['C4'] = {'chains': chains, 'steps_to_find_apple': t.steps}

def part_d():
    rows = []
    factors = [0.25, 0.5, 0.7, 0.9, 1, 1.5, 2, 3]
    for alpha in factors:
        count = round(4096 * alpha)
        t = HashTable(4096, resize=False)
        keys = [f'key_{i:06d}_{rng.getrandbits(64):016x}' for i in range(count)]
        for k in keys: t.put(k, 1)
        present = lookup_steps(t, keys)
        missing = lookup_steps(t, [f'absent_{i:06d}_{rng.getrandbits(64):016x}' for i in range(max(4096, count))])
        rows.append({'alpha': alpha, 'present_steps': present, 'absent_steps': missing,
                     'longest_chain': max(t.chain_lengths())})
    report['D1'] = rows
    write_csv('part_d1_load_sweep.csv', list(rows[0]), rows)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(factors, [r['present_steps'] for r in rows], 'o-', label='Present measured')
    ax.plot(factors, [r['absent_steps'] for r in rows], 'o-', label='Absent measured')
    ax.plot(factors, [1 + a/2 for a in factors], '--', label='Present theory: 1 + alpha/2')
    ax.plot(factors, factors, '--', label='Absent theory: alpha')
    ax.axvline(0.7, linestyle=':', label='Threshold 0.7')
    ax.set(xlabel='Load factor alpha', ylabel='Visited nodes per lookup', title='D1: Chaining load factor and lookup cost')
    ax.legend(); ax.grid(alpha=0.2); fig.tight_layout()
    fig.savefig(OUT / 'plot2_load_factor.png', dpi=170); plt.close(fig)
    keys = [f'key_{i:06d}_{rng.getrandbits(64):016x}' for i in range(100000)]
    rows = []
    for limit in [0.5, 0.7, 1, 2, 4]:
        t = HashTable(8, max_load=limit)
        for key in keys: t.put(key, 1)
        steps = lookup_steps(t, keys)
        rows.append({'resize_when_load_gt': limit, 'final_slots': t.size,
                     'final_load_factor': round(t.load_factor(), 5),
                     'total_moves': t.moves, 'steps_per_lookup': round(steps, 5)})
    report['D2'] = rows
    write_csv('table4_part_d2.csv', list(rows[0]), rows)

def part_e():
    rows = []
    for n in [1000, 10000, 100000, 1000000]:
        data = list(range(n))
        keys = [rng.randrange(n) for _ in range(60 if n <= 10000 else 25)]

        for method in ['simple_list', 'binary_bisect', 'dict_lookup']:
            d = {x: True for x in data} if method == 'dict_lookup' else None
            start = time.perf_counter()
            for k in keys:
                if method == 'simple_list': assert k in data
                elif method == 'binary_bisect': assert data[bisect_left(data, k)] == k
                else: assert d[k]
            elapsed = (time.perf_counter() - start) / len(keys)
            rows.append({'n': n, 'method': method, 'seconds_per_lookup': elapsed})
    report['E1'] = rows
    write_csv('part_e1_search.csv', list(rows[0]), rows)
    fig, ax = plt.subplots(figsize=(9, 5))
    for method in ['simple_list', 'binary_bisect', 'dict_lookup']:
        xs = [r['n'] for r in rows if r['method'] == method]
        ys = [r['seconds_per_lookup'] for r in rows if r['method'] == method]
        ax.plot(xs, ys, 'o-', label=method)
    ax.set(xscale='log', yscale='log', xlabel='Number of keys (n)', ylabel='Seconds per lookup',
           title='E1: Search performance (log-log)')
    ax.legend(); ax.grid(alpha=0.2); fig.tight_layout()
    fig.savefig(OUT / 'plot3_search_comparison.png', dpi=170); plt.close(fig)

    names = [f'a{i:04d}' for i in range(300)]
    results = []
    for name, fn in [('first_letter', hash_c), ('python_hash', hash_python)]:
        t = HashTable(26, hash_fn=fn, resize=False)
        for key in names: t.put(key, True)
        lengths = t.chain_lengths()
        results.append({'method': name, 'slots_used': sum(x > 0 for x in lengths),
                        'longest_chain': max(lengths), 'steps_per_lookup': lookup_steps(t, names)})
    report['E2'] = results

def challenge(requests):
    rows = []
    for cap in [5, 10, 20, 50, 100, 200]:
        cache = LRUCache(cap)
        for url in requests: cache.get(url, lambda u: '<html>' + u + '</html>')
        rows.append({'capacity': cap, 'hit_rate': cache.hits/len(requests),
                     'evictions': cache.evictions})
    report['LRU'] = rows
    write_csv('challenge_lru.csv', list(rows[0]), rows)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot([r['capacity'] for r in rows], [r['hit_rate'] * 100 for r in rows], 'o-')
    ax.set(xscale='log', xlabel='Cache capacity (log scale)', ylabel='Hit rate (%)',
           title='LRU: Cache capacity vs hit rate')
    ax.grid(alpha=0.2); fig.tight_layout()
    fig.savefig(OUT / 'plot4_lru_hit_rate.png', dpi=170); plt.close(fig)

if __name__ == '__main__':
    requests = part_a()
    print('Part A complete')
    part_b(); print('Part B complete')
    part_c(); print('Part C complete')
    part_d(); print('Part D complete')
    part_e(); print('Part E complete')
    challenge(requests); print('LRU challenge complete')
    (OUT / 'measurements.json').write_text(json.dumps(report, indent=2))
    print('All measurements and four figures:', OUT)
