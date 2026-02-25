#!/bin/bash
# VeritasAd Full Modernization Setup Script (2026)
# Migrates Backend, Bot, and Parsers to UV, and prepares Frontend.

echo "рџљЂ Starting VeritasAd Modernization Setup..."

# 1. Initialize UV for all Python components
for dir in backend bot parsers; do
    if [ -d "$dir" ]; then
        echo "рџ“¦ Setting up UV in $dir..."
        cd $dir
        uv sync
        cd ..
    fi
done

# 2. Frontend setup (Assumes npm/node is installed)
if [ -d "frontend" ]; then
    echo "рџ–јпёЏ Setting up Frontend (Next.js 15 + React 19)..."
    cd frontend
    # npm install --legacy-peer-deps # Use this if peer deps are annoying
    echo "Next steps: Run 'cd frontend && npm install' to finalize frontend update."
    cd ..
fi

echo "тЬ… Modernization complete!"
echo "Use 'uv run <command>' in python dirs to start services."
echo "Use 'npm run dev -- --turbo' in frontend dir for fast development."
