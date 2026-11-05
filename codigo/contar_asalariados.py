"""Usage: python codigo/contar_asalariados.py path/to/esi_2025_personas.csv"""
import csv,hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
raw=Path(sys.argv[1])
with raw.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
assert digest==json.loads((root/'fuentes/procedencia.json').read_text())['fuente_original']['sha256']
data=dict(ocupados=0.,asalariados=0.,asalariados_con_ingreso=0.)
with raw.open(encoding='latin1') as f:
    for r in csv.DictReader(f):
        if r['ocup_ref']!='1' or int(r['edad'])<20: continue
        w=float(r['fact_cal_esi']);data['ocupados']+=w
        if r['categoria_ocupacion'] in ('3','4'):
            data['asalariados']+=w
            if float(r['ing_t_p'])>0: data['asalariados_con_ingreso']+=w
assert abs(data['ocupados']-json.loads((root/'datos/dashboard.json').read_text())['domains']['all|all|all']['N'])<1
(root/'fuentes/universo_asalariados.json').write_text(json.dumps(dict(fuente_sha256=digest,criterio='Manual ESI 2025 §6.6: categoria_ocupacion 3 y 4. Universo de referencia ocupado, de 20 años o más.',**data),ensure_ascii=False,indent=2)+'\n')
