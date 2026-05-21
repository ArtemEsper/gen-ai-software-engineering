#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=============================================="
echo "  HW4: 4-Agent Pipeline"
echo "=============================================="
echo ""
echo "Usage: ./run-pipeline.sh [bug-dir]"
echo ""
echo "  bug-dir  Optional. Process a single bug directory"
echo "           (e.g., 001-date-filter-off-by-one)."
echo "           Default: process all bugs in context/bugs/."
echo ""
echo "Pipeline order:"
echo "  1. Research Verifier   -> verified-research.md"
echo "  2. Bug Fixer           -> fix-summary.md + code changes"
echo "  3. Security Verifier   -> security-report.md"
echo "  4. Unit Test Generator -> test-report.md + test files"
echo ""
echo "STATUS: stub — pipeline logic not yet implemented."
echo "        Implement in Phase 6."
exit 0
