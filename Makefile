build:
	docker build -t biwenger_api_image .
	docker run -d --name biwenger_api_container -p 80:80 biwenger_api_image

restart:
	docker stop biwenger_api_container
	docker rm biwenger_api_container
	docker build -t biwenger_api_image .
	docker run -d --name biwenger_api_container -p 80:80 biwenger_api_image
