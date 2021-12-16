DEPLOYMENT_ID=gmrecords
AWS_ID=691237311722
AWS_REGION=us-west-1

ECR_REPO_ID=$(DEPLOYMENT_ID)
ECR_REPO_URL=$(AWS_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

build: 
	docker compose build $(DEPLOYMENT_ID)

run: build
	docker compose run --rm --entrypoint bash $(DEPLOYMENT_ID)

test: build
	docker compose up --remove-orphans $(DEPLOYMENT_ID)

terraform:
	cd cloudburst/terraform
	terraform apply
	cd ../../
	
push: build
	docker tag $(DEPLOYMENT_ID) arkottke/$(DEPLOYMENT_ID)
	docker push arkottke/$(DEPLOYMENT_ID):latest

push-ecr: build
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REPO_URL)
	docker tag $(DEPLOYMENT_ID):latest $(ECR_REPO_URL)/$(ECR_REPO_ID):latest
	docker push $(ECR_REPO_URL)/$(ECR_REPO_ID):latest
