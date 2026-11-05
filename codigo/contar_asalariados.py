"""Usage: python codigo/contar_asalariados.py path/to/esi_2025_personas.csv"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(source):
    with source.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    provenance = json.loads((ROOT / 'fuentes/procedencia.json').read_text())
    assert digest == provenance['fuente_original']['sha256']

    data = dict(ocupados=0., asalariados=0., asalariados_con_ingreso=0.)
    sample = 0
    with source.open(encoding='latin1', newline='') as handle:
        for row in csv.DictReader(handle):
            if row['ocup_ref'] != '1':
                continue
            sample += 1
            weight = float(row['fact_cal_esi'])
            data['ocupados'] += weight
            if row['categoria_ocupacion'] in ('3', '4'):
                data['asalariados'] += weight
                if float(row['ing_t_p']) > 0:
                    data['asalariados_con_ingreso'] += weight

    dashboard = json.loads((ROOT / 'datos/dashboard.json').read_text())
    national = dashboard['domains']['all|all|all']
    assert national['n'] == sample and abs(data['ocupados'] - national['N']) < 1e-5
    result = dict(fuente_sha256=digest,
                  criterio='Manual ESI 2025 §6.6: categorías de ocupación 3 y 4. Universo de referencia completo (ocup_ref=1).',
                  **data)
    (ROOT / 'fuentes/universo_asalariados.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
