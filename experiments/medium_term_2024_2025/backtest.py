"""Daily causal 2024-25 backtest: price proxy vs strict PIT value mode."""
import argparse, json, math
from pathlib import Path
from datetime import timedelta
import requests, duckdb, numpy as np, pandas as pd
START, END, INITIAL, BPS = "2024-01-02","2025-12-31",100000.,6.
SRC="https://github.com/Johnbrick123/sp500-data/releases/download/data/"
HOME=Path(__file__).resolve().parent

def data(cache):
    cache.mkdir(parents=True,exist_ok=True)
    for name in ("prices.parquet","members.parquet","no_trade_days.csv"):
        dest=cache/name
        if dest.exists() and dest.stat().st_size>1024: continue
        print("Downloading",name,flush=True)
        tmp=cache/(name+".part")
        with requests.get(SRC+name,stream=True,timeout=180) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in r.iter_content(2*1024*1024):
                    if chunk: f.write(chunk)
        tmp.replace(dest)
    con=duckdb.connect()
    px=con.execute("""SELECT CAST(date AS DATE) date,ticker,"open","close",
                       adj_close,volume FROM read_parquet(?)
                       WHERE date >= '2023-01-01' AND date <= '2025-12-31'""",
                   [str(cache/"prices.parquet")]).df()
    mem=con.execute("""SELECT CAST(date AS DATE) date,ticker FROM read_parquet(?)
                        WHERE date >= '2022-01-01' AND date <= '2025-12-31'""",
                    [str(cache/"members.parquet")]).df()
    for frame in (px,mem): frame["date"]=pd.to_datetime(frame.date)
    px=px.sort_values(["date","ticker"]).drop_duplicates(["date","ticker"],keep="last")
    assert px.ticker.nunique()>450 and px.date.nunique()>730 and "SPY" in set(px.ticker)
    assert mem.date.nunique()>1
    bad=pd.read_csv(cache/"no_trade_days.csv")
    banned=set()
    if {"date","ticker"}.issubset(bad.columns):
        banned=set(zip(pd.to_datetime(bad.date),bad.ticker.astype(str)))
    px=px.loc[~pd.MultiIndex.from_frame(px[["date","ticker"]]).isin(banned)]
    return px,mem,banned

def member(mem,date):
    snap=mem.loc[mem.date.le(date),"date"].max()
    if pd.isna(snap): raise ValueError("No prior constituent snapshot")
    return set(mem.loc[mem.date.eq(snap),"ticker"])

def valuation(path,mode):
    if not path.exists():
        if mode=="full": raise ValueError("PIT valuation file required")
        return {}
    z=pd.read_csv(path)
    need={"ticker","published_at","pe_ttm","ev_ebitda","fcf_yield","net_debt_ebitda","revenue_growth","operating_margin"}
    if not need.issubset(z.columns): raise ValueError("Missing valuation columns")
    if z.empty and mode=="full": raise ValueError("Missing PIT valuation rows")
    if z.empty:return {}
    z.published_at=pd.to_datetime(z.published_at)
    return {t:g.sort_values("published_at") for t,g in z.groupby("ticker")}

def val_pass(book,t,date):
    if t not in book:return False
    g=book[t]; old=g[g.published_at.le(date-timedelta(days=2))]
    if old.empty:return False
    x=old.iloc[-1]
    pe=pd.to_numeric(x.pe_ttm,errors="coerce")
    ev=pd.to_numeric(x.ev_ebitda,errors="coerce")
    fy=pd.to_numeric(x.fcf_yield,errors="coerce")
    nd=pd.to_numeric(x.net_debt_ebitda,errors="coerce")
    rg=pd.to_numeric(x.revenue_growth,errors="coerce")
    om=pd.to_numeric(x.operating_margin,errors="coerce")
    signals=[0<pe<=30 if pd.notna(pe) else None,
             0<ev<=18 if pd.notna(ev) else None,
             fy>=.035 if pd.notna(fy) else None]
    return (sum(z is not None for z in signals)>=2 and sum(z is True for z in signals)>=2
            and (pd.isna(nd) or nd<=3) and (pd.isna(rg) or rg>=-.1)
            and (pd.isna(om) or om>0))

def universe(mem,p,adv,mode,rank_path):
    output={}
    if mode=="full":
        if not rank_path.exists():raise ValueError("PIT market-cap top100 list required")
        z=pd.read_csv(rank_path)
        if not {"year","ticker","rank","asof_date"}.issubset(z.columns):raise ValueError("Invalid ranking columns")
        for yr in (2024,2025):
            g=z[(z.year==yr)&(z["rank"]<=100)]
            if len(g)!=100 or g.ticker.nunique()!=100:raise ValueError("100 dated names required each year")
            if pd.to_datetime(g.asof_date).max()>=pd.Timestamp(f"{yr}-01-01"):
                raise ValueError("Future market-cap ranking detected")
            output[yr]=set(g.ticker)
        return output,"PIT_MARKET_CAP_TOP100"
    for yr in (2024,2025):
        prev=p.index[p.index<pd.Timestamp(f"{yr}-01-01")][-1]
        active=member(mem,prev)
        selected=adv.loc[prev].dropna()
        selected=selected.loc[selected.index.intersection(list(active))]
        output[yr]=set(selected.nlargest(100).index)
        if len(output[yr])!=100:raise ValueError("Too few preceding-year candidates")
    return output,"PROXY_TOP100_DOLLAR_VOLUME_NOT_MARKET_CAP"

def run(args):
    px,mem,banned=data(Path(args.cache))
    p=px.pivot(index="date",columns="ticker",values="adj_close").sort_index()
    op0=px.pivot(index="date",columns="ticker",values="open").reindex(p.index)
    cl0=px.pivot(index="date",columns="ticker",values="close").reindex(p.index)
    op=op0*p/cl0
    vol=px.pivot(index="date",columns="ticker",values="volume").reindex(p.index)
    ret1=p.pct_change(fill_method=None)
    ret5=p.pct_change(5,fill_method=None)
    ma20=p.rolling(20,min_periods=20).mean()
    ma50=p.rolling(50,min_periods=50).mean()
    ma200=p.rolling(200,min_periods=200).mean()
    max63=p.rolling(63,min_periods=63).max()
    adv=(p*vol).rolling(63,min_periods=63).mean()
    sigma=ret1.rolling(63,min_periods=63).std()*math.sqrt(252)
    up=p.diff().clip(lower=0).rolling(14,min_periods=14).mean()
    down=(-p.diff().clip(upper=0)).rolling(14,min_periods=14).mean()
    rsi=100-100/(1+up/down.replace(0,np.nan))
    bounce=(p/p.rolling(3,min_periods=3).min()>=1.02)&(ret1>0)
    book=valuation(Path(args.fundamentals),args.mode)
    group,label=universe(mem,p,adv,args.mode,Path(args.top100))
    days=p.loc[START:END].index
    assert len(days)>480
    snapshots={date:member(mem,date) for date in p.index[p.index>=days[0]-timedelta(days=10)]}
    cash=INITIAL; held={}; trades=[]; curve=[]; closed=[]
    for date in days:
        i=p.index.get_loc(date); prior=p.index[i-1]
        for t,h in list(held.items()):
            if (date,t) in banned:continue
            mark=p.at[prior,t] if t in p.columns else np.nan
            fill=op.at[date,t] if t in op.columns else np.nan
            if not(pd.notna(mark) and pd.notna(fill) and fill>0):continue
            pct=mark/h["entry"]-1
            reason=("MAX_FOUR_MONTHS" if date>=h["date"]+pd.DateOffset(months=4)
                else "STOP_LOSS" if pct<=-.08 else "TRAILING_STOP" if mark/h["peak"]-1<=-.12
                else "TREND_BROKEN" if h["route"]=="TREND" and pd.notna(ma50.at[prior,t]) and mark<.97*ma50.at[prior,t] and ret1.at[prior,t]<0
                else "DIP_RECOVERED" if h["route"]=="DIP_REVERSAL" and pct>=.06 and pd.notna(ma20.at[prior,t]) and mark>=ma20.at[prior,t]
                else "PROFIT_OVERBOUGHT" if pct>=.20 and rsi.at[prior,t]>72
                else "SP500_REMOVED" if t not in snapshots[prior] else None)
            if reason:
                gross=h["qty"]*fill; fee=gross*BPS/10000
                cash+=gross-fee
                realized=(gross-fee-h["cost"])/h["cost"]
                closed.append(realized)
                trades.append([date.date(),t,"SELL",fill,h["qty"],fee,reason,realized])
                del held[t]
        used=sum(h["qty"]*float(p.at[prior,t]) for t,h in held.items()
                 if t in p.columns and pd.notna(p.at[prior,t]))
        nav=cash+used
        risk_on=bool(pd.notna(ma200.at[prior,"SPY"]) and p.at[prior,"SPY"]>ma200.at[prior,"SPY"])
        cap=(.90 if risk_on else .60)*nav
        candidates=[]
        s5=ret5.at[prior,"SPY"]
        for t in group[date.year]&snapshots[prior]:
            if t not in p or t=="SPY" or (prior,t) in banned:continue
            values=[p.at[prior,t],ret5.at[prior,t],ma20.at[prior,t],ma50.at[prior,t],
                 ma200.at[prior,t],rsi.at[prior,t],max63.at[prior,t],adv.at[prior,t],sigma.at[prior,t]]
            if not np.isfinite(np.asarray(values,dtype=float)).all():continue
            price,r5,a,b,c,rsi14,hi,liq,v=values
            if price<=5 or liq<20e6 or v>.65:continue
            oldclose=p.iloc[i-2][t]; cur_open=op.at[prior,t]
            if not(pd.notna(oldclose) and pd.notna(cur_open) and oldclose>0):continue
            gap=cur_open/oldclose-1
            dip=r5<=-.10 and (r5-s5)<=-.07 and s5>-.04 and gap>-.06
            reverse=bool(bounce.at[prior,t]) and rsi14<48 and price>.90*c
            trend=price>a>b>c and 48<=rsi14<=68 and price>=.94*hi
            if not((dip and reverse) or trend):continue
            if args.mode=="full" and not val_pass(book,t,prior):continue
            score=(35 if dip else 0)+(25 if reverse else 0)+(20 if trend else 0)+max(0,(.65-v)*20)
            candidates.append((score,t,"DIP_REVERSAL" if dip and reverse else "TREND"))
        candidates.sort(reverse=True)
        for _,t,reason in candidates:
            if t in held or len(held)>=10 or (date,t) in banned:continue
            fill=op.at[date,t]
            if not(pd.notna(fill) and np.isfinite(fill) and fill>0):continue
            alloc=min(.12*nav,cap-used,cash/(1+BPS/10000))
            if alloc<1000:break
            qty=alloc/(fill*(1+BPS/10000))
            fee=qty*fill*BPS/10000; cost=qty*fill+fee
            cash-=cost; used+=qty*fill
            held[t]=dict(qty=qty,entry=fill,peak=fill,date=date,cost=cost,last=fill,route=reason)
            trades.append([date.date(),t,"BUY",fill,qty,fee,reason,np.nan])
        equity=cash
        for t,h in held.items():
            close=p.at[date,t] if t in p.columns else np.nan
            close=float(close) if pd.notna(close) else h["last"]
            h["last"]=close; h["peak"]=max(h["peak"],close)
            equity+=h["qty"]*close
        curve.append([date,equity,cash,len(held)])
    df=pd.DataFrame(curve,columns=["date","equity","cash","positions"]).set_index("date")
    orders=pd.DataFrame(trades,columns=["date","ticker","side","price","shares","fee","reason","realized_return"])
    monthly=df.equity.resample("ME").last()
    prev=INITIAL; yrs={}
    for yr in (2024,2025):
        val=float(df[df.index.year==yr].equity.iloc[-1])
        yrs[str(yr)]={"start":round(prev,2),"end":round(val,2),"return_pct":round(100*(val/prev-1),3)}
        prev=val
    bench=p.at[days[-1],"SPY"]/op.at[days[0],"SPY"]-1
    daily=df.equity.pct_change().fillna(0)
    duration=(days[-1]-days[0]).days/365.25
    summary={"status":"COMPLETE","mode":args.mode,"universe_method":label,
       "date_start":START,"date_end":END,"days":len(days),"starting_equity":INITIAL,
       "ending_equity":round(float(equity),2),"strategy_return_pct":round(100*(equity/INITIAL-1),3),
       "spy_return_pct":round(100*bench,3),"excess_return_pp":round(100*(equity/INITIAL-1-bench),3),
       "cagr_pct":round(100*((equity/INITIAL)**(1/duration)-1),3),
       "max_drawdown_pct":round(100*(df.equity/df.equity.cummax()-1).min(),3),
       "volatility_pct":round(100*daily.std()*math.sqrt(252),3),
       "sharpe_zero_rf":round(daily.mean()/daily.std()*math.sqrt(252),3) if daily.std()>0 else None,
       "orders":len(trades),"round_trips":len(closed),
       "win_rate_pct":round(100*sum(z>0 for z in closed)/len(closed),2) if closed else None,
       "remaining_positions":len(held),"yearly":yrs,"cost_bps_side":BPS,
       "universe_by_year":{str(y):sorted(g) for y,g in group.items()},
       "rule_version":"v1.1_route_aware_after_diagnostic","warning":("Technical/price exploratory POST-HOC v1.1 test; NOT exact cap-top100, no valuation/news verification"
                  if args.mode=="proxy" else "PIT inputs supplied; no contemporaneous news verification")}
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"equity_curve.csv")
    orders.to_csv(out/"trades.csv",index=False)
    monthly.pct_change().rename("monthly_return").to_csv(out/"monthly.csv")
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    lines=["# 2024-2025 results: "+args.mode,"","> "+summary["warning"],"",
           "| Metric | Value |","|---|---:|"]
    lines += ["| "+name+" | "+str(summary[name])+" |" for name in
             ("ending_equity","strategy_return_pct","spy_return_pct",
             "excess_return_pp","cagr_pct","max_drawdown_pct","sharpe_zero_rf",
             "orders","round_trips","win_rate_pct","remaining_positions")]
    lines+=["","## Calendar years","","| Year | Opening NAV | Closing NAV | Return % |",
            "|---|---:|---:|---:|"]
    lines += [f"| {y} | {d['start']} | {d['end']} | {d['return_pct']} |" for y,d in yrs.items()]
    lines+=["","All decisions lagged to the next open; 6bp per side; idle cash 0%;",
            "open positions marked to last close; gaps can exceed stop levels."]
    (out/"summary.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k!="universe_by_year"},indent=2),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("proxy","full"),default="proxy")
    ap.add_argument("--cache",default=str(HOME/".cache"))
    ap.add_argument("--fundamentals",default=str(HOME/"input/valuation_pit.csv"))
    ap.add_argument("--top100",default=str(HOME/"input/top100_pit.csv"))
    ap.add_argument("--out",default=str(HOME/"results/proxy"))
    run(ap.parse_args())
