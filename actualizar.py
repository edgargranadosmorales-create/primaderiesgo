from pathlib import Path
from io import StringIO
from datetime import datetime, timezone
import requests
import pandas as pd
import plotly.graph_objects as go
R=Path(__file__).resolve().parent
D=R/'data'; D.mkdir(exist_ok=True)
EY='https://www.multpl.com/s-p-500-earnings-yield/table/by-month'
TY='https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10&cosd=1997-01-01'
s=requests.Session(); s.headers['User-Agent']='Mozilla/5.0'
def get(url):
    r=s.get(url,timeout=60); r.raise_for_status(); return r.text

t=next(t for t in pd.read_html(StringIO(get(EY))) if 'Date' in t.columns and 'Value' in t.columns)
e=pd.DataFrame({'date':pd.to_datetime(t.Date,errors='coerce'),'ey':pd.to_numeric(t.Value.astype(str).str.extract(r'(-?\d+(?:\.\d+)?)')[0],errors='coerce'),'estimated':t.Value.astype(str).str.contains('†',regex=False)}).dropna().sort_values('date')
e=e[e.date>='1997-01-01'].drop_duplicates('date')
b=pd.read_csv(StringIO(get(TY))); b.columns=['date','treasury']
b.date=pd.to_datetime(b.date); b.treasury=pd.to_numeric(b.treasury,errors='coerce'); b=b.dropna().sort_values('date')
today=pd.Timestamp(datetime.now(timezone.utc).date())
e=e[e.date<=today]; b=b[b.date<=today]
if len(e)<300 or len(b)<5000: raise ValueError('Cobertura insuficiente; no se publica.')
l=e.iloc[-1]; bond=b[b.date<=l.date].iloc[-1]; lag=(l.date-bond.date).days
if lag>7: raise ValueError('Treasury atrasado mas de 7 dias; se conserva el HTML anterior.')
m=e[e.date.dt.to_period('M')<l.date.to_period('M')].copy()
m['treasury']=m.date.dt.to_period('M').map(b.groupby(b.date.dt.to_period('M')).treasury.mean())
m=m.dropna(); m['spread']=m.ey-m.treasury
row=pd.DataFrame([dict(date=l.date,ey=l.ey,treasury=bond.treasury,treasury_date=bond.date,spread=l.ey-bond.treasury,estimated=l.estimated,consulted_utc=datetime.now(timezone.utc).isoformat())])
a=D/'observaciones_diarias.csv'
d=pd.concat([pd.read_csv(a,parse_dates=['date','treasury_date']),row],ignore_index=True) if a.exists() else row
d=d.drop_duplicates('date',keep='last').sort_values('date')
f=go.Figure()
f.add_trace(go.Scatter(x=m.date,y=m.spread,name='Historico mensual',line=dict(color='#579aff'),hovertemplate='%{x|%b %Y}: %{y:.2f} pp<extra>Mensual</extra>'))
f.add_trace(go.Scatter(x=d.date,y=d.spread,name='Diario desde instalacion',mode='lines+markers',line=dict(color='#27d6b2'),hovertemplate='%{x|%d %b %Y}: %{y:.2f} pp<extra>Diario archivado</extra>'))
f.add_hline(y=0,line_dash='dash',line_color='#999')
f.update_layout(template='plotly_dark',height=600,yaxis_title='Puntos porcentuales',xaxis=dict(rangeslider=dict(visible=True)),legend=dict(orientation='h'),hovermode='x unified')
chart=f.to_html(full_html=False,include_plotlyjs=True)
stamp=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
html=f"""<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="3600"><title>EY menos Treasury 10Y</title><style>body{{background:#101722;color:#edf3ff;font:16px system-ui;padding:25px}}main{{max-width:1250px;margin:auto}}.cards{{display:flex;gap:20px;flex-wrap:wrap}}.card{{background:#1d293b;padding:20px;border-radius:12px}}p{{line-height:1.6}}a{{color:#78b3ff}}</style><main><h1>S&P 500: earnings yield − Treasury 10 años</h1><p>Utilidades trailing 12 meses · Histórico desde enero de 1997</p><div class="cards"><div class="card">EY TTM: <h2>{l.ey:.2f}%</h2>Fecha: {l.date:%Y-%m-%d}</div><div class="card">Treasury 10Y: <h2>{bond.treasury:.2f}%</h2>Fecha: {bond.date:%Y-%m-%d}</div><div class="card">Diferencial: <h2>{l.ey-bond.treasury:+.2f} pp</h2>Desfase: {lag} días</div></div>{chart}<p>Consulta: {stamp}. Último dato publicado, no necesariamente de hoy. EY actual estimado por la fuente: {bool(l.estimated)}.</p><h2>Metodología</h2><p>Histórico mensual: EY de Multpl menos promedio mensual de DGS10 de FRED. El primero de cada mes identifica el mes, no un cierre diario. Se excluye el mes del dato más reciente de esta curva. La serie diaria empieza con la instalación; archiva una observación por fecha publicada de EY y usa Treasury de esa fecha o el último anterior, mostrando el desfase. No se inventan observaciones diarias desde 1997.</p><p>EY = utilidades de los últimos 12 meses / precio. No es forward ni CAPE. Este diferencial es un indicador relativo de valoración, NO una estimación completa de la prima de riesgo esperada, un rendimiento garantizado o una señal automática de inversión. El histórico revisable no sirve como base point-in-time de backtesting.</p><p>Fuentes: <a href="{EY}">Multpl / S&P</a> y <a href="https://fred.stlouisfed.org/series/DGS10">FRED DGS10</a>. El HTML se recarga cada hora; las consultas se ejecutan por separado diariamente.</p><p><a href="data/historico_mensual.csv">CSV mensual</a> · <a href="data/observaciones_diarias.csv">CSV diario</a></p></main></html>"""
m.to_csv(D/'historico_mensual.csv',index=False); d.to_csv(a,index=False)
tmp=R/'index.tmp'; tmp.write_text(html,encoding='utf-8'); tmp.replace(R/'index.html')
print({'ey_date':str(l.date.date()),'treasury_date':str(bond.date.date()),'spread_pp':float(l.ey-bond.treasury),'monthly_rows':len(m)})
