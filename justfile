log-file := "scrapy.log"

alias cl := clean-log

dev:
    @echo "Setting up development environment..."
    @poetry shell

clean-log:
    @echo "Cleaning up and recreating log file..."
    @rm {{log-file}}
    @touch {{log-file}}

run spider: clean-log
    @echo "Running spider {{spider}}"
    scrapy crawl {{spider}} --logfile {{log-file}}
    
    