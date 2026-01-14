#!/bin/bash

# Diagnose experiment failures and suggest fixes
# Usage: bash scripts/setup/diagnose_failure.sh [job_id]

echo "=================================================="
echo "Experiment Failure Diagnostics"
echo "=================================================="

JOB_ID=$1

if [ -z "$JOB_ID" ]; then
    echo "Finding recent failed jobs..."
    echo ""

    # Show recent failed jobs
    echo "Recent job status:"
    sacct -u megan.j --starttime=today --format=JobID,JobName,State,ExitCode,Start,End -X | grep -E "(FAILED|CANCELLED|TIMEOUT)"

    echo ""
    echo "Usage: $0 <job_id>"
    echo "Example: $0 36300194"
    exit 1
fi

echo "Diagnosing Job ID: $JOB_ID"
echo ""

# Get job details
echo "=== Job Information ==="
sacct -j $JOB_ID --format=JobID,JobName,State,ExitCode,Start,End,Elapsed,ReqMem,MaxRSS,ReqCPUS

echo ""
echo "=== Error Analysis ==="

# Check for log files
cd metagrouper_validation 2>/dev/null || {
    echo "ERROR: Run from project root directory"
    exit 1
}

# Find relevant log files
LOG_FILES=$(find logs/ -name "*${JOB_ID}*" 2>/dev/null)

if [ -z "$LOG_FILES" ]; then
    echo "No log files found for job $JOB_ID"
    echo "Checking SLURM default locations..."
    ls -la slurm-${JOB_ID}.out 2>/dev/null || echo "No slurm-${JOB_ID}.out found"
else
    echo "Found log files:"
    echo "$LOG_FILES"
    echo ""

    for log in $LOG_FILES; do
        echo "=== $log ==="
        echo "Last 20 lines:"
        tail -20 "$log"
        echo ""
    done
fi

echo ""
echo "=== Common Failure Patterns ==="

# Check for common issues
if grep -q "out of memory\|OutOfMemoryError\|killed" $LOG_FILES 2>/dev/null; then
    echo "🔍 MEMORY ISSUE DETECTED"
    echo "Solutions:"
    echo "  - Increase memory in SLURM script (#SBATCH --mem=)"
    echo "  - Check if --mem-per-cpu vs --mem is correct"
    echo "  - Reduce number of parallel processes"
fi

if grep -q "time limit\|DUE TO TIME LIMIT\|TIMEOUT" $LOG_FILES 2>/dev/null; then
    echo "🔍 TIME LIMIT ISSUE DETECTED"
    echo "Solutions:"
    echo "  - Increase time limit in SLURM script (#SBATCH --time=)"
    echo "  - Check if job is hanging (infinite loop/deadlock)"
    echo "  - Optimize parameters for faster execution"
fi

if grep -q "No space left\|disk full\|Disk quota exceeded" $LOG_FILES 2>/dev/null; then
    echo "🔍 DISK SPACE ISSUE DETECTED"
    echo "Solutions:"
    echo "  - Check disk usage: du -sh ."
    echo "  - Clean up intermediate files"
    echo "  - Move to different filesystem"
fi

if grep -q "Permission denied\|cannot access\|No such file" $LOG_FILES 2>/dev/null; then
    echo "🔍 FILE ACCESS ISSUE DETECTED"
    echo "Solutions:"
    echo "  - Check file permissions: ls -la"
    echo "  - Verify paths are correct"
    echo "  - Check if files were deleted during run"
fi

if grep -q "conda\|environment\|command not found" $LOG_FILES 2>/dev/null; then
    echo "🔍 ENVIRONMENT ISSUE DETECTED"
    echo "Solutions:"
    echo "  - Check conda environment activation"
    echo "  - Verify tools are installed: megahit --version, flye --version"
    echo "  - Check PATH and module loading"
fi

echo ""
echo "=== Resource Usage Analysis ==="

# Get resource usage details
MAXRSS=$(sacct -j $JOB_ID --format=MaxRSS --noheader --parsable2 | head -1)
REQMEM=$(sacct -j $JOB_ID --format=ReqMem --noheader --parsable2 | head -1)
ELAPSED=$(sacct -j $JOB_ID --format=Elapsed --noheader --parsable2 | head -1)

echo "Memory requested: $REQMEM"
echo "Memory used (max): $MAXRSS"
echo "Time elapsed: $ELAPSED"

echo ""
echo "=== Quick Recovery Commands ==="
echo "1. Check current experiment status:"
echo "   bash scripts/setup/resume_experiment.sh"
echo ""
echo "2. Clean up and restart failed stage:"
echo "   # (commands will be suggested by resume script)"
echo ""
echo "3. Monitor new jobs:"
echo "   watch squeue -u megan.j"