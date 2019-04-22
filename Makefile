# META ]--------------------------------------------------------------------------------------------
.PHONY: help.stub help
help.stub: help

RED="\033[91m"
END="\033[0m"

help:
	@echo "help         Display this message."
	@echo "run          Generate a collage for the well know YouTuber Gigguk."
	@echo "test         Run testing suite."
	@echo "clean        Cleans userdata anime lists in repository. Image and metadata is"
	@echo "             preserved."
	@echo "deps         Install dependencies."

# EXAMPLES ]----------------------------------------------------------------------------------------
.PHONY: run
run: test deps
	python ScriptTaste.py gigguk

# CORE ]--------------------------------------------------------------------------------------------
.PHONY: test clean deps
test:
	black --diff .
	pylint *.py

clean:
	black .
	@echo $(RED)"Deleting users data:"$(END)
	@for dir in data/users output ; do \
      for file in $$dir/* ; do \
          if [ $$(basename $$file | head -c 6) != "gigguk" ]; then \
					    echo $(RED)"    " $$file$(END); \
              rm $$file; \
          fi \
      done \
  done

deps:
	pip install -r requirements.txt
