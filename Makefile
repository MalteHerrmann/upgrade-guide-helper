# Format codebase
format:
	@echo "formatting codebase"
	@black .

# Lint codebase
lint:
	@echo "linting codebase"
	@pylint .

# Runs the tool
run:
	@python3
