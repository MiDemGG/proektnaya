.PHONY: all build run install-docker clean

# Команда по умолчанию
all: build run

# Установка Docker для Debian/Ubuntu
install-docker:
	@echo "Обновление системы и установка curl..."
	sudo apt-get update && sudo apt-get install -y curl
	@echo "Загрузка и запуск официального скрипта установки Docker..."
	curl -fsSL https://get.docker.com | sudo sh
	@echo "Добавление текущего пользователя в группу docker..."
	sudo usermod -aG docker $$USER
	@echo "✅ Docker установлен! Пожалуйста, перезайдите в систему, чтобы права применились."

# Сборка образа
build:
	docker build -t xml-parser .

# Запуск контейнера
run:
	docker run --rm \
	  -v "$$(pwd):/srv" \
	  -e GEMINI_API_KEY="AIzaSyAVf0HyEDCZfDLiD0hoW5gHydlrQRIfiLs" \
	  -e https_proxy="http://194.147.214.150:41810" \
	  xml-parser

# Очистка сгенерированных XML-файлов
clean:
	rm -rf XML/*.xml
	@echo "Папка XML очищена."
