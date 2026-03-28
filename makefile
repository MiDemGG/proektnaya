.PHONY: all build run

# Команда по умолчанию (если написать просто make)
all: build run

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
