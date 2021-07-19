Steps to create docker image:
- Export the environment:
    > conda env export > environment.yml
- Build the docker image:
  docker build -t gmrecords.
- May need to associate the tag:
  docker tag gmrecords arkottke/gmrecords
- Push the image
  docker push arkottke/gmrecords

Running:
- Need to mount the working directory to the image:
  docker run -v /mnt/hdd/dsgmd:/app/working arkottke/gmrecords
  
Pushing to AWS:

- Attach "AmazonEC2ContainerRegistryFullAccess" permissions to user/group
- Add credentials from user information with "aws configure"
- Login into AWS with docker:
    aws ecr get-login-password | docker login --username AWS --password-stdin 939369860757.dkr.ecr.us-west-2.amazonaws.com
  where
    aws ecr get-login-password | docker login --username AWS --password-stdin <USER>.dkr.ecr.<REGION>.amazonaws.com
    
  <USER> and <REGION> need to be specified
