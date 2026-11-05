"""Reproduce the survey domains and export anonymous aggregate dashboard data.

Run: python3 -B codigo/analizar_dashboard.py
The full design frame is retained. Every selection is a domain indicator.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.special import expit, logit
from scipy.stats import t

from diseno_encuesta import Design

ROOT = Path(__file__).resolve().parents[1]
AGE = [('all', 'Todas las edades', None, None)] + [
    (f'{low}_{low+4}', f'{low}–{low+4} años', low, low+5)
    for low in range(15, 75, 5)
] + [('75_mas', '75 años o más', 75, None)]

OCCUPATIONS = [
    ('all', 'Todas las ocupaciones'),
    ('1', 'Directivos y gerentes'),
    ('2', 'Profesionales, científicos e intelectuales'),
    ('3', 'Técnicos y profesionales de nivel medio'),
    ('4', 'Personal administrativo'),
    ('5', 'Servicios y ventas'),
    ('6', 'Agropecuarios, forestales y pesqueros calificados'),
    ('7', 'Artesanos y operarios de oficios'),
    ('8', 'Operadores de máquinas y ensambladores'),
    ('9', 'Ocupaciones elementales'),
]
SEXES = [('all', 'Ambos sexos'), ('1', 'Hombres'), ('2', 'Mujeres')]
GRID = np.arange(0., 21_000_001., 50_000.)
EDGES = np.arange(0., 21_000_001., 100_000.)


def quantile(y, w, p):
    if not len(y):
        return np.nan
    order = np.argsort(y, kind='stable')
    ys, ws = y[order], w[order]
    j = np.searchsorted(np.cumsum(ws), p * ws.sum(), side='left')
    return float(ys[min(j, len(ys) - 1)])


def restrict_age(domain, ages, low, high):
    if low is not None:
        domain = domain & (ages >= low)
    if high is not None:
        domain = domain & (ages < high)
    return domain


def rounded(v, digits=6):
    """Convert numbers and arrays to portable strict JSON, with null for NaN."""
    if isinstance(v, np.ndarray):
        return [rounded(x, digits) for x in v]
    if isinstance(v, (np.integer, int)):
        return int(v)
    value = float(v)
    return round(value, digits) if np.isfinite(value) else None


def export_table(frame, name):
    frame.to_csv(ROOT / 'tablas' / f'{name}.csv', index=False)
    frame.to_latex(ROOT / 'tablas' / f'{name}.tex', index=False, escape=True, na_rep='--',
                   float_format=lambda value: f'{value:.7g}')


class VectorDesign:
    """Taylor linearization at all 421 thresholds in a single domain batch.

    A[j,k] is the weighted total above threshold k in PSU j. H is a sparse
    stratum-by-PSU matrix. The stratum-centred variance and covariance formula
    expands Var(A - p B), matching Design.event without discarding empty PSUs.
    """
    def __init__(self, frame):
        self.frame = frame
        self.y = frame.ing_t_p.to_numpy(float)
        self.w = frame.fact_cal_esi.to_numpy(float)
        self.psu, self.keys = pd.factorize(pd.MultiIndex.from_frame(
            frame[['estrato', 'conglomerado_correlativo']]), sort=True)
        self.strata, self.hkeys = pd.factorize(self.keys.get_level_values(0), sort=True)
        self.J = len(self.keys)
        self.nh = np.bincount(self.strata)
        self.fac = self.nh / (self.nh - 1.)
        self.facj = self.fac[self.strata]
        self.H = csr_matrix((np.ones(self.J), (self.strata, np.arange(self.J))),
                            shape=(len(self.nh), self.J))

    def all_events(self, domain):
        yg, wg, psu = self.y[domain], self.w[domain], self.psu[domain]
        n_domain = int(domain.sum())
        if not n_domain:
            # An empty denominator has no distribution. Keep observed counts and
            # weight sums additive for the age and sex partition checks below.
            counts = np.zeros(len(GRID), dtype=int)
            missing = np.full(len(GRID), np.nan)
            return dict(n=0, N=0., df=0, mean=np.nan, meanSE=np.nan, p=missing,
                        n_curve=counts, lo=missing, hi=missing, q=counts, ee=missing,
                        total=np.zeros(len(GRID)), ee_total=missing, df_event=counts,
                        cv_total=missing)
        B = np.bincount(psu, weights=wg, minlength=self.J)
        hB = self.H @ B
        N = B.sum()
        df_domain = int((B > 0).sum() - (hB > 0).sum())
        crit = t.ppf(.975, df_domain) if df_domain > 0 else np.nan
        indexes = np.floor(yg / 50_000.).astype(int)
        assert (indexes >= 0).all() and (indexes < len(GRID)).all()
        cells = psu * len(GRID) + indexes
        A = np.bincount(cells, weights=wg,
                        minlength=self.J * len(GRID)).reshape(self.J, len(GRID))
        A = np.cumsum(A[:, ::-1], axis=1)[:, ::-1]
        hA = self.H @ A
        total = A.sum(axis=0)
        p = total / N
        n = np.cumsum(np.bincount(indexes, minlength=len(GRID))[::-1])[::-1]
        # Constant events have exactly zero ratio variance.
        p[n == n_domain] = 1.
        p[n == 0] = 0.
        scale_h = self.fac / self.nh
        variance_total = self.facj @ (A * A) - scale_h @ (hA * hA)
        covariance = (self.facj * B) @ A - (scale_h * hB) @ hA
        variance_B = self.facj @ (B * B) - scale_h @ (hB * hB)
        variance_ratio = (variance_total - 2. * p * covariance + p * p * variance_B) / (N * N)
        variance_ratio[(n == n_domain) | (n == 0)] = 0.
        se = np.sqrt(np.maximum(0., variance_ratio))
        se_total = np.sqrt(np.maximum(0., variance_total))
        event_df = (A > 0).sum(axis=0) - (hA > 0).sum(axis=0)
        cv_total = np.divide(se_total, total, out=np.full(len(GRID), np.nan), where=total > 0) * 100
        max_se = np.minimum(p, 1 - p) ** (2 / 3) / 9
        reliable_proportion = (n_domain >= 60) & (df_domain >= 9) & (n > 0) & (se <= max_se)
        reliable_total = (n >= 60) & (event_df >= 9) & (cv_total <= 15)
        q = np.where(n == 0, 0, np.where(reliable_proportion & reliable_total, 2, 1)).astype(int)
        lo = np.full(len(GRID), np.nan)
        hi = np.full(len(GRID), np.nan)
        inside = (p > 0) & (p < 1) & (se > 0)
        error_logit = np.divide(crit * se, p * (1 - p),
                                out=np.zeros(len(GRID)), where=inside)
        lo[inside] = expit(logit(p[inside]) - error_logit[inside])
        hi[inside] = expit(logit(p[inside]) + error_logit[inside])
        degenerate = (p > 0) & (p < 1) & (se == 0)
        lo[degenerate] = p[degenerate]
        hi[degenerate] = p[degenerate]
        mean = wg @ yg / N
        mean_A = np.bincount(psu, weights=wg * yg, minlength=self.J)
        residual = (mean_A - mean * B) / N
        hresidual = self.H @ residual
        mean_se = np.sqrt(max(0., self.facj @ (residual * residual) - scale_h @ (hresidual * hresidual)))
        return dict(n=n_domain, N=N, mean=mean, meanSE=mean_se, df=df_domain,
                    p=p * 100, n_curve=n, lo=lo * 100, hi=hi * 100, q=q,
                    ee=se * 100, total=total, ee_total=se_total,
                    df_event=event_df, cv_total=cv_total)


def main():
    started = time.perf_counter()
    provenance = json.loads((ROOT / 'fuentes/procedencia.json').read_text())
    input_path = ROOT / 'datos/esi2025_columnas_necesarias.csv.gz'
    assert hashlib.sha256(input_path.read_bytes()).hexdigest() == provenance['sha256_columnas_necesarias']
    frame = pd.read_csv(input_path)
    occupied = frame.ocup_ref.eq(1).to_numpy()
    ages = frame.edad.to_numpy()
    occ = frame.b1.to_numpy()
    sex = frame.sexo.to_numpy()
    imputed = (frame.imp_d1_monto.eq(1) | frame.imp_d5_monto.eq(1)).to_numpy()
    assert len(frame) == 93458 and occupied.sum() == 38729
    assert (occupied & (ages < 20)).sum() == 349
    assert (occupied & np.isin(occ, range(1, 10))).sum() == 38573
    assert not frame.loc[occupied, ['edad', 'sexo', 'b1', 'ing_t_p', 'fact_cal_esi',
                                    'estrato', 'conglomerado_correlativo']].isna().any().any()
    assert (frame.fact_cal_esi > 0).all()
    assert (frame.loc[occupied, 'ing_t_p'] >= 0).all()
    assert frame.loc[occupied, 'ing_t_p'].max() < EDGES[-1]
    assert np.isin(sex[occupied], [1, 2]).all()
    assert (ages[occupied] >= 15).all()
    design = VectorDesign(frame)
    assert design.J == 5440 and len(design.nh) == 232 and (design.nh > 1).all()
    national = Design(frame, occupied)
    national_mean, national_se = national.mean(design.y)
    national_median = quantile(design.y[occupied], design.w[occupied], .5)
    assert abs(national.N - 9022697.147157632) < 1e-5
    assert abs(national_mean - 962944.6993102246) < 1e-5
    assert abs(national_se - 11502.910826247813) < 1e-6
    assert national_median == 680000

    domains = {}
    raw_domains = {}
    summary_rows = []
    reference_rows = []
    checks = []
    # Includes large and small domains, sparse tails, both sexes and all ages.
    crosscheck_keys = {'all|all|all', 'all|all|15_19', 'all|all|20_24', 'all|all|75_mas',
                      '1|1|all', '1|2|20_24', '2|2|30_34', '5|all|50_54',
                      '6|2|20_24', '8|2|75_mas', '9|1|40_44', '5|2|15_19'}
    thresholds = [0, 1, 10, 20, 40, 60, 80, 100, 140, 200, 300, 400, 420]
    for occupation, occ_label in OCCUPATIONS:
        occ_domain = occupied if occupation == 'all' else occupied & (occ == int(occupation))
        for sex_code, sex_label in SEXES:
            sex_domain = occ_domain & (True if sex_code == 'all' else sex == int(sex_code))
            for age_key, age_label, low, high in AGE:
                key = f'{occupation}|{sex_code}|{age_key}'
                domain = restrict_age(sex_domain, ages, low, high)
                result = design.all_events(domain)
                yg, wg = design.y[domain], design.w[domain]
                hist = (np.histogram(yg, bins=EDGES, weights=wg)[0] / result['N'] * 100
                        if result['n'] else np.full(len(EDGES) - 1, np.nan))
                p25, median, p75 = [quantile(yg, wg, probability) for probability in [.25, .5, .75]]
                mean_cv = result['meanSE'] / result['mean'] * 100 if result['mean'] > 0 else np.nan
                mean_q = 1 if result['n'] else 0
                if result['n'] >= 60 and result['df'] >= 9 and mean_cv <= 15:
                    mean_q = 2
                mean_critical = t.ppf(.975, result['df']) if result['df'] > 0 else np.nan
                mean_lo = result['mean'] - mean_critical * result['meanSE']
                mean_hi = result['mean'] + mean_critical * result['meanSE']
                zero_n = int((yg == 0).sum())
                zero_N = float(wg[yg == 0].sum())
                imputed_pct = (design.w[domain & imputed].sum() / result['N'] * 100
                               if result['n'] else np.nan)
                domains[key] = {
                    'n': result['n'], 'N': rounded(result['N']),
                    'mean': rounded(result['mean']), 'meanSE': rounded(result['meanSE']),
                    'meanLo': rounded(mean_lo), 'meanHi': rounded(mean_hi),
                    'meanCV': rounded(mean_cv), 'meanQ': mean_q,
                    'median': rounded(median), 'p25': rounded(p25), 'p75': rounded(p75),
                    'df': result['df'], 'zeroN': rounded(zero_N), 'zero_n': zero_n,
                    'imputedPct': rounded(imputed_pct), 'hist': rounded(hist),
                    'curve': {'p': rounded(result['p']), 'n': rounded(result['n_curve']),
                              'lo': rounded(result['lo']), 'hi': rounded(result['hi']),
                              'q': rounded(result['q'])},
                }
                raw_domains[key] = result
                summary_rows.append(dict(clave=key, ocupacion=occupation,
                    etiqueta_ocupacion=occ_label, sexo=sex_code, etiqueta_sexo=sex_label,
                    edad=age_key, etiqueta_edad=age_label, n=result['n'], personas=result['N'],
                    media=result['mean'], ee_media=result['meanSE'], ic95_media_inf=mean_lo,
                    ic95_media_sup=mean_hi, mediana=median,
                    p25=p25, p75=p75, gdl=result['df'], n_ceros=zero_n,
                    personas_cero=zero_N, imputados_pct=imputed_pct, calidad_media=mean_q))
                for i in [20, 40, 60, 80, 100]:
                    reference_rows.append(dict(clave=key, umbral=GRID[i],
                        n=int(result['n_curve'][i]), personas=result['total'][i] if result['n'] else np.nan,
                        porcentaje=result['p'][i], ee_pp=result['ee'][i],
                        ic95_inf_pct=result['lo'][i], ic95_sup_pct=result['hi'][i],
                        gdl_evento=result['df_event'][i], cv_total_pct=result['cv_total'][i],
                        calidad=int(result['q'][i])))
                if not result['n']:
                    empty = Design(frame, domain)
                    assert empty.N == result['N'] == empty.gdl == result['df'] == 0
                    assert not result['n_curve'].any() and not result['q'].any()
                    assert np.isnan(result['p']).all() and np.isnan(hist).all()
                    continue
                assert abs(hist.sum() - 100) < 1e-8
                assert (np.diff(result['p']) <= 1e-9).all()
                assert (np.diff(result['n_curve']) <= 0).all()
                assert result['p'][0] == 100 and result['p'][-1] == 0
                assert result['n_curve'][0] == result['n'] and result['n_curve'][-1] == 0
                assert np.isin(result['q'], [0, 1, 2]).all()
                assert np.array_equal(result['q'] == 0, result['n_curve'] == 0)
                assert p25 <= median <= p75
                assert abs(result['N'] - wg.sum()) < 1e-7
                if key in crosscheck_keys:
                    slow = Design(frame, domain)
                    m, mse = slow.mean(design.y)
                    np.testing.assert_allclose([result['mean'], result['meanSE']], [m, mse], rtol=1e-10, atol=1e-6)
                    assert slow.gdl == result['df']
                    for i in thresholds:
                        check = slow.event(design.y >= GRID[i])
                        np.testing.assert_allclose(
                            [result['p'][i], result['ee'][i], result['lo'][i], result['hi'][i],
                             result['total'][i], result['ee_total'][i]],
                            [check['porcentaje'], check['ee_pp'], check['ic95_inf_pct'],
                             check['ic95_sup_pct'], check['personas'], check['ee_personas']],
                            rtol=1e-9, atol=1e-6, equal_nan=True)
                        assert result['n_curve'][i] == check['n_muestra']
                        expected_q = 0 if check['n_muestra'] == 0 else (2 if check['resolucion_defendible'] == 'fiable' else 1)
                        assert result['q'][i] == expected_q, (key, GRID[i], result['q'][i], expected_q)
                        checks.append({'key': key, 'threshold': int(GRID[i]), 'pass': True})
            print(f'{occupation}: {occ_label} | {sex_label} | {len(AGE)} dominios calculados', flush=True)

    assert len(domains) == len(OCCUPATIONS) * len(SEXES) * len(AGE)
    national_export = domains['all|all|all']
    assert national_export['n'] == int(occupied.sum()) and national_export['median'] == national_median
    np.testing.assert_allclose([national_export['N'], national_export['mean'], national_export['meanSE']],
                               [national.N, national_mean, national_se], atol=1e-6, rtol=0)
    # The age bands and the two sexes partition each matching aggregate domain.
    for occupation, _ in OCCUPATIONS:
        for sex_code, _ in SEXES:
            parent = raw_domains[f'{occupation}|{sex_code}|all']
            children = [raw_domains[f'{occupation}|{sex_code}|{a[0]}'] for a in AGE[1:]]
            assert sum(d['n'] for d in children) == parent['n']
            np.testing.assert_allclose(sum(d['N'] for d in children), parent['N'], rtol=1e-12)
            np.testing.assert_allclose(sum(d['total'] for d in children), parent['total'], rtol=1e-11, atol=1e-7)
        for age_key, *_ in AGE:
            parent = raw_domains[f'{occupation}|all|{age_key}']
            children = [raw_domains[f'{occupation}|{s}|{age_key}'] for s in ['1', '2']]
            assert sum(d['n'] for d in children) == parent['n']
            np.testing.assert_allclose(sum(d['N'] for d in children), parent['N'], rtol=1e-12)
            np.testing.assert_allclose(sum(d['total'] for d in children), parent['total'], rtol=1e-11, atol=1e-7)
    age_reference = pd.read_csv(ROOT / 'fuentes/referencia_edades.csv')
    for row in age_reference.itertuples():
        high = None if pd.isna(row.edad_max_exclusiva) else int(row.edad_max_exclusiva)
        mask = restrict_age(occupied, ages, int(row.edad_min), high)
        old = Design(frame, mask)
        old_mean, old_se = old.mean(design.y)
        old_median = quantile(design.y[mask], design.w[mask], .5)
        assert int(mask.sum()) == row.n_muestra
        np.testing.assert_allclose([old.N, old_mean, old_se, old_median],
                                  [row.personas, row.media, row.ee_media, row.mediana],
                                  rtol=1e-10, atol=1e-6)

    residual_rows = []
    for code in [10, 999]:
        mask = occupied & (occ == code)
        residual_rows.append({'codigo': code, 'n': int(mask.sum()), 'personas': float(design.w[mask].sum())})
    main_occupations = [raw_domains[f'{code}|all|all'] for code, _ in OCCUPATIONS[1:]]
    assert sum(d['n'] for d in main_occupations + residual_rows) == national_export['n']
    np.testing.assert_allclose(sum(d['N'] for d in main_occupations) + sum(d['personas'] for d in residual_rows),
                               national.N, atol=1e-6, rtol=0)
    meta = {
        'title': 'Ingresos laborales en Chile', 'edition': 'ESI 2025',
        'age': [{'id': key, 'label': label, 'min': low, 'maxExclusive': high}
                for key, label, low, high in AGE],
        'occupation': [{'id': key, 'label': label} for key, label in OCCUPATIONS],
        'sex': [{'id': key, 'label': label} for key, label in SEXES],
        'grid': {'start': 0, 'stop': 21000000, 'step': 50000, 'length': 421,
                 'histStart': 0, 'histStop': 21000000, 'histStep': 100000, 'histLength': 210},
        'income': {'variable': 'ing_t_p', 'unit': 'CLP mensuales',
                   'definition': 'Ingreso neto mensual de la ocupación principal. Incluye personas asalariadas e independientes.',
                   'net': 'Para asalariados, después de descuentos legales e impuestos. Para independientes, ingresos menos costos de la actividad. Incluye los componentes en especie definidos por la ESI.',
                   'zerosIncluded': True, 'imputationsIncluded': True},
        'universe': 'Todas las personas ocupadas de referencia de la ESI 2025 (ocup_ref=1), desde los 15 años. Cada porcentaje usa como denominador el grupo seleccionado.',
        'universeFilter': 'ocup_ref == 1', 'nSourceRecords': len(frame), 'nAllOccupied': int(occupied.sum()),
        'n15To19': int((occupied & (ages < 20)).sum()),
        'occupationResiduals': residual_rows,
        'occupationResidualsNote': 'Todas las ocupaciones incluye los códigos 10 y 999, que no tienen panel propio.',
        'surveyDesign': {'psus': design.J, 'strata': len(design.nh),
                         'weight': 'fact_cal_esi', 'stratum': 'estrato',
                         'psu': 'conglomerado_correlativo',
                         'method': 'Taylor linealizado con el marco completo de UPM y estratos. Selecciones tratadas como dominios.'},
        'precision': {
            'q0': 'Sin casos observados. No equivale a ausencia en la población.',
            'q1': 'Estimación exploratoria o con precisión limitada.',
            'q2': 'Cumple el criterio conservador conjunto de proporción y total.',
            'q2Rule': 'Dominio n≥60 y gdl≥9. EE de la proporción ≤ min(p,1−p)^(2/3)/9. Evento n≥60, gdl≥9 y CV del total ≤15%.',
            'meanQ': '0 si el grupo carece de observaciones. Para grupos observados, 2 si n≥60, gdl≥9 y CV de la media ≤15%; en otro caso 1.',
            'emptyDomain': 'Con n=0, los recuentos observados y la suma de ponderadores son cero. La media, los cuantiles, el histograma y las proporciones e intervalos de la curva son nulos.',
            'interval': 'IC 95% logit de la proporción con t de los grados de libertad del dominio. Null si p=0 o p=1.',
            'quantiles': 'Cuantiles de la distribución empírica ponderada. No se estimó su incertidumbre.',
            'sampleSize': 'Tener 60 casos en el grupo no garantiza precisión de sus ingresos extremos.',
            'rounded': 'Porcentajes, personas y montos mostrados se redondean. Los datos embebidos conservan seis decimales.',
            'thresholds': 'P(ingreso≥umbral). La curva se evalúa cada $50.000. No se interpola para producir percentiles extremos.'},
        'provenance': {'sourceTitle': provenance['fuente_original']['title'],
                       'sourceURL': provenance['fuente_original']['url'],
                       'sha256Original': provenance['fuente_original']['sha256'],
                       'downloadUTC': provenance['fuente_original']['download_utc'],
                       'derivedFrom': 'Columnas seleccionadas del archivo original, sin filtrar filas del diseño.',
                       'aggregation': f'{len(domains)} dominios precomputados. El JSON solo contiene datos agregados.'},
        'generatedUTC': datetime.now(timezone.utc).isoformat(),
    }
    data = {'meta': meta, 'domains': domains}
    output = ROOT / 'datos/dashboard.json'
    output.write_text(json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':')))
    # Validate the exported precision, rather than just the in-memory arrays.
    reloaded = json.loads(output.read_text())
    for key, d in reloaded['domains'].items():
        assert len(d['hist']) == 210
        assert all(len(d['curve'][field]) == 421 for field in ['p', 'n', 'lo', 'hi', 'q'])
        if d['n'] == 0:
            assert d['N'] == d['df'] == d['meanQ'] == d['zero_n'] == d['zeroN'] == 0
            assert all(d[f] is None for f in ('mean', 'meanLo', 'meanHi', 'meanSE', 'meanCV', 'p25', 'median', 'p75', 'imputedPct'))
            assert all(v is None for field in ('p', 'lo', 'hi') for v in d['curve'][field])
            assert all(v is None for v in d['hist']) and not any(d['curve']['n']) and not any(d['curve']['q'])
            continue
        assert abs(sum(d['hist']) - 100) <= 0.000105
        assert max(np.diff(d['curve']['p'])) <= 1e-12
        assert all(x is None or 0 <= x <= 100 for field in ['lo', 'hi'] for x in d['curve'][field])
    summary = pd.DataFrame(summary_rows)
    refs = pd.DataFrame(reference_rows)
    export_table(summary, 'resumen_dominios')
    export_table(refs, 'referencias_1_a_5_millones')
    export_table(pd.DataFrame(residual_rows), 'ocupaciones_residuales')
    specific_cells = summary.loc[summary.ocupacion.ne('all') & summary.sexo.ne('all') & summary.edad.ne('all')]
    validation = {
        'pass': True, 'specificCells': len(specific_cells), 'domains': len(domains), 'originalRows': len(frame),
        'occupied': int(occupied.sum()), 'occupied15To19': meta['n15To19'],
        'mainOccupation': int((occupied & np.isin(occ, range(1, 10))).sum()),
        'residualOccupation': residual_rows, 'psus': design.J, 'strata': len(design.nh),
        'observedAgeRange': [int(ages[occupied].min()), int(ages[occupied].max())],
        'emptyDomains': [key for key, d in domains.items() if not d['n']],
        'singletonStrata': int((design.nh == 1).sum()),
        'nationalPopulation': float(national.N), 'nationalMean': national_mean,
        'nationalMeanSE': national_se, 'nationalMedian': national_median,
        'referenceAgeValidation': True, 'partitionAgeValidation': True,
        'partitionSexValidation': True, 'histogramsSum100': True,
        'curvesMonotonic': True, 'strictJSONNoNaN': True,
        'crosschecksAgainstOriginalDesign': checks,
        'specificCellSampleMin': int(specific_cells.n.min()), 'specificCellSampleMax': int(specific_cells.n.max()),
        'specificCellsUnder60': int(specific_cells.n.lt(60).sum()),
        'dashboardBytes': output.stat().st_size,
        'dashboardSHA256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'runtimeSeconds': time.perf_counter() - started,
    }
    (ROOT / 'datos/validacion.json').write_text(json.dumps(validation, indent=2, ensure_ascii=False, allow_nan=False))
    print(json.dumps({k: v for k, v in validation.items() if k != 'crosschecksAgainstOriginalDesign'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
