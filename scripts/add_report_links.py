import os
import argparse
import json
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup


def get_report_dir():
    """Resolves the date-stamped report directory (same convention as screener.py)."""
    project_root = Path(__file__).resolve().parent.parent
    today_str = datetime.now().strftime("%Y%m%d")
    return project_root / "report" / f"{today_str}_report"


def add_links_and_sorting(input_path, output_path, metrics_data=None):
    """
    Reads the dma_200_screen_results.html file and:
    1. Wraps each ticker badge in a link.
    2. Injects metrics data for sorting.
    3. Adds a sorting interface.
    """
    print(f"Reading {input_path}...")
    if not os.path.exists(input_path):
        print(f"ERROR: Input file not found: {input_path}")
        print("Hint: Run screener.py first to generate the HTML report.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find all ticker badges (e.g., <span class="ticker-badge">TTD</span>)
    subtitle = soup.find('p', class_='subtitle')
    if subtitle and " - Generated when " not in subtitle.get_text():
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subtitle.string = f"{subtitle.get_text().strip()} - Generated when {now_str}"

    badges = soup.find_all('span', class_='ticker-badge')
    print(f"Found {len(badges)} ticker badges to link.")

    for badge in badges:
        ticker = badge.text.strip()
        # The folders are named after the uppercase ticker,
        # and the files are named after the lowercase ticker.
        # Example: TTD/ttd_financial_data.html
        # Determine market subfolder
        market_subfolder = "US_stock"
        if ticker.endswith('.T'):
            market_subfolder = "JP_stock"
        elif ticker.endswith('.TW') or ticker.endswith('.TWO'):
            market_subfolder = "TW_stock"
            
        # Example: US_stock/TTD/ttd_financial_data.html
        link_url = f"{market_subfolder}/{ticker}/{ticker.lower()}_financial_data.html"

        # Create a new <a> tag that opens in a new tab
        link_tag = soup.new_tag('a', href=link_url, target='_blank')
        # Add style to remove underline and make it look like a button/badge
        link_tag['style'] = 'text-decoration: none; display: inline-block;'

        # Wrap the span inside the <a> tag
        badge.wrap(link_tag)

        # Step 2: Inject metrics into the row (tr)
        row = link_tag.find_parent('tr')
        if row:
            # Add data-discount attribute for current default sorting
            # This should ALWAYS be added if we can find it
            cells = row.find_all('td')
            if cells:
                try:
                    # Discount is usually the last column before we added the new one
                    # In the original HTML it's cells[5] (% Discount)
                    discount_text = cells[5].text.replace('%', '').strip()
                    row['data-discount'] = float(discount_text)
                except:
                    row['data-discount'] = 0.0
            
            if metrics_data and ticker in metrics_data:
                m = metrics_data[ticker]
                # Add metrics attributes
                for metric in ['roe', 'ps', 'pe', 'pb']:
                    if metric in m:
                        for year, val in m[metric].items():
                            row[f'data-{metric}-{year}'] = val
                        row[f'data-{metric}-avg'] = m.get(f'avg_{metric}_past', 0.0)

    # Step 3: Add Sorting UI and column
    thead = soup.find('thead')
    if thead:
        tr = thead.find('tr')
        if tr:
            new_th = soup.new_tag('th', style="text-align: right")
            new_th['id'] = 'dynamic-metric-header'
            new_th.string = "Metric"
            tr.append(new_th)

    tbody = soup.find('tbody')
    if tbody:
        for row in tbody.find_all('tr'):
            new_td = soup.new_tag('td', style="text-align: right; font-weight: bold; color: #38bdf8;")
            new_td['class'] = 'dynamic-metric-cell'
            new_td.string = "-"
            row.append(new_td)

    # Inject Sorting Controls
    header_section = soup.find('header')
    if header_section:
        # Determine available years from metrics
        years = set()
        if metrics_data:
            for m in metrics_data.values():
                years.update(m.get('roe', {}).keys())
        sorted_years = sorted(list(years), reverse=True)

        controls_html = f"""
        <div class="sorting-controls" style="margin-bottom: 30px; background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 140px;">
                <span style="font-weight: 600; color: #94a3b8; white-space: nowrap;">Filter:</span>
                <input type="text" id="ticker-filter" placeholder="Ticker or Name..." style="background: #1e293b; color: white; border: 1px solid #38bdf8; padding: 8px 12px; border-radius: 6px; outline: none; width: 100%; min-width: 100px;">
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 120px;">
                <span style="font-weight: 600; color: #94a3b8; white-space: nowrap;">Metric:</span>
                <select id="metric-type" style="background: #1e293b; color: white; border: 1px solid #38bdf8; padding: 8px 12px; border-radius: 6px; cursor: pointer; outline: none; flex: 1;">
                    <option value="dma">200-DMA</option>
                    <option value="roe">ROE</option>
                    <option value="pe">P/E</option>
                    <option value="ps">P/S</option>
                    <option value="pb">P/B</option>
                </select>
            </div>

            <div id="range-container" style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 120px;">
                <span style="font-weight: 600; color: #94a3b8; white-space: nowrap;">Range:</span>
                <select id="metric-range" style="background: #1e293b; color: white; border: 1px solid #38bdf8; padding: 8px 12px; border-radius: 6px; cursor: pointer; outline: none; flex: 1;">
                    <option value="avg">Average</option>
                    {"".join([f'<option value="{y}">{y}</option>' for y in sorted_years])}
                </select>
            </div>

            <button id="apply-sort" style="background: #38bdf8; color: #000; border: none; padding: 10px 25px; border-radius: 6px; font-weight: 700; cursor: pointer; transition: all 0.2s; white-space: nowrap; width: 100%;">Apply</button>
        </div>
        """
        controls_soup = BeautifulSoup(controls_html, 'html.parser')
        header_section.append(controls_soup)

    # Step 4: Add JS Sorting Logic
    body = soup.find('body')
    if body:
        js_code = """
        <script>
        function applySortAndFilter() {
            const type = document.getElementById('metric-type').value;
            const range = document.getElementById('metric-range').value;
            const filterText = document.getElementById('ticker-filter').value.toLowerCase();
            const tbody = document.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const header = document.getElementById('dynamic-metric-header');
            const rangeContainer = document.getElementById('range-container');

            // Construct method key and handle UI state
            let method = '';
            let label = '';
            
            if (type === 'dma') {
                method = 'discount';
                label = '200-DMA % Discount';
                rangeContainer.style.opacity = '0.3';
                rangeContainer.style.pointerEvents = 'none';
            } else {
                method = type + '-' + range;
                const typeLabel = type === 'roe' ? 'ROE' : type.toUpperCase();
                const rangeLabel = range === 'avg' ? 'Average' : range;
                label = typeLabel + ' (' + rangeLabel + ')';
                rangeContainer.style.opacity = '1';
                rangeContainer.style.pointerEvents = 'auto';
            }
            
            header.innerText = label;

            rows.sort((a, b) => {
                let valA = parseFloat(a.getAttribute('data-' + method)) || 0;
                let valB = parseFloat(b.getAttribute('data-' + method)) || 0;
                
                // If both are 0 (likely N/A), put them at the end
                if (valA === 0 && valB !== 0) return 1;
                if (valB === 0 && valA !== 0) return -1;

                // Ascending (Lower is better) for valuations and DMA discount
                if (type === 'dma' || type === 'pe' || type === 'ps' || type === 'pb') {
                    return valA - valB;
                }
                // Descending (Higher is better) for ROE
                return valB - valA;
            });

            rows.forEach(row => {
                // Filter logic
                const ticker = row.cells[0].innerText.toLowerCase();
                const name = row.cells[1].innerText.toLowerCase();
                const matches = ticker.includes(filterText) || name.includes(filterText);
                row.style.display = matches ? '' : 'none';

                const cell = row.querySelector('.dynamic-metric-cell');
                const val = row.getAttribute('data-' + method);
                const roeVal = row.getAttribute('data-roe-' + range);
                
                if (val !== null && val !== '0' && val !== 0) {
                    const numVal = parseFloat(val);
                    let displayStr = '';
                    
                    if (type === 'roe') {
                        displayStr = numVal.toFixed(1) + '%';
                        cell.style.color = numVal > 15 ? '#4ade80' : (numVal > 0 ? '#fbbf24' : '#f87171');
                    } else if (type === 'dma') {
                        displayStr = numVal.toFixed(2) + '%';
                        cell.style.color = '#38bdf8';
                    } else {
                        displayStr = numVal.toFixed(2);
                        if (roeVal && type !== 'roe') {
                            displayStr += ' <span style="font-size: 0.8em; color: #94a3b8;">(ROE: ' + parseFloat(roeVal).toFixed(1) + '%)</span>';
                        }
                        cell.style.color = '#38bdf8';
                    }
                    cell.innerHTML = displayStr;
                } else {
                    cell.innerText = 'N/A';
                    cell.style.color = '#94a3b8';
                }
                tbody.appendChild(row);
            });
        }

        document.getElementById('apply-sort').addEventListener('click', applySortAndFilter);
        document.getElementById('ticker-filter').addEventListener('input', applySortAndFilter);
        document.getElementById('metric-type').addEventListener('change', applySortAndFilter);
        document.getElementById('metric-range').addEventListener('change', applySortAndFilter);
        
        window.addEventListener('load', () => {
            applySortAndFilter();
        });
        </script>
        """
        js_soup = BeautifulSoup(js_code, 'html.parser')
        body.append(js_soup)

    # Enhance the CSS with a hover effect for better interactivity
    style_tag = soup.find('style')
    if style_tag and '.ticker-badge:hover' not in style_tag.string:
        hover_css = """
        .ticker-badge {
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .ticker-badge:hover {
            filter: brightness(1.2);
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);
        }
        """
        style_tag.append(hover_css)

    # Write the modified HTML to the output file
    print(f"Writing updated report to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add links to screener report")
    parser.add_argument('--market', choices=['us', 'tw', 'jp', 'all', 'test'], default='us', help='Market to process')
    args = parser.parse_args()

    report_dir = get_report_dir()

    # Load metrics data if available
    metrics_data = {}
    metrics_path = report_dir / "metrics_summary.json"
    if metrics_path.exists():
        try:
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            print(f"Loaded metrics for {len(metrics_data)} tickers.")
        except Exception as e:
            print(f"Warning: Could not load metrics: {e}")

    # Expand 'all' into individual market keys
    markets = ['us', 'tw', 'jp'] if args.market == 'all' else [args.market]

    for market_key in markets:
        report_in  = report_dir / f"dma_200_screen_results_{market_key}.html"
        report_out = report_dir / f"dma_200_screen_result_link_{market_key}.html"
        print(f"\n--- Processing {market_key.upper()} market ---")
        add_links_and_sorting(str(report_in), str(report_out), metrics_data)

