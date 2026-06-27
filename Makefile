# =============================================================================
# Investment Screener — Makefile
# =============================================================================
#
# USAGE
# -----
#   make                    Run the full pipeline for ALL markets and sync to report/last
#   make all                Same as above
#   make pipeline-us        Run the complete pipeline for US only (auto-syncs to report/last)
#   make pipeline-tw        Run the complete pipeline for TW only (auto-syncs to report/last)
#   make pipeline-jp        Run the complete pipeline for JP only (auto-syncs to report/last)
#
#   make quick              Quick mode: top 10 most discounted stocks per market (screen only)
#   make quick-us           Quick mode: US only
#   make quick-tw           Quick mode: TW only
#   make quick-jp           Quick mode: JP only
#
#   DEBUG=1 make ...        Run any command using the FROZEN debug cache (offline)
#   make freeze-cache       Snapshot today's live data into the debug cache
#   make clean              Clear old cache folders (preserves today and debug)
#   make update-last        Force sync today's reports to report/last folder
#
#   make screen             Screen stocks only (all markets)
#   make reports            Generate individual financial reports (all markets)
#   make links              Inject ticker links into dashboard HTML (all markets)
#
#   make gen-report TICKER=AAPL  Generate manual report for specific ticker(s)
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
#   All files land in a nested date-stamped folder: ./report/<YYYYMMDD>_report/
#   e.g. ./report/20260509_report/
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
LAST_DIR   := report/last
TODAY      := $(shell date +%Y%m%d)
TODAY_DIR  := report/$(TODAY)_report
QUICK_TOP  := 10

# Debug mode support
ifdef DEBUG
    DEBUG_ENV := YF_DEBUG=1
else
    DEBUG_ENV := 
endif

# ── Default target ────────────────────────────────────────────────────────────
# Running `make` with no arguments executes the full pipeline for all markets.
.PHONY: all
all: check pipeline-us pipeline-tw pipeline-jp
	@echo ""
	@echo "✅  Full pipeline complete for ALL markets."

# ── Step 0: Check Connectivity ────────────────────────────────────────────────
.PHONY: check
check:
	@$(DEBUG_ENV) $(PYTHON) $(CHECK_YF)

# ── Full pipeline shortcuts ───────────────────────────────────────────────────
# NOTE: update-last is called in the recipe (not as a prerequisite) so that
#       Make executes it independently for each pipeline.  When it was a shared
#       .PHONY prerequisite, Make only ran it once — leaving report/last with
#       stale data from the first pipeline.
.PHONY: pipeline-us
pipeline-us: screen-us reports-us links-us
	@$(MAKE) update-last
	@echo ""
	@echo "✅  Full pipeline complete for US market."

.PHONY: pipeline-tw
pipeline-tw: screen-tw reports-tw links-tw
	@$(MAKE) update-last
	@echo ""
	@echo "✅  Full pipeline complete for TW market."

.PHONY: pipeline-jp
pipeline-jp: screen-jp reports-jp links-jp
	@$(MAKE) update-last
	@echo ""
	@echo "✅  Full pipeline complete for JP market."

.PHONY: pipeline-test
pipeline-test: screen-test reports-test links-test
	@echo ""
	@echo "✅  Full pipeline complete for TEST market."

# ── Step 1: Screener ──────────────────────────────────────────────────────────
# Scans all markets, saves results CSV + premium HTML dashboard.
# Scans all markets sequentially to preserve cache stability.
.PHONY: screen
screen: check screen-us screen-tw screen-jp

# Screen US only (S&P 500 + NASDAQ-100).
.PHONY: screen-us
screen-us: check
	@echo "🔍  Screening US market…"
	$(DEBUG_ENV) $(PYTHON) $(SCREENER) --market us

# Screen Taiwan only (TWSE + TPEx).
.PHONY: screen-tw
screen-tw: check
	@echo "🔍  Screening TW market…"
	$(DEBUG_ENV) $(PYTHON) $(SCREENER) --market tw

# Screen Japan only (Nikkei 225).
.PHONY: screen-jp
screen-jp: check
	@echo "🔍  Screening JP market…"
	$(DEBUG_ENV) $(PYTHON) $(SCREENER) --market jp

.PHONY: screen-test
screen-test: check
	@echo "🔍  Screening TEST market…"
	$(DEBUG_ENV) $(PYTHON) $(SCREENER) --market test

# ── Quick mode: Screen & link only, top N most discounted ─────────────────────
# Runs the screener and link injector with --quick flag (default top 10), skipping report gen.
.PHONY: quick
quick: check quick-us quick-tw quick-jp
	@echo ""
	@echo "✅  Quick screen complete for ALL markets (top $(QUICK_TOP))."

.PHONY: quick-us
quick-us: check
	@echo "⚡  Quick screening US market (top $(QUICK_TOP))…"
	$(DEBUG_ENV) $(PYTHON) $(SCREENER) --market us --top $(QUICK_TOP) --quick
	@echo "🔗  Injecting ticker links for quick US market…"
	$(PYTHON) $(LINKS) --market us --quick
	@$(MAKE) update-last

.PHONY: quick-tw
quick-tw: check
	@echo "⚡  Quick screening TW market (top $(QUICK_TOP))…"
	$(DEBUG_ENV) $(PYTHON) $(SCREENER) --market tw --top $(QUICK_TOP) --quick
	@echo "🔗  Injecting ticker links for quick TW market…"
	$(PYTHON) $(LINKS) --market tw --quick
	@$(MAKE) update-last

.PHONY: quick-jp
quick-jp: check
	@echo "⚡  Quick screening JP market (top $(QUICK_TOP))…"
	$(DEBUG_ENV) $(PYTHON) $(SCREENER) --market jp --top $(QUICK_TOP) --quick
	@echo "🔗  Injecting ticker links for quick JP market…"
	$(PYTHON) $(LINKS) --market jp --quick
	@$(MAKE) update-last

# ── Step 2: Generate individual financial reports ─────────────────────────────
# Reads screener CSV, fetches financial data from yfinance, writes per-ticker
# HTML and Markdown reports into report/<YYYYMMDD>_report/<TICKER>/ folders.
# Generate individual financial reports for all markets.
.PHONY: reports
reports: check reports-us reports-tw reports-jp

.PHONY: reports-us
reports-us: check
	@echo "📊  Generating reports for US market…"
	$(DEBUG_ENV) $(PYTHON) $(REPORTS) --market us

.PHONY: reports-tw
reports-tw: check
	@echo "📊  Generating reports for TW market…"
	$(DEBUG_ENV) $(PYTHON) $(REPORTS) --market tw

.PHONY: reports-jp
reports-jp: check
	@echo "📊  Generating reports for JP market…"
	$(DEBUG_ENV) $(PYTHON) $(REPORTS) --market jp

.PHONY: reports-test
reports-test: check
	@echo "📊  Generating reports for TEST market…"
	$(DEBUG_ENV) $(PYTHON) $(REPORTS) --market test

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
# Inject report links into the dashboard HTML for all markets.
.PHONY: links
links: check links-us links-tw links-jp

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

.PHONY: links-test
links-test:
	@echo "🔗  Injecting ticker links for TEST market…"
	$(PYTHON) $(LINKS) --market test

# ── Step 4: Sync Latest ───────────────────────────────────────────────────────
# Copies the CSV and HTML results from the current date folder to report/last/
# for easy version control and quick access.
.PHONY: update-last
update-last:
	@mkdir -p $(LAST_DIR)
	@echo "📂  Syncing all reports and sub-folders to $(LAST_DIR)…"
	@cp -rf $(TODAY_DIR)/* $(LAST_DIR)/ 2>/dev/null || true
	@echo "✅  $(LAST_DIR) updated."

# ── Developer Tools ───────────────────────────────────────────────────────────
.PHONY: freeze-cache
freeze-cache:
	@echo "❄️  Freezing today's cache as 'debug' template…"
	@mkdir -p scratch/cache/debug
	@cp -rf scratch/cache/$(shell date +%Y%m%d)/* scratch/cache/debug/
	@echo "✅  Cache frozen in scratch/cache/debug/"

.PHONY: clean
clean:
	@echo "🧹 Cleaning old cache folders (preserving 'debug' and today's data)..."
	@find scratch/cache -mindepth 1 -maxdepth 1 -type d \
		! -name "debug" \
		! -name "$(shell date +%Y%m%d)" \
		-exec rm -rf {} +
	@echo "✅  Old cache cleared."

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
	@echo "  make quick            Quick mode: top 10 most discounted — all markets"
	@echo "  make quick-us         Quick mode — US only"
	@echo "  make quick-tw         Quick mode — TW only"
	@echo "  make quick-jp         Quick mode — JP only"
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
