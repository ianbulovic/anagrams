# display this help message
@help:
    just --list --unsorted

# build and run (use e.g. --host 1.2.3.4 and/or --port 1234 to customize)
@run *ARGS:
    echo '{{ ITALIC + WHITE }}Starting up...{{ NORMAL }}'
    cd src/anagrams/ui; npm i --silent; npm run build > /dev/null
    uv run --quiet anagrams {{ ARGS }}

# run in dev mode (live reloading)
@dev:
    # run the backend and frontend both in development mode,
    # and trap sigint so both are interrupted with ctrl-C
    # (interruption handling courtesy of chatGPT)
    uv run uvicorn src.anagrams.server.server:app --reload --host 0.0.0.0 & pgid1=$!; \
    cd src/anagrams/ui && npm run dev & pgid2=$!; \
    trap 'wait $pgid1 $pgid2' SIGINT; \
    wait $pgid1 $pgid2

# run pytest test suite for backend
@test:
    uv run pytest -q

# lint, format, and sync backend dependencies
@tidy:
    uv sync -q
    uv run ruff check --fix --show-fixes -q
    uv run ruff format
    # TODO lint and format UI code
