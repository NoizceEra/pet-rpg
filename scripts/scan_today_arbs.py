import json
import urllib.request
from datetime import datetime
import sys

def get_gamma_markets():
    # Fetch active markets from Gamma API
    # limit=500 to get a good chunk of recent/active markets
    url = "https://gamma-api.polymarket.com/markets?limit=500&active=true&closed=false&order=volume&ascending=false"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def check_market_arb(market, min_edge=0.05):
    # Check for arbitrage opportunity in a market
    outcomes = market.get('outcomes', [])
    outcome_prices = market.get('outcomePrices', [])
    
    if not outcomes or not outcome_prices:
        return None

    # Parse prices
    prices = []
    try:
        # Prices are strings in API response, sometimes JSON array of strings
        if isinstance(outcome_prices, str):
            try:
                prices = [float(p) for p in json.loads(outcome_prices)]
            except:
                # Fallback if it's not a JSON string list
                pass
        else:
            prices = [float(p) for p in outcome_prices]
    except (ValueError, TypeError):
        return None
        
    if len(prices) < 2:
        return None
        
    prob_sum = sum(prices) * 100
    
    # Arbitrage condition: Sum of all outcome prices < 1 (100%)
    if prob_sum < 100:
        net_profit = 100 - prob_sum
        # Filter by min edge
        if net_profit >= min_edge:
            return {
                'title': market.get('question'),
                'slug': market.get('slug'),
                'market_id': market.get('id'),
                'prob_sum': prob_sum,
                'net_profit': net_profit,
                'prices': dict(zip(outcomes, prices)),
                'volume': market.get('volume', 0)
            }
    
    return None

def main():
    print(f"Scanning Polymarket for BTC/ETH sprint arbs (Edge > 0.05%)...", file=sys.stderr)
    
    try:
        markets = get_gamma_markets()
    except Exception as e:
        print(f"Error fetching markets: {e}", file=sys.stderr)
        return

    now = datetime.now()
    today_long = now.strftime("%B %d").replace(" 0", " ") # February 18
    today_short = now.strftime("%b %d").replace(" 0", " ") # Feb 18
    today_dot = now.strftime("%b. %d").replace(" 0", " ") # Feb. 18
    
    today_alts = [today_long, today_short, today_dot, "Today", "Sprint", "Daily"]
    
    print(f"Filtering for markets related to: {today_alts}", file=sys.stderr)
    
    opportunities = []
    
    for m in markets:
        question = m.get('question', '')
        slug = m.get('slug', '')
        
        # Filter for BTC/ETH sprint markets
        is_crypto = 'bitcoin' in question.lower() or 'ethereum' in question.lower() or 'btc' in question.lower() or 'eth' in question.lower()
        is_today = any(alt in question or alt in slug for alt in today_alts)
        
        if is_crypto and is_today:
            # Re-parse prices for logging (redundant but safe)
            try:
                outcome_prices = m.get('outcomePrices', [])
                if isinstance(outcome_prices, str):
                    raw_prices = [float(p) for p in json.loads(outcome_prices)]
                else:
                    raw_prices = [float(p) for p in outcome_prices]
                raw_prob = sum(raw_prices) * 100
                # print(f"Checking market: {question} (Sum: {raw_prob:.2f}%)", file=sys.stderr)
            except:
                pass
                
            arb = check_market_arb(m)
            if arb:
                opportunities.append(arb)
                
    if not opportunities:
        print("NO_REPLY")
    else:
        print(f"Found {len(opportunities)} arbitrage opportunities:")
        for op in opportunities:
            print(f"- {op['title']}")
            print(f"  Profit: {op['net_profit']:.2f}% | Sum: {op['prob_sum']:.2f}%")
            # print(f"  Prices: {op['prices']}")
            print(f"  URL: https://polymarket.com/event/{op['slug']}")
            print("-" * 40)

if __name__ == "__main__":
    main()
