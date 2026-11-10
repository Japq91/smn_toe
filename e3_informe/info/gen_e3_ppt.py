import base64, re, sys
import pandas as pd
ROOT='/p1-swell/japq/loca/smn_toe/'
e2=open(ROOT+'e2_informe/info/e2_ppt.html',encoding='utf-8').read()
head=e2[:e2.index('<body>')].replace('<title>Entregable 2 — Evaluación ENOS CMIP6</title>','<title>Entregable 3 — Proyecciones de la TSM y del ENOS</title>')
script=e2[e2.index('<script>'):]
script=script.replace("var sectionLabels = {1:'Introducción',2:'Estado medio',3:'ENOS y eventos',4:'Método',5:'Selección',6:'Anexo'};",
                      "var sectionLabels = {1:'Introducción',2:'Estado medio',3:'Variabilidad y umbrales',4:'Eventos',5:'Síntesis',6:'Anexo'};")
assert "Variabilidad y umbrales" in script

def img(name, cls='fig-larga'):
    b=base64.b64encode(open(ROOT+f'figures/e3/{name}.png','rb').read()).decode()
    return f'<img class="{cls}" alt="{name}.png" src="data:image/png;base64,{b}">'

def larga(sec, kicker, h1, fig, bullets, nota=None):
    li=''.join(f'<li>{b}</li>' for b in bullets)
    n=f'\n  <p class="nota-pie">{nota}</p>' if nota else ''
    return f'''<section class="slide larga" data-section="{sec}">
<div class="kicker">{kicker}</div>
  <h1>{h1}</h1>
  <figure class="fig-larga-wrap">{img(fig)}<figcaption>{fig}</figcaption></figure>
  <ul class="bajo">{li}</ul>{n}
</section>
'''
def anexo(h1, fig):
    return f'''<section class="slide " data-section="6">
<div class="kicker">Anexo</div>
  <h1 style="font-size:clamp(1.2rem,2vw,1.7rem)">{h1}</h1>
  <figure class="center-col" style="height:auto">{img(fig,'fig-anexo')}<figcaption>{fig}</figcaption></figure>
</section>
'''

# --- tabla de sintesis desde q10 ---
rm=pd.read_csv(ROOT+'data/processed/e3/resumen_multimodelo_ref1985-2014.csv',dtype={'grupo':str})
r=rm[rm.grupo=='15']
VARS=[("delta","nino34","ΔTSM Niño 3.4 [°C]"),("delta","nino12","ΔTSM Niño 1+2 [°C]"),
 ("delta_relativo","nino34","ΔTSM rel. Niño 3.4 [°C]"),("delta_relativo","nino12","ΔTSM rel. Niño 1+2 [°C]"),
 ("delta_sigma_3m_pct","nino34","Δσ<sub>3m</sub> Niño 3.4 [%]"),("delta_sigma_3m_pct","nino12","Δσ<sub>3m</sub> Niño 1+2 [%]"),
 ("razon_frec","ONI","Frecuencia P/ref ONI"),("razon_frec","RONI","Frecuencia P/ref RONI"),("razon_frec","ICEN","Frecuencia P/ref ICEN"),
 ("n_fuerte_mas","ONI","Eventos fuertes+ ONI (ref: 3)"),("n_fuerte_mas","RONI","Eventos fuertes+ RONI (ref: 3)"),("n_fuerte_mas","ICEN","Eventos fuertes+ ICEN (ref: 0)")]
cats=[(e,p) for e in ['ssp245','ssp370','ssp585'] for p in ['P1','P2']]
filas=[]
for var,clave,lab in VARS:
    tds=[]
    for e,p in cats:
        x=r[(r.variable==var)&(r.caja_indice==clave)&(r.escenario==e)&(r.periodo==p)].iloc[0]
        if var=='razon_frec': v=f"{x.mediana:.2f}"
        elif var=='n_fuerte_mas': v=f"{x.mediana:.0f}"
        elif var=='delta_sigma_3m_pct': v=f"{x.mediana:+.0f}".replace('-0','0') if abs(x.mediana)>=0.5 else '0'
        else: v=f"{x.mediana:+.2f}"
        v=v.replace('-','−')
        if pd.notna(x.acuerdo_signo) and x.acuerdo_signo>=0.8: v=f"<strong>{v}</strong>"
        if x.signif: v+='*'
        tds.append(f'<td style="text-align:right">{v}</td>')
    filas.append(f'<tr><td>{lab}</td>'+''.join(tds)+'</tr>')
tabla='\n'.join(filas)

slides=[]
slides.append('''<section class="slide title-slide" data-section="1">
<div class="kicker">Servicio prestado para el SENAMHI</div>
  <h1>Entregable 3<br><span style="color:var(--fg)">Proyecciones de la TSM y del ENOS en Niño 3.4 y Niño 1+2</span></h1>
  <h2 class="sub">Estado medio, variabilidad y eventos extremos (actividad c del TdR) en 2036–2065 y 2071–2100<br>bajo SSP2-4.5, SSP3-7.0 y SSP5-8.5, con los 15 modelos CMIP6 seleccionados</h2>
  <div class="divider" style="width:40%"></div>
  <p class="lead"><strong>Jonathan Paredes</strong> — Ingeniero Meteorólogo</p>
  <p class="small">Noviembre de 2026</p>
</section>
''')
slides.append('''<section class="slide " data-section="1">
<div class="kicker">Resumen · lo que pide el TdR</div>
  <h1>El mar se calienta con seguridad; el ENOS cambia menos, pero los Niños fuertes aumentan</h1>
  <div class="grid3">
    <div class="card"><strong>1. Estado medio</strong><div class="stat">+2.3 a +3.6 °C</div><div class="stat-label">Calentamiento de Niño 1+2 a fin de siglo (2071–2100), del escenario intermedio al muy alto. <strong>Los 15 modelos coinciden.</strong></div></div>
    <div class="card"><strong>2. Variabilidad del ENOS</strong><div class="stat">+11 a +26 %</div><div class="stat-label">Intensidad típica de Niños y Niñas en Niño 3.4 a fin de siglo. <strong>Incierto:</strong> los modelos no coinciden. En Niño 1+2, sin cambio claro.</div></div>
    <div class="card"><strong>3. Eventos extremos (ONI, ICEN)</strong><div class="stat">3 → 5 a 9</div><div class="stat-label">Niños fuertes o más intensos cada 30 años (ONI y RONI), con emisiones altas y muy altas. <strong>Aumento significativo.</strong> En el ICEN, pocos y sin cambio claro.</div></div>
  </div>
  <ul style="margin-top:1em">
    <li><strong>Cuántos Niños:</strong> la frecuencia total sube en la mediana (+11 a +44 %), pero con ~9 eventos por periodo no se distingue del azar.</li>
    <li><strong>Con el umbral de hoy:</strong> a fin de siglo Niño 1+2 estaría sobre el umbral de El Niño casi todo el tiempo. Es el calentamiento de fondo, no más Niños.</li>
  </ul>
  <p class="nota-pie">Cada número es la mediana de los 15 modelos seleccionados en el Entregable 2, comparando 2071–2100 con 1985–2014 en cada modelo. Escenarios: SSP2-4.5 (intermedio), SSP3-7.0 (alto) y SSP5-8.5 (muy alto). <strong>Significativo</strong>: no se explica por azar (Wilcoxon con corrección de Holm).</p>
</section>
''')
slides.append('''<section class="slide " data-section="1">
<div class="kicker">Marco común</div>
  <h1>Datos y criterios</h1>
  <div class="grid2">
    <div class="card"><ul>
      <li><strong>Modelos:</strong> los 15 seleccionados en el Entregable 2 (conjunto principal) y los 40 como contraste; un miembro por modelo</li>
      <li><strong>Controles de sensibilidad:</strong> 40 (sin selección), 11 (sin los 4 de Niño costero más débil) y 7 (solo los mejores en ambas cajas): ¿el resultado depende de qué modelos se eligen?</li>
      <li><strong>Series:</strong> <span class="mono">historical</span> + escenario, 1850–2100</li>
      <li><strong>Escenarios:</strong> SSP2-4.5 (intermedio), SSP3-7.0 (alto) y SSP5-8.5 (muy alto)</li>
      <li><strong>Periodos de 30 años:</strong> ref 1985–2014, P1 2036–2065, P2 2071–2100: conteos y σ con muestras del mismo largo</li>
    </ul></div>
    <div class="card"><ul>
      <li><strong>Cada modelo contra sí mismo:</strong> cambio = P − ref del mismo modelo; su sesgo fijo se cancela</li>
      <li><strong>Mediana y percentiles 10–90</strong> entre modelos: un modelo extremo no arrastra el resultado</li>
      <li><strong>Acuerdo de signo ≥ 0.8:</strong> al menos 12 de 15 modelos coinciden en la dirección (criterio del IPCC) → robusto</li>
      <li><strong>*</strong> significativo: Wilcoxon con corrección de Holm, p &lt; 0.05, en las 30 pruebas que responden al TdR</li>
    </ul></div>
  </div>
  <p class="nota-pie">Cálculo en <span class="mono">scripts_e3/</span> (pasos q01–q11, <span class="mono">./rune3.sh</span>); figuras en <span class="mono">scripts_e3/plot&lt;código&gt;_*.py</span> (<span class="mono">bash rune3plot.sh</span>; el código es el número de la figura en el informe). El kicker de cada diapositiva indica el paso que produce el dato.</p>
</section>
''')
slides.append('''<section class="slide " data-section="1">
<div class="kicker">Marco común · glosario</div>
  <h1>Términos clave: índices, eventos y variabilidad</h1>
  <div class="grid2">
    <div class="card"><strong>Índices del ENOS</strong><ul class="small-list">
      <li><strong>ONI</strong> (NOAA): anomalía de TSM en Niño 3.4, promedio móvil de 3 meses</li>
      <li><strong>ICEN</strong> (ENFEN): lo mismo en Niño 1+2, frente a la costa de Perú y Ecuador</li>
      <li><strong>RONI</strong>: ONI menos la anomalía del trópico; quita el calentamiento de fondo</li>
      <li><strong>Base móvil</strong> (ONI, ICEN): el “normal” se actualiza cada 5 años. <strong>Base fija</strong> (ONIfija, ICENfija): el “normal” es siempre 1985–2014</li>
    </ul></div>
    <div class="card"><strong>Eventos y variabilidad</strong><ul class="small-list">
      <li><strong>Evento cálido:</strong> ONI ≥ 0.5 °C en 5 trimestres seguidos; ICEN &gt; 0.5 °C en 3 meses seguidos. Los dos índices son promedios de 3 meses: el 5 y el 3 son cuánto debe durar</li>
      <li><strong>Fuerte o más:</strong> ONI ≥ 1.5 °C; ICEN &gt; 2.1 °C (ENFEN, 2024)</li>
      <li><strong>Eventos por 30 años:</strong> el conteo de cada periodo (ref, P1 y P2 duran 30 años)</li>
      <li><strong>σ<sub>3m</sub>:</strong> desviación estándar de la anomalía suavizada a 3 meses, la misma serie del ONI y del ICEN. Mide qué tan intensos son los Niños y las Niñas típicos; <strong>Δσ<sub>3m</sub></strong> es su cambio en %</li>
    </ul></div>
  </div>
  <p class="nota-pie">Glosario completo en el Cuadro 1 del informe, después del Resumen.</p>
</section>
''')
slides.append('''<section class="slide " data-section="1">
<div class="kicker">Marco común · q10</div>
  <h1>¿Cuándo un cambio es “real”? Tres filtros</h1>
  <div class="grid3">
    <div class="card"><strong>1. Mediana</strong><p class="small">El valor del medio de los 15 modelos. Un modelo extremo no la mueve.</p><p class="small"><em>Ej.:</em> σ<sub>3m</sub> de Niño 3.4 va de −29 a +105 %; la mediana es +26 %.</p></div>
    <div class="card"><strong>2. Acuerdo de signo</strong><p class="small">Fracción de modelos que van en la dirección de la mediana. ≥ 0.8 (12 de 15) = robusto.</p><p class="small"><em>Ej.:</em> Niño 1+2 relativo al trópico: 15 de 15 → 1.00.</p></div>
    <div class="card"><strong>3. Wilcoxon + Holm (*)</strong><p class="small">Wilcoxon: ¿los 15 cambios, por signo y tamaño, se separan de 0? Holm: exige más porque se hacen 30 pruebas a la vez.</p><p class="small"><em>Ej.:</em> eventos fuertes del ONI, SSP3-7.0, P2: p = 0.0014; es la 13.ª de 30 pruebas → ×18 = 0.025 &lt; 0.05 *</p></div>
  </div>
  <p class="nota-pie">Solo se prueban las 30 variables que pide el TdR (estado medio, variabilidad, frecuencia, intensidad, extremos, duración y fracción costera). El cambio relativo al trópico se lee por acuerdo de signo. “Significativo” no es lo mismo que “grande”.</p>
</section>
''')
slides.append(larga(2,'Estado medio · q02','Hasta 2050 los escenarios casi no se distinguen; a 2100 deciden entre +2 y +4 °C','e3_01_trayectoria_tsm',[
 'Anomalía = TSM anual menos la media 1985–2014 del mismo modelo (base fija); línea = mediana, sombra = p10–p90',
 'Hacia 2050, Niño 3.4 está entre +1.2 y +1.5 °C con los tres escenarios',
 'Hacia 2100: +2.0, +3.2 y +4.1 °C en Niño 3.4; +2.3, +3.4 y +4.2 °C en Niño 1+2',
 'Fila de abajo: caja menos trópico; Niño 1+2 se aparta del trópico de forma gradual desde ~2020']))
slides.append(larga(2,'Estado medio · q02','Los 15 modelos calientan las dos cajas; Niño 1+2 más que el trópico','e3_03_cambio_cajas_por_modelo',[
 'Cada punto es un modelo (color: los 15; gris: los 40); barra negra = mediana; número arriba = acuerdo de signo; * = significativo',
 'P2, cambio total: Niño 1+2 +2.25, +2.79 y +3.64 °C; Niño 3.4 +1.91, +2.63 y +3.36 °C; 15 de 15 modelos y significativo en todos los casos',
 'Entre modelos hay mucha diferencia: con SSP5-8.5, Niño 1+2 va de +2.6 a +5.5 °C',
 'Fila de abajo: Niño 1+2 se calienta 0.4–0.7 °C más que el trópico (15 de 15); Niño 3.4, 0.2–0.4 °C y con menos acuerdo']))
slides.append(larga(3,'Variabilidad · q05','Niño 3.4: más variabilidad en la mediana, pero sin acuerdo entre modelos','e3_05_cambio_sigma_por_modelo',[
 'σ<sub>3m</sub> mide qué tan intensos son los Niños y las Niñas típicos: es la desviación estándar de la misma serie suavizada a 3 meses con la que se calculan el ONI y el ICEN y sus umbrales',
 'Su cambio en %: +10 % = las oscilaciones típicas son 10 % más amplias, y los umbrales de El Niño se superan con más facilidad',
 'Niño 3.4, P2: +11, +23 y +26 %; con SSP5-8.5 suben 13 de 15 modelos, pero de −29 a +105 % → no significativo (solo P1 con SSP3-7.0 y SSP5-8.5 *)',
 'Niño 1+2: de −0.5 a +10 %, con 8 a 12 de 15 modelos de acuerdo: sin cambio claro',
 'En ventanas móviles, el aumento de Niño 3.4 es gradual y llega a +21 a +31 % hacia 2067–2072 (Anexo)']))
slides.append(larga(3,'Índices ENOS · q06–q08','Con la base actual, el umbral de El Niño se supera casi siempre','e3_07_tiempo_sobre_umbral',[
 'Fracción de meses con el índice sobre el umbral de inicio (0.5 °C), sin exigir duración',
 'Base móvil (clima de su época): ONI 31 % → 35–41 %; ICEN 24 % → 29–36 % en P2',
 'Base fija 1985–2014: ONIfija 31 % → 88–98 %; ICENfija 23 % → 99–100 %',
 'La diferencia es el calentamiento de fondo, no un ENOS más activo'],
 nota='<strong>Base móvil</strong> (ONI, ICEN): el “normal” se actualiza cada 5 años con los 30 años alrededor, como hacen NOAA y el ENFEN. <strong>RONI</strong>: el “normal” es el promedio del trópico en el mismo mes. <strong>Base fija</strong> (ONIfija, ICENfija): el “normal” es siempre 1985–2014.'))
slides.append(larga(4,'Eventos cálidos · q07–q08','Más eventos en la mediana, casi ninguno significativo','e3_08_razon_frecuencia',[
 'Frecuencia en P / frecuencia en ref de cada modelo; 1 = sin cambio; eje logarítmico',
 'P2: ONI 1.25 con los tres escenarios; RONI 1.22–1.44; ICEN 1.11–1.20',
 'En absoluto: ONI 8 → 10–11 eventos cada 30 años; RONI 9 → 11–13 (ERSSTv5 1900–2014: 8 y 9)',
 'Acuerdo ≤ 0.87: con ~9 eventos por periodo, la señal no se distingue del azar; no significa que no cambie',
 'Única excepción: RONI con SSP2-4.5 en P2 (1.30 *)']))
slides.append(larga(4,'Eventos cálidos · q08','Más eventos extremos, y algo más largos e intensos','e3_09_duracion_magnitud',[
 '<strong>Eventos fuertes o más (por 30 años):</strong> ONI 3 → 5–7 y RONI 3 → 5–9 con SSP3-7.0 y SSP5-8.5 * (ICEN: 0 → 1–2, no significativo)',
 'ICEN: duración media de 8.0 a 10.1 y 11.0 meses (SSP5-8.5, P1 y P2) y a 9.2 (SSP3-7.0, P2) *',
 'RONI: pico medio de 1.38 a 1.7–2.0 °C con SSP3-7.0 y SSP5-8.5 *',
 'Eventos ≥ 2σ de la referencia (sin prueba): 1 → 5 en ONI y RONI; coherente con más variabilidad en Niño 3.4',
 'Tipo de evento (Anexo): los extendidos suben de 8 a 10 cada 30 años; los costeros se mantienen en 1–2']))
slides.append(f'''<section class="slide " data-section="5">
<div class="kicker">Síntesis · q10</div>
  <h1>Qué es robusto y qué no</h1>
  <table class="tabla-datos">
    <thead><tr><th rowspan="2">Variable (mediana de 15 modelos)</th><th colspan="2" style="text-align:center">SSP2-4.5</th><th colspan="2" style="text-align:center">SSP3-7.0</th><th colspan="2" style="text-align:center">SSP5-8.5</th></tr>
    <tr><th style="text-align:right">P1</th><th style="text-align:right">P2</th><th style="text-align:right">P1</th><th style="text-align:right">P2</th><th style="text-align:right">P1</th><th style="text-align:right">P2</th></tr></thead>
    <tbody>
{tabla}
    </tbody>
  </table>
  <p class="nota-pie"><strong>Negrita</strong>: robusto (acuerdo de signo ≥ 0.8). <strong>*</strong>: significativo con Wilcoxon y Holm (p &lt; 0.05). Las razones de frecuencia se comparan con 1 (sin cambio); los eventos fuertes, con su número en ref; el resto, con 0. El cambio relativo no se prueba. Las medianas casi no cambian con 40, 11 o 7 modelos (Anexo).</p>
</section>
''')
slides.append('''<section class="slide " data-section="5">
<div class="kicker">Discusión</div>
  <h1>Conclusiones y limitaciones</h1>
  <div class="grid2">
    <div class="card"><strong>Conclusiones</strong><ul class="small-list">
      <li><strong>Estado medio:</strong> calentamiento seguro, +2.3 a +3.6 °C en Niño 1+2 a fin de siglo, y más que el trópico</li>
      <li><strong>Variabilidad:</strong> tiende a subir en Niño 3.4, sin acuerdo entre modelos; Niño 1+2 sin cambio claro</li>
      <li><strong>Eventos extremos:</strong> los Niños fuertes o más intensos (ONI, RONI) suben de 3 a 5–9 cada 30 años, de forma significativa; la frecuencia total, no</li>
      <li><strong>Umbrales de hoy:</strong> se superarían casi siempre; es el fondo, no el ENOS</li>
      <li><strong>Recomendación:</strong> comunicar por separado el calentamiento de fondo y el cambio del ENOS</li>
    </ul></div>
    <div class="card"><strong>Limitaciones</strong><ul class="small-list">
      <li>Un miembro por modelo: la variabilidad interna de 30 años puede crear o borrar diferencias (se cuantifica en el Entregable 4)</li>
      <li>~9 eventos por periodo: baja potencia para detectar cambios</li>
      <li>Modelos de un mismo centro no son independientes: el p de Wilcoxon es optimista</li>
      <li>Los modelos no reproducen los Niños costeros extraordinarios (asimetría del ICEN; Anexo)</li>
    </ul></div>
  </div>
</section>
''')
slides.append('''<section class="slide title-slide" data-section="5">
<h1>Gracias</h1>
  <p class="lead">Entregable 3 — Proyecciones de la TSM y del ENOS en Niño 3.4 y Niño 1+2</p>
  <div class="divider" style="width:30%"></div>
  <p><strong>Jonathan Paredes</strong><br>Ingeniero Meteorólogo</p>
  <p class="small">Servicio prestado para el SENAMHI</p>
</section>
''')
slides.append(anexo('Patrón del calentamiento: cambio relativo al trópico','e3_A01_mapas_cambio_relativo'))
slides.append(anexo('Ciclo anual: Niño 1+2 se calienta más en invierno y su ciclo se aplana','e3_A02_ciclo_anual'))
slides.append(anexo('σ<sub>3m</sub> en ventanas móviles de 30 años','e3_06_sigma_movil'))
slides.append(anexo('Eventos por tipo: costero, extendido y central','e3_A08_tipo_eventos'))
slides.append(anexo('Asimetría y curtosis: los modelos no generan la cola de Niños costeros extraordinarios','e3_A05_asimetria_curtosis'))
slides.append(anexo('Sensibilidad al conjunto de modelos (15, 40, 11 y 7) en P2','e3_A10_sensibilidad_conjuntos'))

n=len(slides)
body=f'''<body>

<button class="theme-toggle" id="themeToggle" title="Cambiar tema">🌓</button>
<div class="progress" id="progress"></div>
<div class="deck" id="deck">

{''.join(slides)}

</div>

<button class="nav-btn" id="prevBtn" aria-label="Anterior">‹</button>
<button class="nav-btn" id="nextBtn" aria-label="Siguiente">›</button>
<div class="section-nav" id="sectionNav"></div>
<div class="footer">
  <span>Entregable 3 — Proyecciones de la TSM y del ENOS en Niño 3.4 y Niño 1+2 — Servicio prestado para el SENAMHI</span>
  <span id="counter">1 / {n}</span>
</div>
'''
out=ROOT+'e3_informe/info/e3_ppt.html'
open(out,'w',encoding='utf-8').write(head+body+script)
print(out, n, 'slides')
