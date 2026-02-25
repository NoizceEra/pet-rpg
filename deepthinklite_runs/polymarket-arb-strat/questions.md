# Polymarket Arbitrage - Investigation Map

## 🎯 Investigation Plan
This session aims to define the machine learning architecture and high-frequency execution strategy for the Polymarket Arbitrage Bot. We are moving beyond basic math arbitrage into predictive modeling and multi-market correlation.

## 📝 High-Leverage Questions

1. **Market Selection & Liquidity**
   - *Question*: Which market categories (Politics, Crypto, Sports) show the highest frequency of math arbitrage (prob sum < 100%)?
   - *Source*: Local Polymarket skill data + web search for historical arb frequency.

2. **Machine Learning for Predictive Edge**
   - *Question*: Can we train a model to predict "Arb Closure Time"? (i.e., How long do we have to execute before the window shuts?)
   - *Source*: ML Research papers on prediction market efficiency + existing bot patterns.

3. **Execution Logic (Phase 4)**
   - *Question*: What is the optimal simultaneous execution pattern on Polygon to minimize gas wars while ensuring all legs of the arb fill?
   - *Source*: Polygon gas optimization docs + Polymarket API technical limits.

4. **Cross-Market Semantic Matching**
   - *Question*: How can we reliably match a "US Election" outcome on Polymarket with a similar outcome on a competitor (e.g., Betfair or PredictIt) without manual mapping?
   - *Source*: NLP / LLM-based semantic matching strategies.

## 🛠 Next Steps
1. Execute web research for historical Polymarket arb frequency.
2. Analyze the `polymarket-arbitrage` skill's existing Python scripts to identify performance bottlenecks.
3. Draft the "Response.md" with a concrete technical architecture.
