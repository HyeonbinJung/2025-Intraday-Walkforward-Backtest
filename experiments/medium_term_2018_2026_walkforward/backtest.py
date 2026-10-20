"""2018 development -> 2019H1 forward -> yearly walk-forward -> June 2026 exit.
Historical price-only proxy by default; strict PIT fundamentals require real dated inputs.
No future dates are consulted for signals or selection. Public historical prices are
retrospectively adjusted, so this is not a perfect data-vintage reconstruction.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
DATA_URL = "https://github.com/Johnbrick123/sp500-data/releases/download/data/"
START, LAST_ENTRY, END = "2018-01-02", "2025-12-31", "2026-06-30"
CAPITAL = 100_000.0
COST_BPS = 6.0  # Commission + modeled slippage per side.
HOLD_MONTHS = 6
TAKE_PROFIT = 0.10
STOP_LOSS = -0.08
TRAILING_STOP = -0.12
INPUT_FILES = ("prices.parquet", "members.parquet", "no_trade_days.csv", "recycled_tickers.csv")
FUN_COLS = ("ticker", "published_at", "sector", "pe_ttm", "ev_ebitda",
            "fcf_yield", "net_debt_ebitda", "revenue_growth", "operating_margin", "source_url")
NEWS_COLS = ("ticker", "signal_date", "reviewed_at", "coverage_verified",
             "material_adverse", "source_url")


@dataclass(frozen=True)
class Profile:
    name: str
    drop_5d: float
    excess_drop: float
    vol_max: float
    min_dollar_volume: float
    max_positions: int
    risk_gross: float
    weak_gross: float
    reversal_rsi: float
    trend_rsi_max: float
    use_reversal: bool = True
    use_trend: bool = True


PROFILES = (
    Profile("defensive", -0.12, -0.08, 0.50, 30e6, 8, 0.70, 0.35, 43, 65),
    Profile("balanced", -0.10, -0.07, 0.65, 20e6, 10, 0.85, 0.45, 49, 70),
    Profile("trend_bias", -0.12, -0.09, 0.55, 25e6, 10, 0.85, 0.40, 45, 67,
            use_reversal=False),
    Profile("reversal_bias", -0.10, -0.06, 0.60, 20e6, 8, 0.75, 0.35, 52, 67,
            use_trend=False),
)
PROFILE_BY_NAME = {p.name: p for p in PROFILES}


def download(cache: Path) -> dict:
    cache.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name in INPUT_FILES:
        target = cache / name
        if not target.exists() or target.stat().st_size < 100:
            temp = target.with_suffix(target.suffix + ".partial")
            with requests.get(DATA_URL + name, stream=True, timeout=240) as response:
                response.raise_for_status()
                with temp.open("wb") as fh:
                    for chunk in response.iter_content(2 * 1024 * 1024):
                        if chunk:
                            fh.write(chunk)
            temp.replace(target)
        digest = hashlib.sha256()
        with target.open("rb") as fh:
            for chunk in iter(lambda: fh.read(4 * 1024 * 1024), b""):
                digest.update(chunk)
        manifest[name] = {"bytes": target.stat().st_size, "sha256": digest.hexdigest(),
                          "source": DATA_URL + name}
    return manifest


def load_market(cache: Path):
    manifest = download(cache)
    con = duckdb.connect()
    px = con.execute("""
        SELECT CAST(date AS DATE) AS date, ticker, "open", "close", adj_close, volume
        FROM read_parquet(?) WHERE date >= '2017-01-01' AND date <= '2026-06-30'
    """, [str(cache / "prices.parquet")]).df()
    mem = con.execute("""
        SELECT CAST(date AS DATE) AS date, ticker FROM read_parquet(?)
        WHERE date >= '2017-01-01' AND date <= '2026-06-30'
    """, [str(cache / "members.parquet")]).df()
    for frame in (px, mem):
        frame["date"] = pd.to_datetime(frame["date"])
    if px.empty or mem.empty or px.date.max() < pd.Timestamp(END):
        raise ValueError("Source lacks the full 2026-06-30 exit horizon; no partial report as COMPLETE")
    if px.ticker.nunique() < 450 or mem.date.nunique() < 2000:
        raise ValueError("Missing historical S&P 500 price/membership coverage")
    if px.duplicated(["date", "ticker"]).any():
        px = px.sort_values(["date", "ticker"]).drop_duplicates(["date", "ticker"], keep="last")
    bad = pd.read_csv(cache / "no_trade_days.csv")
    bad_pairs = set(zip(pd.to_datetime(bad.date), bad.ticker.astype(str))) if \
        {"date", "ticker"}.issubset(bad.columns) else set()
    ix = pd.MultiIndex.from_frame(px[["date", "ticker"]])
    px = px.loc[~ix.isin(bad_pairs)].copy()
    recycled = pd.read_csv(cache / "recycled_tickers.csv")
    recycled_names = set(recycled.ticker.dropna().astype(str)) if \
        "ticker" in recycled.columns else set()
    px = px.loc[~px.ticker.isin(recycled_names)]
    mem = mem.loc[~mem.ticker.isin(recycled_names)]
    mem = mem.sort_values(["date", "ticker"]).drop_duplicates(["date", "ticker"])
    snapshots = {date: frozenset(chunk.ticker) for date, chunk in mem.groupby("date")}
    dates = sorted(snapshots)

    def universe(date):
        idx = bisect.bisect_right(dates, date) - 1
        if idx < 0:
            raise ValueError("No historic membership snapshot before " + str(date))
        return snapshots[dates[idx]]

    p = px.pivot(index="date", columns="ticker", values="adj_close").sort_index()
    raw_open = px.pivot(index="date", columns="ticker", values="open").reindex_like(p)
    raw_close = px.pivot(index="date", columns="ticker", values="close").reindex_like(p)
    # Normalize next-open fills to adjusted close share units; retrospective adjustment caveat.
    op = raw_open * p / raw_close.where(raw_close > 0)
    volume = px.pivot(index="date", columns="ticker", values="volume").reindex_like(p)
    if "SPY" not in p or p.loc[START:END, "SPY"].dropna().empty:
        raise ValueError("SPY benchmark is not available")
    trading_days = p.loc[START:END].index.intersection(p.index[p.SPY.notna()])
    if len(trading_days) < 2000 or trading_days[-1] != pd.Timestamp(END):
        raise ValueError("Trading calendar does not cover 2018 to final June 2026 session")
    return p, op, volume, universe, bad_pairs, manifest, trading_days


def features(p: pd.DataFrame, volume: pd.DataFrame):
    r1 = p.pct_change(fill_method=None)
    up = p.diff().clip(lower=0).rolling(14, min_periods=14).mean()
    down = (-p.diff().clip(upper=0)).rolling(14, min_periods=14).mean()
    return {
        "ret1": r1,
        "ret5": p.pct_change(5, fill_method=None),
        "ret20": p.pct_change(20, fill_method=None),
        "sma20": p.rolling(20, min_periods=20).mean(),
        "sma50": p.rolling(50, min_periods=50).mean(),
        "sma200": p.rolling(200, min_periods=200).mean(),
        "max63": p.rolling(63, min_periods=63).max(),
        "low3": p.rolling(3, min_periods=3).min(),
        "dollarvol": (p * volume).rolling(63, min_periods=63).mean(),
        "vol": r1.rolling(63, min_periods=63).std() * math.sqrt(252),
        "rsi": 100 - 100 / (1 + up / down.replace(0, np.nan)),
    }


class PointInTimeGates:
    """Fail-closed financial/peer/news checks. Never fill absent data with guessed values."""
    def __init__(self, mode: str, fundamentals: Path, reviews: Path):
        self.mode = mode
        self.latest_cache = {}
        self.rows = {}
        self.reviews = {}
        self.checked = 0
        self.approved = 0
        if mode == "proxy":
            return
        if not fundamentals.is_file() or not reviews.is_file():
            raise ValueError("Strict mode needs both real PIT fundamentals and dated news reviews")
        f = pd.read_csv(fundamentals)
        n = pd.read_csv(reviews)
        if not set(FUN_COLS).issubset(f.columns) or not set(NEWS_COLS).issubset(n.columns):
            raise ValueError("Strict inputs missing required as-of/source fields")
        if f.empty or n.empty:
            raise ValueError("Strict mode refuses empty historic fundamentals or news reviews")
        f["published_at"] = pd.to_datetime(f["published_at"], utc=True, errors="raise")
        n["reviewed_at"] = pd.to_datetime(n["reviewed_at"], utc=True, errors="raise")
        n["signal_date"] = pd.to_datetime(n["signal_date"], errors="raise").dt.normalize()
        for name, grp in f.sort_values("published_at").groupby("ticker"):
            self.rows[str(name)] = grp.to_dict("records")
        for item in n.to_dict("records"):
            self.reviews[(str(item["ticker"]), item["signal_date"])] = item

    def latest(self, ticker, decision_date):
        key = (ticker, decision_date)
        if key in self.latest_cache:
            return self.latest_cache[key]
        # Two full calendar days of conservative release lag.
        asof = pd.Timestamp(decision_date).tz_localize("UTC") - pd.Timedelta(days=2)
        valid = [r for r in self.rows.get(ticker, ()) if r["published_at"] <= asof]
        row = valid[-1] if valid else None
        self.latest_cache[key] = row
        return row

    def passes(self, ticker, decision_date, peers):
        if self.mode == "proxy":
            return True
        self.checked += 1
        row = self.latest(ticker, decision_date)
        review = self.reviews.get((ticker, pd.Timestamp(decision_date).normalize()))
        if row is None or review is None:
            return False
        verified = str(review["coverage_verified"]).lower() in ("true", "1", "yes")
        adverse = str(review["material_adverse"]).lower() in ("true", "1", "yes")
        if not verified or adverse or not str(review["source_url"]).startswith("http"):
            return False
        end = pd.Timestamp(decision_date).tz_localize("UTC") + pd.Timedelta(days=1)
        if review["reviewed_at"] >= end or not str(row["source_url"]).startswith("http"):
            return False
        try:
            pe, ev, fy, debt, growth, margin = (
                float(row[k]) for k in ("pe_ttm", "ev_ebitda", "fcf_yield",
                                         "net_debt_ebitda", "revenue_growth", "operating_margin")
            )
        except (ValueError, TypeError):
            return False
        if not all(map(math.isfinite, (pe, ev, fy, debt, growth, margin))):
            return False
        if not (pe > 0 and ev > 0 and fy > 0 and debt <= 3 and growth >= -0.10 and margin > 0):
            return False
        sector = str(row["sector"])
        others = []
        for other in peers:
            if other == ticker:
                continue
            v = self.latest(other, decision_date)
            if v is not None and str(v["sector"]) == sector:
                others.append(v)
        if len(others) < 3:
            return False
        def median(key):
            vals = pd.to_numeric(pd.Series([a[key] for a in others]), errors="coerce")
            vals = vals[np.isfinite(vals) & (vals > 0)]
            return float(vals.median()) if len(vals) >= 3 else float("nan")
        med_pe, med_ev, med_fy = median("pe_ttm"), median("ev_ebitda"), median("fcf_yield")
        comps = [pe <= 1.25 * med_pe, ev <= 1.25 * med_ev, fy >= 0.8 * med_fy]
        if sum(bool(v) for v in comps) < 2:
            return False
        self.approved += 1
        return True


def ranked_candidates(date, profile: Profile, p, f, universe, gates):
    """Close-of-date features ONLY. Orders cannot fill until the next open."""
    try:
        m = universe(date)
        close = p.loc[date]
        r1, r5 = f["ret1"].loc[date], f["ret5"].loc[date]
        a, b, c = (f[k].loc[date] for k in ("sma20", "sma50", "sma200"))
        rsi, sigma, adv = (f[k].loc[date] for k in ("rsi", "vol", "dollarvol"))
        spy_r5 = float(r5["SPY"])
        market_ok = float(close["SPY"]) > float(c["SPY"])
        valid = ((close > 5) & (adv >= profile.min_dollar_volume) &
                 (sigma <= profile.vol_max) & (rsi.notna()) & c.notna() &
                 close.index.isin(m))
        rebound = ((close / f["low3"].loc[date] >= 1.02) & (r1 > 0) &
                   (close > 0.88 * c) & (rsi < profile.reversal_rsi))
        dip = ((r5 <= profile.drop_5d) &
               ((r5 - spy_r5) <= profile.excess_drop) & (spy_r5 > -0.06) & rebound)
        trend = ((close > a) & (a > b) & (b > c) & (rsi.between(47, profile.trend_rsi_max)) &
                 (close / f["max63"].loc[date] >= 0.92))
        if not profile.use_reversal:
            dip &= False
        if not profile.use_trend:
            trend &= False
        picks = valid & (dip | trend)
        selected = []
        for ticker in picks.index[picks.fillna(False)]:
            if ticker == "SPY" or not gates.passes(ticker, date, m):
                continue
            route = "REVERSAL" if bool(dip[ticker]) else "TREND"
            strength = ((0.40 if route == "REVERSAL" else 0.25) +
                        0.25 * min(1, max(0, float(adv[ticker]) / 2e8)) +
                        0.20 * max(0, 1 - float(sigma[ticker])) +
                        0.15 * (1 if market_ok else 0))
            selected.append((round(strength, 6), ticker, route))
        selected.sort(key=lambda row: (-row[0], row[1]))
        return selected
    except KeyError as exc:
        raise ValueError("Required price/factor column absent: " + str(exc)) from exc


def account():
    return {"cash": CAPITAL, "held": {}, "equity": [], "trades": [],
            "nonexec_writeoffs": 0, "fees": 0.0}


def portfolio_value(state, date, p):
    cash = state["cash"]
    for ticker, lot in state["held"].items():
        mark = p.at[date, ticker] if ticker in p.columns else float("nan")
        mark = float(mark) if np.isfinite(mark) and mark > 0 else lot["last"]
        cash += lot["qty"] * mark
    return float(cash)


def step(state, date, prior, profile, picks, p, op, f, universe, banned, allow_buy):
    held = state["held"]
    for ticker, lot in list(held.items()):
        mark = p.at[prior, ticker] if ticker in p.columns else float("nan")
        if not np.isfinite(mark) or mark <= 0:
            mark = lot["last"]
        mark = float(mark)
        gross_ret = mark / lot["entry"] - 1
        reason = ("FORCED_JUNE_2026" if date == pd.Timestamp(END)
                  else "TAKE_PROFIT_10PCT" if gross_ret >= TAKE_PROFIT
                  else "STOP_LOSS_8PCT" if gross_ret <= STOP_LOSS
                  else "TRAILING_STOP_12PCT" if mark / lot["peak"] - 1 <= TRAILING_STOP
                  else "MAX_SIX_MONTHS" if date >= lot["date"] + pd.DateOffset(months=HOLD_MONTHS)
                  else "MEMBERSHIP_EXIT" if ticker not in universe(prior)
                  else None)
        opened = op.at[date, ticker] if ticker in op.columns else float("nan")
        tradable = (np.isfinite(opened) and opened > 0 and (date, ticker) not in banned)
        if not tradable:
            lot["untradeable"] += 1
            if date == pd.Timestamp(END) or (lot["untradeable"] >= 10 and
                                              ticker not in universe(prior)):
                # ZERO dollars received; flagged as unverified write-off, NOT a sale.
                state["nonexec_writeoffs"] += 1
                state["trades"].append({
                    "date": str(date.date()), "ticker": ticker, "side": "NON_EXECUTABLE_WRITEOFF",
                    "price": 0.0, "shares": lot["qty"], "fee": 0.0,
                    "reason": "NO_VERIFIABLE_OPEN_OR_CORPORATE_PAYOUT",
                    "profile": lot["profile"], "realized_return": -1.0,
                })
                del held[ticker]
            continue
        lot["untradeable"] = 0
        if reason is None:
            continue
        fill = float(opened)
        proceeds = lot["qty"] * fill
        fee = proceeds * COST_BPS / 10000
        state["cash"] += proceeds - fee
        state["fees"] += fee
        realized = (proceeds - fee - lot["cost"]) / lot["cost"]
        state["trades"].append({
            "date": str(date.date()), "ticker": ticker, "side": "SELL", "price": fill,
            "shares": lot["qty"], "fee": fee, "reason": reason,
            "profile": lot["profile"], "realized_return": realized,
        })
        del held[ticker]

    nav = portfolio_value(state, prior, p)
    invested = nav - state["cash"]
    spy_close = p.at[prior, "SPY"]
    spy_sma = f["sma200"].at[prior, "SPY"]
    risk_on = np.isfinite(spy_sma) and spy_close > spy_sma
    gross_cap = nav * (profile.risk_gross if risk_on else profile.weak_gross)
    if allow_buy:
        for _, ticker, route in picks:
            if ticker in held or len(held) >= profile.max_positions:
                continue
            if (date, ticker) in banned or ticker not in universe(prior):
                continue
            fill = op.at[date, ticker] if ticker in op else float("nan")
            if not np.isfinite(fill) or fill <= 0:
                continue
            # End-of-2025 entries may continue into 2026 but no new 2026 entries.
            budget = min(0.10 * nav, gross_cap - invested,
                         state["cash"] / (1 + COST_BPS / 10000))
            if budget < 1_000:
                break
            qty = budget / (float(fill) * (1 + COST_BPS / 10000))
            fee = qty * float(fill) * COST_BPS / 10000
            cost = qty * float(fill) + fee
            state["cash"] -= cost
            state["fees"] += fee
            invested += qty * float(fill)
            held[ticker] = {"qty": qty, "entry": float(fill), "date": date,
                            "peak": float(fill), "last": float(fill),
                            "cost": cost, "profile": profile.name, "untradeable": 0}
            state["trades"].append({
                "date": str(date.date()), "ticker": ticker, "side": "BUY",
                "price": float(fill), "shares": qty, "fee": fee,
                "reason": route, "profile": profile.name, "realized_return": None,
            })
    nav_close = state["cash"]
    for ticker, lot in held.items():
        mark = p.at[date, ticker] if ticker in p else float("nan")
        mark = float(mark) if np.isfinite(mark) and mark > 0 else lot["last"]
        lot["last"] = mark
        lot["peak"] = max(lot["peak"], mark)
        nav_close += lot["qty"] * mark
    state["equity"].append({"date": date, "equity": float(nav_close),
                            "cash": float(state["cash"]), "positions": len(held),
                            "profile": profile.name})


def evaluate_shadow(equity_rows, lookback):
    series = np.asarray([z["equity"] for z in equity_rows[-lookback:]], dtype=float)
    if len(series) < 63:
        return float("-inf"), 0.0, 0.0
    growth = series[-1] / series[0] - 1
    dd = float((series / np.maximum.accumulate(series) - 1).min())
    daily = np.diff(series) / series[:-1]
    vol = float(np.std(daily) * math.sqrt(252))
    # Deterministic conservative reward; only PRIOR equity observations.
    score = float(growth + 0.75 * dd - 0.12 * vol)
    return score, growth, dd


def selection_schedule(days):
    """First trading days of periods; all calibration ends at prior close."""
    dates = {}
    dates[days[0]] = ("INITIAL_DEVELOPMENT", None)
    for y in range(2019, 2026):
        subset = days[(days.year == y) & (days.month == 1)]
        if len(subset):
            dates[subset[0]] = ("JANUARY_ANNUAL_REVIEW", 252 if y > 2019 else 252)
    second_half = days[(days.year == 2019) & (days.month == 7)]
    if len(second_half):
        dates[second_half[0]] = ("2019H1_FORWARD_REVIEW", 252)
    return dates


def stats(rows, p, first_day, end_day):
    table = pd.DataFrame(rows).set_index("date")
    sub = table.loc[first_day:end_day, "equity"]
    if sub.empty:
        raise ValueError("Empty performance window")
    prior_idx = p.index[p.index < first_day]
    prev_day = prior_idx[-1]
    initial_nav = CAPITAL if first_day == pd.Timestamp(START) else float(
        table.loc[table.index < first_day, "equity"].iloc[-1])
    final_nav = float(sub.iloc[-1])
    spy_return = float(p.at[end_day, "SPY"] / p.at[prev_day, "SPY"] - 1)
    mdd = float((sub / sub.cummax() - 1).min())
    return {
        "period_start": str(first_day.date()), "period_end": str(end_day.date()),
        "opening_nav": round(initial_nav, 2), "ending_nav": round(final_nav, 2),
        "return_pct": round((final_nav / initial_nav - 1) * 100, 3),
        "spy_return_pct": round(spy_return * 100, 3),
        "max_drawdown_pct": round(mdd * 100, 3),
        "sessions": len(sub),
    }


def run(args):
    p, op, volume, universe, banned, manifest, days = load_market(Path(args.cache))
    f = features(p, volume)
    gates = PointInTimeGates(args.mode, Path(args.fundamentals), Path(args.reviews))
    primary = account()
    shadows = {profile.name: account() for profile in PROFILES}
    dates = selection_schedule(days)
    active = PROFILE_BY_NAME["balanced"]
    policies = []
    for date in days:
        i = p.index.get_loc(date)
        prior = p.index[i - 1]
        if date in dates:
            event, trailing = dates[date]
            if trailing is not None:
                ranking = []
                for candidate in PROFILES:
                    score, gain, drawdown = evaluate_shadow(
                        shadows[candidate.name]["equity"], trailing)
                    ranking.append({"policy": candidate.name, "score": round(score, 8),
                                    "trailing_return": round(gain, 8),
                                    "trailing_drawdown": round(drawdown, 8)})
                # Tie-break in favor of lower risk and stable alphabetical name.
                ranking.sort(key=lambda r: (-r["score"], r["policy"]))
                active = PROFILE_BY_NAME[ranking[0]["policy"]]
            else:
                ranking = []
            policies.append({"effective_date": str(date.date()), "trained_through": str(prior.date()),
                             "event": event, "chosen_profile": active.name,
                             "ranking": ranking})
        # Identical signal inventory per profile. Every signal is derived at 'prior'.
        signals = {profile.name: ranked_candidates(prior, profile, p, f, universe, gates)
                   for profile in PROFILES} if date.year <= 2025 else {}
        for profile in PROFILES:
            step(shadows[profile.name], date, prior, profile,
                 signals.get(profile.name, ()), p, op, f, universe, banned,
                 allow_buy=(date.year <= 2025))
        step(primary, date, prior, active, signals.get(active.name, ()),
             p, op, f, universe, banned, allow_buy=(date.year <= 2025))
        if (date.month == 1 and date.day <= 4) or date == days[-1]:
            print(str(date.date()), "policy", active.name, "NAV",
                  round(primary["equity"][-1]["equity"], 2), flush=True)

    if primary["held"]:
        raise AssertionError("June 2026 liquidation invariant broken")
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    curve = pd.DataFrame(primary["equity"])
    orders = pd.DataFrame(primary["trades"])
    curve.assign(date=curve.date.dt.strftime("%Y-%m-%d")).to_csv(
        output / "equity_curve.csv", index=False)
    orders.to_csv(output / "trades.csv", index=False)
    years = []
    for year in range(2018, 2027):
        subset = days[days.year == year]
        if len(subset):
            row = stats(primary["equity"], p, subset[0], subset[-1])
            row["year"] = year
            row["classification"] = ("DEVELOPMENT" if year == 2018 else
                                      "FORWARD_POLICY_SELECTION" if year == 2019 else
                                      "WALK_FORWARD" if year <= 2025 else "LIQUIDATION_ONLY")
            years.append(row)
    pd.DataFrame(years).to_csv(output / "yearly.csv", index=False)
    (output / "policy_log.json").write_text(json.dumps(policies, indent=2) + "\n")
    daily = curve.equity.pct_change().dropna()
    final_nav = float(curve.equity.iloc[-1])
    n_sells = int((orders.side == "SELL").sum()) if not orders.empty else 0
    wins = orders[(orders.side == "SELL") & (orders.realized_return > 0)]
    summary = {
        "status": ("COMPLETE_PROXY_WITH_UNVERIFIED_WRITEOFFS"
                   if primary["nonexec_writeoffs"] and args.mode == "proxy" else
                   "COMPLETE_PROXY" if args.mode == "proxy" else
                   "STRICT_PIT_INPUT_BACKTEST_WITH_UNVERIFIED_WRITEOFFS"
                   if primary["nonexec_writeoffs"] else "STRICT_PIT_INPUT_BACKTEST"),
        "mode": args.mode, "data_source": DATA_URL, "dataset_manifest": manifest,
        "date_start": START, "last_new_buy": LAST_ENTRY, "date_end": END,
        "initial_nav": CAPITAL, "final_nav": round(final_nav, 2),
        "total_return_pct": round(100 * (final_nav / CAPITAL - 1), 3),
        "spy_total_return_pct": round(100 * (
            p.at[pd.Timestamp(END), "SPY"] / p.at[p.index[p.index < days[0]][-1], "SPY"] - 1), 3),
        "max_drawdown_pct": round(100 * (curve.equity / curve.equity.cummax() - 1).min(), 3),
        "sharpe_zero_rf": round(float(daily.mean() / daily.std() * math.sqrt(252)), 3)
        if daily.std() > 0 else None,
        "buy_orders": int((orders.side == "BUY").sum()) if not orders.empty else 0,
        "executed_sells": n_sells,
        "win_rate_executed_pct": round(100 * len(wins) / n_sells, 2) if n_sells else None,
        "nonexecuted_zero_recovery_writeoffs": primary["nonexec_writeoffs"],
        "total_fees_usd": round(primary["fees"], 2),
        "positions_remaining": len(primary["held"]),
        "terminal_cash_usd": round(primary["cash"], 2),
        "years": years, "policy_log": policies,
        "fundamental_reviews_checked": gates.checked, "fundamental_reviews_passed": gates.approved,
        "rules": {"max_months": HOLD_MONTHS, "take_profit_pct": 10,
                  "stop_loss_pct": -8, "trailing_stop_pct": -12,
                  "transaction_cost_bps_per_side": COST_BPS,
                  "signal_close_then_next_open": True,
                  "no_new_entries_after": LAST_ENTRY},
        "caveats": [
            "Price-only proxy does NOT validate genuine as-filed fundamentals or competitor valuation" if args.mode == "proxy"
            else "Strict financial & news inputs are externally supplied and not independently verified",
            "2018 is model-development/in-sample; 2019H1 decisions use only 2018 calibration",
            "Selection considers only trailing shadow account observations before each effective date",
            "Retrospectively adjusted market data and reconstructed constituent vintages remain ex-post sources",
            "ZERO-recovery write-offs are NOT executed liquidation fills or verified merger proceeds",
            "No new buy in 2026; June30 open forced exits for tradable positions",
            "Fractional shares, zero cash interest, 6bp/side costs and no shorting/leverage",
        ],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if not orders.empty:
        buy = orders[orders.side == "BUY"]
        if len(buy) and max(buy.date) > LAST_ENTRY:
            raise AssertionError("2026 purchase slipped into liquidation-only period")
    if abs(summary["final_nav"] - summary["terminal_cash_usd"]) > 0.02:
        raise AssertionError("Terminal NAV must equal cash after portfolio disposition")
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("dataset_manifest", "years", "policy_log", "caveats")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("proxy", "strict"), default="proxy")
    parser.add_argument("--cache", default=str(HERE / ".cache"))
    parser.add_argument("--fundamentals", default=str(HERE / "input" / "fundamentals_pit.csv"))
    parser.add_argument("--reviews", default=str(HERE / "input" / "news_reviews_pit.csv"))
    parser.add_argument("--out", default=str(HERE / "results" / "proxy"))
    run(parser.parse_args())
