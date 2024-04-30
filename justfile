log-file := "scrapy.log"

alias cl := clean-log

dev:
    @echo "Setting up development environment..."
    touch {{log-file}} 
    @echo "Remeber to start the api. Go to  discisntock_api and run just dev, as well."

clean-log:
    @echo "Cleaning up and recreating log file..."
    @rm {{log-file}}
    @touch {{log-file}}

run spider: clean-log
    @echo "Running spider {{spider}}"
    scrapy crawl {{spider}} --logfile {{log-file}}
    
start:
    @echo "Running all spiders..."
    poetry run crawl
    
ruff:
    poetry run ruff check --fix && poetry run ruff format