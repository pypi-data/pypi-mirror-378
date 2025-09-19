-include .env
export

test:
	export IAI_FS_BUCKET_NAME=test-bucket && \
	docker compose up -d --wait minio && \
	PACKAGE_DIRS="logging,metrics,file_store,auth"; \
	IFS=,; for dir in $$PACKAGE_DIRS; do \
	uv run pytest \
		src/i_dot_ai_utilities/$$dir \
		--cov-config=.coveragerc \
		--cov src/i_dot_ai_utilities/$$dir \
		--cov-report term-missing \
		--cov-fail-under 75 || exit 1; \
	done; \
	docker compose down minio

lint:
	uv run ruff format --check
	uv run ruff check
	uv run mypy src/i_dot_ai_utilities/ --ignore-missing-imports
	uv run bandit -ll -r src/i_dot_ai_utilities
