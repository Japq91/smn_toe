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
 ("delta_amplitud","nino34","Δ amplitud Niño 3.4 [°C]"),("delta_amplitud","nino12","Δ amplitud Niño 1+2 [°C]"),
 ("delta_sigma_3m_pct","nino34","Δσ<sub>3m</sub> Niño 3.4 [%]"),("delta_sigma_3m_pct","nino12","Δσ<sub>3m</sub> Niño 1+2 [%]"),
 ("razon_frec","ONI","Frecuencia P/ref ONI"),("razon_frec","RONI","Frecuencia P/ref RONI"),("razon_frec","ICEN","Frecuencia P/ref ICEN")]
cats=[(e,p) for e in ['ssp245','ssp370','ssp585'] for p in ['P1','P2']]
filas=[]
for var,clave,lab in VARS:
    tds=[]
    for e,p in cats:
        x=r[(r.variable==var)&(r.caja_indice==clave)&(r.escenario==e)&(r.periodo==p)].iloc[0]
        if var=='razon_frec': v=f"{x.mediana:.2f}"
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
  <h2 class="sub">Estado medio, ciclo anual, variabilidad y eventos cálidos en 2036–2065 y 2071–2100<br>bajo SSP2-4.5, SSP3-7.0 y SSP5-8.5, con los 15 modelos CMIP6 seleccionados</h2>
  <div class="divider" style="width:40%"></div>
  <p class="lead"><strong>Jonathan Paredes</strong> — Ingeniero Meteorólogo</p>
  <p class="small">Noviembre de 2026</p>
</section>
''')
slides.append('''<section class="slide " data-section="1">
<div class="kicker">Resumen</div>
  <h1>El fondo se calienta con seguridad; el ENOS cambia poco y con incertidumbre</h1>
  <div class="grid3">
    <div class="card"><div class="stat">+3.6 °C</div><div class="stat-label">Niño 1+2 en 2071–2100 con SSP5-8.5 (+2.3 con SSP2-4.5); 15 de 15 modelos</div></div>
    <div class="card"><div class="stat">+0.7 °C</div><div class="stat-label">Niño 1+2 se calienta más que el trópico: patrón “tipo El Niño” permanente frente al Perú</div></div>
    <div class="card"><div class="stat">99–100 %</div><div class="stat-label">de los meses sobre el umbral de El Niño actual (ICEN con base fija) a fin de siglo</div></div>
  </div>
  <ul style="margin-top:1em">
    <li>El ciclo anual de Niño 1+2 se aplana: el invierno se calienta más que el verano.</li>
    <li>Variabilidad de Niño 3.4: +11 a +26 % en la mediana, sin acuerdo entre modelos. En Niño 1+2, sin cambio claro.</li>
    <li>Eventos cálidos: +11 a +44 % en la mediana, algo más largos e intensos; ningún aumento de frecuencia es significativo.</li>
  </ul>
  <p class="nota-pie"><strong>ref</strong>: 1985–2014; <strong>P1</strong>: 2036–2065; <strong>P2</strong>: 2071–2100. Los valores son la mediana de los 15 modelos seleccionados en el Entregable 2. <strong>Base fija</strong>: anomalía respecto del clima de 1985–2014, sin quitar el calentamiento.</p>
</section>
''')
slides.append('''<section class="slide " data-section="1">
<div class="kicker">Marco común</div>
  <h1>Datos y criterios</h1>
  <div class="grid2">
    <div class="card"><ul>
      <li><strong>Modelos:</strong> los 15 seleccionados en el Entregable 2 (conjunto principal) y los 40 como contraste; un miembro por modelo</li>
      <li><strong>Series:</strong> <span class="mono">historical</span> + escenario, 1850–2100</li>
      <li><strong>Escenarios:</strong> SSP2-4.5 (intermedio), SSP3-7.0 (alto) y SSP5-8.5 (muy alto)</li>
      <li><strong>Periodos de 30 años:</strong> ref 1985–2014, P1 2036–2065, P2 2071–2100: conteos y σ con muestras del mismo largo</li>
    </ul></div>
    <div class="card"><ul>
      <li><strong>Cada modelo contra sí mismo:</strong> cambio = P − ref del mismo modelo; su sesgo fijo se cancela</li>
      <li><strong>Mediana y percentiles 10–90</strong> entre modelos: un modelo extremo no arrastra el resultado</li>
      <li><strong>Acuerdo de signo ≥ 0.8:</strong> al menos 12 de 15 modelos coinciden en la dirección (criterio del IPCC) → robusto</li>
      <li><strong>*</strong> significativo: Wilcoxon con corrección de Holm, p &lt; 0.05</li>
    </ul></div>
  </div>
  <p class="nota-pie">Cálculo en <span class="mono">scripts_e3/</span> (pasos q01–q11, <span class="mono">./rune3.sh</span>); figuras en <span class="mono">plots_e3.ipynb</span>. El kicker de cada diapositiva indica el paso que produce el dato.</p>
</section>
''')
slides.append(larga(2,'Estado medio · q02','Hasta 2050 los escenarios casi no se distinguen; a 2100 deciden entre +2 y +4 °C','e3_01a_trayectoria_tsm',[
 'TSM anual menos la media 1985–2014 de cada modelo; línea = mediana, sombra = p10–p90',
 'Hacia 2050, Niño 3.4 está entre +1.2 y +1.5 °C con los tres escenarios',
 'Hacia 2100: +2.0, +3.2 y +4.1 °C en Niño 3.4; +2.3, +3.4 y +4.2 °C en Niño 1+2',
 'Derecha: caja menos trópico; Niño 1+2 se aparta del trópico de forma gradual desde ~2020']))
slides.append(larga(2,'Estado medio · q03','Calentamiento extra en el ecuador oriental y la costa norte del Perú','e3_01c_mapas_cambio_relativo',[
 'Cambio de cada punto menos el cambio medio del trópico (20°S–20°N); rojo = se calienta más que el trópico',
 'Niño 1+2 en P2: +0.42, +0.51 y +0.70 °C más que el trópico, con 15 de 15 modelos',
 'Niño 3.4: +0.19 a +0.36 °C, con menos acuerdo',
 'El Pacífico suroriental (10–30°S) se calienta menos; tramado = menos del 80 % de acuerdo',
 'En valor total, la costa norte del Perú supera +4 °C en P2 con SSP5-8.5 (por modelo: Anexo)']))
slides.append(larga(2,'Ciclo anual · q04','Niño 1+2 se calienta más en invierno: su ciclo anual se aplana','e3_02a_ciclo_anual',[
 'Cajas: distribución de los 15 modelos en cada mes; gris = ref; número bajo cada caja = calentamiento de ese mes',
 'Niño 1+2, P2, SSP5-8.5: marzo 28.1 → 31.6 °C (+3.3); agosto 22.8 → 27.0 °C (+3.8)',
 'Amplitud de Niño 1+2 en P2: −0.36, −0.37 y −0.49 °C (13–14 de 15 modelos)',
 'Niño 3.4, al revés: el máximo de abril–mayo sube más que el mínimo y la amplitud crece (+0.13 a +0.40 °C)']))
slides.append(larga(3,'Variabilidad · q05','Niño 3.4: más variabilidad en la mediana, pero sin acuerdo entre modelos','e3_03b_cambio_sigma_por_modelo',[
 'σ<sub>3m</sub>: desviación estándar de la anomalía suavizada a 3 meses (escala del ONI y del ICEN), sin ciclo anual ni tendencia',
 'Niño 3.4, P2: +11, +23 y +26 %; con SSP5-8.5 suben 13 de 15 modelos, pero de −29 a +105 % → no significativo',
 'Niño 1+2: de −0.5 a +10 %, con 8 a 12 de 15 modelos de acuerdo: sin cambio claro',
 'En ventanas móviles, el aumento de Niño 3.4 es gradual y llega a +21 a +31 % hacia 2067–2072 (Anexo)']))
slides.append(larga(3,'Índices ENOS · q06–q08','Con la base actual, el umbral de El Niño se supera casi siempre','e3_04a_tiempo_sobre_umbral',[
 'Fracción de meses con el índice sobre el umbral de inicio (0.5 °C), sin exigir duración',
 'Base móvil (clima de su época): ONI 31 % → 35–41 %; ICEN 24 % → 29–36 % en P2',
 'Base fija 1985–2014: ONIfija 31 % → 88–98 %; ICENfija 23 % → 99–100 %',
 'La diferencia es el calentamiento de fondo, no un ENOS más activo'],
 nota='<strong>Base móvil</strong> (ONI, ICEN): el “normal” se actualiza cada 5 años con los 30 años alrededor, como hacen NOAA y el ENFEN. <strong>RONI</strong>: el “normal” es el promedio del trópico en el mismo mes. <strong>Base fija</strong> (ONIfija, ICENfija): el “normal” es siempre 1985–2014.'))
slides.append(larga(4,'Eventos cálidos · q07–q08','Más eventos en la mediana, ninguno significativo','e3_05a_razon_frecuencia',[
 'Frecuencia en P / frecuencia en ref de cada modelo; 1 = sin cambio; eje logarítmico',
 'P2: ONI 1.25 con los tres escenarios; RONI 1.22–1.44; ICEN 1.11–1.20',
 'En absoluto: ONI 27 → 33–37 eventos por siglo; RONI 30 → 37–43 (ERSSTv5 1900–2014: 26 y 30)',
 'Acuerdo ≤ 0.87: con ~9 eventos por periodo, la señal no se distingue del azar; no significa que no cambie']))
slides.append(larga(4,'Eventos cálidos · q08','Eventos algo más largos e intensos','e3_05b_duracion_magnitud',[
 'ICEN, SSP5-8.5: duración media de 8.0 a 10.1 y 11.0 meses en P1 y P2 *',
 'RONI, SSP3-7.0: pico medio de 1.38 a 1.71 y 1.93 °C *',
 'Eventos fuertes o más (por 30 años), SSP5-8.5: ONI 3 → 7; RONI 3 → 9',
 'Eventos ≥ 2σ de la referencia: 1 → 5 en ONI y RONI; coherente con más variabilidad en Niño 3.4',
 'Tipo de evento (Anexo): los extendidos suben de 26 a 32–33 por siglo; los costeros se mantienen en ~5']))
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
  <p class="nota-pie"><strong>Negrita</strong>: robusto (acuerdo de signo ≥ 0.8). <strong>*</strong>: significativo con Wilcoxon y Holm (p &lt; 0.05). Las razones de frecuencia se comparan con 1; el resto, con 0. Las medianas casi no cambian con 40, 11 o 7 modelos (Anexo).</p>
</section>
''')
slides.append('''<section class="slide " data-section="5">
<div class="kicker">Discusión</div>
  <h1>Conclusiones y limitaciones</h1>
  <div class="grid2">
    <div class="card"><strong>Conclusiones</strong><ul class="small-list">
      <li>El calentamiento medio es seguro y crece con las emisiones: +2.3 a +3.6 °C en Niño 1+2 a fin de siglo</li>
      <li>Niño 1+2 se calienta más que el trópico y su ciclo anual se aplana</li>
      <li>El ENOS tiende a más variabilidad (Niño 3.4) y a más eventos, más largos e intensos, pero sin robustez estadística</li>
      <li>Con los umbrales actuales, la costa norte viviría en condición de “Niño” casi permanente: efecto del fondo, no del ENOS</li>
      <li>Comunicar por separado el calentamiento de fondo y el cambio del ENOS</li>
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
slides.append(anexo('Cambio de la TSM media en las cajas, por modelo','e3_01d_cambio_cajas_por_modelo'))
slides.append(anexo('σ<sub>3m</sub> en ventanas móviles de 30 años','e3_03c_sigma_movil'))
slides.append(anexo('Eventos por tipo: costero, extendido y central','e3_05c_tipo_eventos'))
slides.append(anexo('Asimetría y curtosis: los modelos no generan la cola de Niños costeros extraordinarios','e3_A2_asimetria_curtosis'))
slides.append(anexo('Sensibilidad al conjunto de modelos (15, 40, 11 y 7) en P2','e3_A6_sensibilidad_conjuntos'))

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
