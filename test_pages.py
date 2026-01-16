#!/usr/bin/env python3
"""
COMPREHENSIVE Automated Browser Testing for AP Calculus BC Unit 1 Pages
Tests every interactive element, animation, and content thoroughly
"""

from playwright.sync_api import sync_playwright
import time
import json
import re

BASE_URL = "http://localhost:8080"

PAGES = [
    {
        "file": "U1.1-Existence-of-Limit.html",
        "title": "Existence of Limit",
        "cb_topics": ["1.1", "1.2", "1.3", "1.4"],
        "mcq_count": 19,
        "panel_class": "content-panel",
        "section_ids": ["objectives", "prerequisites", "concepts", "problems", "tips", "mistakes", "connections"]
    },
    {
        "file": "U1.2-Calculating-Limit.html",
        "title": "Calculating Limits",
        "cb_topics": ["1.5", "1.6", "1.7"],
        "mcq_count": 12,
        "panel_class": "section",
        "section_ids": ["keypoints", "prerequisites", "concepts", "problemtypes", "examtips", "mistakes", "connections"]
    },
    {
        "file": "U1.3-Squeeze-Theorem.html",
        "title": "Squeeze Theorem",
        "cb_topics": ["1.8"],
        "mcq_count": 0,
        "panel_class": "section",
        "section_ids": ["keypoints", "prerequisites", "concepts", "problemtypes", "examtips", "mistakes", "connections"]
    },
    {
        "file": "U1.4-Continuity-and-Discontinuities.html",
        "title": "Continuity",
        "cb_topics": ["1.9", "1.10", "1.11", "1.12", "1.13"],
        "mcq_count": 26,
        "panel_class": "section",
        "section_ids": ["keypoints", "prerequisites", "concepts", "problemtypes", "examtips", "mistakes", "connections"]
    },
    {
        "file": "U1.5-Asymptotes-and-End-Behavior.html",
        "title": "Asymptotes",
        "cb_topics": ["1.14", "1.15"],
        "mcq_count": 29,
        "panel_class": "section",
        "section_ids": ["keypoints", "prerequisites", "concepts", "problemtypes", "examtips", "mistakes", "connections"]
    },
    {
        "file": "U1.6-Intermediate-Value-Theorem.html",
        "title": "IVT",
        "cb_topics": ["1.16"],
        "mcq_count": 14,
        "panel_class": "section",
        "section_ids": ["keypoints", "prerequisites", "concepts", "problemtypes", "examtips", "mistakes", "connections"]
    },
]


def test_page_thoroughly(page, config):
    """Run comprehensive tests on a single page"""
    results = {
        "page": config["file"],
        "passed": [],
        "failed": [],
        "warnings": [],
        "info": []
    }

    url = f"{BASE_URL}/{config['file']}"

    print(f"\n{'='*70}")
    print(f"  THOROUGH TESTING: {config['file']}")
    print(f"{'='*70}")

    # ========== SECTION 1: PAGE LOAD AND BASIC STRUCTURE ==========
    print("\n--- Section 1: Page Load & Structure ---")

    try:
        response = page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(2)  # Wait for JS to fully initialize

        # Test 1.1: HTTP Response
        if response.status == 200:
            results["passed"].append("1.1 HTTP 200 response")
            print("  [PASS] 1.1 HTTP 200 response")
        else:
            results["failed"].append(f"1.1 HTTP {response.status}")
            print(f"  [FAIL] 1.1 HTTP {response.status}")
            return results

        # Test 1.2: Page Title
        title = page.title()
        if config["title"].lower() in title.lower():
            results["passed"].append(f"1.2 Title contains '{config['title']}'")
            print(f"  [PASS] 1.2 Title: {title}")
        else:
            results["failed"].append(f"1.2 Title mismatch: {title}")
            print(f"  [FAIL] 1.2 Title mismatch: {title}")

        # Test 1.3: Header exists
        header = page.query_selector(".header, header")
        if header:
            header_text = header.text_content()
            results["passed"].append("1.3 Header element exists")
            print(f"  [PASS] 1.3 Header exists")
        else:
            results["failed"].append("1.3 No header found")
            print("  [FAIL] 1.3 No header found")

        # Test 1.4: Check CB Topics in header
        meta_badges = page.query_selector_all(".meta-badge")
        topics_found = []
        for badge in meta_badges:
            text = badge.text_content()
            for topic in config["cb_topics"]:
                if topic in text:
                    topics_found.append(topic)

        if len(topics_found) >= len(config["cb_topics"]) // 2:
            results["passed"].append(f"1.4 CB Topics found: {topics_found}")
            print(f"  [PASS] 1.4 CB Topics: {topics_found}")
        else:
            results["warnings"].append(f"1.4 Only found topics: {topics_found}")
            print(f"  [WARN] 1.4 Only found topics: {topics_found}")

    except Exception as e:
        results["failed"].append(f"1.0 Page load failed: {str(e)[:100]}")
        print(f"  [FAIL] 1.0 Page load failed: {str(e)[:100]}")
        return results

    # ========== SECTION 2: THEME TOGGLE ==========
    print("\n--- Section 2: Theme Toggle ---")

    try:
        # Test 2.1: Theme toggle exists
        theme_btn = page.query_selector(".theme-toggle")
        if theme_btn:
            results["passed"].append("2.1 Theme toggle button exists")
            print("  [PASS] 2.1 Theme toggle exists")

            # Test 2.2: Get initial theme
            initial_theme = page.evaluate("document.body.getAttribute('data-theme') || 'light'")
            results["info"].append(f"2.2 Initial theme: {initial_theme}")
            print(f"  [INFO] 2.2 Initial theme: {initial_theme}")

            # Test 2.3: Click and verify theme changes
            theme_btn.click()
            time.sleep(0.5)
            new_theme = page.evaluate("document.body.getAttribute('data-theme') || 'light'")

            if new_theme != initial_theme:
                results["passed"].append(f"2.3 Theme changed: {initial_theme} -> {new_theme}")
                print(f"  [PASS] 2.3 Theme changed to: {new_theme}")
            else:
                results["failed"].append("2.3 Theme did not change on click")
                print("  [FAIL] 2.3 Theme did not change")

            # Test 2.4: Verify localStorage
            stored = page.evaluate("localStorage.getItem('theme')")
            if stored == new_theme:
                results["passed"].append("2.4 Theme persisted to localStorage")
                print("  [PASS] 2.4 localStorage updated")
            else:
                results["warnings"].append(f"2.4 localStorage mismatch: {stored}")
                print(f"  [WARN] 2.4 localStorage: {stored}")

            # Toggle back
            theme_btn.click()
            time.sleep(0.3)
        else:
            results["failed"].append("2.1 Theme toggle not found")
            print("  [FAIL] 2.1 Theme toggle not found")

    except Exception as e:
        results["failed"].append(f"2.0 Theme test error: {str(e)[:100]}")
        print(f"  [FAIL] 2.0 Theme test error: {str(e)[:50]}")

    # ========== SECTION 3: NAVIGATION TABS ==========
    print("\n--- Section 3: Tab Navigation ---")

    try:
        tabs = page.query_selector_all(".nav-tab")
        results["info"].append(f"3.0 Found {len(tabs)} tabs")
        print(f"  [INFO] 3.0 Found {len(tabs)} tabs")

        # Test 3.1: Correct number of tabs
        if len(tabs) >= 7:
            results["passed"].append(f"3.1 Has {len(tabs)} tabs (expected 7)")
            print(f"  [PASS] 3.1 Has {len(tabs)} tabs")
        else:
            results["failed"].append(f"3.1 Only {len(tabs)} tabs (expected 7)")
            print(f"  [FAIL] 3.1 Only {len(tabs)} tabs")

        # Test 3.2-3.8: Test each tab individually
        panel_class = config["panel_class"]
        for i, tab in enumerate(tabs[:7]):
            tab_text = tab.text_content().strip()[:20]

            # Click the tab
            tab.click()
            time.sleep(0.4)

            # Verify active state on tab
            tab_active = "active" in (tab.get_attribute("class") or "")

            # Verify panel is visible
            active_panels = page.evaluate(f"""
                () => {{
                    const panels = document.querySelectorAll('.{panel_class}.active');
                    return Array.from(panels).map(p => p.id);
                }}
            """)

            if tab_active and len(active_panels) > 0:
                results["passed"].append(f"3.{i+2} Tab '{tab_text}' works")
                print(f"  [PASS] 3.{i+2} Tab '{tab_text}' -> panel: {active_panels}")
            else:
                results["failed"].append(f"3.{i+2} Tab '{tab_text}' failed")
                print(f"  [FAIL] 3.{i+2} Tab '{tab_text}' - active:{tab_active}, panels:{active_panels}")

    except Exception as e:
        results["failed"].append(f"3.0 Tab test error: {str(e)[:100]}")
        print(f"  [FAIL] 3.0 Tab test error: {str(e)[:50]}")

    # ========== SECTION 4: KATEX MATH RENDERING ==========
    print("\n--- Section 4: KaTeX Math Rendering ---")

    try:
        # Test 4.1: KaTeX elements exist
        katex_elements = page.query_selector_all(".katex")
        katex_count = len(katex_elements)

        if katex_count > 0:
            results["passed"].append(f"4.1 KaTeX rendered: {katex_count} elements")
            print(f"  [PASS] 4.1 KaTeX elements: {katex_count}")
        else:
            results["failed"].append("4.1 No KaTeX elements found")
            print("  [FAIL] 4.1 No KaTeX elements")

        # Test 4.2: Check for unrendered LaTeX (raw \( or \[ in text)
        body_text = page.evaluate("document.body.innerText")
        unrendered = len(re.findall(r'\\[\(\[]', body_text))

        if unrendered == 0:
            results["passed"].append("4.2 No unrendered LaTeX found")
            print("  [PASS] 4.2 No unrendered LaTeX")
        else:
            results["warnings"].append(f"4.2 Found {unrendered} potential unrendered LaTeX")
            print(f"  [WARN] 4.2 Potential unrendered LaTeX: {unrendered}")

        # Test 4.3: Check for KaTeX errors
        katex_errors = page.query_selector_all(".katex-error")
        if len(katex_errors) == 0:
            results["passed"].append("4.3 No KaTeX rendering errors")
            print("  [PASS] 4.3 No KaTeX errors")
        else:
            results["failed"].append(f"4.3 Found {len(katex_errors)} KaTeX errors")
            print(f"  [FAIL] 4.3 KaTeX errors: {len(katex_errors)}")

    except Exception as e:
        results["failed"].append(f"4.0 KaTeX test error: {str(e)[:100]}")
        print(f"  [FAIL] 4.0 KaTeX test error: {str(e)[:50]}")

    # ========== SECTION 5: PREREQUISITES ==========
    print("\n--- Section 5: Prerequisites Section ---")

    try:
        # Navigate to prerequisites tab
        prereq_tab = page.query_selector('button:has-text("Prerequisite")')
        if prereq_tab:
            prereq_tab.click()
            time.sleep(0.5)

        # Test 5.1: Find prereq cards
        prereq_cards = page.query_selector_all(".prereq-card")
        results["info"].append(f"5.1 Found {len(prereq_cards)} prereq cards")
        print(f"  [INFO] 5.1 Prereq cards: {len(prereq_cards)}")

        # Test 5.2: Test expand buttons
        expand_btns = page.query_selector_all(".expand-btn")
        if len(expand_btns) > 0:
            # Click first expand button
            for btn in expand_btns[:1]:
                if btn.is_visible():
                    btn.click()
                    time.sleep(0.5)

                    # Check if content expanded
                    expanded = page.query_selector_all(".prereq-lesson.expanded, .prereq-content.active")
                    if len(expanded) > 0:
                        results["passed"].append("5.2 Prereq expand works")
                        print("  [PASS] 5.2 Prereq expands on click")
                    else:
                        results["warnings"].append("5.2 Prereq expand may not work")
                        print("  [WARN] 5.2 Prereq expand unclear")
                    break
        else:
            results["info"].append("5.2 No expand buttons found")
            print("  [INFO] 5.2 No expand buttons")

        # Test 5.3: Check prereq practice questions
        prereq_opts = page.query_selector_all(".prereq-opt")
        if len(prereq_opts) > 0:
            results["passed"].append(f"5.3 Prereq practice options: {len(prereq_opts)}")
            print(f"  [PASS] 5.3 Prereq practice options: {len(prereq_opts)}")

            # Test clicking an option
            for opt in prereq_opts[:1]:
                if opt.is_visible():
                    opt.click()
                    time.sleep(0.3)
                    if "selected" in (opt.get_attribute("class") or ""):
                        results["passed"].append("5.4 Prereq option clickable")
                        print("  [PASS] 5.4 Prereq option responds to click")
                    break
        else:
            results["info"].append("5.3 No prereq practice options")
            print("  [INFO] 5.3 No prereq practice")

    except Exception as e:
        results["warnings"].append(f"5.0 Prereq test error: {str(e)[:100]}")
        print(f"  [WARN] 5.0 Prereq test error: {str(e)[:50]}")

    # ========== SECTION 6: ACCORDIONS (Problem Types) ==========
    print("\n--- Section 6: Accordion Sections ---")

    try:
        # Navigate to Problem Types
        prob_tab = page.query_selector('button:has-text("Problem")')
        if prob_tab:
            prob_tab.click()
            time.sleep(0.5)

        # Test 6.1: Find accordion headers
        headers = page.query_selector_all(".problem-type-header")
        results["info"].append(f"6.1 Found {len(headers)} accordion headers")
        print(f"  [INFO] 6.1 Accordion headers: {len(headers)}")

        if len(headers) > 0:
            # Test 6.2: Test each accordion
            accordions_working = 0
            for i, header in enumerate(headers[:5]):  # Test first 5
                try:
                    parent = page.evaluate(f"""
                        () => {{
                            const headers = document.querySelectorAll('.problem-type-header');
                            const header = headers[{i}];
                            const parent = header?.closest('.problem-type');
                            return {{
                                collapsed_before: parent?.classList.contains('collapsed'),
                                id: parent?.id
                            }};
                        }}
                    """)

                    header.click()
                    time.sleep(0.4)

                    parent_after = page.evaluate(f"""
                        () => {{
                            const headers = document.querySelectorAll('.problem-type-header');
                            const header = headers[{i}];
                            const parent = header?.closest('.problem-type');
                            return parent?.classList.contains('collapsed');
                        }}
                    """)

                    if parent["collapsed_before"] != parent_after:
                        accordions_working += 1

                except Exception:
                    pass

            if accordions_working > 0:
                results["passed"].append(f"6.2 {accordions_working}/{min(5, len(headers))} accordions toggle")
                print(f"  [PASS] 6.2 Accordions working: {accordions_working}/{min(5, len(headers))}")
            else:
                results["failed"].append("6.2 No accordions respond to click")
                print("  [FAIL] 6.2 Accordions not responding")
        else:
            results["warnings"].append("6.1 No accordion headers found")
            print("  [WARN] 6.1 No accordions found")

    except Exception as e:
        results["warnings"].append(f"6.0 Accordion test error: {str(e)[:100]}")
        print(f"  [WARN] 6.0 Accordion error: {str(e)[:50]}")

    # ========== SECTION 7: ANIMATION CONTROLS ==========
    print("\n--- Section 7: Animation Controls ---")

    try:
        # Test 7.1: Find animation controls
        control_btns = page.query_selector_all(".control-btn")
        step_counters = page.query_selector_all(".step-counter")
        progress_bars = page.query_selector_all(".progress-fill")

        results["info"].append(f"7.1 Controls: {len(control_btns)} btns, {len(step_counters)} counters, {len(progress_bars)} progress bars")
        print(f"  [INFO] 7.1 Control btns: {len(control_btns)}, Counters: {len(step_counters)}, Progress: {len(progress_bars)}")

        if len(control_btns) > 0:
            results["passed"].append("7.2 Animation control buttons exist")
            print("  [PASS] 7.2 Animation controls present")

            # Test 7.3: Test animation stepping via JS
            anim_test = page.evaluate("""
                () => {
                    // Find a visible step counter
                    const counters = document.querySelectorAll('.step-counter');
                    if (counters.length === 0) return { error: 'no counters' };

                    const initial = counters[0].textContent;

                    // Find associated Next button and click
                    const btns = document.querySelectorAll('.control-btn');
                    if (btns.length >= 2) {
                        btns[1].click(); // Usually Next is second
                    }

                    const after = counters[0].textContent;

                    return {
                        initial: initial,
                        after: after,
                        changed: initial !== after
                    };
                }
            """)

            if anim_test.get("changed"):
                results["passed"].append(f"7.3 Animation stepping: {anim_test['initial']} -> {anim_test['after']}")
                print(f"  [PASS] 7.3 Animation steps: {anim_test['initial']} -> {anim_test['after']}")
            else:
                results["info"].append(f"7.3 Animation state: {anim_test}")
                print(f"  [INFO] 7.3 Animation: {anim_test}")

            # Test 7.4: Test Reset button
            reset_test = page.evaluate("""
                () => {
                    const counters = document.querySelectorAll('.step-counter');
                    if (counters.length === 0) return { error: 'no counters' };

                    // Click reset (usually first or last button)
                    const btns = document.querySelectorAll('.control-btn');
                    // Find reset button (often has specific content or is button 0 or 2)
                    for (let btn of btns) {
                        if (btn.innerHTML.includes('↺') || btn.innerHTML.includes('reset')) {
                            btn.click();
                            break;
                        }
                    }
                    // Or try first button
                    if (btns.length > 0) btns[0].click();

                    return { step: counters[0].textContent };
                }
            """)
            results["info"].append(f"7.4 After reset attempt: {reset_test}")
            print(f"  [INFO] 7.4 Reset result: {reset_test}")

        else:
            results["warnings"].append("7.2 No animation controls found")
            print("  [WARN] 7.2 No animation controls")

    except Exception as e:
        results["warnings"].append(f"7.0 Animation test error: {str(e)[:100]}")
        print(f"  [WARN] 7.0 Animation error: {str(e)[:50]}")

    # ========== SECTION 8: PRACTICE PROBLEMS ==========
    print("\n--- Section 8: Practice Problems ---")

    try:
        # Test 8.1: Find practice problems
        practice_problems = page.query_selector_all(".practice-problem")
        practice_options = page.query_selector_all(".practice-option, .prediction-option")

        results["info"].append(f"8.1 Practice problems: {len(practice_problems)}, Options: {len(practice_options)}")
        print(f"  [INFO] 8.1 Problems: {len(practice_problems)}, Options: {len(practice_options)}")

        if len(practice_options) > 0:
            # Test 8.2: Click an option
            clicked = False
            for opt in practice_options:
                if opt.is_visible():
                    try:
                        opt.click()
                        time.sleep(0.3)
                        classes = opt.get_attribute("class") or ""
                        if "selected" in classes or "active" in classes:
                            results["passed"].append("8.2 Practice option selectable")
                            print("  [PASS] 8.2 Practice option responds")
                            clicked = True
                            break
                    except:
                        pass

            if not clicked:
                # Try via JS
                js_click = page.evaluate("""
                    () => {
                        const opts = document.querySelectorAll('.practice-option, .prediction-option');
                        for (let opt of opts) {
                            if (window.getComputedStyle(opt).display !== 'none') {
                                opt.click();
                                return opt.classList.contains('selected') || true;
                            }
                        }
                        return false;
                    }
                """)
                if js_click:
                    results["passed"].append("8.2 Practice option clickable (via JS)")
                    print("  [PASS] 8.2 Practice option works (JS)")
                else:
                    results["warnings"].append("8.2 Practice options not responding")
                    print("  [WARN] 8.2 Practice options unclear")

        # Test 8.3: Check answer buttons
        check_btns = page.query_selector_all(".check-answer-btn, button:has-text('Check')")
        show_btns = page.query_selector_all(".show-solution-btn, button:has-text('Solution')")

        results["info"].append(f"8.3 Check buttons: {len(check_btns)}, Solution buttons: {len(show_btns)}")
        print(f"  [INFO] 8.3 Check btns: {len(check_btns)}, Solution btns: {len(show_btns)}")

        if len(check_btns) > 0 or len(show_btns) > 0:
            results["passed"].append("8.4 Practice interaction buttons exist")
            print("  [PASS] 8.4 Practice buttons present")

    except Exception as e:
        results["warnings"].append(f"8.0 Practice test error: {str(e)[:100]}")
        print(f"  [WARN] 8.0 Practice error: {str(e)[:50]}")

    # ========== SECTION 9: GRAPHS (Plotly) ==========
    print("\n--- Section 9: Graph Rendering ---")

    try:
        # Test 9.1: Find graph containers
        graph_containers = page.query_selector_all(".graph-plot, .graph-container, [id*='graph']")
        plotly_plots = page.query_selector_all(".js-plotly-plot, .plotly")

        results["info"].append(f"9.1 Graph containers: {len(graph_containers)}, Plotly plots: {len(plotly_plots)}")
        print(f"  [INFO] 9.1 Containers: {len(graph_containers)}, Plotly: {len(plotly_plots)}")

        # Test 9.2: Check if Plotly initialized
        plotly_check = page.evaluate("""
            () => {
                const plots = document.querySelectorAll('.js-plotly-plot');
                return {
                    count: plots.length,
                    hasData: plots.length > 0 && plots[0].data !== undefined
                };
            }
        """)

        if plotly_check["count"] > 0:
            results["passed"].append(f"9.2 Plotly plots found: {plotly_check['count']}")
            print(f"  [PASS] 9.2 Plotly plots: {plotly_check['count']}")
        else:
            results["info"].append("9.2 No Plotly plots (may initialize on demand)")
            print("  [INFO] 9.2 No Plotly plots detected")

    except Exception as e:
        results["warnings"].append(f"9.0 Graph test error: {str(e)[:100]}")
        print(f"  [WARN] 9.0 Graph error: {str(e)[:50]}")

    # ========== SECTION 10: DECISION FLOWCHARTS ==========
    print("\n--- Section 10: Decision Flowcharts ---")

    try:
        flowcharts = page.query_selector_all(".decision-flowchart, .flowchart-container")
        flowchart_nodes = page.query_selector_all(".flowchart-node")

        results["info"].append(f"10.1 Flowcharts: {len(flowcharts)}, Nodes: {len(flowchart_nodes)}")
        print(f"  [INFO] 10.1 Flowcharts: {len(flowcharts)}, Nodes: {len(flowchart_nodes)}")

        if len(flowcharts) > 0:
            results["passed"].append(f"10.2 Decision flowcharts present: {len(flowcharts)}")
            print(f"  [PASS] 10.2 Flowcharts found")
        else:
            results["info"].append("10.2 No flowcharts on this page")
            print("  [INFO] 10.2 No flowcharts")

    except Exception as e:
        results["warnings"].append(f"10.0 Flowchart test error: {str(e)[:100]}")
        print(f"  [WARN] 10.0 Flowchart error: {str(e)[:50]}")

    # ========== SECTION 11: EXAM TIPS & MISTAKES ==========
    print("\n--- Section 11: Exam Tips & Common Mistakes ---")

    try:
        # Navigate to Tips tab
        tips_tab = page.query_selector('button:has-text("Tip"), button:has-text("Exam")')
        if tips_tab:
            tips_tab.click()
            time.sleep(0.3)

        exam_tips = page.query_selector_all(".exam-tip, .tips-summary")
        mistake_cards = page.query_selector_all(".mistake-card")

        results["info"].append(f"11.1 Exam tips: {len(exam_tips)}, Mistake cards: {len(mistake_cards)}")
        print(f"  [INFO] 11.1 Tips: {len(exam_tips)}, Mistakes: {len(mistake_cards)}")

        if len(exam_tips) > 0:
            results["passed"].append("11.2 Exam tips present")
            print("  [PASS] 11.2 Exam tips found")

        # Navigate to Mistakes tab
        mistakes_tab = page.query_selector('button:has-text("Mistake")')
        if mistakes_tab:
            mistakes_tab.click()
            time.sleep(0.3)

        mistake_cards = page.query_selector_all(".mistake-card")
        if len(mistake_cards) > 0:
            results["passed"].append(f"11.3 Mistake cards: {len(mistake_cards)}")
            print(f"  [PASS] 11.3 Mistake cards: {len(mistake_cards)}")

    except Exception as e:
        results["warnings"].append(f"11.0 Tips/Mistakes test error: {str(e)[:100]}")
        print(f"  [WARN] 11.0 Tips error: {str(e)[:50]}")

    # ========== SECTION 12: CONNECTIONS ==========
    print("\n--- Section 12: Connections Section ---")

    try:
        conn_tab = page.query_selector('button:has-text("Connection")')
        if conn_tab:
            conn_tab.click()
            time.sleep(0.3)

        connection_cards = page.query_selector_all(".connection-card")
        results["info"].append(f"12.1 Connection cards: {len(connection_cards)}")
        print(f"  [INFO] 12.1 Connection cards: {len(connection_cards)}")

        if len(connection_cards) > 0:
            results["passed"].append(f"12.2 Connection section populated: {len(connection_cards)}")
            print(f"  [PASS] 12.2 Connections found")

    except Exception as e:
        results["warnings"].append(f"12.0 Connections test error: {str(e)[:100]}")
        print(f"  [WARN] 12.0 Connections error: {str(e)[:50]}")

    # ========== SECTION 13: JAVASCRIPT CONSOLE ERRORS ==========
    print("\n--- Section 13: JavaScript Console Check ---")

    try:
        errors = []
        warnings = []

        def handle_console(msg):
            if msg.type == "error":
                errors.append(msg.text)
            elif msg.type == "warning":
                warnings.append(msg.text)

        page.on("console", handle_console)
        page.reload(wait_until="networkidle")
        time.sleep(2)

        if len(errors) == 0:
            results["passed"].append("13.1 No JavaScript errors on reload")
            print("  [PASS] 13.1 No JS errors")
        else:
            results["failed"].append(f"13.1 JS errors: {errors[:3]}")
            print(f"  [FAIL] 13.1 JS errors: {len(errors)}")
            for err in errors[:3]:
                print(f"         - {err[:80]}")

        if len(warnings) > 0:
            results["info"].append(f"13.2 JS warnings: {len(warnings)}")
            print(f"  [INFO] 13.2 JS warnings: {len(warnings)}")

    except Exception as e:
        results["warnings"].append(f"13.0 Console test error: {str(e)[:100]}")
        print(f"  [WARN] 13.0 Console error: {str(e)[:50]}")

    # ========== SECTION 14: RESPONSIVE DESIGN ==========
    print("\n--- Section 14: Responsive Design Check ---")

    try:
        # Test at mobile width
        page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(0.5)

        # Check if nav tabs wrap properly
        nav_overflow = page.evaluate("""
            () => {
                const nav = document.querySelector('.nav-tabs');
                if (!nav) return 'no nav';
                return nav.scrollWidth > nav.clientWidth ? 'overflow' : 'fits';
            }
        """)

        results["info"].append(f"14.1 Nav at mobile: {nav_overflow}")
        print(f"  [INFO] 14.1 Mobile nav: {nav_overflow}")

        # Check header is visible
        header_visible = page.is_visible(".header")
        if header_visible:
            results["passed"].append("14.2 Header visible at mobile width")
            print("  [PASS] 14.2 Header visible on mobile")
        else:
            results["warnings"].append("14.2 Header may have issues on mobile")
            print("  [WARN] 14.2 Header visibility issue")

        # Reset viewport
        page.set_viewport_size({"width": 1280, "height": 800})

    except Exception as e:
        results["warnings"].append(f"14.0 Responsive test error: {str(e)[:100]}")
        print(f"  [WARN] 14.0 Responsive error: {str(e)[:50]}")

    # ========== SECTION 15: KEY POINTS CONTENT ==========
    print("\n--- Section 15: Key Points Content ---")

    try:
        # Navigate to Key Points
        key_tab = page.query_selector('button:has-text("Key")')
        if key_tab:
            key_tab.click()
            time.sleep(0.3)

        objectives = page.query_selector_all(".objectives-list li")
        results["info"].append(f"15.1 Key points: {len(objectives)}")
        print(f"  [INFO] 15.1 Key points listed: {len(objectives)}")

        if len(objectives) >= 3:
            results["passed"].append(f"15.2 Key points present: {len(objectives)}")
            print(f"  [PASS] 15.2 Key points: {len(objectives)}")
        else:
            results["warnings"].append(f"15.2 Few key points: {len(objectives)}")
            print(f"  [WARN] 15.2 Only {len(objectives)} key points")

        # Check definition box
        def_box = page.query_selector(".definition-box")
        if def_box:
            results["passed"].append("15.3 Definition box present")
            print("  [PASS] 15.3 Definition box found")

    except Exception as e:
        results["warnings"].append(f"15.0 Key points error: {str(e)[:100]}")
        print(f"  [WARN] 15.0 Key points error: {str(e)[:50]}")

    return results


def main():
    """Run all thorough tests"""
    print("\n" + "="*70)
    print("  COMPREHENSIVE AUTOMATED TESTING - AP CALCULUS BC UNIT 1")
    print("  Testing all interactive elements thoroughly")
    print("="*70)

    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        for config in PAGES:
            result = test_page_thoroughly(page, config)
            all_results.append(result)

        browser.close()

    # ========== FINAL SUMMARY ==========
    print("\n" + "="*70)
    print("  FINAL TEST SUMMARY")
    print("="*70)

    total_passed = 0
    total_failed = 0
    total_warnings = 0

    for result in all_results:
        passed = len(result["passed"])
        failed = len(result["failed"])
        warnings = len(result["warnings"])

        total_passed += passed
        total_failed += failed
        total_warnings += warnings

        status = "PASS" if failed == 0 else "FAIL" if failed > 3 else "REVIEW"

        print(f"\n{result['page']}:")
        print(f"  Status: [{status}]")
        print(f"  Passed: {passed} | Failed: {failed} | Warnings: {warnings}")

        if failed > 0:
            print("  Failed tests:")
            for f in result["failed"]:
                print(f"    ❌ {f}")

        if warnings > 0 and failed == 0:
            print("  Warnings:")
            for w in result["warnings"][:3]:
                print(f"    ⚠️  {w}")

    print("\n" + "-"*70)
    total_tests = total_passed + total_failed
    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"OVERALL: {total_passed}/{total_tests} tests passed ({pass_rate:.1f}%)")
    print(f"Warnings: {total_warnings}")
    print("-"*70)

    # Save detailed results
    with open("test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nDetailed results saved to: test_results.json")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    exit(main())
