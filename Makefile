# =============================================================================
# Investment Screener — Makefile
# =============================================================================
#
# USAGE
# -----
#   make                    Run the full pipeline for ALL markets (us + tw + jp)
#   make all                Same as above
#   make screen             Screen stocks only (all markets)
#   make reports            Generate individual financial reports (all markets)
#   make links              Inject ticker links into dashboard HTML (all markets)
#
#   make screen-us          Screen US stocks only (S&P500 + NASDAQ-100)
#   make screen-tw          Screen Taiwan stocks only (TWSE + TPEx)
#   make screen-jp          Screen Japan stocks only (Nikkei 225)
#   make reports-us         Generate individual HTML/MD reports for US results
#   make reports-tw         Generate individual HTML/MD reports for TW results
#   make reports-jp         Generate individual HTML/MD reports for JP results
#   make links-us           Inject ticker hyperlinks into US dashboard HTML
#   make links-tw           Inject ticker hyperlinks into TW dashboard HTML
#   make links-jp           Inject ticker hyperlinks into JP dashboard HTML
#
#   make pipeline-us        Run the complete pipeline for US only
#   make pipeline-tw        Run the complete pipeline for TW only
#   make pipeline-jp        Run the complete pipeline for JP only
#
#   make gen-report TICKER=AAPL  Generate manual report for specific ticker(s)
#
#   make help               Show this help message
#
# PIPELINE ORDER (per market)
#   1. screener.py              → scans tickers, saves CSV + dashboard HTML
#   2. generate_automated_reports.py → reads CSV, fetches yfinance data, writes
#                                      per-ticker HTML + MD files
#   3. add_report_links.py      → patches the dashboard HTML so ticker badges
#                                 link to the per-ticker reports
#
# OUTPUT
#   All files land in a date-stamped folder: ./<YYYYMMDD>_report/
#   e.g. ./20260508_report/
#
# REQUIREMENTS
#   Python venv must exist at ./.venv (run `python3 -m venv .venv` if missing)
#   Install deps: ./.venv/bin/pip install -r requirements.txt
#
# =============================================================================

PYTHON    := ./.venv/bin/python3
SCREENER  := scripts/screener.py
REPORTS   := scripts/generate_automated_reports.py
LINKS      := scripts/add_report_links.py
GEN_REPORT := scripts/gen_report.py
CHECK_YF   := scripts/check_yf.py

# ── Default target ────────────────────────────────────────────────────────────
# Running `make` with no arguments executes the full pipeline for all markets.
.PHONY: all
all: check screen reports links
	@echo ""
	@echo "✅  Full pipeline complete for ALL markets."

# ── Step 0: Check Connectivity ────────────────────────────────────────────────
.PHONY: check
check:
	@$(PYTHON) $(CHECK_YF)

# ── Full pipeline shortcuts ───────────────────────────────────────────────────
.PHONY: pipeline-us
pipeline-us: screen-us reports-us links-us
	@echo ""
	@echo "✅  Full pipeline complete for US market."

.PHONY: pipeline-tw
pipeline-tw: screen-tw reports-tw links-tw
	@echo ""
	@echo "✅  Full pipeline complete for TW market."

.PHONY: pipeline-jp
pipeline-jp: screen-jp reports-jp links-jp
	@echo ""
	@echo "✅  Full pipeline complete for JP market."

# ── Step 1: Screener ──────────────────────────────────────────────────────────
# Scans all markets, saves results CSV + premium HTML dashboard.
.PHONY: screen
screen: check
	@echo "🔍  Screening ALL markets (US + TW + JP)…"
	$(PYTHON) $(SCREENER) --market all

# Screen US only (S&P 500 + NASDAQ-100).
.PHONY: screen-us
screen-us: check
	@echo "🔍  Screening US market…"
	$(PYTHON) $(SCREENER) --market us

# Screen Taiwan only (TWSE + TPEx).
.PHONY: screen-tw
screen-tw: check
	@echo "🔍  Screening TW market…"
	$(PYTHON) $(SCREENER) --market tw

# Screen Japan only (Nikkei 225).
.PHONY: screen-jp
screen-jp: check
	@echo "🔍  Screening JP market…"
	$(PYTHON) $(SCREENER) --market jp

# ── Step 2: Generate individual financial reports ─────────────────────────────
# Reads screener CSV, fetches financial data from yfinance, writes per-ticker
# HTML and Markdown reports into <YYYYMMDD>_report/<TICKER>/ folders.
.PHONY: reports
reports: check
	@echo "📊  Generating reports for ALL markets…"
	$(PYTHON) $(REPORTS) --market all

.PHONY: reports-us
reports-us: check
	@echo "📊  Generating reports for US market…"
	$(PYTHON) $(REPORTS) --market us

.PHONY: reports-tw
reports-tw: check
	@echo "📊  Generating reports for TW market…"
	$(PYTHON) $(REPORTS) --market tw

.PHONY: reports-jp
reports-jp: check
	@echo "📊  Generating reports for JP market…"
	$(PYTHON) $(REPORTS) --market jp

# Generate manual reports for specific ticker(s).
# Usage: make gen-report TICKER="AAPL MSFT VITL"
.PHONY: gen-report
gen-report:
	@if [ -z "$(TICKER)" ]; then \
		echo "Usage: make gen-report TICKER=\"TICKER1 TICKER2 ...\""; \
		exit 1; \
	fi
	@echo "📊  Generating custom report for: $(TICKER)…"
	$(PYTHON) $(GEN_REPORT) $(TICKER)

# ── Step 3: Inject report links into the dashboard HTML ──────────────────────
# Patches the dashboard HTML so each ticker badge becomes a clickable link
# to the per-ticker financial report. Saves a new *_link_*.html file.
.PHONY: links
links:
	@echo "🔗  Injecting ticker links for ALL markets…"
	$(PYTHON) $(LINKS) --market all

.PHONY: links-us
links-us:
	@echo "🔗  Injecting ticker links for US market…"
	$(PYTHON) $(LINKS) --market us

.PHONY: links-tw
links-tw:
	@echo "🔗  Injecting ticker links for TW market…"
	$(PYTHON) $(LINKS) --market tw

.PHONY: links-jp
links-jp:
	@echo "🔗  Injecting ticker links for JP market…"
	$(PYTHON) $(LINKS) --market jp

# ── Help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "Investment Screener — available targets:"
	@echo ""
	@echo "  make / make all       Full pipeline for ALL markets (screen → reports → links)"
	@echo "  make pipeline-us      Full pipeline for US only"
	@echo "  make pipeline-tw      Full pipeline for TW only"
	@echo "  make pipeline-jp      Full pipeline for JP only"
	@echo ""
	@echo "  make screen           Screener only — all markets"
	@echo "  make screen-us        Screener only — US"
	@echo "  make screen-tw        Screener only — TW"
	@echo "  make screen-jp        Screener only — JP"
	@echo ""
	@echo "  make reports          Generate per-ticker reports — all markets"
	@echo "  make reports-us       Generate per-ticker reports — US"
	@echo "  make reports-tw       Generate per-ticker reports — TW"
	@echo "  make reports-jp       Generate per-ticker reports — JP"
	@echo ""
	@echo "  make links            Inject dashboard ticker links — all markets"
	@echo "  make links-us         Inject dashboard ticker links — US"
	@echo "  make links-tw         Inject dashboard ticker links — TW"
	@echo "  make links-jp         Inject dashboard ticker links — JP"
	@echo ""
	@echo "  make help             Show this message"
	@echo ""
