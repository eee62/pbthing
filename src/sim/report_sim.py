"""Markdown tables from the *_events.json files written by scenario.py.
Usage: python src/sim/report_sim.py out/sim/runA_events.json [more.json ...]"""
import sys, json


def table(path):
    ev = json.load(open(path))
    rows = ['| step | rigid contact depth (mm) | hand lag (mm) | jam | ribbon min radius (mm) | ribbon max strain | worst wire strain | worst squeeze (mm) |', '|---|---|---|---|---|---|---|---|']
    for label, w in ev:
        per = w['per']
        rib = per['ribbon']
        wires = {k: v for k, v in per.items() if k != 'ribbon'}
        ws = max(wires.items(), key=lambda kv: kv[1]['strain'])
        pq = max(per.items(), key=lambda kv: kv[1]['pinch'])
        rows.append(f"| {label} | {w['depth']:.3f} | {w['err']:.2f} | {'JAM' if w['jam'] else 'no'} | {rib['R']:.2f} | {100*rib['strain']:.1f} % | "
                    f"{100*ws[1]['strain']:.1f} % ({ws[0]}) | {pq[1]['pinch']:.2f} ({pq[0]}, vs {pq[1]['pinch_body']}) |")
    return '\n'.join(rows)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        print('###', p)
        print(table(p))
        print()
