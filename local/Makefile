.PHONY: install start stop reload nuke help

.DEFAULT_GOAL := help

install: ## Generate systemd units and copy configs for VictoriaMetrics
	podman quadlet install victoriametrics-data.volume victoriametrics.container
	install -d -m 700 -o $(USER) ~/.config/bobor/dashboards
	cp dashboard.json ~/.config/bobor/dashboards/
	cp prometheus.yml ~/.config/bobor/

start: reload ## Start VictoriaMetrics container and Flask app
	systemctl --user start victoriametrics.service
	$(MAKE) -C ../ serve

stop: ## Stop VictoriaMetrics container
	systemctl --user stop victoriametrics.service

browse: ## Open VictoriaMetrics in a browser
	xdg-open "http://127.0.0.1:8428/vmui/#/dashboards"

reload: ## Reload systemd unit files
	systemctl --user daemon-reload

nuke: stop reload ## Remove everything
	podman quadlet rm victoriametrics-data.volume victoriametrics.container
	rm -rf ~/.config/bobor

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

%: ## Avoid "nothing to be done" for any target that doesn't have a rule
	@:
